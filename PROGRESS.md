# PROGRESS.md — LazyTools launch tracker

Started: 2026-09-28 · Hosting target: $0/month · Owner: see `INFO.md` (git-ignored)

## 🟢 THE SITE IS LIVE → **https://lazytools.pages.dev**

Deployed 2026-09-28 to Cloudflare Pages (free tier). Source: https://github.com/darkgambit/lazytools

**Verified on the live URL, not locally:** deploy contract **PASSED** (all 20 sitemap URLs 200
with matching canonicals, 4 security headers present, repo-only paths disallowed, unknown path
→ 404) and the real-browser suite **25/25** — every one of the 17 tools computes correctly in
Chrome against production.

**Still earning $0** — ads are not wired up yet (Step 6) and the site is not yet indexed
(Step 4). Being live is necessary, not sufficient.

| Step | What | Status | Date |
|---|---|---|---|
| 0 | INFO.md (personal data, git-ignored) | ✅ done — name, email, contact, domain + analytics decided | 2026-09-28 |
| 1 | Finalize site — build, verify, git init, v1 commit | ✅ done | 2026-09-28 |
| 1b | Production-readiness pass (URLs, OG, headers, guards) | ✅ done | 2026-09-28 |
| 1c | Real site config + self-updating OG card + README corrections | ✅ done | 2026-09-28 |
| 2 | GitHub: gh auth + public repo + push | ✅ done — https://github.com/darkgambit/lazytools | 2026-09-28 |
| 3 | Deploy free (Cloudflare Pages) + verify live | ✅ done — https://lazytools.pages.dev | 2026-09-28 |
| 4 | Google Search Console + Bing + sitemap | 🔄 verification tag **live & matched** — click Verify, then submit the sitemap | 2026-09-28 |
| 4b | IndexNow ping to Bing/Yandex/Seznam/Naver — no account needed | ✅ done — HTTP 202 accepted | 2026-09-28 |
| 4 | Google Search Console + Bing + sitemap | ⏸ blocked on step 3 | — |
| 5 | Analytics — Cloudflare Web Analytics; build plumbing **done**, snippet pending deploy | 🔄 half done | 2026-09-28 |
| 6 | Adsterra ad units + ads.txt | ⏸ blocked on step 3 | — |
| 7 | Affiliate links — shortlist prepared below | 🔄 prepared, needs your signups | — |
| 8 | Growth loop — cycle 1: 3 tools added (**14 → 17**) | ✅ done | 2026-09-28 |
| 8b | Launch kit written — Product Hunt, Show HN, Reddit, X, Pinterest | ✅ done — see `LAUNCH.md` | 2026-09-28 |
| — | Monetization reality check + earnings math + 30-day plan (section below) | ✅ done | 2026-09-28 |

Legend: ⬜ not started · 🔄 in progress · ✅ done · ⏸ blocked

---

## ✅ GitHub — authenticated and published

Device-flow login completed 2026-09-28 as **darkgambit** (token scopes: `repo`, `read:org`,
`gist`). Public repo: **https://github.com/darkgambit/lazytools** — 4 commits, 42 files,
default branch `main`, every commit authored as the owner.

Verified **after** pushing, not assumed: `INFO.md` and `.workbuddy-ai/` are absent from the
remote (checked through the GitHub API), and a scan of every tracked file found no secrets,
tokens or private keys.

**Never paste a password or an OTP into this chat** — the device flow exists precisely so you
don't have to, and I will never ask.

---

## ⏸ BLOCKED ON YOU — the rest of the queue

**1. `INFO.md`** — ✅ **done.** Only `payout_wallet` is outstanding, and it is not needed until
the first Adsterra payout (not before signup).

**2. Then, one at a time (I'll prompt you for each):**

- **GitHub login** — ✅ done (as `darkgambit`).
- **Cloudflare login** — ✅ done. Project `lazytools` created, first deployment live.
- **Google Search Console** — 🔶 **tag deployed, sitemap submitted by you.** Confirm you clicked
  **Verify** and that the property shows as verified; then I'll record the date. Bing imports
  from GSC next (no second tag needed).
- **Cloudflare Web Analytics** — ⏭ **next, and it's the easiest win.** Cookieless, free,
  unlimited, no consent banner. Open the Cloudflare dashboard → **Web Analytics** → add
  `lazytools.pages.dev` → copy the one-line snippet → paste it to me. I put it in
  `ANALYTICS_CODE`, rebuild and redeploy. (I can't do it for you: the wrangler login token
  doesn't carry the `analytics` / `rum` scope.)
- **Adsterra** — the step that starts earning. Publisher signup with your email, then add the
  website and create 3 ad units; paste the 3 codes to me. **The code is now safe to paste** —
  see "Step 6 prep" below.
- **Affiliate signups** — see Step 7 below.

---

## ✅ Step 1 + 1b — what was done and proven

**Built:** `python _generator/build.py` → 21 files (index, 14 tools, about, privacy, 404,
sitemap, robots, ads.txt, `_headers`).

### 🐞 Bug 1 — tools were dead on load (found by real-browser testing)
`assets/app.js` was loaded with `defer` from `<head>`. Deferred scripts run *after* HTML
parsing, but every tool page runs its init inline at the end of `<body>` — so the inline
script ran first and threw **`$id is not defined`** on 7 pages.

Real impact: the **Unit Converter's dropdowns were completely empty** (tool unusable), and
age / date / loan / compound-interest / invoice / password tools never pre-filled or
auto-calculated on load.

**Fixed:** `app.js` is now loaded non-deferred (also removes a flash of the wrong theme,
since the theme class is now set before first paint). `ads.js` stays deferred. Documented in
the head template and guarded by `_tests/check_static.py`.

### 🐞 Bug 2 — every canonical and sitemap entry pointed at a redirect
Canonicals and the sitemap used `/about/` and `/tools/bmi-calculator/`, but the files are
`about.html` and `tools/bmi-calculator.html`. Verified against Cloudflare's own emulator
(`wrangler pages dev`):

| URL | Result |
|---|---|
| `/about` · `/tools/bmi-calculator` | **200** ← the only direct URL |
| `/about.html` · `/tools/bmi-calculator.html` | 308 → extensionless |
| `/about/` · `/tools/bmi-calculator/` | 308 → extensionless |

So **all 17 canonical/sitemap URLs were redirects**, which is exactly the duplicate-URL trap
Google warns about. **Fixed:** canonicals and sitemap are now extensionless and slashless —
the final 200 URL. Internal links stay `.html` so local preview and `file://` still work.

### Also hardened
- **`og:image` + `twitter:summary_large_image`** — a 1200×630 `og-image.png` rendered from
  the brand card, so Step 8's Pinterest / X / Product Hunt shares don't look broken.
- **`_headers`** (Cloudflare Pages) — `X-Content-Type-Options`, `Referrer-Policy`,
  `X-Frame-Options`, `Permissions-Policy`. Verified applied on the emulator. Deliberately
  **no** `Cache-Control`: Cloudflare already sends `max-age=0, must-revalidate`, and a long
  `max-age` on `/assets/*` would serve stale CSS/JS after a rebuild.
- **`404.html`** now carries `noindex` and no canonical (a 404 canonicalises nothing).
- **`privacy.html`** "last updated" is generated, not a placeholder.

### ⚠️ Known limitation (not fixable with Pages config)
The repo root **is** the deploy directory, so `README.md`, `PROGRESS.md`, `_tests/` and
`_generator/` are technically reachable on the deployed site. I tested both fixes:
Cloudflare Pages `_redirects` only supports status 200/301/302/303/307/308 (**a `404` rule is
silently ignored**), and `.assetsignore` is **not honoured by Pages**. So they are kept out of
search results via `Disallow` rules in `robots.txt` instead. None of them contain personal
data. If you want them genuinely unreachable, the fix is deploying from a separate build
output directory (e.g. `dist/`) — say the word and I'll restructure it.

### Verification — all green, all reproducible
```
python _tests/check_static.py      # links, SEO tags, JS syntax, canonical-resolves guard
node   _tests/e2e.js               # 19 browser checks against the Pages emulator
python _tests/check_deploy.py      # deploy contract: 200s, no redirects, headers, robots
```
- **Static:** 274 local links/assets, **0 broken**. All 14 inline tool scripts + both asset
  scripts pass `node --check`. Every tool page has canonical, title, meta description,
  3 JSON-LD blocks and 3 ad slots.
- **Browser E2E: 19/19, run 5× consecutively with zero flakiness**, zero console errors.
  Verified outputs: age `36 y 4 m 13 d` · 15% of 200 = 30 · compound interest `54,623.32` ·
  BMI `24.2 (Healthy)` · loan `386.66/mo` · tip `97.18` · `1 meter = 3.28 foot` ·
  invoice `300.00` · date diff `364` days · word count `12`.
- **Deploy contract:** all 17 sitemap URLs 200 with matching canonical, security headers
  present, `_headers` not served, repo-only paths disallowed, unknown path → 404 page.
- **`file://` rung:** double-clicking `index.html` still works.
- **The canonical guard was itself tested** with negative controls (reintroducing the
  trailing-slash bug is caught) — after the first version of the guard silently missed it.

### Git
`main` branch, **1 commit** (`254ca7d`), 42 files tracked, authored as
**the owner \<kingripper9@gmail.com\>**. `INFO.md`, `.workbuddy-ai/` and `.wrangler/` are
git-ignored (verified with `git check-ignore`, and the staged file list is asserted clean of
personal files before every commit).

> ### ⚠️ Repository incident — 2026-09-28
> While re-authoring the original 6 commits to the real git identity, I ran
> `git rebase --root --exec 'git commit --amend --reset-author'`. **It destroyed the entire
> `.git` directory** — `fatal: not a git repository`. The working tree survived completely
> intact (every file, including the regenerated `og-image.png`), but the object store was gone
> and could not be recovered; a filesystem search found no surviving `packed-refs`, `ORIG_HEAD`
> or stray `.git` anywhere under the home directory.
>
> **Damage: zero content lost, zero public history lost** — the repo had never been pushed, so
> no one ever saw those commits. The history was rebuilt as a single honest commit describing
> the full verified state, which is what the first push would have looked like anyway.
>
> **Lesson: do not attempt history rewriting in this environment.** `git rebase --root`,
> `git filter-branch` and friends are not safe here. Set the git identity *before* the first
> commit and never re-author afterwards — the identity was already correct for the new commit,
> which is the one that mattered.

### Tooling notes
- `gh` (GitHub CLI 2.101.0) installed via winget, **not on the Git Bash PATH**:
  `export PATH="$PATH:/c/Program Files/GitHub CLI"`. Not authenticated yet.
- No browser is bundled; `playwright-core` drives your installed Chrome.
- `jsdom` is installed but **does not auto-select the first `<option>`** of a dynamically
  filled `<select>` (real browsers do) — it produced a false failure. Trust the real browser.

---

## ✅ Step 1c — real site config, OG card, README corrections (2026-09-28)

### Configured (no longer placeholders)
- **`CONTACT_EMAIL`** is the real address, so About and Privacy render a working `mailto:`.
  Verified **on the served pages** via the emulator, not just in the source.
- **`SITE_URL`** is `https://lazytools.pages.dev` — **provisional**. Every canonical, the
  sitemap, `robots.txt` and `og:image` derive from it, so it must be corrected to the real
  production hostname at the first Cloudflare Pages deploy, then rebuilt and redeployed.

### `og-image.png` was stale, and would keep going stale
The shipped card said **"14 tools"** while the site had 17. It is baked into a PNG, so no
rebuild could ever fix it — and the growth loop adds tools regularly, so the number was
guaranteed to rot again. Replaced the one-off card with **`_generator/make_og.py`**, which
derives both the tool count *and* the emoji row from the tool data and screenshots the card
headless. Re-running it after a growth cycle is now always correct.
Verified output: 1200×630, 115 KB, "17 fast, private calculators, converters & generators."

### README corrected
- 14 → 17 tools, and the three new tools listed.
- **The RPM claim was wrong.** It quoted **$2.50–$12.50** per 1,000 pageviews, which is AdSense
  money with premium US/UK finance traffic. A new Adsterra site with mixed-geo traffic should be
  budgeted at **$0.50–$3.00**, so its "10k pageviews ≈ $50" was optimistic by **2–10×**. The
  README now points at the earnings table above instead of quoting a number that flatters.

### Step 5 pre-wired (analytics)
You chose **Cloudflare Web Analytics** — cookieless, so no consent banner and no privacy-policy
complication. Added an `ANALYTICS_CODE` constant to `_generator/build.py` plus a `__ANALYTICS__`
injection point in `head()`, so Step 5 is now: paste the dashboard snippet, rebuild, redeploy.
An empty constant emits **zero** third-party bytes, so shipping it blank is safe.
`privacy.html` already documents aggregate analytics, so no policy change is needed.

Proved both paths rather than assuming: with a test snippet the tag appears in the head of every
page; with the constant blank, no tag and no leftover placeholder are emitted.

### New guard: unsubstituted template tokens
`_tests/check_static.py` now fails if any `__TOKEN__` survives into built HTML. Adding a
placeholder to a template and forgetting its `.replace()` ships the literal token into
production — invisible in a browser and very easy to miss. **Negative-tested**: deleting the
`__ANALYTICS__` replace made the guard report it on all 21 pages; restored, rebuilt, clean again.

### Verified after all changes
`check_static.py` 0 issues (319 refs, 17 JS blocks) · `e2e.js` **25/25** · `check_deploy.py`
**PASSED** (20 sitemap URLs all 200 with matching canonicals, security headers present, repo-only
paths disallowed, unknown path → 404) · `mailto:` present on `/about` and `/privacy` as served.

### Emulator gotcha (cost me one failed run)
Starting `wrangler pages dev` detached in a subshell makes it die as soon as the Bash command
returns, so a *later* command sees a dead server and every URL returns **502**. Run the server,
the readiness poll and the check **in the same shell invocation**.

---

## ✅ Step 3 — deployed to Cloudflare Pages (2026-09-28)

**Live: https://lazytools.pages.dev**

- `npx wrangler login` — OAuth, free tier, no card.
- `npx wrangler pages project create lazytools --production-branch main` — **the name was free**,
  so the assigned hostname matched the provisional `SITE_URL` exactly and **no rebuild was
  needed**. Had it been taken, Cloudflare would have appended a suffix and every canonical,
  the sitemap and `og:image` would have pointed at a host that does not exist — which is
  precisely why `SITE_URL` was flagged provisional rather than assumed.
- `npx wrangler pages deploy . --project-name lazytools --branch main` — 44 files in 2.9s.

### Verified against the LIVE URL, not locally
```
python _tests/check_deploy.py https://lazytools.pages.dev   # → DEPLOY CHECK PASSED
LT_BASE=https://lazytools.pages.dev node _tests/e2e.js      # → 25 passed, 0 failed
```
- All 20 sitemap URLs return **200 directly** with a canonical matching the live URL.
- All four security headers present on the **real edge**, not just the emulator.
- Unknown path → 404 page. `/_headers` not served.
- **25/25 real-browser checks in Chrome against production** — all 17 tools compute correctly
  (age `36 y 4 m 13 d`, compound interest `54,623.32`, loan `386.66/mo`, weekly time card
  `35.00 h`, reverse sales tax net `250` / tax `20.63`), with zero console errors.

### 🐞 Environment bugs found only by testing the live site
1. **`curl -o /dev/null` fails with exit 23** on this machine ("Failed writing body"), and `/tmp`
   is not writable either. Write curl output into the gitignored `.wrangler/` directory instead.
2. **The outbound proxy returns 403 for Python's default User-Agent.** `check_deploy.py` reported
   **40 failures, all 403**, against a site that curl fetched perfectly with a browser UA. Fixed
   permanently: the checker now sends a real browser UA. Without that fix a live-site run tests
   the proxy, not the site — and would have "proven" a working deployment was broken.

### Deployment mechanics
Deploys are currently **manual** (`wrangler pages deploy`). Connecting the GitHub repo in the
Cloudflare dashboard would auto-deploy on every push — worth doing before the ad-tuning phase,
since every ad-code change requires a redeploy.

---

## ✅ Step 8 — growth cycle 1 (14 → 17 tools)

Since Steps 2–6 need your accounts, I ran the growth loop — it is the one part of the
pipeline that needs nothing from you. Took the **top 3 by search value** from the list:

| New tool | Category | Why it was picked |
|---|---|---|
| **Hours Calculator (Time Card)** | Business | "hours calculator" / "time card calculator" are very high-volume commercial queries, and Business had only one tool |
| **Discount Calculator** | Everyday | "percent off" is one of the highest-volume shopping queries on the web |
| **Sales Tax Calculator** | Finance | "sales tax calculator" + "reverse sales tax" (VAT/GST) — very high volume, and the reverse mode is what people actually search for |

Each one got the full treatment, not a stub: unique title/meta/description/keywords,
3 JSON-LD blocks, 3 ad slots, 3 FAQs, two "about" paragraphs, and a working tool with the
edge cases handled (overnight shifts, successive discounts, and the reverse-tax trap where
subtracting the percentage gives the wrong answer).

### Internal linking — fixed a structural gap
The new tools were auto-linked by the related-tools grid, but **Hours Calculator only had 2
inbound links** because `related_for()` filled all four slots from the same category first —
so any tool in a small category stayed invisible to the rest of the site.

Changed `related_for()` to reserve one slot for a **rotating** popular tool from another
category (rotated by position, so different pages surface different tools rather than every
page pointing at the same one). Measured effect on inbound internal links:

- `hours-calculator` **2 → 5** · `invoice-generator` **→ 5**
- Link graph is now denser overall (2–16 inbound links per tool instead of a few hubs).

Also added three genuine **contextual** links in body copy, which carry more weight than
navigation links: Percentage → Discount, Invoice → Hours ("turns a week of start and finish
times into the decimal hours these line items need"), Tip → Sales Tax ("separates the tax from
the food so you can tip on the right number").

### Still to do in this cycle
The **launch/sharing drafts** (Product Hunt blurb, Show HN post, r/SideProject post, 3 X
drafts, 5 Pinterest pin descriptions) — these all need the live URL, so they are queued for
the moment Step 3 completes. Say the word and I'll produce them against a placeholder.

### Verification after the change
`25/25` browser checks × 5 consecutive runs · static checks 0 issues (319 local refs, 17 tool
scripts syntax-checked) · deploy contract PASSED · sitemap now 20 URLs.

New checks added to the suite: the weekly time card (Mon–Fri 09:00–17:00 with a 60-min break
→ **35.00 h**, 5 days), an overnight shift (22:00–06:00 → 8 h), the discount reverse modes
(120 → 84 = **30% off**; 84 after 30% off = **120**), and reverse sales tax (270.63 incl 8.25%
→ net **250**, tax **20.63**).

---

## ✅ Step 6 prep — real ad code can no longer blank the site (2026-09-28)

This is the one piece of Step 6 that could be done without your Adsterra account, and it
was worth doing **before** you paste anything in. It also turned out to be a revenue bug,
not just a safety bug.

### The problem

Adsterra's banner codes load a cross-origin `invoke.js` which calls `document.write`.
`document.write` is only legal while a parser is active. I measured what it actually does
in headless Chrome, in this repo, rather than trusting the docs:

| When the write lands | What happens |
|---|---|
| `readyState` = `interactive` (script arrived fast) | **Silently swallowed.** Page survives, nothing logged, **nothing written — the ad never appears.** |
| `readyState` = `complete` (script arrived after load) | Implicit `document.open()` → **the entire document is erased.** Visitor gets a blank tab. |

So without a fix you get one of two outcomes, and which one depends only on network timing:
you either lose the page, or you lose the ad and have no symptom to debug. The blank-tab case
is the one that only shows up **after** real ad code is pasted in — i.e. on launch day, for
every visitor.

### The fix

`assets/ads.js` now renders any slot whose code is known to write inside a same-origin
`srcdoc` iframe. `srcdoc` is parsed normally, so the write lands inside the iframe while a
parser is active: **the ad renders correctly and the page is untouched.** Isolation is
therefore load-bearing for revenue, not just for safety.

Detection can't just look for the string `document.write`, because the snippet you paste
usually contains no such thing — the write lives in `invoke.js` on another host. So it also
matches the known ad-script hostnames. **If you switch networks and see blank slots, add that
network's host to `needsIsolation()`.** Plain markup (AdSense, most native units) still goes
in inline, because some networks require their tag in the top-level document.

Also fixed: `AD_SIZES` and the `ad(slot)` helper were **dead code** — all five ad slots were
hardcoded markup, so the sizes never reached the page. They now emit
`data-w` / `data-h`, which is what the iframe is sized from.

### Verification

`_tests/check_ads.js` is new — **10 checks, 10/10, stable across 5 consecutive runs**, run
against both the emulator and the live site. The ad config is injected by intercepting the
`ads.js` request, so fake ad code can never be left behind in the repo. It asserts **both
halves**: page intact *and* the ad actually rendered inside the iframe.

Critically it carries **two negative controls** that disable the isolation branch, because a
suite that cannot fail proves nothing:

- isolation off + late write → `bodyLen=69 h1=0` — **page confirmed wiped**
- isolation off + instant write → page survives but `payloadTop=false` — **ad confirmed lost**

Both reproduce the real bugs, so the suite's ability to catch them is proven rather than
assumed.

Committed as `91cf1dc`, pushed, deployed. Live markup verified on the edge:
`<div class="ad-slot" data-slot="top" data-w="728" data-h="90" …>` on tool pages and the
homepage. Full live re-verification after deploy: deploy contract **PASSED** · e2e **25/25** ·
ads **10/10**.

---

## Step 7 — affiliate shortlist (prepared, waiting on your signups)

Pages that monetise well: **Invoice Generator**, **Loan/Compound Interest**, **Password
Generator**, **BMI/Water Intake**, and the About page.

**Payout reality first (this is the part that bites):** for countries without easy access to
US/EU banking, the rails that clear reliably are **crypto (USDT)** and **SWIFT wire**;
Payoneer is accepted by some networks but is the exception, not the rule. Network minimums
typically cluster at **$50–100**, and published terms (net-15/net-30) describe when a network
*may* release payment — expect an extra **5–15 business days** of KYC/compliance hold.
**Adsterra itself** supports wire, Payoneer (limited), WebMoney and crypto, which is why it is
the right first network.

**Candidates, best fit first** — verify Libya eligibility and the payout rail *before*
generating any volume:

| # | Program | Where it goes | Why it fits |
|---|---|---|---|
| 1 | **Web hosting** (Hostinger / Namecheap / SiteGround) | About page, footer | Highest payouts on this list; "how I built this" framing is natural on an About page |
| 2 | **VPN / security** (NordVPN / Surfshark / PureVPN) | Password Generator | Perfect contextual fit — the user is literally thinking about security |
| 3 | **Invoicing / accounting** (FreshBooks / Zoho Invoice / Invoice Ninja) | Invoice Generator | The highest-intent page on the site; recurring commissions on some programs |
| 4 | **Email / creator tools** (ConvertKit / Beehiiv) | Word Counter, Case Converter | Writers and creators are the audience for those pages |
| 5 | **Crypto exchange referral** (Binance / Bybit) | Loan + Compound Interest | Pays in crypto by default, no bank needed — but check local regulatory rules first |

**Two honest cautions.** (a) Most affiliate programs review your site and many reject empty
or brand-new sites — apply *after* the site has some traffic, and expect rejections early.
(b) I could not verify Libya-specific acceptance for any of these; sources on publisher
payouts by country cover CIS countries, not North Africa. Confirm with each program's
affiliate manager **in writing** which countries and rails cleared payouts in the last 30
days, and treat the first payout as the real test.

When you've signed up, send me the tracking links and I'll insert them with
`rel="sponsored noopener"`, update the About-page disclosure, rebuild and verify.

---

## 🔄 Step 4 — Google Search Console (tag deployed, awaiting your click)

**The verification tag is live and verified.** `GOOGLE_VERIFICATION` in `build.py` holds the
token Google issued, and `verification_tags()` renders it into **every** page's `<head>` —
Google only checks the property URL, but carrying it site-wide means a future rebuild can never
drop it from the one page that matters. `BING_VERIFICATION` is stubbed for the same treatment.

Checked against production rather than the local build:

| URL | Result |
|---|---|
| `https://lazytools.pages.dev/` | tag present, token **matches** Google's exactly |
| `https://lazytools.pages.dev/about` | tag present, token **matches** |
| Local build | tag on **21 / 21** pages |

Deploy contract re-run after the change: **PASSED**.

### 👉 What you need to do
1. Go back to the **Search Console** tab where you copied the tag
2. Click **Verify**
3. Once it says *"Ownership verified"*, open **Sitemaps** in the left menu
4. Enter `sitemap.xml` and click **Submit**

Then tell me and I'll do the Bing side (it imports straight from GSC, no second tag needed).

> **Note on a red herring:** my first check after deploying reported the tag missing. It was not —
> Cloudflare's CDN had not finished propagating. A deploy reporting success is not the same as the
> edge serving the new bytes, so always re-check the live URL after a short pause before believing
> a failure.

---

## ✅ Step 4b — IndexNow: search engines told about the site (2026-09-28)

Google is **not** an IndexNow participant, so this does **not** replace Search Console — but it is
the one indexing lever that needs no account at all, and it covers **Bing** (which also feeds
Copilot / ChatGPT search), **Yandex**, **Seznam** and **Naver**.

- `build.py` now generates `<key>.txt`, which is how IndexNow proves you own the host. That file
  must stay publicly readable, so it is deliberately **not** in the robots.txt Disallow list.
- `_generator/indexnow.py` verifies the key file is **live and byte-correct before submitting**.
  Submitting against an unreachable key file just returns 403 and teaches you nothing, so the
  script aborts instead. It caught exactly that on its very first dry run, before the file had
  been deployed — the guard did its job the first time it was asked to.
- All 20 URLs submitted → **HTTP 202, accepted**.

This keeps paying off every growth cycle: each new tool gets pinged immediately instead of waiting
for a recrawl.

---

## ✅ Step 8b — launch kit written (2026-09-28)

`LAUNCH.md` — the drafts that were queued waiting on a live URL. Now complete and ready to post:

- **Product Hunt:** name, a 43-character tagline, description, and a ready-to-paste first comment
- **Show HN:** title + body that leads with the two real bugs instead of a feature list
- **r/SideProject:** post built around what was actually learned building it
- **3 X posts:** launch, privacy angle (the strongest), build angle
- **5 Pinterest pins** with titles + descriptions, matched to the tools Pinterest actually sends
  traffic to — sleep cycle, BMI, compound interest, time card, discount
- A **"what to watch" table**, plus an explicit warning not to respond to a weak launch by adding
  30 more tools

The copy deliberately leads with *"no signup"* and *"your data never leaves your device"* rather
than "17 tools". The count is not the interesting part, and both claims are literally true here
because every tool computes client-side.

---

## 💰 Will this get monetized? — the honest math (2026-09-28)

**Short answer: the mechanism is real and the site is built for it, but revenue today is $0 and
stays $0 until three things happen that only you can do.**

### What is actually blocking money right now

| # | Blocker | Evidence in the repo | Effect |
|---|---|---|---|
| 1 | **The site is not on the internet** | `SITE_URL` is still `https://YOUR-DOMAIN.com`; no GitHub repo; never deployed | 0 pageviews → 0 revenue. Nothing else matters until this is fixed. |
| 2 | **No ad codes exist** | `assets/ads.js` → `top: ""`, `middle: ""`, `bottom: ""` | A deployed site with empty slots earns exactly $0. |
| 3 | **No public contact address** | `CONTACT_EMAIL` unset → About page has no real email | Ad networks and AdSense read a missing contact as a disposable site. Cheapest fix on the list. |

### The RPM figure in the README is too optimistic — correct it

`README.md` claims **$2.50–$12.50 RPM**. That is the *top* of the range, achievable on AdSense
with premium US/UK finance traffic. A brand-new tool site on Adsterra with mixed-geo traffic
should be **planned at $0.50–$3.00 RPM**. So the README's "10k pageviews ≈ $50" is optimistic by
**2–10×**. Plan against the table below instead.

| Monthly target | @ $0.50 RPM | @ $1.50 RPM | @ $3.00 RPM |
|---|---|---|---|
| **$50** | 100,000 pv | 33,000 pv | 17,000 pv |
| **$250** | 500,000 pv | 167,000 pv | 83,000 pv |
| **$1,000** | 2,000,000 pv | 667,000 pv | 333,000 pv |

*Adsterra pays out from **$5** via crypto/Tether/Paxum (local-currency methods have a $25
minimum), so the first payout is reachable long before the site is profitable.*

### Honest timeline
- **Month 1–3 — ~$0.** New site; Google indexes slowly; 20 URLs at best.
- **Month 3–6 — first trickle.** A few hundred to a few thousand pageviews/mo → **$1–10/mo**.
- **Month 6–12 — the real test.** If you keep adding tools (25+ is the target) and the pages
  rank → **$50–$300/mo**.
- **The bottleneck is not code, it is traffic.** Traffic is a 6–12 month compounding game, and
  a tool site is a portfolio of lottery tickets: most pages earn nothing, a few earn everything.

### Risks that could hard-block it
1. **Ad-network approval.** Adsterra approves most sites quickly and even publishes a guide to
   monetizing Blogspot sites — so free hosting is not automatically disqualifying. Still, confirm
   the `*.pages.dev` URL is accepted at submission. If it is refused, a ~$10/yr domain removes
   the objection entirely.
2. **AdSense is not available yet.** AdSense requires a domain you control and rejects free
   subdomains. Adsterra first; revisit AdSense at ~10k visits/mo on a real domain.
3. **Affiliate rejections.** Most programs review sites and reject brand-new, traffic-less ones.
   Apply after month 3, not week 1.
4. **Nothing is verifiable yet.** Every number above is a projection. Until the site is live and
   indexed there is no data — and no data means no decision.

### The 30-day plan (do not skip week 1; nothing else works without it)

**Week 1 — get it live** *(needs you, ~45 minutes total)*
- Fill `INFO.md` → I set `SITE_URL` + `CONTACT_EMAIL`, rebuild, verify, push, deploy to
  Cloudflare Pages, then `curl` the live URL and re-run `check_deploy.py` against it.
- Re-author the commits to your real git identity (currently "LazyTools Builder").
- Refresh `og-image.png` — it still says "14 tools" and there are now 17.

**Week 2 — get it found**
- Google Search Console + Bing: verify, submit `sitemap.xml`, record the dates here.
- Turn on Cloudflare Web Analytics (free, no cookie banner needed).
- Apply to Adsterra, submit the site, create the 3 ad units, paste the codes, add the `ads.txt`
  line, redeploy, confirm ads render on the live site.

**Week 3 — add surface area**
- 3 more tools from the prioritised list, each with contextual internal links.
- Publish the queued launch drafts (Product Hunt, Show HN, r/SideProject, 3 X posts, 5 Pinterest
  pins) — they are written and waiting on the live URL.

**Week 4 — measure, do not guess**
- Report: indexed pages, impressions, clicks, top queries, RPM, revenue.
- Double down on whichever tool page earned the most impressions; do not delete the losers yet.
- **Decision point:** 0 impressions by day 30 means the problem is *indexation*, not content.
  The fix is a real domain + a few backlinks — **not more tools.**

**The one mistake to avoid:** adding 30 tools before the site is indexed. Indexation is the
constraint, not content volume. 17 well-linked tools that Google has indexed beat 50 that it
has not.

---

## Log

### 2026-09-28 — Step 1 + production-readiness pass
- Read the repo: `build.py` (354 lines) generates everything from `tools_core.py` (9 tools)
  + `tools_extra.py` (5 tools) = **14 tools**. Ad codes live in `assets/ads.js`.
- Created `INFO.md` (template, git-ignored), `.gitignore`, `PROGRESS.md`.
- Environment: git 2.55 · node v22.22.2 + npx 10.9.7 · python 3.13.14 · `gh` **missing**
  → installed 2.101.0 via winget · winget available.
- Built, found and fixed the two bugs above, verified with a layered suite, committed.

### 2026-09-28 — Step 8 growth cycle 1 + monetization reality check
- Added Hours, Discount and Sales Tax calculators (14 → 17 tools); rewrote `related_for()` to
  fix the small-category silo. Verified: 25/25 browser checks ×5, static 0 issues, deploy
  contract PASSED, sitemap 20 URLs. Commit `a693739`.
- Answered "will this get monetized?" with the honest math above. Corrected the README's RPM
  claim ($2.50–$12.50 → plan at $0.50–$3.00 for Adsterra/mixed geo). Confirmed the three live
  blockers: not deployed, no ad codes, no public contact email.
- Confirmed Adsterra's payout floor is **$5** via crypto/Tether/Paxum ($25 for local-currency
  methods), and that Adsterra monetizes Blogspot sites — i.e. free hosting is not automatically
  disqualifying, but the `*.pages.dev` URL should still be confirmed at submission.
- Nothing deployed or published; still waiting on `INFO.md`.

### 2026-09-28 — Step 1c: real config wired in + repo incident
- You supplied **name: [scrubbed]**, **email / contact_email: kingripper9@gmail.com**. Wrote them
  into `INFO.md` (still git-ignored) and wired `CONTACT_EMAIL` into the build, so About and
  Privacy now serve a real `mailto:`. Set `SITE_URL` to the provisional production hostname.
- Regenerated the OG card via the new `_generator/make_og.py` (was stale at "14 tools").
- Corrected the README's tool count and its optimistic RPM claim.
- **Lost the 6-commit history to a `git rebase --root` accident** (see "Repository incident").
  No content and no public history lost; repo rebuilt as one honest commit, now authored as
  the owner. Verified again after rebuilding: 25/25 E2E, static 0 issues, deploy contract PASSED.
- Still needed from you: **`domain`** (or "none"), and `payout_wallet` before the first payout.

### 2026-09-28 — decisions locked in; GitHub device login issued
- **You decided:** no custom domain (free `lazytools.pages.dev`), **Cloudflare Web Analytics**,
  and GitHub first. All recorded in `INFO.md`.
- **Step 5 pre-wired.** `ANALYTICS_CODE` constant + `__ANALYTICS__` injection in `head()`.
  Verified both directions: a test snippet injects on every page; blank emits nothing at all.
  Step 5 is now a one-line paste after deploy.
- **New guard:** `check_static.py` fails on any unsubstituted `__TOKEN__` in built HTML.
  Negative-tested by deleting the `__ANALYTICS__` replace — caught on all 21 pages.
- **GitHub device flow issued** (`gh auth login --web`). Code **`1BBF-B91F`**, waiting on you at
  https://github.com/login/device. Repo creation and push follow as soon as it's approved.
- Static checks still 0 issues (319 refs, 17 JS blocks).

### 2026-09-28 — Step 2 complete: the site is on GitHub
- **GitHub login completed** as **darkgambit** via the device flow. The first code expired before
  use (that is normal and harmless) — a second one was issued and approved.
- **Public repo created and pushed: https://github.com/darkgambit/lazytools**
  4 commits, 42 files, branch `main`, all authored as the owner.
- **Pre-publish safety scan** over every tracked file: no secrets, tokens or private keys. The
  only personal data that goes public is `kingripper9@gmail.com`, and that is deliberate — it is
  the published contact address on `/about` and `/privacy`, which ad networks require.
  `INFO.md` and `.workbuddy-ai/` confirmed absent from the remote via the GitHub API.
- Local quirk worth remembering: the `origin/main` remote-tracking ref does not persist on this
  filesystem (`git branch -r` is empty, `git rev-parse origin/main` fails) even though the fetch
  reports success and the push works. Push with an explicit refspec if a command ever needs it.
- **Next: Step 3 — Cloudflare Pages deploy.** Needs your Cloudflare login.

### 2026-09-28 — Step 3 complete: THE SITE IS LIVE
- **https://lazytools.pages.dev** — Cloudflare Pages free tier, project `lazytools`, 44 files.
- The project name was free, so the assigned hostname matched the provisional `SITE_URL`
  exactly and no rebuild was needed. Verified live: homepage 200 with correct title + canonical,
  17 tool cards, tool pages 200, contact `mailto:` live on `/about`.
- **Deploy contract PASSED against the live URL** and **browser E2E 25/25 in Chrome against
  production** with zero console errors.
- Two environment bugs found only because I tested the live site rather than stopping at the
  emulator: `curl -o /dev/null` exit 23 (plus `/tmp` being unwritable), and the proxy returning
  **403 for Python's default User-Agent** — which made the deploy checker report 40 false
  failures until it was given a browser UA.
- **Next: Step 4 — Google Search Console.** Needs your Google login; I inject the verification
  tag, redeploy, then you click Verify.

### 2026-09-28 — Step 4b (IndexNow) + Step 8b (launch kit) while Step 4 waits
- **IndexNow live.** `build.py` generates `<key>.txt`; `_generator/indexnow.py` checks that file
  is live and byte-correct *before* submitting, then posts all 20 URLs → **HTTP 202 accepted**.
  Covers Bing (and thus Copilot/ChatGPT search), Yandex, Seznam, Naver. No account needed. The
  pre-flight guard aborted correctly on its first dry run because the key file had not been
  deployed yet.
- **`LAUNCH.md` written** — Product Hunt, Show HN, r/SideProject, 3 X posts and 5 Pinterest pins,
  all ready to paste now that there is a live URL to point at. Also added `/LAUNCH.md` to the
  robots.txt Disallow list, since the repo root is the deploy directory.
- Verified: static checks 0 issues · live `og-image.png` 200 (`image/png`, 117 KB) so social
  previews will render · live key file 200 with the correct body.
- **Still blocked on you for Step 4** (Google Search Console). Everything else that can be done
  without your credentials is now done.

### 2026-09-28 — Step 4: verification tag deployed and matched
- the owner supplied the GSC token. Added `GOOGLE_VERIFICATION` + `verification_tags()` to
  `build.py`, rendered into **every** page's `<head>` (21/21), so a future rebuild can never drop
  it from the one page Google checks. `BING_VERIFICATION` stubbed for the same flow.
- **Checked against production, not the local build:** the token on
  `https://lazytools.pages.dev/` and `/about` matches Google's exactly. Deploy contract PASSED.
- **Red herring worth remembering:** the first post-deploy check reported the tag *missing*. It
  wasn't — Cloudflare's CDN had not finished propagating. A deploy reporting success is not the
  same as the edge serving the new bytes. Pause and re-fetch before believing a failure.
- **Awaiting the owner:** click **Verify**, then submit `sitemap.xml`. Bing imports from GSC next.

### 2026-09-28 — Step 6 prep: ad code can no longer blank the site
- The open item from the previous session was a **failing negative control** in the ad-isolation
  suite. Diagnosed it instead of papering over it, and the diagnosis changed the design brief.
- **Measured `document.write` behaviour directly** with a throwaway probe that ran the real
  `assets/ads.js` with the isolation branch dead, recording `readyState` at write time:
  - at `interactive` → write silently swallowed, `lenBefore=8988 lenAfter=8988`, page survives,
    nothing written;
  - at `complete` → `lenBefore=9222 lenAfter=29`, `h1` gone, `readyState` reset to `loading` —
    the document really is erased.
- So the original negative control was **mis-timed, not wrong about the hazard**: it injected the
  ad during the deferred-script phase, which is precisely the no-op case. The real failure needs
  the write to land after load, which is what any cold cross-origin fetch does.
- A second finding, and the more expensive one: with isolation off and an instant write, the page
  survives but **the ad never renders** (`payloadTop=false`). Blank slots, no error, no symptom.
  Isolation is therefore load-bearing for **revenue**, not just safety.
- **Rewrote `_tests/check_ads.js`** around the measured behaviour: 10 checks, 10/10, stable across
  5 consecutive runs, green against the emulator *and* live. Now asserts both halves — page intact
  *and* ad rendered inside the iframe — and carries two negative controls, one per failure mode.
  Both reproduce real bugs, so the suite is proven able to fail.
- Corrected the `assets/ads.js` header comment to describe what was measured rather than what was
  assumed, and documented that new ad networks may need their host added to `needsIsolation()`.
- Commit `91cf1dc`, pushed, deployed. Post-deploy live re-verification: deploy contract PASSED ·
  e2e 25/25 · ads 10/10 · slot markup with `data-w`/`data-h` confirmed on the edge.
- **Next blocker is unchanged and still yours:** the Adsterra publisher account (Step 6).
