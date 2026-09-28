# LAUNCH.md — launch and sharing kit

Everything here is written and ready. The site is live at **https://lazytools.pages.dev**, so
there is nothing left to wait for. Copy, paste, post.

---

## Before you post — a 2-minute checklist

- [ ] **Open the live site on your phone** and use two or three tools. Do this before a stranger
      does; a broken mobile layout discovered by your first 50 visitors is unrecoverable.
- [ ] **Check the social preview.** Paste `https://lazytools.pages.dev` into
      <https://www.opengraph.xyz>. You should see the dark card reading *"Free online tools that
      work while you sleep"*. If you see a blank box, stop and tell me — a post with a broken
      preview loses most of its clicks.
- [ ] **Decide where you will actually reply.** A launch post the maker never answers reads worse
      than no post at all. Pick the one or two places you'll genuinely watch for a few hours.
- [ ] **Have the elevator pitch ready** (below). If you can't explain it in one line, neither can
      anyone reading it.

---

## The elevator pitch — use this everywhere

> **17 free calculators, converters and generators that run entirely in your browser. No signup,
> no uploads, no limits — your data never leaves your device. Built and run by one person.**

Why this works: *"no signup"* and *"your data never leaves your device"* are the two things people
actually care about, and both are literally true here — every tool computes client-side. Lead with
those, not with "17 tools", because the number is not the interesting part.

---

## Product Hunt

**Name:** LazyTools

**Tagline (43 chars, limit is 60):**
```
17 free tools that never ask you to sign up
```

**Description:**

> Every "free online calculator" I tried wanted an email, an account, or sent my numbers to a
> server. So I built the opposite: 17 tools that run entirely in your browser. Nothing is
> uploaded, nothing is stored, nothing is limited.
>
> Age and date calculators, compound interest and loan maths, BMI, sleep cycles, a unit
> converter, word counter, password generator, invoice generator, a time-card calculator that
> totals your week in decimal hours, sales tax and discount calculators — and more.
>
> No signup. No account. No usage limits. Open a tool, get your answer, close the tab.

**First comment — post this immediately after launching:**

> Hi PH 👋
>
> I built this because I got tired of "free" calculators that want your email before they'll show
> you a number. It always felt backwards: the maths is trivial, the data collection isn't.
>
> Everything here runs client-side. Open DevTools, watch the network tab, and use any tool — it
> stays quiet. Your inputs genuinely never leave your device, which matters for the ones where
> the input is personal: your weight, your salary, your birth date.
>
> It's 17 tools today and I add a few most weeks. If there's one you'd actually use that isn't
> there, tell me — that's literally how the last three got built.
>
> Happy to answer anything about how it's put together.

---

## Show HN

**Title:**
```
Show HN: 17 browser-only calculators and converters, no signup
```

**Body:**

> I kept hitting the same annoyance: searching for a simple calculator, landing on a page that
> wants an account, or that quietly posts my numbers somewhere.
>
> So this is a static site with 17 tools that all compute client-side — plain JS, no backend, no
> accounts, no database. Unit converter, compound interest, loan amortisation, BMI, sleep cycles,
> date maths, time cards in decimal hours, invoice generator, password generator.
>
> Two things I got wrong and only caught by testing the deployed site rather than trusting my own
> build output:
>
> 1. I had the shared script `defer`-loaded. Deferred scripts run after HTML parsing, but each
>    tool page ran its init inline at the end of `<body>` — so the init ran first and threw. The
>    unit converter's dropdowns were simply empty. The page still rendered, and anything wired to
>    a click still worked, so it looked completely healthy.
> 2. Every canonical URL pointed at a redirect, because Cloudflare Pages serves extensionless
>    paths and I'd written trailing slashes. All 17 pages were telling Google "the real URL is
>    somewhere else".
>
> Both were invisible in a local preview and obvious against production. Worth the extra rung.
>
> No signup, no uploads, no tracking beyond a page count. Feedback welcome — especially "this
> one's wrong", because a calculator that is subtly wrong is worse than no calculator at all.

---

## r/SideProject

**Title:**
```
I built 17 browser-only tools because I hated "free" calculators that want your email
```

**Body:**

> I got annoyed enough to build something about it.
>
> Every time I searched for a simple calculator I'd land on a site that wanted an account, or
> that sent my numbers to a server. The maths is trivial. The data collection is the whole point
> of the site.
>
> So: 17 tools, all client-side, no signup, no accounts, no limits. Age and date maths, compound
> interest, loans, BMI, sleep cycles, unit conversion, word counting, password generation, an
> invoice generator, a time-card calculator.
>
> What I learned building it:
>
> - **The boring distribution problem is the real problem.** Building 17 tools took a fraction of
>   the time I've spent on getting anyone to find them.
> - **Testing the deployed thing is not optional.** Two real bugs — dead dropdowns on load, and
>   every canonical URL pointing at a redirect — only appeared against production. Local preview
>   said everything was fine.
> - **Static hosting is genuinely free now.** No server, no database, $0/month, and it will not
>   fall over if something gets popular.
>
> Not monetised yet beyond a plan for ads. Right now I'm just trying to get it in front of people
> and find out which tools are actually useful.
>
> Link: https://lazytools.pages.dev — tell me what's missing and I'll build it.

---

## X / Twitter

**Post 1 — the launch**

> I built 17 free tools that run entirely in your browser.
>
> No signup. No account. No uploads. No limits.
>
> Age, dates, compound interest, loans, BMI, sleep cycles, unit conversion, word counts,
> passwords, invoices, time cards.
>
> https://lazytools.pages.dev

**Post 2 — the privacy angle (the strongest one)**

> Most "free" online calculators ask for your email before they'll do arithmetic.
>
> This one doesn't, because the arithmetic happens on your device.
>
> Open DevTools, watch the network tab, use any of the 17 tools. It stays quiet.
>
> Your weight, salary and birth date never leave your browser.

**Post 3 — the build angle**

> Two bugs that only showed up after I deployed, not in local preview:
>
> 1. The unit converter's dropdowns were completely empty on load
> 2. All 17 pages told Google their real URL was somewhere else
>
> Both passed every local check. Test the deployed thing.

---

## Pinterest

Pinterest is a real traffic source for exactly these queries, and the pins that work are the
*visual* ones — a chart or a table, not a screenshot of a form. Make each pin from the matching
tool page.

**Pin 1 — Sleep Cycle Calculator**
> **Title:** The best time to wake up, based on 90-minute sleep cycles
> **Description:** Sleep runs in roughly 90-minute cycles, so waking between them leaves you
> groggy no matter how long you slept. Work out your ideal bedtime — or what time to set the
> alarm — from the time you actually need to get up. Free, no signup.

**Pin 2 — BMI Calculator**
> **Title:** BMI chart and healthy weight range (metric + imperial)
> **Description:** Work out your BMI in metric or imperial and see where you sit in the WHO
> categories, plus the healthy weight range for your height. Free online BMI calculator — nothing
> to install, nothing to sign up for.

**Pin 3 — Compound Interest Calculator**
> **Title:** See what your savings actually become, year by year
> **Description:** Compound interest is the whole game with long-term saving, and it's genuinely
> hard to feel from a formula. Put in your starting amount, monthly deposit and rate, and see the
> year-by-year table — including what happens when you raise the monthly amount.

**Pin 4 — Hours / Time Card Calculator**
> **Title:** Time card calculator — turn a week of shifts into decimal hours
> **Description:** Payroll needs decimal hours, not "9:15 to 5:30". Enter your week's start and
> finish times, add breaks, and get the total in decimal hours ready to hand in. Handles overnight
> shifts. Free, no signup.

**Pin 5 — Discount Calculator**
> **Title:** Percent off calculator — and what you actually save
> **Description:** Work out the sale price, the amount you save, and the original price from a
> discounted one. Includes the reverse mode most calculators get wrong: find the pre-discount
> price when all you know is the final price and the percentage.

---

## What to watch afterwards

Track these and nothing else for the first 30 days:

| Signal | Where | What it means |
|---|---|---|
| Impressions | Search Console → Performance | Google has started showing pages. **Zero here by day 30 means the problem is indexation, not content.** |
| Clicks + top queries | Search Console → Performance | Which tools people actually want — build more of those |
| Referrals | Cloudflare Web Analytics | Which launch post worked |
| Pageviews | Cloudflare Web Analytics | The only number that turns into revenue |

**Do not add 30 more tools because a launch post underperformed.** If nothing is indexed by day
30, the fix is a real domain and a few backlinks — not more pages nobody can find.
