/* ============================================================================
   Ad-slot isolation checks.

   Run with the Pages emulator up:
     npx --yes wrangler@4 pages dev . --port 8788 --ip 127.0.0.1
     NODE_PATH=<managed node_modules> node _tests/check_ads.js

   WHAT THIS PROVES  (measured, not assumed — see MEASURED BEHAVIOUR below)
   Adsterra's banner codes load a cross-origin invoke.js that calls document.write.
   Whether that is survivable depends entirely on WHEN the write lands:

     readyState "interactive" (deferred-script phase)
         document.write is silently SWALLOWED. The page survives, but nothing is
         written — the ad never renders. Revenue lost, no error anywhere.
     readyState "complete" (page loaded)
         document.write implicitly calls document.open(), which ERASES THE WHOLE
         DOCUMENT. The visitor gets a blank tab. This is the real failure mode,
         and it is what happens whenever the ad script arrives after load, i.e.
         on any normal network.

   So an ad is only safe AND visible if its document.write happens while a parser
   is active. That is exactly what rendering it into a same-origin srcdoc iframe
   achieves: srcdoc is parsed normally, the write lands inside the iframe, and
   the page is untouched.

   This suite therefore asserts BOTH halves — page intact AND ad rendered — and
   includes two negative controls that disable the isolation branch to prove the
   suite actually detects the bugs it exists to catch. A suite that cannot fail
   proves nothing.

   The ad config is injected by intercepting the ads.js request rather than by
   editing the file, so the test can never leave fake ad code behind in the repo.
============================================================================ */
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const CHROME = process.env.LT_CHROME ||
  'C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE = (process.env.LT_BASE || 'http://127.0.0.1:8788').replace(/\/$/, '');
const ADS_JS = path.join(__dirname, '..', 'assets', 'ads.js');
const AD_HOST = '**/www.highperformanceformat.com/**';

let pass = 0, fail = 0;
function check(label, ok, detail) {
  console.log((ok ? 'PASS ' : 'FAIL ') + label + (detail ? '  | ' + detail : ''));
  ok ? pass++ : fail++;
}

/* What a real Adsterra unit writes out. */
const PAYLOAD = '<div id="ad-payload" style="width:728px;height:90px">AD PAYLOAD</div>';

/* The snippet the publisher pastes: a config block plus the cross-origin invoke.js.
   Note there is no literal document.write in THIS string — the write happens inside
   invoke.js — so detection cannot rely on scanning for "document.write" alone. */
function adsterraAd(key) {
  return '<script type="text/javascript">\n' +
    "  atOptions = { 'key': '" + key + "', 'format': 'iframe', 'height': 90, 'width': 728, 'params': {} };\n" +
    '</script>\n' +
    '<script type="text/javascript" src="//www.highperformanceformat.com/' + key + '/invoke.js"></script>';
}

/* invoke.js, two timings. Instant = fast network / warm cache. Late = the write
   lands in a task, which is what a cold cross-origin fetch looks like. */
const INVOKE_INSTANT = 'document.write(' + JSON.stringify(PAYLOAD) + ');';
const INVOKE_LATE =
  'setTimeout(function () { document.write(' + JSON.stringify(PAYLOAD) + '); }, 400);';

/* An Adsterra-style snippet that does call document.write inline, so detection by
   literal match can be exercised too. */
const DOCWRITE_AD =
  '<script type="text/javascript">\n' +
  "  atOptions = { 'key': 'testkey', 'format': 'iframe', 'height': 90, 'width': 728, 'params': {} };\n" +
  "  document.write('<scr' + 'ipt type=\"text/javascript\" src=\"//www.highperformanceformat.com/testkey/invoke.js\"><\\/scr' + 'ipt>');\n" +
  '</script>';

/* Plain markup, the shape AdSense-style/native units can take — must stay inline. */
const PLAIN_AD =
  '<div id="plain-ad" style="width:300px;height:250px;background:#eee">plain unit</div>';

function patchAdsJs(adCode) {
  const src = fs.readFileSync(ADS_JS, 'utf8');
  const out = src.replace('top:    "",', 'top: ' + JSON.stringify(adCode) + ',');
  if (out === src) throw new Error('could not inject test ad code into ads.js');
  return out;
}

/* Negative control: disable the isolation decision entirely, so the ad code runs in
   the top-level document. This is the bug the suite exists to catch, and the suite
   is only trustworthy if it actually fails here. */
function patchAdsJsUnisolated(adCode) {
  const src = patchAdsJs(adCode);
  const marker = 'if (cfg.forceIsolate || needsIsolation(code)) {';
  if (!src.includes(marker)) throw new Error('isolation branch marker not found');
  return src.replace(marker, 'if (false) {');
}

async function scenario(browser, { adCode, invokeBody, unisolated, settle = 1500 }) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e.message)));
  await page.route('**/assets/ads.js', r => r.fulfill({
    status: 200, contentType: 'application/javascript',
    body: unisolated ? patchAdsJsUnisolated(adCode) : patchAdsJs(adCode)
  }));
  if (invokeBody) {
    await page.route(AD_HOST, r => r.fulfill({
      status: 200, contentType: 'application/javascript', body: invokeBody
    }));
  }
  await page.goto(BASE + '/tools/bmi-calculator', { waitUntil: 'load' });
  await page.waitForTimeout(settle);

  let out = { bodyLen: -1, h1: -1, iframes: -1, slotLive: -1, plainInline: -1,
              payloadTop: null, payloadInFrame: null, errs };
  try {
    out = Object.assign(out, await page.evaluate(() => {
      const frame = document.querySelector('.ad-slot[data-slot="top"] iframe');
      let payloadInFrame = null;
      if (frame) {
        try {
          const d = frame.contentDocument;
          payloadInFrame = !!(d && d.querySelector('#ad-payload'));
        } catch (e) { payloadInFrame = 'ERR'; }
      }
      return {
        bodyLen: document.body ? document.body.innerHTML.length : -1,
        h1: document.querySelectorAll('h1').length,
        iframes: document.querySelectorAll('.ad-slot[data-slot="top"] iframe').length,
        slotLive: document.querySelectorAll('.ad-slot[data-slot="top"].live').length,
        plainInline: document.querySelectorAll('.ad-slot[data-slot="top"] #plain-ad').length,
        payloadTop: !!document.querySelector('#ad-payload'),
        payloadInFrame
      };
    }));
  } catch (e) { /* a wiped document can make evaluation itself fail */ }
  await ctx.close();
  return out;
}

const alive = r => r.bodyLen > 3000 && r.h1 > 0;

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME, headless: true,
    args: ['--disable-gpu', '--no-sandbox']
  });
  let r;

  /* ---- 1. Adsterra unit whose invoke.js arrives LATE — the real-world case ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_LATE
  });
  check('late document.write ad does NOT wipe the page',
        alive(r), 'bodyLen=' + r.bodyLen + ' h1=' + r.h1);
  check('late document.write ad is isolated in an iframe',
        r.iframes === 1, 'iframes=' + r.iframes);
  check('slot is marked live', r.slotLive === 1, 'live=' + r.slotLive);
  check('late document.write ad actually RENDERS inside the iframe',
        r.payloadInFrame === true,
        'payloadInFrame=' + r.payloadInFrame + ' payloadTop=' + r.payloadTop);

  /* ---- 2. Same unit, invoke.js writes instantly — must behave identically ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_INSTANT
  });
  check('instant document.write ad is isolated and renders',
        r.iframes === 1 && r.payloadInFrame === true && alive(r),
        'iframes=' + r.iframes + ' payloadInFrame=' + r.payloadInFrame +
        ' bodyLen=' + r.bodyLen);

  /* ---- 3. A snippet with a literal document.write, but no invoke.js needed ---- */
  r = await scenario(browser, { adCode: DOCWRITE_AD });
  check('literal document.write snippet is isolated',
        r.iframes === 1 && alive(r),
        'iframes=' + r.iframes + ' bodyLen=' + r.bodyLen);

  /* ---- 4. Plain markup — must stay inline, because some networks require the
             top-level document and an iframe would break their measurement. ---- */
  r = await scenario(browser, { adCode: PLAIN_AD });
  check('plain ad code stays inline (no iframe)',
        r.plainInline === 1 && r.iframes === 0,
        'inline=' + r.plainInline + ' iframes=' + r.iframes);
  check('plain ad code does not break the page',
        alive(r), 'bodyLen=' + r.bodyLen + ' h1=' + r.h1);

  /* ---- 5. NEGATIVE CONTROL A — the page-wipe bug.
             Isolation off + late write must DESTROY the page. The assertion is
             inverted on purpose: this test is expected to "fail" as a check. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_LATE, unisolated: true
  });
  check('NEGATIVE CONTROL: without isolation the late write DOES wipe the page',
        !alive(r), 'bodyLen=' + r.bodyLen + ' h1=' + r.h1);

  /* ---- 6. NEGATIVE CONTROL B — the silent-revenue-loss bug.
             Isolation off + instant write survives the page but the ad never
             renders. Proves isolation is load-bearing for revenue, not just
             for safety. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_INSTANT, unisolated: true
  });
  check('NEGATIVE CONTROL: without isolation the instant write silently loses the ad',
        alive(r) && r.payloadTop === false && r.iframes === 0,
        'bodyLen=' + r.bodyLen + ' payloadTop=' + r.payloadTop + ' iframes=' + r.iframes);

  await browser.close();
  console.log('');
  console.log('==== ' + pass + ' passed, ' + fail + ' failed ====');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('HARNESS ERROR: ' + e.message); process.exit(1); });
