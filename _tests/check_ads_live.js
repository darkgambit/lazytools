/* ============================================================================
   Live ad-render check — does the REAL ad tag actually fire in production?

   Run against the live site (or the emulator on the staged tree):
     LT_BASE=https://lazytools.pages.dev node _tests/check_ads_live.js
     LT_BASE=http://127.0.0.1:8788          node _tests/check_ads_live.js

   This is NOT part of check_ads.js, and the split is deliberate.
   check_ads.js is hermetic: it mocks invoke.js, so it can prove that a write RENDERS,
   deterministically and offline. This file is the opposite — it needs the real network
   and the real publisher tag, and it answers the one question the mock cannot: is the
   tag that is actually configured in assets/ads.js live, or is it silently doing nothing?

   WHAT IS PROVABLE HERE, AND WHAT IS NOT
   Adsterra deliberately serves nothing to headless/bot traffic, so asserting on a
   rendered creative would be asserting on their anti-fraud policy rather than on this
   site's code. What IS provable, and is the part this site controls:
     - the isolation iframe was created for the filled slot,
     - the ad script was actually REQUESTED (so the srcdoc parsed and the tag executed —
       i.e. the write path is live rather than silently swallowed),
     - the page survived, and no slot is advertising itself to visitors.
   A page that carries no slot for the configured unit is reported as NOTE, not a
   failure — that is a placement decision, not a defect.
============================================================================ */
const { chromium } = require('playwright-core');

const CHROME = process.env.LT_CHROME ||
  'C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE = (process.env.LT_BASE || 'http://127.0.0.1:8788').replace(/\/$/, '');
const PAGES = [
  { path: '/tools/bmi-calculator' },
  { path: '/' },
  { path: '/tools/compound-interest-calculator' },
  /* The forced-navigation reports are a MOBILE problem, and `top` serves a different unit
     at this width, so one page is checked phone-sized with a mobile UA rather than assumed
     to behave like the desktop pass. */
  { path: '/tools/bmi-calculator', mobile: true }
];

const AD_REQ = /highrevenueformat|highperformanceformat|profitableratecpmnetwork|profitabledisplay|effectivegatecpm|adsterra|invoke\.js/i;

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME, headless: true, args: ['--disable-gpu', '--no-sandbox']
  });
  let bad = 0, note = 0;

  for (const entry of PAGES) {
    const p = entry.path + (entry.mobile ? '  [mobile 390x844]' : '');
    const ctx = await browser.newContext(entry.mobile
      ? { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true,
          userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ' +
                     'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 ' +
                     'Safari/604.1' }
      : { viewport: { width: 1280, height: 900 } });
    const page = await ctx.newPage();
    const adReqs = [];
    page.on('request', r => { if (AD_REQ.test(r.url())) adReqs.push(r.url()); });
    /* Adsterra banner units are reported to force navigation on mobile even when no
       redirect format is configured, and this project's own policy says to re-test for
       exactly that once codes are live. A visitor who taps a calculator and lands
       somewhere else is the worst failure this site can have, and it would never show up
       as a console error — so it gets its own assertion rather than a footnote. */
    const popups = [];
    ctx.on('page', pg => popups.push(pg.url() || '(about:blank)'));
    let loadedUrl = '';
    try {
      await page.goto(BASE + entry.path, { waitUntil: 'domcontentloaded', timeout: 30000 });
      loadedUrl = page.url();
      /* The isolation iframe is `loading="lazy"`, so a slot below the fold genuinely does
         not load until it is scrolled near. Scroll first, or this reports "no request"
         for a page whose ad is in fact fine. */
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 3));
      await page.waitForTimeout(6000);

      const out = await page.evaluate(() => {
        const slots = [].slice.call(document.querySelectorAll('.ad-slot[data-slot]'));
        const filled = slots.filter(s => s.classList.contains('live'));
        const first = filled[0];
        const frame = first && first.querySelector('iframe');
        let tags = [];
        if (frame) {
          try {
            const d = frame.contentDocument;
            tags = [].slice.call(d.body ? d.body.children : []).map(n => n.tagName.toLowerCase());
          } catch (e) { tags = ['ERR']; }
        }
        return {
          alive: document.body.innerHTML.length > 3000 && document.querySelectorAll('h1').length > 0,
          slots: slots.length,
          live: filled.length,
          hidden: slots.filter(s => getComputedStyle(s).display === 'none').length,
          demo: document.querySelectorAll('.ad-slot .ad-demo').length,
          filledSlot: first ? first.getAttribute('data-slot') : null,
          iframe: !!frame,
          innerTags: tags.join(',')
        };
      });

      const hijack = page.url() !== loadedUrl || popups.length > 0;
      const detail = `slots=${out.slots} live=${out.live} hidden=${out.hidden} demo=${out.demo} ` +
                     `slot=${out.filledSlot} iframe=${out.iframe} inner=[${out.innerTags}] ` +
                     `adReq=${adReqs.length} popups=${popups.length} ` +
                     `nav=${page.url() !== loadedUrl}`;

      if (hijack) {
        bad++;
        console.log('BAD  ' + p + '  UNEXPECTED NAVIGATION  ' + detail);
        if (page.url() !== loadedUrl) console.log('       -> ' + page.url());
        popups.forEach(u => console.log('       popup: ' + u));
      } else if (!out.alive || out.demo > 0) {
        bad++;
        console.log('BAD  ' + p + '  ' + detail);
      } else if (!out.filledSlot) {
        note++;
        console.log('NOTE ' + p + '  no slot is filled for the configured unit — ' + detail);
      } else if (out.iframe && adReqs.length > 0) {
        console.log('OK   ' + p + '  ' + detail);
      } else {
        bad++;
        console.log('BAD  ' + p + '  filled slot did not fire  ' + detail);
      }
      if (adReqs.length) console.log('       ' + adReqs.join('\n       '));
    } catch (e) {
      bad++;
      console.log('BAD  ' + p + '  ' + e.message.split('\n')[0]);
    }
    await ctx.close();
  }

  await browser.close();
  console.log('');
  console.log('==== ' + (bad ? bad + ' page(s) FAILED' : 'all checked pages fired the ad') +
              (note ? ', ' + note + ' page(s) with no slot for the unit' : '') + ' ====');
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error('HARNESS ERROR: ' + e.message); process.exit(1); });
