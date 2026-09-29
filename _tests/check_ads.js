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

/* The hosts Adsterra serves from, as seen in the wild. Three are exercised: the historical
   banner host, the one the site actually ships banners from, and the native-banner host. */
const HOST_LEGACY = 'www.highperformanceformat.com';
const HOST_LIVE = 'www.highrevenueformat.com';
const HOST_NATIVE = 'pl31559854.profitableratecpmnetwork.com';

/* Any Adsterra-family host must be aborted outright. Belt and braces: the slot config is
   neutralised below, but if a future edit reintroduces real code into ads.js, this keeps
   the suite hermetic instead of silently letting it hit the network. */
const AD_HOSTS_RE = /(highperformanceformat|highrevenueformat|profitableratecpmnetwork|profitabledisplayformat|profitabledisplaynetwork|effectivegatecpm)\.com/i;

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
function adsterraAd(key, host, w, h) {
  host = host || HOST_LEGACY;
  w = w || 728;
  h = h || 90;
  return '<script type="text/javascript">\n' +
    "  atOptions = { 'key': '" + key + "', 'format': 'iframe', 'height': " + h +
    ", 'width': " + w + ", 'params': {} };\n" +
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
  /* The `top` slot ships a 728x90 / 320x50 pair and picks one by viewport, so a scenario
     has to be able to say which side of the breakpoint it is testing. */
  const ctx = await browser.newContext(o.viewport ? { viewport: o.viewport } : {});
  const page = await ctx.newPage();
  const errs = [];
  const adReqs = [];
  page.on('pageerror', e => errs.push(String(e.message)));
  page.on('request', r => { if (AD_HOSTS_RE.test(r.url())) adReqs.push(r.url()); });

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
              iframeW: -1, iframeH: -1,
              payloadTop: null, payloadInFrame: null, errs, adReqs };
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
        iframeW: frame ? Math.round(frame.getBoundingClientRect().width) : -1,
        iframeH: frame ? Math.round(frame.getBoundingClientRect().height) : -1,
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

  /* ---- 8. THE NATIVE BANNER HOST. The native unit carries no atOptions and no declared
             size — it is a script plus a container div — so nothing about it looks like a
             banner. It must still be isolated, because this family of tags writes. ---- */
  const NATIVE_AD =
    '<script async="async" data-cfasync="false" src="https://' + HOST_NATIVE +
    '/0c1cdb3f8eac447dfc4b82a0243e3fda/invoke.js"></script>\n' +
    '<div id="container-0c1cdb3f8eac447dfc4b82a0243e3fda"></div>';
  r = await scenario(browser, { adCode: NATIVE_AD, host: HOST_NATIVE, invokeBody: INVOKE_LATE });
  check('native banner tag is isolated and renders',
        r.iframes === 1 && r.payloadInFrame === true && alive(r),
        'iframes=' + r.iframes + ' payloadInFrame=' + r.payloadInFrame +
        ' bodyLen=' + r.bodyLen);

  /* ---- 9. THE 728x90 / 320x50 PAIR. `top` carries both units and picks by viewport.
             Both halves matter: pick the wrong one and the frame is sized for the other
             unit, which clips the ad. Assert the SIZE and that the matching key was the one
             actually requested — a size-only check would pass even if the wrong creative
             loaded, and a key-only check would pass on a wrongly-sized frame. ---- */
  const PAIR = {
    wide:   { w: 728, h: 90, code: adsterraAd('widekey', HOST_LIVE, 728, 90) },
    narrow: { w: 320, h: 50, code: adsterraAd('narrowkey', HOST_LIVE, 320, 50) }
  };

  r = await scenario(browser, {
    adCode: PAIR, host: HOST_LIVE, invokeBody: INVOKE_LATE,
    viewport: { width: 1280, height: 900 }
  });
  check('wide viewport picks the 728x90 unit and sizes the frame to match',
        r.iframeW === 728 && r.iframeH === 90 && r.adReqs.some(u => u.includes('widekey')),
        'w=' + r.iframeW + ' h=' + r.iframeH + ' reqs=' + r.adReqs.join(','));

  r = await scenario(browser, {
    adCode: PAIR, host: HOST_LIVE, invokeBody: INVOKE_LATE,
    viewport: { width: 400, height: 800 }
  });
  check('narrow viewport picks the 320x50 unit, sizes the frame, and does NOT load the wide one',
        r.iframeW === 320 && r.iframeH === 50 &&
        r.adReqs.some(u => u.includes('narrowkey')) &&
        !r.adReqs.some(u => u.includes('widekey')),
        'w=' + r.iframeW + ' h=' + r.iframeH + ' reqs=' + r.adReqs.join(','));

  /* ---- 10. NEGATIVE CONTROL A — the page-wipe bug.
             Isolation off + late write must DESTROY the page. The assertion is
             inverted on purpose: this test is expected to "fail" as a check. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_LATE, unisolated: true
  });
  check('NEGATIVE CONTROL: without isolation the late write DOES wipe the page',
        !alive(r), 'bodyLen=' + r.bodyLen + ' h1=' + r.h1);

  /* ---- 11. NEGATIVE CONTROL B — the silent-revenue-loss bug.
             Isolation off + instant write survives the page but the ad never
             renders. Proves isolation is load-bearing for revenue, not just
             for safety. ---- */
  r = await scenario(browser, {
    adCode: adsterraAd('testkey'), invokeBody: INVOKE_INSTANT, unisolated: true
  });
  check('NEGATIVE CONTROL: without isolation the instant write silently loses the ad',
        alive(r) && r.payloadTop === false && r.iframes === 0,
        'bodyLen=' + r.bodyLen + ' payloadTop=' + r.payloadTop + ' iframes=' + r.iframes);

  /* ---- 12. NEGATIVE CONTROL C — blind the ad-script detection entirely.
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
