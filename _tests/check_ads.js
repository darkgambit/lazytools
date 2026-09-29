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
   includes negative controls that disable the detection branch to prove the
   suite actually detects the bugs it exists to catch. A suite that cannot fail
   proves nothing.

   The ad config is injected by intercepting the ads.js request rather than by
   editing the file, so the test can never leave fake ad code behind in the repo.
   That interception also NEUTRALISES the real slots in ads.js, so the suite never
   depends on a live third-party ad network and the ad under test is the only one
   on the page.
============================================================================ */
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const CHROME = process.env.LT_CHROME ||
  'C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE = (process.env.LT_BASE || 'http://127.0.0.1:8788').replace(/\/$/, '');
const ADS_JS = path.join(__dirname, '..', 'assets', 'ads.js');

/* The host Adsterra serves invoke.js from, as seen in the wild. Two are exercised: the
   historical one the suite has always used, and the one the site actually ships today. */
const HOST_LEGACY = 'www.highperformanceformat.com';
const HOST_LIVE = 'www.highrevenueformat.com';

/* Any Adsterra-family host must be aborted outright. Belt and braces: the slot config is
   neutralised below, but if a future edit reintroduces real code into ads.js, this keeps
   the suite hermetic instead of silently letting it hit the network. */
const AD_HOSTS_RE = /(highperformanceformat|highrevenueformat|profitabledisplayformat|profitabledisplaynetwork|effectivegatecpm)\.com/i;

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
function adsterraAd(key, host) {
  host = host || HOST_LEGACY;
  return '<script type="text/javascript">\n' +
    "  atOptions = { 'key': '" + key + "', 'format': 'iframe', 'height': 90, 'width': 728, 'params': {} };\n" +
    '</script>\n' +
    '<script type="text/javascript" src="//' + host + '/' + key + '/invoke.js"></script>';
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

/* Put the ad under test in `top`, and blank the other two slots.

   This is not tidiness — ads.js ships a REAL Adsterra unit in `middle`. If the suite left it
   in place, every scenario would (a) fetch a live third-party script, making the suite fail
   whenever Adsterra has a bad day, and (b) put a second ad on the page that could interfere
   with the one under test. So the whole slots block is replaced, and the absence of
   `middle`/`bottom` is what makes the empty-slot assertions below meaningful. */
function patchAdsJs(adCode, opts) {
  opts = opts || {};
  const src = fs.readFileSync(ADS_JS, 'utf8');
  const replacement = 'slots: {\n    top: ' + JSON.stringify(adCode) +
    ',\n    middle: "",\n    bottom: ""\n  },';
  const out = src.replace(/slots:\s*\{[\s\S]*?\n  \},/, replacement);
  if (out === src) throw new Error('could not replace the slots block in ads.js');
  if (opts.showPlaceholders) {
    const flipped = out.replace('showPlaceholders: false', 'showPlaceholders: true');
    if (flipped === out) throw new Error('could not flip showPlaceholders in ads.js');
    return flipped;
  }
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

/* Negative control: blind the ad-script detection, so a snippet that writes is treated as
   inline. Proves the detection — the host list AND the /invoke.js path — is load-bearing
   rather than decorative. Note this must blind BOTH layers: the host list alone is
   defence-in-depth, because /invoke.js already matches this snippet. */
function patchAdsJsDetectionBlind(adCode) {
  const src = patchAdsJs(adCode);
  const marker = 'AD_SCRIPT.test(code)';
  if (!src.includes(marker)) throw new Error('AD_SCRIPT marker not found');
  return src.replace(marker, 'false');
}

async function scenario(browser, o) {
  const adCode = o.adCode, invokeBody = o.invokeBody, settle = o.settle || 2000;
  const host = o.host || HOST_LEGACY;
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e.message)));

  /* This suite is about ad slots, not analytics, so the analytics beacon is aborted outright.

     It is not cosmetic. Measured: with the beacon's real network fetch allowed, `load` took
     3046 ms; with it aborted, 234 ms. Because every scenario here gets a FRESH browser context,
     that cold third-party fetch is paid on every single page load, and any stall in it holds the
     `load` event open — which surfaced as an intermittent `page.goto: Timeout 30000ms exceeded`
     that looked like a bug in the ad code and was nothing of the sort. (e2e.js does not hit this
     because it reuses one context, so the beacon is cached after the first page.)

     Aborting also keeps the suite honest and offline-capable: it asserts the page's own
     behaviour, and never depends on a third party being up. */
  await page.route('**cloudflareinsights.com/**', r => r.abort());

  /* Hermeticity net: no scenario may reach a real ad network, whatever the slot config says. */
  await page.route(AD_HOSTS_RE, r => r.abort());

  await page.route('**/assets/ads.js', r => r.fulfill({
    status: 200, contentType: 'application/javascript',
    body: o.unisolated ? patchAdsJsUnisolated(adCode)
        : o.detectionBlind ? patchAdsJsDetectionBlind(adCode)
        : patchAdsJs(adCode, { showPlaceholders: o.showPlaceholders })
  }));
  if (invokeBody) {
    await page.route('**/' + host + '/**', r => r.fulfill({
      status: 200, contentType: 'application/javascript', body: invokeBody
    }));
  }
  /* `domcontentloaded`, not `load`. Every assertion below reads DOM state after a settle
     period, so waiting for `load` adds no coverage — it only adds a dependency on every
     third-party request the page makes. ads.js is deferred, so it has already run and the
     slots are populated by the time this resolves. */
  await page.goto(BASE + '/tools/bmi-calculator', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(settle);

  let out = { bodyLen: -1, h1: -1, iframes: -1, slotLive: -1, plainInline: -1,
              emptySlots: -1, hiddenUnfilled: -1, demoText: -1,
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
      const unfilled = [].slice.call(
        document.querySelectorAll('.ad-slot[data-slot="middle"], .ad-slot[data-slot="bottom"]'));
      return {
        bodyLen: document.body ? document.body.innerHTML.length : -1,
        h1: document.querySelectorAll('h1').length,
        iframes: document.querySelectorAll('.ad-slot[data-slot="top"] iframe').length,
        slotLive: document.querySelectorAll('.ad-slot[data-slot="top"].live').length,
        plainInline: document.querySelectorAll('.ad-slot[data-slot="top"] #plain-ad').length,
        emptySlots: document.querySelectorAll('.ad-slot.empty').length,
        hiddenUnfilled: unfilled.filter(s => getComputedStyle(s).display === 'none').length,
        demoText: document.querySelectorAll('.ad-demo').length,
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

  /* ---- 4. THE PRODUCTION HOST. The site ships an Adsterra unit served from
             highrevenueformat.com. Detection there must not rest on the literal
             document.write branch, because the pasted snippet has none. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('0bab55ec2855e74946a5c24ac4862018', HOST_LIVE),
    host: HOST_LIVE, invokeBody: INVOKE_LATE
  });
  check('production host (highrevenueformat.com) ad is isolated and renders',
        r.iframes === 1 && r.payloadInFrame === true && alive(r),
        'iframes=' + r.iframes + ' payloadInFrame=' + r.payloadInFrame +
        ' bodyLen=' + r.bodyLen);

  /* ---- 5. Plain markup — must stay inline, because some networks require the
             top-level document and an iframe would break their measurement. ---- */
  r = await scenario(browser, { adCode: PLAIN_AD });
  check('plain ad code stays inline (no iframe)',
        r.plainInline === 1 && r.iframes === 0,
        'inline=' + r.plainInline + ' iframes=' + r.iframes);
  check('plain ad code does not break the page',
        alive(r), 'bodyLen=' + r.bodyLen + ' h1=' + r.h1);

  /* ---- 6. UNFILLED SLOTS MUST NOT ADVERTISE THEMSELVES.
             With only one of three slots sold, the other two are what a visitor would
             otherwise see: a dashed "Ad space — add code in assets/ads.js" box, on every
             page of the site. That was live before this test existed. ---- */
  r = await scenario(browser, { adCode: adsterraAd('testkey'), invokeBody: INVOKE_LATE });
  check('unfilled slots are collapsed, not shown',
        r.emptySlots === 2 && r.hiddenUnfilled === 2,
        'empty=' + r.emptySlots + ' hidden=' + r.hiddenUnfilled);
  check('no "add code in assets/ads.js" text reaches the page',
        r.demoText === 0, 'demoText=' + r.demoText);

  /* ---- 7. ...but the placeholder must still be available for local development,
             otherwise the flag that hides it is just dead code. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_LATE, showPlaceholders: true
  });
  check('showPlaceholders:true still renders the dev placeholder',
        r.demoText === 2 && r.emptySlots === 0,
        'demoText=' + r.demoText + ' empty=' + r.emptySlots);

  /* ---- 8. NEGATIVE CONTROL A — the page-wipe bug.
             Isolation off + late write must DESTROY the page. The assertion is
             inverted on purpose: this test is expected to "fail" as a check. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_LATE, unisolated: true
  });
  check('NEGATIVE CONTROL: without isolation the late write DOES wipe the page',
        !alive(r), 'bodyLen=' + r.bodyLen + ' h1=' + r.h1);

  /* ---- 9. NEGATIVE CONTROL B — the silent-revenue-loss bug.
             Isolation off + instant write survives the page but the ad never
             renders. Proves isolation is load-bearing for revenue, not just
             for safety. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_INSTANT, unisolated: true
  });
  check('NEGATIVE CONTROL: without isolation the instant write silently loses the ad',
        alive(r) && r.payloadTop === false && r.iframes === 0,
        'bodyLen=' + r.bodyLen + ' payloadTop=' + r.payloadTop + ' iframes=' + r.iframes);

  /* ---- 10. NEGATIVE CONTROL C — blind the ad-script detection entirely.
              The pasted snippet contains no literal document.write, so with detection
              blinded nothing marks it as unsafe, it runs inline, and the late write
              erases the document. Proves the host list / invoke.js matching is
              load-bearing rather than decorative. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('0bab55ec2855e74946a5c24ac4862018', HOST_LIVE),
    host: HOST_LIVE, invokeBody: INVOKE_LATE, detectionBlind: true
  });
  check('NEGATIVE CONTROL: with detection blinded the production ad wipes the page',
        !alive(r), 'bodyLen=' + r.bodyLen + ' h1=' + r.h1);

  await browser.close();
  console.log('');
  console.log('==== ' + pass + ' passed, ' + fail + ' failed ====');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('HARNESS ERROR: ' + e.message); process.exit(1); });
