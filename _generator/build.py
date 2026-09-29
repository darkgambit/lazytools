#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LazyTools static site generator.

Usage:   python3 _generator/build.py

Before deploying:
  1. Edit SITE_URL below to your real domain (e.g. https://lazytools.com)
  2. Edit CONTACT_EMAIL below
  3. Re-run this script — it regenerates every page, canonical URLs and sitemap.

Adding a new tool = adding one dict to tools_core.py / tools_extra.py and re-running.
"""
import json
import os
import sys
import datetime
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools_core import TOOLS_CORE
from tools_extra import TOOLS_EXTRA

# --------------------------------------------------------------------------- #
#  SITE CONFIGURATION — edit these two lines before you deploy!               #
# --------------------------------------------------------------------------- #
SITE_NAME    = "LazyTools"
# Decided 2026-09-28: no custom domain — the site ships on Cloudflare's free *.pages.dev
# subdomain. NOTE: the exact hostname is assigned by `wrangler pages project create`. If
# "lazytools" is already taken there, Cloudflare appends a suffix, so this line MUST be
# corrected to the real hostname before the site is indexed. Canonicals, the sitemap,
# og:image and robots.txt all derive from it.
SITE_URL     = "https://lazytools.pages.dev"
CONTACT_EMAIL = "kingripper9@gmail.com"

# Cloudflare Web Analytics (chosen 2026-09-28). Cookieless, so no consent banner is needed
# and privacy.html already covers aggregate analytics. An empty string emits no analytics tag
# at all, so blank is safe to ship. Injected into every page's <head> via the __ANALYTICS__
# token in head() — never paste a tracking snippet into a page by hand, the pages are generated.
ANALYTICS_CODE = """<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "acfbc9d4873643d981ed1837233ae31c"}'></script>"""

# IndexNow — instant "these URLs changed" pings to Bing, Yandex, Seznam and Naver. No account
# required: ownership is proven by serving https://<host>/<key>.txt containing exactly this key,
# so main() generates that file and it must stay publicly readable (do NOT add it to the
# robots.txt Disallow list). Submit with:  python _generator/indexnow.py
INDEXNOW_KEY = "d328e91fa97904481ce908132cc8af34"

# Search-engine ownership proofs, injected into every page's <head> by verification_tags().
# Google Search Console only checks the property URL, but carrying the tag site-wide means a
# rebuild can never drop it from the one page that matters. Bing can be verified by importing
# from GSC, or by pasting its own token into BING_VERIFICATION.
GOOGLE_VERIFICATION = "2gqxtbCOJQVOaYka5Ycs_7T08h4rrPWn6Ug1dtAC8Go"
BING_VERIFICATION = ""
# ---------------------------------------------------------------------------- #

BUILD_DATE = datetime.date.today().strftime("%d %B %Y")

TOOLS = TOOLS_CORE + TOOLS_EXTRA
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

DESCRIPTION = ("LazyTools is a collection of free online tools — calculators, converters and "
               "generators that run entirely in your browser. No signup, no uploads, no limits.")

def slug_path(t):
    # NOTE: no trailing slash. Cloudflare Pages (and GitHub Pages) serve
    # /tools/<slug> with a 200 and 308-redirect both /tools/<slug>/ and
    # /tools/<slug>.html to it. A canonical must point at the final 200 URL,
    # so it must be extensionless and slashless. Verified with `wrangler pages dev`.
    return "/tools/" + t["slug"]

# --------------------------------------------------------------------------- #
#  shared blocks
# --------------------------------------------------------------------------- #
def logo_svg(size=26):
    return ('<svg width="%d" height="%d" viewBox="0 0 64 64" aria-hidden="true">'
            '<rect width="64" height="64" rx="14" fill="#0a0f1e"/>'
            '<path d="M42 10a21 21 0 1 0 12.5 33.5A17 17 0 1 1 42 10z" fill="#f5b53f"/>'
            '<circle cx="19" cy="46" r="4.5" fill="#8fa4ff"/>'
            '<path d="M22.2 42.8l8.6-8.6" stroke="#8fa4ff" stroke-width="4.5" stroke-linecap="round"/>'
            '</svg>') % (size, size)

def header(rel, active):
    tools_cls = "nav-a-active" if active == "tools" else ""
    about_cls = "nav-a-active" if active == "about" else ""
    return ('<header class="site-header"><div class="header-inner">'
            '<a class="logo" href="' + rel + 'index.html">' + logo_svg() + '<span>Lazy<span class="dot">Tools</span></span></a>'
            '<nav class="nav">'
            '<a href="' + rel + 'index.html" class="' + tools_cls + '">All Tools</a>'
            '<a href="' + rel + 'about.html" class="' + about_cls + '">About</a>'
            '<button class="theme-btn" id="theme-btn" onclick="toggleTheme()" title="Toggle dark / light theme" aria-label="Toggle theme">☀️</button>'
            '</nav></div></header>')

def footer(rel):
    pop = [t for t in TOOLS if t.get("popular")][:5]
    links = "".join('<li><a href="' + rel + ("tools/" + t["slug"] + ".html") + '">' + t["name"] + "</a></li>" for t in pop)
    return ('<footer class="site-footer"><div class="container">'
            '<div class="footer-grid">'
            '<div style="max-width:300px">'
            '<a class="logo" href="' + rel + 'index.html">' + logo_svg(22) + '<span>Lazy<span class="dot">Tools</span></span></a>'
            '<p style="color:var(--muted);font-size:.9rem;margin-top:12px">Free online tools that run entirely in your browser. '
            'Up 24/7 — they work while you sleep, and while we do too.</p></div>'
            '<div><h4>Popular tools</h4><ul>' + links + "</ul></div>"
            '<div><h4>Site</h4><ul>'
            '<li><a href="' + rel + 'index.html">All tools</a></li>'
            '<li><a href="' + rel + 'about.html">About &amp; disclosures</a></li>'
            '<li><a href="' + rel + 'privacy.html">Privacy policy</a></li>'
            "</ul></div>"
            "</div>"
            '<div class="footer-bottom"><span>© <span id="year">2025</span> ' + SITE_NAME + ". Made for the whole planet.</span>"
            "<span>Supported by ads &amp; affiliate links — see <a href='" + rel + "about.html#disclosure'>disclosures</a>.</span></div>"
            "</div></footer>")

def head(title, desc, path, rel, keywords=None, jsonld=None, noindex=False):
    url = SITE_URL + path
    kw = ("<meta name=\"keywords\" content=\"" + keywords + "\">\n    ") if keywords else ""
    # a 404 page must not carry a canonical (there is nothing to canonicalise) —
    # it gets noindex instead, so it can never be indexed as a duplicate.
    canon = ('<meta name="robots" content="noindex">' if noindex
             else '<link rel="canonical" href="' + url + '">')
    og = ('<meta property="og:type" content="website">'
          '<meta property="og:title" content="' + title + '">'
          '<meta property="og:description" content="' + desc + '">'
          '<meta property="og:url" content="' + url + '">'
          '<meta property="og:site_name" content="' + SITE_NAME + '">'
          '<meta property="og:image" content="' + SITE_URL + '/og-image.png">'
          '<meta property="og:image:width" content="1200">'
          '<meta property="og:image:height" content="630">'
          '<meta name="twitter:card" content="summary_large_image">'
          '<meta name="twitter:title" content="' + title + '">'
          '<meta name="twitter:description" content="' + desc + '">'
          '<meta name="twitter:image" content="' + SITE_URL + '/og-image.png">')
    ld = ""
    if jsonld:
        ld = "\n    ".join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False) + "</script>" for b in jsonld)
    # Analytics tag — empty until ANALYTICS_CODE is filled in at Step 5. Emitted on every
    # page including the 404, since a 404 hit is itself a signal that someone followed a
    # dead link. Blank config means zero bytes of third-party script on the site.
    an = ("\n    " + ANALYTICS_CODE) if ANALYTICS_CODE else ""
    vf = verification_tags()
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>__TITLE__</title>
    <meta name="description" content="__DESC__">
    __KW____CANON__
    __OG____VERIFY__
    <meta name="theme-color" content="#0a0f1e">
    <link rel="icon" href="__REL__favicon.svg" type="image/svg+xml">
    <link rel="manifest" href="__REL__site.webmanifest">
    <link rel="stylesheet" href="__REL__assets/style.css">
    <script src="__REL__assets/app.js"></script>
    <!-- app.js MUST stay non-deferred: tool pages run their init inline at the end of
         <body>, which executes before any deferred script. It also sets the theme
         class before first paint, avoiding a flash of the wrong theme. -->
    <script defer src="__REL__assets/ads.js"></script>
    __LD____ANALYTICS__
</head>
<body>
""".replace("__TITLE__", title).replace("__DESC__", esc_attr(desc)).replace("__URL__", url) \
   .replace("__KW__", kw).replace("__CANON__", canon).replace("__OG__", og).replace("__REL__", rel).replace("__LD__", ld) \
   .replace("__ANALYTICS__", an).replace("__VERIFY__", vf)

def esc_attr(s):
    return s.replace('"', "&quot;")

def verification_tags():
    """Search-engine ownership proofs. Empty config emits nothing at all."""
    out = []
    if GOOGLE_VERIFICATION:
        out.append('<meta name="google-site-verification" content="' + GOOGLE_VERIFICATION + '">')
    if BING_VERIFICATION:
        out.append('<meta name="msvalidate.01" content="' + BING_VERIFICATION + '">')
    return ("\n    " + "\n    ".join(out)) if out else ""

# Intended ad dimensions per slot. assets/ads.js uses these to size the isolation iframe it
# renders third-party ad code into. The iframe is capped at 100% width, so a 728px leaderboard
# simply clips on a phone rather than breaking the layout.
AD_SIZES = {"top": (728, 90), "middle": (300, 250), "bottom": (300, 250)}

# Adsterra publisher account ID (owner, 2026-09-28). Used ONLY by ads_txt() below — the ad
# CODE itself never lives here, it goes in assets/ads.js. Leave blank to omit the ads.txt line.
ADSTERRA_PUBLISHER_ID = "6084129"

# Amazon Associates tracking ID (owner, 2026-09-28). Every Amazon link on the site is built
# from this one constant — deliberately, because of a hard Amazon rule:
#
#   If a new Associates account is withdrawn for failing to refer 3 qualifying sales within
#   180 days, Amazon does NOT reinstate that ID. You reapply and get a NEW tag, and EVERY link
#   still carrying the old tag earns nothing. So the tag must be swappable in one place.
#
# Empty string disables all Amazon links site-wide and hides the "Recommended gear" blocks,
# which is the correct state if the account lapses — links pointing at a dead tag are worse
# than no links, because they still send visitors to Amazon while earning nothing.
AMAZON_TAG = "lazytool-20"
AMAZON_DOMAIN = "www.amazon.com"

def ad(slot):
    w, h = AD_SIZES.get(slot, (300, 250))
    return ('<div class="ad-slot" data-slot="' + slot + '" data-w="' + str(w) +
            '" data-h="' + str(h) + '" aria-label="Advertisement"></div>')

# --------------------------------------------------------------------------- #
#  Amazon Associates
# --------------------------------------------------------------------------- #
# Amazon's Program Policies make two things mandatory, and BOTH are listed reasons for account
# closure if you get them wrong:
#   1. A clear disclosure on any page carrying affiliate links.
#   2. NO hardcoded prices and NO star ratings. Showing either without pulling it live from an
#      Amazon API is a closure trigger, so the product data in tools_*.py carries a name and a
#      reason to recommend it — never a price, never a rating.
AMAZON_DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

def amazon_link(item):
    """Build one affiliate link. Returns "" when AMAZON_TAG is blank, which hides every link.

    Two shapes, chosen by the data:
      - item has "asin" -> a canonical product link:  /dp/<ASIN>?tag=...
      - otherwise       -> a search link:             /s?k=<query>&tag=...

    Search links are an Amazon-sanctioned link type (SiteStripe generates them), and they are the
    honest default here: inventing an ASIN would send visitors to the wrong product, which is
    worse than a search page. Swap any entry to a real ASIN once you have one from SiteStripe.

    rel="sponsored noopener nofollow" — Google requires affiliate links to be marked `sponsored`,
    and an unmarked paid link is a ranking risk. Amazon does not ask for it; Google does.
    rel="noopener" is required whenever target="_blank" is used.
    """
    if not AMAZON_TAG:
        return ""
    if item.get("asin"):
        url = "https://" + AMAZON_DOMAIN + "/dp/" + item["asin"] + "?tag=" + AMAZON_TAG
    else:
        url = ("https://" + AMAZON_DOMAIN + "/s?k=" +
               urllib.parse.quote_plus(item["query"]) + "&tag=" + AMAZON_TAG)
    return ('<a class="gear-link" href="' + esc_attr(url) +
            '" rel="sponsored noopener nofollow" target="_blank">' + item["label"] + "</a>")

def gear_block(t):
    """Optional per-tool product recommendations.

    Rendered ONLY when the tool defines a "gear" list AND a tag is configured. A tool without
    "gear" gets no section at all, so adding this costs the other 13 pages nothing — and no page
    ever ships an empty "Recommended gear" heading, which would be worse than not having one.
    """
    items = t.get("gear")
    if not items or not AMAZON_TAG:
        return ""
    lis = "".join("<li>" + amazon_link(i) + ' <span class="gear-why">' + i["why"] + "</span></li>"
                  for i in items)
    return ('<section class="gear">\n'
            '  <h2 class="section">Recommended gear</h2>\n'
            '  <p class="gear-disclosure">' + AMAZON_DISCLOSURE + '</p>\n'
            '  <ul class="gear-list">' + lis + '</ul>\n'
            '</section>\n')

def tool_card(t, rel):
    return ('<a class="tool-card" href="' + rel + "tools/" + t["slug"] + '.html" '
            'data-slug="' + t["slug"] + '" data-cat="' + t["cat"] + '" '
            'data-name="' + esc_attr(t["name"]) + '" data-keywords="' + esc_attr(t["short"] + " " + t["keywords"]) + '">'
            '<span class="ico">' + t["icon"] + "</span>"
            "<h3>" + t["name"] + "</h3><p>" + t["short"] + "</p></a>")

# --------------------------------------------------------------------------- #
#  tool pages
# --------------------------------------------------------------------------- #
def related_for(t):
    """Up to 4 related tools.

    Same-category first, but one slot is reserved for a *rotating* popular tool from
    another category. Without that, a category with 4+ tools never links out of its own
    silo — so a newly added tool in a small category (e.g. Business) ends up reachable
    from almost nowhere. The rotation is indexed by position so different pages surface
    different tools instead of every page pointing at the same one.
    """
    same = [x for x in TOOLS if x["cat"] == t["cat"] and x["slug"] != t["slug"]]
    others = [x for x in TOOLS if x["cat"] != t["cat"] and x.get("popular")]
    picks = same[:3]
    if others:
        picks.append(others[TOOLS.index(t) % len(others)])
    for x in same[3:] + others:
        if len(picks) >= 4:
            break
        if x not in picks:
            picks.append(x)
    return picks[:4]

def tool_page(t):
    rel = "../"
    path = slug_path(t)
    faq_entities = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faqs"]]
    jsonld = [
        {"@context": "https://schema.org", "@type": "WebApplication",
         "name": t["name"], "url": SITE_URL + path,
         "applicationCategory": "UtilityApplication", "operatingSystem": "Any",
         "description": t["desc"], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": t["name"], "item": SITE_URL + path}]},
    ]
    h = head(t["title"] + " | " + SITE_NAME, t["desc"], path, rel, t["keywords"], jsonld)
    reltools = related_for(t)
    relhtml = "".join(tool_card(x, rel) for x in reltools)
    faqs = "".join("<details><summary>" + q + "</summary><p>" + a + "</p></details>" for q, a in t["faqs"])
    about = "".join("<p>" + p + "</p>" for p in t["about"])
    html = h + header(rel, "tools") + """<main class="container">
<nav class="breadcrumb"><a href="__REL__index.html">Home</a> › __CAT__ › __NAME__</nav>
<div class="tool-hero">
  <span class="badge">__CAT__</span>
  <h1>__ICON__ __NAME__</h1>
  <p class="lead">__LEAD__</p>
</div>
__AD_TOP__
__BODY__
__AD_MIDDLE__
<section class="content">
  <h2 class="section">About the __NAME__</h2>
  __ABOUT__
</section>
<section>
  <h2 class="section">Frequently asked questions</h2>
  <div class="faq">__FAQS__</div>
</section>
__GEAR__
<section class="related">
  <h2 class="section">Related tools</h2>
  <div class="tool-grid">__RELT__</div>
</section>
__AD_BOTTOM__
</main>
__FOOTER__
<script>__JS__</script>
</body>
</html>
"""
    html = (html.replace("__REL__", rel).replace("__CAT__", t["cat"]).replace("__NAME__", t["name"])
                .replace("__ICON__", t["icon"]).replace("__LEAD__", t["lead"])
                .replace("__BODY__", t["body"]).replace("__ABOUT__", about)
                .replace("__FAQS__", faqs).replace("__RELT__", relhtml).replace("__JS__", t["js"])
                .replace("__GEAR__", gear_block(t))
                .replace("__FOOTER__", footer(rel))
                .replace("__AD_TOP__", ad("top")).replace("__AD_MIDDLE__", ad("middle"))
                .replace("__AD_BOTTOM__", ad("bottom")))
    return html

# --------------------------------------------------------------------------- #
#  home page
# --------------------------------------------------------------------------- #
def home_page():
    rel = ""
    cats = []
    for t in TOOLS:
        if t["cat"] not in cats:
            cats.append(t["cat"])
    chips = '<button class="chip active" data-cat="all">All</button>' + "".join(
        '<button class="chip" data-cat="' + c + '">' + c + "</button>" for c in cats)
    cards = "".join(tool_card(t, rel) for t in TOOLS)
    jsonld = [{"@context": "https://schema.org", "@type": "WebSite",
               "name": SITE_NAME, "url": SITE_URL + "/", "description": DESCRIPTION}]
    h = head(SITE_NAME + " — Free Online Tools, Calculators & Converters (No Signup)",
             DESCRIPTION, "/", rel, "free online tools, calculator, converter, generator, no signup", jsonld)
    html = h + header(rel, "tools") + """<main>
<section class="hero container">
  <h1>Free online tools that <span class="grad">work while you sleep</span></h1>
  <p class="lead">__N__ fast, private calculators, converters and generators. No signup, no uploads — every tool runs entirely in your browser.</p>
  <div class="searchbox"><span class="mag">🔍</span><input type="search" id="tool-search" placeholder="Search tools… try “bmi”, “password”, “invoice”" autocomplete="off" aria-label="Search tools"></div>
  <div class="hero-stats"><span><b>__N__</b> tools</span><span><b>0</b> signups needed</span><span><b>100%</b> private</span><span><b>$0</b> forever</span></div>
</section>
<div class="container">
  <div class="chips">__CHIPS__</div>
  <div class="tool-grid">__CARDS__</div>
  <p class="no-results" id="no-results">No tools match that search — try another word. 🤔</p>
  __AD_TOP__
</div>
<section class="container content">
  <h2 class="section">Why LazyTools?</h2>
  <div class="why-grid">
    <div class="why"><b>🔒 Truly private</b><p>Every calculation happens on your device. Your numbers, dates and text are never uploaded, logged or sold.</p></div>
    <div class="why"><b>⚡ Instant, no friction</b><p>No accounts, no paywalls, no “upgrade to see results”. Open a tool, use it, done.</p></div>
    <div class="why"><b>🌙 Always on</b><p>Tools don't sleep — 3 a.m. invoicing or exam-morning age checks are equally welcome.</p></div>
    <div class="why"><b>🌍 Works everywhere</b><p>Loads fast on any phone or computer, even on slow connections, in dark or light mode.</p></div>
  </div>
  <h2 class="section">How LazyTools keeps the lights on</h2>
  <p>The tools are free because the site shows unobtrusive ads and occasional affiliate links. That's the whole business model — no data selling, no subscriptions. If a tool saved you time, sharing it with a friend is the best thank-you.</p>
</section>
<div class="container">__AD_BOTTOM__</div>
</main>
""" .replace("__N__", str(len(TOOLS))).replace("__CHIPS__", chips).replace("__CARDS__", cards).replace("__AD_TOP__", ad("top")).replace("__AD_BOTTOM__", ad("bottom"))
    return html + footer(rel) + "</body>\n</html>"

# --------------------------------------------------------------------------- #
#  about / privacy / 404
# --------------------------------------------------------------------------- #
def about_page():
    rel = ""
    pop = [t for t in TOOLS if t.get("popular")][:6]
    links = ", ".join('<a href="tools/' + t["slug"] + '.html">' + t["name"] + "</a>" for t in pop)
    h = head("About LazyTools — Free Tools, Honest Business Model",
             "What LazyTools is, how it makes money (ads and affiliate links — nothing shady), and how to contact us.",
             "/about", rel)
    html = h + header(rel, "about") + """<main class="container">
<nav class="breadcrumb"><a href="index.html">Home</a> › About</nav>
<div class="tool-hero"><span class="badge">About</span><h1>About LazyTools</h1>
<p class="lead">A small, honest collection of free browser tools — built to be fast, private and permanently free.</p></div>
<section class="content">
  <h2 class="section">What is this?</h2>
  <p>LazyTools is a growing library of everyday utilities — calculators, converters and generators such as __LINKS__ and more. Every tool runs 100% in your browser: nothing you type is sent to a server, which is both faster for you and safer for your data.</p>
  <h2 class="section" id="disclosure">How we make money (full disclosure)</h2>
  <p>Two ways, and only two ways:</p>
  <p><b>1. Display advertising.</b> Banner slots on these pages are served by third-party ad networks. They may use cookies as described in our <a href="privacy.html">privacy policy</a>.</p>
  <p><b>2. Affiliate links.</b> A few pages recommend a product we think is genuinely useful, and we earn a small commission if you buy it through our link — at no extra cost to you. <b>As an Amazon Associate I earn from qualifying purchases.</b> Anything we recommend is labelled as an affiliate link on the page itself, and a commission never changes what we recommend: we only list things we would mention anyway.</p>
  <p>We do not sell your data, we do not have accounts, and we do not charge for any tool. If that model ever changes, this page changes with it.</p>
  <h2 class="section">Contact</h2>
  <p>Found a bug? Want a tool added? Email <a href="mailto:__EMAIL__">__EMAIL__</a> — a human reads every message.</p>
</section>
</main>
""".replace("__LINKS__", links).replace("__EMAIL__", CONTACT_EMAIL)
    return html + footer(rel) + "</body>\n</html>"

def privacy_page():
    rel = ""
    h = head("Privacy Policy | " + SITE_NAME,
             "LazyTools privacy policy: what we collect (almost nothing), what ad partners do, and your choices.",
             "/privacy", rel)
    html = h + header(rel, "tools") + """<main class="container">
<nav class="breadcrumb"><a href="index.html">Home</a> › Privacy</nav>
<div class="tool-hero"><span class="badge">Legal</span><h1>Privacy Policy</h1>
<p class="lead">Short version: the tools process everything locally and we don't collect your personal data. Ads and analytics may set cookies — details below.</p></div>
<section class="content">
  <h2 class="section">What the tools collect</h2>
  <p>Nothing. All calculators, converters and generators run in your browser. The numbers, dates, passwords and text you enter never leave your device.</p>
  <h2 class="section">Server logs &amp; analytics</h2>
  <p>Like virtually every website, our hosting provider records basic, aggregate technical logs (IP address, browser type, pages requested) for security and performance. We also use <strong>Cloudflare Web Analytics</strong> to count page views. It is <strong>cookieless</strong>: it sets no cookies, stores no identifiers in your browser and does not track you across other websites. The figures we see are aggregate — we cannot identify you from them.</p>
  <h2 class="section">Advertising cookies</h2>
  <p>This site displays ads from third-party ad networks (such as Adsterra and/or Google AdSense). These partners may set cookies or use similar technologies to show you more relevant ads and measure performance. You can opt out of personalised advertising through your browser settings, or via your ad provider's opt-out page. Visiting an ad partner's site is governed by that partner's own privacy policy — for example, see <a href="https://adsterra.com/privacy-policy/" rel="noopener" target="_blank">Adsterra's privacy policy</a>.</p>
  <h2 class="section">Affiliate links</h2>
  <p>Some outbound links are affiliate links — currently from the <strong>Amazon Associates</strong> programme. If you click one and make a purchase, we may earn a commission at no extra cost to you. As an Amazon Associate I earn from qualifying purchases. Affiliate partners may set their own cookies to attribute the referral; see <a href="https://www.amazon.com/gp/help/customer/display.html?nodeId=468496" rel="noopener" target="_blank">Amazon's privacy notice</a>.</p>
  <h2 class="section">Your choices</h2>
  <p>You can clear or block cookies in your browser at any time; the tools will continue to work perfectly. You may also use an ad blocker — the tools remain free either way.</p>
  <h2 class="section">Changes &amp; contact</h2>
  <p>If this policy changes, we will update this page. Questions? Contact <a href="mailto:__EMAIL__">__EMAIL__</a>.</p>
  <p><em>Last updated: __DATE__.</em></p>
</section>
</main>
""".replace("__EMAIL__", CONTACT_EMAIL).replace("__DATE__", BUILD_DATE)
    return html + footer(rel) + "</body>\n</html>"

def err_page():
    rel = ""
    h = head("Page not found | " + SITE_NAME, "That page does not exist — but the tools do.", "/404.html", rel, noindex=True)
    html = h + header(rel, "tools") + """<main class="container" style="text-align:center;padding:70px 20px">
<h1 style="font-size:3rem;margin:0">🛠️ 404</h1>
<p style="color:var(--muted)">This page is missing — but every tool is still one click away.</p>
<p><a class="btn-primary" style="display:inline-block;margin-top:10px;text-decoration:none" href="index.html">Browse all tools →</a></p>
</main>
"""
    return html + footer(rel) + "</body>\n</html>"

# --------------------------------------------------------------------------- #
#  sitemap / robots / ads.txt
# --------------------------------------------------------------------------- #
def sitemap():
    urls = [SITE_URL + "/"]
    for t in TOOLS:
        urls.append(SITE_URL + slug_path(t))
    urls += [SITE_URL + "/about", SITE_URL + "/privacy"]
    body = "\n".join(
        "  <url><loc>" + u + "</loc><changefreq>weekly</changefreq><priority>" +
        ("1.0" if i == 0 else "0.8") + "</priority></url>" for i, u in enumerate(urls))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")

def robots():
    # The repo root is also the deploy directory, so repo-only files are technically
    # reachable on the deployed site. Pages' `_redirects` cannot 404 them (it only
    # supports 200/301/302/303/307/308) and `.assetsignore` is not honoured by Pages,
    # so robots.txt is the guard. See redirects_file() for the verified detail.
    return ("User-agent: *\n"
            "Allow: /\n"
            "# repo-only files — reachable, but must never be indexed\n"
            "Disallow: /_tests/\n"
            "Disallow: /_generator/\n"
            "Disallow: /README.md\n"
            "Disallow: /PROGRESS.md\n"
            "Disallow: /LAUNCH.md\n"
            "Disallow: /CLAUDE-CODE-PROMPT.md\n"
            "Disallow: /.gitignore\n"
            "\nSitemap: " + SITE_URL + "/sitemap.xml\n")

def ads_txt():
    """ads.txt — the IAB file buyers check before bidding on our inventory.

    A missing or wrong line does not break the site; it makes buyers bid lower (or not at
    all), so it costs revenue silently. One line per network, never more than one line for
    the same network, and the domain must be the ADVERTISING SYSTEM's domain.

    ⚠️ VERIFY THE EXACT STRING in the Adsterra dashboard (Websites → your site → ads.txt).
    Adsterra's ad-serving hostnames seen in its own tags are highperformanceformat.com,
    profitabledisplaynetwork.com and effectivegatecpm.com. If the dashboard shows one of
    those instead of adsterra.com, change the first field below to match — the ID stays.
    """
    lines = ["# ads.txt — LazyTools",
             "# One line per ad network. Format: <advertising system domain>, <publisher id>, DIRECT"]
    if ADSTERRA_PUBLISHER_ID:
        lines.append("adsterra.com, " + ADSTERRA_PUBLISHER_ID + ", DIRECT")
    else:
        lines.append("# Adsterra: set ADSTERRA_PUBLISHER_ID in _generator/build.py to enable.")
    lines.append("# AdSense (later):  google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0")
    return "\n".join(lines) + "\n"

def headers_file():
    """Cloudflare Pages `_headers`: security headers only.
    Cloudflare's default caching for static assets is already correct (ETag +
    revalidate on deploy), so we deliberately set no Cache-Control here — a long
    max-age on /assets/* would serve stale CSS/JS after a rebuild.
    Ignored by GitHub Pages and Netlify; harmless if present."""
    return ("/*\n"
            "  X-Content-Type-Options: nosniff\n"
            "  Referrer-Policy: strict-origin-when-cross-origin\n"
            "  X-Frame-Options: SAMEORIGIN\n"
            "  Permissions-Policy: geolocation=(), microphone=(), camera=()\n")

def redirects_file():
    """NOT GENERATED — kept as a note so nobody re-adds it by mistake.

    Cloudflare Pages `_redirects` only supports status 200/301/302/303/307/308 —
    a `404` rule is silently ignored, and `.assetsignore` is not honoured by
    Pages at all. Both were tried and verified against `wrangler pages dev`.
    Since the repo root is the deploy directory, the repo-only files (README,
    PROGRESS, _tests/, _generator/) ARE reachable on the deployed site; they are
    kept out of search results by the Disallow rules in robots() instead.
    If they must be unreachable, the fix is a separate build-output directory
    (e.g. deploy `dist/`) rather than a Pages config file.
    """
    return ""

# --------------------------------------------------------------------------- #
#  build
# --------------------------------------------------------------------------- #
def main():
    wrote = []

    os.makedirs(os.path.join(ROOT, "tools"), exist_ok=True)

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(home_page()); wrote.append("index.html")
    for t in TOOLS:
        p = os.path.join(ROOT, "tools", t["slug"] + ".html")
        with open(p, "w", encoding="utf-8") as f:
            f.write(tool_page(t)); wrote.append("tools/" + t["slug"] + ".html")
    for name, fn in [("about.html", about_page), ("privacy.html", privacy_page), ("404.html", err_page)]:
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(fn()); wrote.append(name)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap()); wrote.append("sitemap.xml")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots()); wrote.append("robots.txt")
    with open(os.path.join(ROOT, "ads.txt"), "w", encoding="utf-8") as f:
        f.write(ads_txt()); wrote.append("ads.txt")
    with open(os.path.join(ROOT, "_headers"), "w", encoding="utf-8") as f:
        f.write(headers_file()); wrote.append("_headers")
    # IndexNow ownership proof — the filename IS the key, and the body must be the key too.
    with open(os.path.join(ROOT, INDEXNOW_KEY + ".txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY); wrote.append(INDEXNOW_KEY + ".txt")

    print("Built %d files:" % len(wrote))
    for w in wrote:
        print("  ✓", w)
    print("\nSite URL: %s  (edit SITE_URL in _generator/build.py if this is a placeholder)" % SITE_URL)

if __name__ == "__main__":
    main()
