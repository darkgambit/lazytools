# -*- coding: utf-8 -*-
"""LazyTools static checks — broken links, missing assets, SEO tags, JS syntax.

    python _tests/check_static.py

Walks every generated .html, verifies every local href/src resolves, and checks
each page carries a canonical, title, meta description, JSON-LD and ad slots.
Exits non-zero on any problem.
"""
import datetime
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SKIP_DIRS = {".git", "node_modules", "_generator", "_tests", ".wrangler", ".netlify"}
HREF = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"')
INLINE_JS = re.compile(r'<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>(.*?)</script>', re.S)

issues = []
checked = 0

html_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    html_files += [os.path.join(dirpath, f) for f in filenames if f.endswith(".html")]
html_files.sort()

tmp = tempfile.mkdtemp(prefix="lt_js_")
js_count = 0
node_failures = []

for path in html_files:
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    txt = open(path, encoding="utf-8").read()

    for target in HREF.findall(txt):
        t = target.strip()
        if not t or t.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:", "//")):
            continue
        checked += 1
        local = os.path.join(ROOT, t.lstrip("/")) if t.startswith("/") else os.path.join(os.path.dirname(path), t)
        local = local.split("#")[0].split("?")[0]
        if t.endswith("/") or os.path.isdir(local):
            local = os.path.join(local, "index.html")
        if not os.path.exists(local):
            issues.append("%s -> broken link %s" % (rel, t))

    for tag, present in [("title", "<title>" in txt),
                         ("meta description", 'name="description"' in txt)]:
        if not present:
            issues.append("%s -> missing %s" % (rel, tag))
    # every indexable page needs a canonical; the 404 page must NOT have one and
    # must carry noindex instead (a canonical on a 404 canonicalises nothing).
    if rel == "404.html":
        if 'name="robots" content="noindex"' not in txt:
            issues.append("404.html -> missing noindex")
        if '<link rel="canonical"' in txt:
            issues.append("404.html -> must not carry a canonical")
    elif '<link rel="canonical"' not in txt:
        issues.append("%s -> missing canonical" % rel)

    # The canonical must resolve to a real file. This is the guard for the bug where
    # canonicals used trailing slashes (/about/) while the files were about.html:
    # Cloudflare Pages 308-redirects those, so every canonical pointed at a redirect.
    m = re.search(r'<link rel="canonical" href="([^"]+)"', txt)
    if m:
        after_host = m.group(1).split("://", 1)[-1]
        path = after_host.split("/", 1)[1] if "/" in after_host else ""
        path = path.split("#")[0].split("?")[0]
        raw = path.lstrip("/")
        if raw == "":
            ok = os.path.exists(os.path.join(ROOT, "index.html"))
        elif raw.endswith("/"):
            # a trailing slash must be backed by a real directory index — Cloudflare
            # Pages 308-redirects /about/ to /about, so this is NOT the final URL.
            ok = os.path.exists(os.path.join(ROOT, raw, "index.html"))
        else:
            ok = (os.path.exists(os.path.join(ROOT, raw))
                  or os.path.exists(os.path.join(ROOT, raw + ".html")))
        if not ok:
            issues.append("%s -> canonical %s resolves to no file" % (rel, m.group(1)))
    # JSON-LD is required on the home page and every tool page; 404/about/privacy don't need it
    if (rel.startswith("tools/") or rel == "index.html") and 'application/ld+json' not in txt:
        issues.append("%s -> missing JSON-LD" % rel)
    if rel.startswith("tools/"):
        for slot in ("top", "middle", "bottom"):
            if 'data-slot="%s"' % slot not in txt:
                issues.append("%s -> missing ad slot %s" % (rel, slot))

    # Site-wide footer. It is not decoration: it carries the only links to /about and
    # /privacy from every page, plus the "Popular tools" list that feeds the internal
    # link graph. tool_page() originally forgot to render it, so all 20 tool pages
    # shipped with no footer at all and /privacy ended up with two inbound links —
    # on the exact page an ad network reviewer opens.
    m_foot = re.search(r'<footer class="site-footer">.*?</footer>', txt, re.S)
    if not m_foot:
        issues.append("%s -> missing the site footer" % rel)
    else:
        foot = m_foot.group(0)
        for dest in ("about.html", "privacy.html"):
            if dest not in foot:
                issues.append("%s -> footer does not link to %s" % (rel, dest))
        # footer() emits plain <li><a> entries (5 popular tools + 3 site links), not
        # tool-card markup — so count anchors, not classes.
        if len(re.findall(r"<a\s", foot)) < 8:
            issues.append("%s -> footer is missing its popular-tools / site links" % rel)

    for i, code in enumerate(INLINE_JS.findall(txt)):
        if not code.strip():
            continue
        js_count += 1
        f = os.path.join(tmp, rel.replace("/", "__") + "__%d.js" % i)
        open(f, "w", encoding="utf-8").write(code)
        r = subprocess.run(["node", "--check", f], capture_output=True, text=True)
        if r.returncode != 0:
            node_failures.append("%s (block %d): %s" % (rel, i, (r.stderr or "").strip().splitlines()[:2]))

for f in ("assets/app.js", "assets/ads.js"):
    r = subprocess.run(["node", "--check", os.path.join(ROOT, f)], capture_output=True, text=True)
    if r.returncode != 0:
        node_failures.append("%s: %s" % (f, (r.stderr or "").strip().splitlines()[:2]))

# generator invariant: app.js must not be deferred (see _generator/build.py)
build = open(os.path.join(ROOT, "_generator", "build.py"), encoding="utf-8").read()
if re.search(r'<script\s+defer\s+src="__REL__assets/app\.js"', build):
    issues.append("_generator/build.py -> app.js is deferred again; tool pages will throw '$id is not defined'")

# generator invariant: every __TOKEN__ in a template must have been substituted.
# Adding a placeholder to head()/a page template and forgetting its .replace() ships the
# literal token into production HTML — invisible in a browser and very easy to miss.
# Requires a trailing "__" so JS identifiers like window.__LAZYTOOLS_ADS don't false-positive.
PLACEHOLDER = re.compile(r"__[A-Z][A-Z_]{2,}__")
for rel in html_files:
    txt = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    for token in sorted(set(PLACEHOLDER.findall(txt))):
        issues.append("%s -> unsubstituted template token %s" % (rel, token))

# sitemap.xml must carry a valid ISO <lastmod> on every URL. <lastmod> is the only freshness
# signal the file has — Google ignores <changefreq> and <priority> — and it is what tells a
# crawler to come back. The original sitemap omitted it entirely, so a brand-new site that
# changed daily was announcing nothing at all.
sitemap_path = os.path.join(ROOT, "sitemap.xml")
if os.path.exists(sitemap_path):
    sm = open(sitemap_path, encoding="utf-8").read()
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    mods = re.findall(r"<lastmod>(.*?)</lastmod>", sm)
    if not locs:
        issues.append("sitemap.xml -> no <loc> entries")
    if len(mods) != len(locs):
        issues.append("sitemap.xml -> %d <loc> but %d <lastmod>; every URL needs one"
                      % (len(locs), len(mods)))
    for m in mods:
        try:
            datetime.date.fromisoformat(m.strip())
        except ValueError:
            issues.append("sitemap.xml -> <lastmod> %r is not a valid ISO date" % m)

# Amazon Associates invariants. Both failure modes are silent and one is fatal:
#   * An untagged link still sends the visitor to Amazon but earns NOTHING. There is no
#     error, no log and no symptom — you simply never get paid for that click.
#   * A missing disclosure is a listed reason for account closure, and a lapsed Associates
#     ID is never reinstated (you reapply with a NEW tag and must swap every link).
#   * A hardcoded price or star rating is also a closure trigger, so nothing in a gear block
#     may contain one.
# These are asserted against the GENERATED HTML, not the generator source, so a broken
# gear_block() cannot slip through.
_m = re.search(r'^AMAZON_TAG\s*=\s*"([^"]*)"', build, re.M)
AMZ_TAG = _m.group(1) if _m else ""
_d = re.search(r'^AMAZON_DISCLOSURE\s*=\s*"([^"]*)"', build, re.M)
AMZ_DISCLOSURE = _d.group(1) if _d else ""
amz_links = 0
if AMZ_TAG:
    PRICEY = re.compile(r"\$\s?\d|★|stars\b|out of 5", re.I)
    # Affiliate links are exactly the ones gear_block() emits, and they carry class="gear-link".
    # Matching on the class rather than the domain matters: /privacy links to Amazon's *help*
    # pages for legal reference, which is an informational link and must NOT carry a tracking
    # tag. Matching any amazon.com anchor flagged that as a defect — a false positive.
    AFF = re.compile(r'<a[^>]*class="gear-link"[^>]*>')
    # ...but a hand-pasted product or search link would bypass the class, and that is precisely
    # the silent failure worth catching. So any OTHER amazon link whose URL has an affiliate
    # shape is reported, while a help-page link is left alone.
    AFFILIATE_SHAPED = re.compile(r"amazon\.[a-z.]+/(dp/|s\?)", re.I)
    for rel in html_files:
        txt = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        anchors = AFF.findall(txt)
        if anchors:
            amz_links += len(anchors)
            if AMZ_DISCLOSURE and AMZ_DISCLOSURE not in txt:
                issues.append("%s -> %d Amazon affiliate link(s) but no required disclosure text"
                              % (rel, len(anchors)))
            for a in anchors:
                href = re.search(r'href="([^"]*)"', a)
                href = href.group(1) if href else ""
                if ("tag=" + AMZ_TAG) not in href:
                    issues.append("%s -> Amazon link without the tracking tag (earns nothing): %s"
                                  % (rel, href))
                if "sponsored" not in a or "noopener" not in a:
                    issues.append("%s -> Amazon link missing rel=\"sponsored noopener\"" % rel)
        for a in re.findall(r"<a[^>]*amazon\.[^>]*>", txt):
            if "gear-link" in a:
                continue
            href = re.search(r'href="([^"]*)"', a)
            href = href.group(1) if href else ""
            if AFFILIATE_SHAPED.search(href):
                issues.append("%s -> Amazon product/search link that is NOT a gear-link, so it is "
                              "probably untagged: %s" % (rel, href))
        for block in re.findall(r'<ul class="gear-list">.*?</ul>', txt, re.S):
            hit = PRICEY.search(block)
            if hit:
                issues.append("%s -> gear block contains a price/rating (%r); that is an "
                              "Amazon closure trigger" % (rel, hit.group(0)))

# --------------------------------------------------------------------------- #
#  ad config guards (assets/ads.js)
# --------------------------------------------------------------------------- #
# Two traps in the ad config that are invisible in a browser until they cost money, and
# one policy line that is easy to cross by pasting the wrong snippet from the dashboard.
ADS_JS = os.path.join(ROOT, "assets", "ads.js")
ads_src = open(ADS_JS, encoding="utf-8").read()

# 1. ONE KEY = ONE SLOT. Adsterra's banner snippet assigns the GLOBAL `atOptions` and then
#    loads a script that reads it back, so the same unit pasted into two slots means the
#    second assignment overwrites the first and only ONE of the two ever renders. The
#    duplicate is silent: the slot still gets its iframe, it just never fills.
ad_keys = re.findall(r"'key'\s*:\s*'([0-9a-f]+)'", ads_src)
dupes = sorted({k for k in ad_keys if ad_keys.count(k) > 1})
if dupes:
    issues.append("assets/ads.js -> ad unit key reused (%s); atOptions is a global, so only "
                  "ONE of them will render — one unit per slot"
                  % ", ".join("%s x%d" % (k, ad_keys.count(k)) for k in dupes))

# 2. BANNER AND NATIVE BANNER ONLY. Popunder / Social Bar tags hijack clicks site-wide and
#    Direct Links are a bare URL with nowhere on the page to live; both are excluded by
#    policy. They are recognisable by PATH SHAPE, not by host — the native banner sits on
#    the same profitableratecpmnetwork.com host as the popunder and differs only in path.
#
#    The character class excludes a backslash as well as quotes: these URLs live inside
#    escaped JS string literals (`src=\"https://…/invoke.js\"`), so a naive match ends with
#    a trailing `\` and the legitimate native unit reads as unrecognised. That false
#    positive was caught by negative-testing this guard, not by running it on the real file.
for url in re.findall(r"https?://[^\s\"'<>\\]+", ads_src):
    if "profitableratecpmnetwork.com" not in url:
        continue
    path = re.sub(r"^https?://[^/]+", "", url)
    if re.match(r"^/[0-9a-f]{32}/invoke\.js$", path):
        continue                                   # the native banner — allowed
    if re.match(r"^/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]+\.js$", path):
        issues.append("assets/ads.js -> Popunder/Social Bar tag (%s): excluded by policy, it "
                      "hijacks clicks site-wide" % url)
    elif "key=" in url:
        issues.append("assets/ads.js -> Direct Link / Smartlink (%s): excluded by policy, there "
                      "is nowhere on the page for it to live" % url)
    else:
        issues.append("assets/ads.js -> unrecognised profitableratecpmnetwork.com tag (%s); if "
                      "this is a new banner/native unit, teach this guard its path shape" % url)

print("Ad units           : %d keys, %d distinct (banner/native only)"
      % (len(ad_keys), len(set(ad_keys))))
print("HTML files checked : %d" % len(html_files))
print("Local refs checked : %d" % checked)
print("Inline JS blocks   : %d (syntax-checked)" % js_count)
print("Amazon links       : %d (tagged, disclosed, price-free)" % amz_links)
print("Broken links / SEO : %d" % len(issues))
for i in issues:
    print("  ! " + i)
print("JS syntax failures : %d" % len(node_failures))
for i in node_failures:
    print("  ! " + i)

sys.exit(1 if (issues or node_failures) else 0)
