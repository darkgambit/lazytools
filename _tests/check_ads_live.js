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
const PAGES = ['/tools/bmi-calculator', '/', '/tools/compound-interest-calculator'];

const AD_REQ = /highrevenueformat|highperformanceformat|profitabledisplay|effectivegatecpm|adsterra|invoke\.js/i;

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME, headless: true, args: ['--disable-gpu', '--no-sandbox']
  });
  let bad = 0, note = 0;

  for (const p of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await ctx.newPage();
    const adReqs = [];
    page.on('request', r => { if (AD_REQ.test(r.url())) adReqs.push(r.url()); });
    try {
      await page.goto(BASE + p, { waitUntil: 'domcontentloaded', timeout: 30000 });
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

      const detail = `slots=${out.slots} live=${out.live} hidden=${out.hidden} demo=${out.demo} ` +
                     `slot=${out.filledSlot} iframe=${out.iframe} inner=[${out.innerTags}] ` +
                     `adReq=${adReqs.length}`;

      if (!out.alive || out.demo > 0) {
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
