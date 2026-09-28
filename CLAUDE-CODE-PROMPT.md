# 🤖 The "do everything" prompt for Claude Code

Copy **everything inside the box below** and paste it as your first message in
[Claude Code](https://claude.com/claude-code), run from inside this `lazytools` folder:

```bash
cd lazytools
claude
```

> **What it automates:** finalizing the site → GitHub → free deployment → search engine
> submission → analytics → ad integration → weekly growth loop.
> **What needs you (unavoidable, by design):** creating accounts that require YOUR email,
> OTP codes or identity (GitHub login, Adsterra, Google Search Console). The prompt is built
> so Claude Code prepares every form, value and click-path for those, then pauses exactly
> where only you can act, and resumes on its own afterwards. Never paste passwords into the chat.

---

```
You are my autonomous launch engineer. Your job: turn this LazyTools repository into a
live, indexed, monetized website that earns money from display ads while I sleep — doing
EVERY step yourself, pausing only where a human is legally/technically required (account
signups, email/OTP verification, identity or tax forms).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MY INFO SHEET — read this first
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If INFO.md does not exist in this folder, create it with exactly this template, show it
to me, and WAIT until I fill it in (or answer the questions in chat and fill it for me):

  # INFO.md (never commit this file)
  name:            (my real name, for account signups)
  email:           (Gmail recommended — used for GitHub, Adsterra, Google Search Console)
  country:         Libya
  github_username:
  site_name:       LazyTools
  domain:          (leave empty if I don't have one — a free subdomain is fine)
  contact_email:   (email shown on the site's About page)
  analytics:       (empty for now)
  adsterra_top:    (empty for now)
  adsterra_middle: (empty for now)
  adsterra_bottom: (empty for now)
  payout_wallet:   (my USDT TRC-20 address or other payout details for ad networks)
  notes:           (anything else)

Add INFO.md to .gitignore IMMEDIATELY so my personal data never reaches GitHub.
Keep a PROGRESS.md checklist in this repo and update it after every step below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — FINALIZE THE SITE (do this yourself, no input needed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Read the repo: _generator/build.py generates all pages from _generator/tools_core.py
   and _generator/tools_extra.py. assets/ads.js holds the ad codes.
2. Edit the top of _generator/build.py: set SITE_URL and CONTACT_EMAIL from INFO.md
   (if domain is empty, we will fill the real URL after deploy in Step 3 and rebuild).
3. Run `python3 _generator/build.py` and confirm all pages build.
4. Sanity-check: open index.html and 3 random tool pages with your headless tools;
   confirm no broken links, scripts load, tools compute.
5. Initialize git: `git init`, create .gitignore (INFO.md, .DS_Store, node_modules/),
   commit everything as "LazyTools v1 — 14 tools".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — GITHUB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Check `gh auth status`. If not logged in, run `gh auth login` and GUIDE me through
   the terminal prompts (I do the browser part + OTP myself). Do NOT ask me for passwords.
2. Create a PUBLIC repo named after INFO.md site_name (lowercase), push the code:
   `gh repo create lazytools --public --source=. --push`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — DEPLOY FREE (target: $0/month)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Try in this order, stop at the first success:
A) Cloudflare Pages (best — unlimited free bandwidth):
   - `npx wrangler login` (I complete the browser auth myself)
   - `npx wrangler pages project create lazytools --production-branch main`
   - `npx wrangler pages deploy . --project-name lazytools`
B) GitHub Pages fallback (zero new accounts):
   - `gh api user` to confirm login, then enable Pages on the repo via
     `gh api -X POST repos/{owner}/{repo}/pages -f source[branch]=main -f source[path]=/`
     (adjust to current GitHub API; deploy from root or /docs as needed)
C) Netlify fallback: `npx netlify-cli deploy --prod --dir .`
4. When live: set SITE_URL in _generator/build.py to the real URL, rebuild, push,
   and curl the live URL to verify (expect HTTP 200 and our homepage title).
5. If INFO.md has a domain: walk me through pointing its DNS to the host (A/CNAME
   records), then rebuild with the final domain as SITE_URL. If I have no domain,
   the free subdomain is fine — note that a $5–10/yr domain can be added anytime.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — SEARCH ENGINES (the traffic engine)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: site verified in Google Search Console + Bing Webmaster, sitemap submitted.
1. Google Search Console: tell me to open https://search.google.com/search-console
   with my Google account, add a "URL prefix" property for the live URL, choose
   "HTML tag" verification, and PASTE the meta tag content back to you.
   Then you: add that tag into the <head> template in _generator/build.py, rebuild,
   push, wait for deploy, tell me to click "Verify", then submit the sitemap
   (sitemap.xml) in the GSC UI — or via the API if I give you a token.
2. Bing Webmaster Tools: same flow (it also imports from GSC). Paste its meta tag
   to me, I add it, verify, submit sitemap.
3. Record both verification dates in PROGRESS.md.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5 — ANALYTICS (free, privacy-friendly)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. If we deployed on Cloudflare: tell me to enable Web Analytics in the Cloudflare
   dashboard for the site and paste the token/beacon snippet back to you.
   Otherwise create a free GoatCounter account and get its snippet.
2. You: inject the snippet into the head template (a new ANALYTICS_CODE constant in
   _generator/build.py), rebuild, push, verify it appears in the live HTML.
3. Add a line to privacy.html about aggregate analytics. Rebuild + push.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 6 — MONETIZE: ADSTERRA (works from Libya, payouts from $5 incl. crypto)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Tell me to create a publisher account at https://adsterra.com (Publishers → Sign up)
   with my INFO.md email — I do the email verification myself.
2. Then in Adsterra: Websites → Add website (give me the exact values to type:
   live URL, category "Computers/Internet", description you write for me,
   traffic "organic"). Approval usually takes under 48h — remind me to check.
3. When approved: I create 3 ad units (728×90 or 320×50 banner → "top";
   300×250 banner → "middle"; 300×250 or native → "bottom") and copy each code.
   I paste all 3 codes into chat (or INFO.md fields adsterra_top/middle/bottom).
4. You: paste them into assets/ads.js slots, add the Adsterra line to ads.txt
   (format: atterraform.com, ZONE_ID, DIRECT — derive from the codes), rebuild,
   push, then curl a live tool page to confirm the ad script is present.
5. In Adsterra settings, remind me to set the payout method to USDT/WebMoney/etc
   using INFO.md payout_wallet, minimum payout threshold, and enable 2FA.
6. Later growth note: once we reach ~10,000 visits/month, also apply to Google
   AdSense and add its line to ads.txt — better rates, same slots.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 7 — AFFILIATE LINKS (bonus income)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Suggest 3–5 affiliate programs relevant to our pages (e.g. accounting software
   on the invoice page, web hosting on the about page, VPN/security on the
   password page). Prioritize programs that pay via Payoneer, wire or crypto.
2. For each: prepare the signup URL, the exact form values to type, and where the
   link will go. I sign up; you insert links with rel="sponsored noopener",
   update about.html disclosures, rebuild, push.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 8 — GROWTH LOOP (run whenever I say "grow")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Each time I say "grow":
1. Add 2–3 new tools. Pick from this list (already sorted by search value):
   hours calculator (time card) · discount calculator · sales tax calculator ·
   GPA calculator · love calculator · date of birth + due date (pregnancy) ·
   calorie/BMR calculator · running pace calculator · time zone converter ·
   random name picker / wheel spinner · coin flip / dice roller · roman numerals ·
   binary/hex converter · morse code translator · color code converter ·
   gradient generator · aspect ratio calculator · base64 encoder/decoder ·
   hash generator (SHA-256 via WebCrypto) · URL encoder · lorem ipsum generator ·
   typing speed test · countdown to date · email validator · slug generator.
   Build each the same way as existing tools: unique title/meta/FAQ, JSON-LD,
   body+js in a tools_*.py file, rebuild, push, verify live.
2. Add internal links from related existing pages to the new tools.
3. Launch/sharing (I do the posting; you draft everything): give me a ready
   Product Hunt blurb, a Show HN post, an r/SideProject post, 3 tweet/X drafts,
   and 5 Pinterest pin descriptions (Pinterest is a top traffic source for
   calculator sites). One new platform per growth cycle.
4. Report: pages indexed (Search Console), clicks, top queries, RPM and revenue
   from Adsterra, and what to build next based on queries we almost rank for.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULES (always)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Never ask me for passwords, OTP codes, or card numbers. Pause, tell me exactly
  what to do in the browser, and wait for my "done".
- Never commit INFO.md or secrets to git. Keep everything on free tiers; ask me
  before anything that costs money (e.g. a domain).
- After every deploy, verify the live site with curl before declaring success.
- Work autonomously through all steps; only stop for the human-only actions above.
- Update PROGRESS.md after each step with date + status.
- If anything fails, try the documented fallback and tell me what happened.

DONE WHEN: site live on a real URL → committed to GitHub → verified in Google
Search Console and Bing with sitemap submitted → analytics counting visits →
Adsterra codes live on every page and ads.txt updated → PROGRESS.md complete.
Then tell me the earnings math (pageviews needed at current RPM for $50/$250/$1000
per month) and the 30-day growth plan.
```

---

## How to use it (3 commands, honestly)

1. `cd lazytools && claude` — start Claude Code in this folder
2. Paste the block above as your first message
3. Fill `INFO.md` when it asks (your name, email, GitHub username — 60 seconds)

Claude Code will then run the whole pipeline and only interrupt you for:
GitHub login, Google account verification, Adsterra signup/OTP, and pasting ad codes.
That's the minimum any human must do — no AI should ever type your passwords or verify
your email for you, and any tool claiming otherwise is asking to be robbed.

## What to say afterwards

| You say | Claude Code does |
|---|---|
| **"grow"** | Adds 2–3 new tools, links them, drafts launch posts, reports traffic |
| **"add a tool: X"** | Builds, SEO-tags, deploys a new tool page |
| **"swap ads to AdSense"** | Migrates ad codes + ads.txt once you're approved |
| **"report"** | Traffic, indexed pages, revenue, next 3 actions |
