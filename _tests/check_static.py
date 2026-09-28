# -*- coding: utf-8 -*-
"""LazyTools static checks — broken links, missing assets, SEO tags, JS syntax.

    python _tests/check_static.py

Walks every generated .html, verifies every local href/src resolves, and checks
each page carries a canonical, title, meta description, JSON-LD and ad slots.
Exits non-zero on any problem.
"""
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

print("HTML files checked : %d" % len(html_files))
print("Local refs checked : %d" % checked)
print("Inline JS blocks   : %d (syntax-checked)" % js_count)
print("Broken links / SEO : %d" % len(issues))
for i in issues:
    print("  ! " + i)
print("JS syntax failures : %d" % len(node_failures))
for i in node_failures:
    print("  ! " + i)

sys.exit(1 if (issues or node_failures) else 0)
