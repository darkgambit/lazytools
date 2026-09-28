#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate og-image.png — the 1200x630 social share card.

Usage:   python3 _generator/make_og.py

WHY THIS IS A SCRIPT AND NOT A ONE-OFF IMAGE
The card states the tool count, and the site's entire growth model is "add tools
regularly". A hard-coded number therefore rots within weeks — the shipped card said
"14" while the site had 17. Here the count and the icon row are both derived from the
tool data, so re-running this after every growth cycle is automatically correct.

Run it after any change to tools_core.py / tools_extra.py, then rebuild + redeploy.

Requires Google Chrome (driven headless). No third-party packages.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools_core import TOOLS_CORE
from tools_extra import TOOLS_EXTRA

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "og-image.png")

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

CARD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:1200px; height:630px; overflow:hidden; }
  body {
    font-family:'Segoe UI',-apple-system,Roboto,Helvetica,Arial,sans-serif;
    background:#0a0f1e; color:#eef2ff; position:relative;
  }
  .glow { position:absolute; border-radius:50%; filter:blur(90px); }
  .g1 { width:520px; height:520px; background:#f5b53f; top:-190px; right:-120px; opacity:.20; }
  .g2 { width:460px; height:460px; background:#8fa4ff; bottom:-210px; left:-120px; opacity:.18; }
  .wrap { position:relative; padding:64px 72px; height:100%; display:flex; flex-direction:column; }
  .brand { display:flex; align-items:center; gap:16px; }
  .brand span { font-size:34px; font-weight:800; letter-spacing:-.5px; }
  .brand .dot { color:#f5b53f; }
  h1 { font-size:76px; line-height:1.06; font-weight:800; letter-spacing:-2.5px; margin-top:auto; }
  h1 .grad { color:#f5b53f; }
  .sub { font-size:29px; color:#9fb0d9; margin-top:24px; font-weight:400; }
  .row { display:flex; gap:14px; margin-top:38px; flex-wrap:wrap; }
  .pill {
    font-size:22px; font-weight:600; padding:11px 22px; border-radius:999px;
    background:rgba(143,164,255,.12); border:1px solid rgba(143,164,255,.35); color:#c7d2fe;
  }
  .pill.gold { background:rgba(245,181,63,.13); border-color:rgba(245,181,63,.45); color:#f7cd7f; }
  .icons { position:absolute; right:72px; top:74px; font-size:40px; letter-spacing:12px; opacity:.45; }
</style>
</head>
<body>
  <div class="glow g1"></div>
  <div class="glow g2"></div>
  <div class="wrap">
    <div class="brand">
      <svg width="52" height="52" viewBox="0 0 64 64" aria-hidden="true">
        <rect width="64" height="64" rx="14" fill="#0a0f1e"/>
        <path d="M42 10a21 21 0 1 0 12.5 33.5A17 17 0 1 1 42 10z" fill="#f5b53f"/>
        <circle cx="19" cy="46" r="4.5" fill="#8fa4ff"/>
        <path d="M22.2 42.8l8.6-8.6" stroke="#8fa4ff" stroke-width="4.5" stroke-linecap="round"/>
      </svg>
      <span>Lazy<span class="dot">Tools</span></span>
    </div>
    <h1>Free online tools that<br><span class="grad">work while you sleep</span></h1>
    <p class="sub">__COUNT__ fast, private calculators, converters &amp; generators.</p>
    <div class="row">
      <div class="pill">No signup</div>
      <div class="pill">100% in-browser</div>
      <div class="pill gold">$0 forever</div>
    </div>
  </div>
  <div class="icons">__ICONS__</div>
</body>
</html>
"""


def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def build_icons(tools, limit=5):
    """Emoji row drawn from the popular tools, so it tracks the real tool set."""
    popular = [t for t in tools if t.get("popular")]
    picks = (popular or tools)[:limit]
    return " ".join(t.get("icon", "") for t in picks)


def main():
    tools = TOOLS_CORE + TOOLS_EXTRA
    count = len(tools)

    chrome = find_chrome()
    if not chrome:
        print("ERROR: Google Chrome not found. Looked in:")
        for p in CHROME_CANDIDATES:
            print("   " + p)
        return 1

    html = CARD.replace("__COUNT__", str(count)).replace("__ICONS__", build_icons(tools))

    card = os.path.join(tempfile.gettempdir(), "og_card.html")
    with open(card, "w", encoding="utf-8") as f:
        f.write(html)

    if os.path.exists(OUT):
        os.remove(OUT)

    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=1200,630",
        "--screenshot=" + OUT,
        Path(card).as_uri(),
    ]
    subprocess.run(cmd, capture_output=True, timeout=120)

    if not os.path.exists(OUT):
        print("ERROR: Chrome produced no screenshot.")
        return 1

    # Read the real dimensions straight out of the PNG header (bytes 16-24).
    with open(OUT, "rb") as f:
        head = f.read(24)
    w = int.from_bytes(head[16:20], "big")
    h = int.from_bytes(head[20:24], "big")

    size_kb = os.path.getsize(OUT) / 1024
    print("og-image.png written: %d x %d, %.0f KB" % (w, h, size_kb))
    print("   tool count baked in : %d" % count)
    print("   icon row            : %s" % build_icons(tools))

    if (w, h) != (1200, 630):
        print("ERROR: expected 1200x630, got %dx%d" % (w, h))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
