# -*- coding: utf-8 -*-
"""LazyTools deploy contract check — run against the Pages emulator or the live site.

    python _tests/check_deploy.py                          # emulator on :8788
    python _tests/check_deploy.py https://lazytools.pages.dev

Asserts the things that must be true of ANY host serving this site:
  1. every URL in sitemap.xml returns 200 (NOT a redirect) and its canonical
     points back at itself — this is the guard for the trailing-slash bug;
  2. the home page, og-image, robots.txt, sitemap.xml and ads.txt are reachable;
  3. repo-only files (README/PROGRESS/_tests/_generator) are NOT served.

Exits non-zero on any failure.
"""
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = __file__.rsplit("_tests", 1)[0]
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8788").rstrip("/")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)
# This machine routes outbound traffic through a proxy that rejects Python's default
# User-Agent ("Python-urllib/3.x") with a 403. Without a browser UA, every URL in a
# live-site run reports 403 and the check appears to fail catastrophically when the
# site is actually fine. Send a real UA so the result reflects the site, not the proxy.
OPENER.addheaders = [("User-Agent",
                      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")]


def probe(path):
    """Return (status, body_bytes, location)."""
    try:
        r = OPENER.open(BASE + path, timeout=15)
        return r.status, r.read(), ""
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        return e.code, body, e.headers.get("Location", "")
    except Exception as e:
        return 0, str(e).encode(), ""


failures = []

# ---- 1. every sitemap URL is a direct 200 whose canonical matches ----
xml = open(ROOT + "sitemap.xml", encoding="utf-8").read()
urls = re.findall(r"<loc>([^<]+)</loc>", xml)
print("--- sitemap URLs (%d) ---" % len(urls))
for u in urls:
    path = re.sub(r"^https?://[^/]+", "", u) or "/"
    status, body, loc = probe(path)
    m = re.search(rb'<link rel="canonical" href="([^"]+)"', body)
    canon = re.sub(r"^https?://[^/]+", "", m.group(1).decode()) if m else "(none)"
    ok = status == 200 and canon == path
    if not ok:
        failures.append("%s -> status=%s canonical=%s redirect=%s" % (path, status, canon, loc))
    print("%-6s %-46s %s canonical=%s" % ("OK" if ok else "FAIL", path, status, canon))

# ---- 2. required site assets ----
print("--- required assets ---")
for p in ["/og-image.png", "/robots.txt", "/sitemap.xml", "/ads.txt", "/favicon.svg",
          "/site.webmanifest", "/assets/style.css", "/assets/app.js", "/assets/ads.js"]:
    status, _, _ = probe(p)
    ok = status == 200
    if not ok:
        failures.append("%s -> status=%s (expected 200)" % (p, status))
    print("%-6s %-46s %s" % ("OK" if ok else "FAIL", p, status))

# ---- 2b. security headers from _headers, and _headers itself not served ----
print("--- security headers (_headers) ---")
try:
    hr = OPENER.open(BASE + "/", timeout=15)
    hdrs = {k.lower(): v for k, v in hr.headers.items()}
except Exception:
    hdrs = {}
for h in ["x-content-type-options", "referrer-policy", "x-frame-options", "permissions-policy"]:
    ok = h in hdrs
    if not ok:
        failures.append("missing response header %s" % h)
    print("%-6s %-46s %s" % ("OK" if ok else "FAIL", h, hdrs.get(h, "MISSING")))
status, _, _ = probe("/_headers")
ok = status == 404
if not ok:
    failures.append("/_headers -> status=%s (config file must not be served)" % status)
print("%-6s %-46s %s" % ("OK" if ok else "FAIL", "/_headers (config, must 404)", status))

# ---- 3. repo-only files must NOT be served at all ----
# Not merely Disallow'ed in robots.txt. robots.txt is a request, not access control: it
# stops a compliant crawler indexing a URL, and does nothing to stop a human, a scraper
# that ignores it, or a link someone shares. It also never covered /INFO.md or
# /.workbuddy-ai/ at all. The site is published from a staged directory
# (_generator/deploy.py) that excludes them, so they must 404.
#
# The cache-busting query string is load-bearing. These paths were fetched while the leak
# was being diagnosed, so they sit in Cloudflare's edge cache with a week-long TTL, and a
# clean origin can still answer 200 for a while. Without the query string a correct
# deploy would look broken, and with it a stale edge copy is not mistaken for a leak.
print("--- repo-only files must 404 (not just be disallowed) ---")
CB = "?cb=" + str(int(time.time()))
for p in ["/INFO.md", "/PROGRESS.md", "/CLAUDE-CODE-PROMPT.md", "/README.md", "/LAUNCH.md",
          "/.gitignore", "/.workbuddy-ai/memory/MEMORY.md",
          "/_tests/check_static.py", "/_generator/build.py"]:
    status, _, _ = probe(p + CB)
    ok = status == 404
    if not ok:
        failures.append("%s -> status=%s (must 404; is the emulator serving the repo "
                        "root instead of .wrangler/deploy?)" % (p, status))
    print("%-6s %-46s %s" % ("OK" if ok else "FAIL", p, status))

# ---- 3b. ...and they stay Disallow'ed, as belt-and-braces ----
print("--- repo-only files must also be Disallow'ed in robots.txt ---")
_, rbody, _ = probe("/robots.txt")
robots_txt = rbody.decode("utf-8", "replace")
for p in ["/_tests/", "/_generator/", "/README.md", "/PROGRESS.md", "/CLAUDE-CODE-PROMPT.md",
          "/INFO.md", "/.workbuddy-ai/"]:
    ok = ("Disallow: " + p) in robots_txt
    if not ok:
        failures.append("robots.txt does not disallow %s" % p)
    print("%-6s %-46s %s" % ("OK" if ok else "FAIL", p, "disallowed" if ok else "MISSING"))

# ---- 4. unknown path yields the 404 page ----
status, body, _ = probe("/this-page-does-not-exist")
ok = status == 404 and b"404" in body
if not ok:
    failures.append("/this-page-does-not-exist -> status=%s" % status)
print("--- 404 handling ---")
print("%-6s %-46s %s" % ("OK" if ok else "FAIL", "/this-page-does-not-exist", status))

print()
if failures:
    print("DEPLOY CHECK FAILED (%d problem(s)):" % len(failures))
    for f in failures:
        print("  ! " + f)
else:
    print("DEPLOY CHECK PASSED — %s" % BASE)
sys.exit(1 if failures else 0)
