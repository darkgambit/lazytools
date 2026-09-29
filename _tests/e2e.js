/* LazyTools E2E suite — real headless Chrome via playwright-core.
 *
 * Run against the Cloudflare Pages emulator so URLs behave exactly as in production
 * (clean, extensionless URLs; /about.html 308-redirects to /about):
 *
 *   npx --yes wrangler@4 pages dev . --port 8788 --ip 127.0.0.1
 *   NODE_PATH=<managed node_modules> node _tests/e2e.js
 *
 * Override the target with LT_BASE=... (e.g. a live URL after deploy).
 * Checks every tool page actually computes, plus links, ad slots, JSON-LD,
 * search/filter/theme on the home page, and that NO page logs a JS error.
 * Exits non-zero on any failure. Run it at least 5x before declaring success.
 */
const { chromium } = require('playwright-core');

const BASE = process.env.LT_BASE || 'http://127.0.0.1:8788';
const CHROME = process.env.LT_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';

// Pages are requested at their CANONICAL url: extensionless, no trailing slash.
// (404.html is the one page that must be fetched by its literal filename.)
const nav = (rel) => {
  if (rel === 'index.html') return BASE + '/';
  if (rel === '404.html') return BASE + '/404.html';   // fetched by literal filename
  return BASE + '/' + rel.replace(/\.html$/, '');
};

const fill = {
  'tools/age-calculator.html': { dob: '1990-05-15' },
  'tools/percentage-calculator.html': { p1a: '15', p1b: '200', p2a: '30', p2b: '150', p3a: '80', p3b: '100' },
  'tools/compound-interest-calculator.html': {},
  'tools/sleep-cycle-calculator.html': { 'wake-time': '07:00' },
  'tools/date-calculator.html': { d1: '2026-01-01', d2: '2026-12-31' },
  'tools/bmi-calculator.html': {},
  'tools/word-counter.html': { 'wc-text': 'Hello world. This is a test sentence for counting. Second paragraph here.' },
  'tools/password-generator.html': {},
  'tools/tip-calculator.html': { 'tip-bill': '84.50' },
  'tools/unit-converter.html': { 'uc-val': '1' },
  'tools/loan-calculator.html': {},
  'tools/water-intake-calculator.html': {},
  'tools/invoice-generator.html': {},
  'tools/case-converter.html': { 'cc-in': 'hello world example text' },
  'tools/hours-calculator.html': {},
  'tools/discount-calculator.html': { 'd1-price': '120' },
  'tools/sales-tax-calculator.html': { 'st1-net': '250' },
  'tools/gpa-calculator.html': {},
  'tools/calorie-calculator.html': {},
  'tools/time-zone-converter.html': { 'tz-date': '2026-01-15' },
};

const resultSel = {
  'tools/age-calculator.html': '#age-main',
  'tools/percentage-calculator.html': '#p1-out',
  'tools/compound-interest-calculator.html': '#ci-final',
  'tools/sleep-cycle-calculator.html': '#wake-list',
  'tools/date-calculator.html': '#dif-days',
  'tools/bmi-calculator.html': '#bmi-val',
  'tools/word-counter.html': '#wc-words',
  'tools/password-generator.html': '#pw-out',
  'tools/tip-calculator.html': '#tip-total',
  'tools/unit-converter.html': '#uc-out',
  'tools/loan-calculator.html': '#ln-pay',
  'tools/water-intake-calculator.html': '#w-liters',
  'tools/invoice-generator.html': '#inv-total',
  'tools/case-converter.html': '#cc-out',
  'tools/hours-calculator.html': '#hc-hm',
  'tools/discount-calculator.html': '#d1-final',
  'tools/sales-tax-calculator.html': '#st1-gross',
  'tools/gpa-calculator.html': '#gpa-val',
  'tools/calorie-calculator.html': '#cal-tdee',
  'tools/time-zone-converter.html': '#tz-out',
};

let pass = 0, fail = 0;

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--disable-gpu'] });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });

  /* Error collection is scoped to FIRST-PARTY origins on purpose.

     This site embeds third-party scripts by design: Cloudflare Web Analytics on every page,
     and ad-network code once the slots are filled. Those requests fail for reasons that have
     nothing to do with this site — ad blockers, corporate DNS filters, and (on a non-standard
     localhost port) Cloudflare's own RUM endpoint echoing `Access-Control-Allow-Origin:
     http://127.0.0.1` WITHOUT the port, which fails the CORS preflight for http://127.0.0.1:8788.

     Counting that noise as a defect made all 21 page checks report FAIL while every functional
     assertion in them still passed (`cards=17`, `ads=3`, `ld=3`, correct results). A suite that
     cries wolf on a third-party CDN gets ignored, which is worse than not having it.

     So a failure only counts against this site when it comes from this site's own origin.
     Known third-party noise is still collected and printed, never hidden — and the beacon's
     presence is asserted positively below, so filtering the noise does not lose the coverage. */
  const THIRD_PARTY = [
    'cloudflareinsights.com',      // Cloudflare Web Analytics
    'highperformanceformat.com',   // Adsterra banner / native tags
    'profitabledisplaynetwork.com',
    'effectivegatecpm.com',
  ];
  const isThirdParty = (s) => THIRD_PARTY.some((h) => s.includes(h));

  async function newPage() {
    const page = await ctx.newPage();
    const errs = [];        // first-party — these fail the suite
    const noise = [];       // known third-party — reported only
    const bucket = (s) => (isThirdParty(s) ? noise : errs);
    page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
    page.on('console', (m) => {
      if (m.type() !== 'error') return;
      const text = m.text();
      // A failed subresource logs a generic "Failed to load resource" message, so the
      // message text alone is not enough — the source URL identifies the culprit.
      const src = (m.location && m.location().url) || '';
      bucket(text + ' ' + src).push('console: ' + text + (src ? ' [' + src + ']' : ''));
    });
    page.on('requestfailed', (r) => bucket(r.url()).push('reqfail: ' + r.url()));
    return { page, errs, noise };
  }
  const report = (ok, label, detail) => {
    ok ? pass++ : fail++;
    console.log((ok ? 'PASS ' : 'FAIL ') + label.padEnd(26) + '| ' + detail);
  };

  // ---------- home ----------
  try {
    const { page, errs, noise } = await newPage();
    const homeResp = await page.goto(nav('index.html'), { waitUntil: 'load' });
    const homeDirect = !!homeResp && homeResp.status() === 200 && page.url() === nav('index.html');
    const title = await page.title();
    const cards = await page.locator('.tool-card[data-slug]').count();
    const slots = await page.locator('.ad-slot[data-slot]').count();
    const beacon = await page.locator("script[src*='cloudflareinsights.com/beacon.min.js']").count();
    await page.fill('#tool-search', 'bmi');
    await page.waitForTimeout(150);
    const visible = await page.locator('.tool-card[data-slug]:visible').count();
    const first = await page.locator('.tool-card[data-slug]:visible').first().getAttribute('data-slug');
    await page.fill('#tool-search', 'zzzzz');
    await page.waitForTimeout(150);
    const noResults = await page.locator('#no-results').isVisible();
    await page.fill('#tool-search', '');
    await page.locator('.chip[data-cat="Finance"]').click();
    await page.waitForTimeout(150);
    const fin = await page.locator('.tool-card[data-slug]:visible').count();
    const t0 = await page.evaluate(() => document.documentElement.classList.contains('light'));
    await page.locator('#theme-btn').click();
    const t1 = await page.evaluate(() => document.documentElement.classList.contains('light'));
    report(title.includes('LazyTools') && cards >= 14 && slots >= 1 && visible === 1 &&
           first === 'bmi-calculator' && noResults && fin >= 3 && t0 !== t1 && errs.length === 0 &&
           homeDirect && beacon === 1,
      'home', `cards=${cards} search->${first} noResults=${noResults} finance=${fin} theme=${t0}->${t1} direct=${homeDirect} beacon=${beacon} errs=${errs.length} 3rdparty=${noise.length}`);
    errs.forEach((e) => console.log('        ' + e));
    noise.forEach((e) => console.log('        (third-party, ignored) ' + e));
    await page.close();
  } catch (e) { report(false, 'home', e.message.split('\n')[0]); }

  // ---------- tool pages ----------
  for (const rel of Object.keys(fill)) {
    const label = rel.replace('tools/', '').replace('.html', '');
    try {
      const { page, errs, noise } = await newPage();
      const resp = await page.goto(nav(rel), { waitUntil: 'load' });
      // the canonical URL must be served directly: 200, no redirect
      const direct = !!resp && resp.status() === 200 && page.url() === nav(rel);
      // assert the INITIAL state is alive before touching anything
      const initialErrs = errs.length;
      for (const [id, v] of Object.entries(fill[rel])) {
        const loc = page.locator('#' + id);
        try { await loc.fill(v, { timeout: 2000 }); }
        catch (e) { await page.evaluate(([i, val]) => { const el = document.getElementById(i); if (el) el.value = val; }, [id, v]); }
      }
      // date-calculator's first .btn-primary is a tab button, not the action
      const sel = rel === 'tools/date-calculator.html' ? 'button[onclick="runDiff()"]' : 'button.btn-primary';
      const action = page.locator(sel);
      if (await action.count() > 0) await action.first().click();
      await page.waitForTimeout(250);
      const val = ((await page.locator(resultSel[rel]).first().textContent()) || '').trim();
      const slots = await page.locator('.ad-slot[data-slot]').count();
      const demo = await page.locator('.ad-slot .ad-demo').count();
      const related = await page.locator('.related .tool-card').count();
      const faqs = await page.locator('.faq details').count();
      const ld = await page.locator('script[type="application/ld+json"]').count();
      const canonical = await page.locator('link[rel="canonical"]').getAttribute('href');
      // Analytics must reach EVERY page, not just the homepage — a page missing the beacon
      // is invisible traffic. Asserted positively so filtering third-party noise loses nothing.
      const beacon = await page.locator("script[src*='cloudflareinsights.com/beacon.min.js']").count();
      // The site footer is the only place /about and /privacy are linked from a tool page,
      // and tool_page() once forgot to render it entirely. Asserted per page, in a browser.
      const footLinks = await page.locator('.site-footer a').count();
      report(!/NaN|undefined|Infinity|^—$|^$/.test(val) && slots === 3 && demo + (slots - demo) === 3 &&
             related >= 1 && faqs >= 3 && ld === 3 && !!canonical && errs.length === 0 && initialErrs === 0 &&
             direct && beacon === 1 && footLinks >= 8,
        label, `result="${val.slice(0, 24)}" ads=${slots} related=${related} faq=${faqs} ld=${ld} foot=${footLinks} direct=${direct} beacon=${beacon} errs=${errs.length}`);
      errs.forEach((e) => console.log('        ' + e));
      noise.forEach((e) => console.log('        (third-party, ignored) ' + e));
      await page.close();
    } catch (e) { report(false, label, e.message.split('\n')[0]); }
  }

  // ---------- date calculator, second tab ----------
  try {
    const { page, errs } = await newPage();
    await page.goto(nav('tools/date-calculator.html'), { waitUntil: 'load' });
    await page.locator('#tab-add-btn').click();
    await page.fill('#ad-start', '2026-01-01');
    await page.fill('#ad-n', '30');
    await page.locator('#dt-add button.btn-primary').click();
    await page.waitForTimeout(250);
    const val = ((await page.locator('#add-out').textContent()) || '').trim();
    report(val.length > 4 && !/NaN|undefined/.test(val) && errs.length === 0, 'date-calc (add tab)', `result="${val}"`);
    await page.close();
  } catch (e) { report(false, 'date-calc (add tab)', e.message.split('\n')[0]); }

  // ---------- hours calculator: weekly time card ----------
  try {
    const { page, errs } = await newPage();
    await page.goto(nav('tools/hours-calculator.html'), { waitUntil: 'load' });
    // Mon–Fri 09:00–17:00 with a 60-minute unpaid break = 7 h/day = 35.00 h
    const rows = page.locator('#hc-week li');
    const n = await rows.count();
    for (let i = 0; i < 5; i++) {
      await rows.nth(i).locator('.hc-in').fill('09:00');
      await rows.nth(i).locator('.hc-out').fill('17:00');
      await rows.nth(i).locator('.hc-brk').fill('60');
    }
    await page.waitForTimeout(250);
    const total = ((await page.locator('#hc-wtotal').textContent()) || '').trim();
    const hm = ((await page.locator('#hc-whm').textContent()) || '').trim();
    const days = ((await page.locator('#hc-wdays').textContent()) || '').trim();
    report(n === 7 && total === '35.00' && hm === '35 h 0 m' && days === '5' && errs.length === 0,
      'hours (weekly card)', `rows=${n} total=${total} hm="${hm}" days=${days} errs=${errs.length}`);
    await page.close();
  } catch (e) { report(false, 'hours (weekly card)', e.message.split('\n')[0]); }

  // ---------- discount: reverse modes ----------
  try {
    const { page, errs } = await newPage();
    await page.goto(nav('tools/discount-calculator.html'), { waitUntil: 'load' });
    await page.fill('#d2-orig', '120'); await page.fill('#d2-sale', '84');
    await page.locator('button[onclick="runD2()"]').click();
    await page.fill('#d3-sale', '84'); await page.fill('#d3-pct', '30');
    await page.locator('button[onclick="runD3()"]').click();
    await page.waitForTimeout(200);
    const d2 = ((await page.locator('#d2-pct').textContent()) || '').trim();
    const d3 = ((await page.locator('#d3-orig').textContent()) || '').trim();
    report(d2 === '30%' && d3 === '120' && errs.length === 0,
      'discount (reverse)', `120->84 = ${d2} off ; 84 after 30% = ${d3} errs=${errs.length}`);
    await page.close();
  } catch (e) { report(false, 'discount (reverse)', e.message.split('\n')[0]); }

  // ---------- sales tax: reverse mode ----------
  try {
    const { page, errs } = await newPage();
    await page.goto(nav('tools/sales-tax-calculator.html'), { waitUntil: 'load' });
    await page.fill('#st2-gross', '270.63'); await page.fill('#st2-rate', '8.25');
    await page.locator('button[onclick="runST2()"]').click();
    await page.waitForTimeout(200);
    const net = ((await page.locator('#st2-net').textContent()) || '').trim();
    const tax = ((await page.locator('#st2-tax').textContent()) || '').trim();
    report(net === '250' && tax === '20.63' && errs.length === 0,
      'sales tax (reverse)', `270.63 incl 8.25% -> net=${net} tax=${tax} errs=${errs.length}`);
    await page.close();
  } catch (e) { report(false, 'sales tax (reverse)', e.message.split('\n')[0]); }

  // ---------- GPA: credit-weighted maths and the cumulative combine ----------
  try {
    const { page, errs } = await newPage();
    await page.goto(nav('tools/gpa-calculator.html'), { waitUntil: 'load' });
    // A(3) + B(4) + A-(3) + B+(3) -> (12 + 12 + 11.1 + 9.9) / 13 = 3.4615... -> 3.46
    const rows = page.locator('#gpa-rows li');
    const grades = ['4', '3', '3.7', '3.3'];
    const credits = ['3', '4', '3', '3'];
    for (let i = 0; i < 4; i++) {
      await rows.nth(i).locator('.gpa-grade').selectOption(grades[i]);
      await rows.nth(i).locator('.gpa-cr').fill(credits[i]);
    }
    await page.locator('button[onclick="runGPA()"]').click();
    await page.waitForTimeout(200);
    const gpa = ((await page.locator('#gpa-val').textContent()) || '').trim();
    const cr = ((await page.locator('#gpa-credits').textContent()) || '').trim();
    // 3.2 over 60 credits + 45.0 quality points over 13 -> 237/73 = 3.2466 -> 3.25
    await page.locator('button[onclick="runCGPA()"]').click();
    await page.waitForTimeout(200);
    const cum = ((await page.locator('#cg-new').textContent()) || '').trim();
    const change = ((await page.locator('#cg-change').textContent()) || '').trim();
    report(gpa === '3.46' && cr === '13' && cum === '3.25' && change === '+0.05' && errs.length === 0,
      'gpa (weighted)', `gpa=${gpa} credits=${cr} cumulative=${cum} change=${change} errs=${errs.length}`);
    await page.close();
  } catch (e) { report(false, 'gpa (weighted)', e.message.split('\n')[0]); }

  // ---------- calorie: BMR / TDEE checked against the formula by hand ----------
  try {
    const { page, errs } = await newPage();
    await page.goto(nav('tools/calorie-calculator.html'), { waitUntil: 'load' });
    // male, 30 y, 180 cm, 80 kg, moderately active (1.55)
    // Mifflin-St Jeor: 10*80 + 6.25*180 - 5*30 + 5 = 1780 ; TDEE = 1780 * 1.55 = 2759
    await page.selectOption('#cal-sex', 'male');
    await page.fill('#cal-h', '180');
    await page.fill('#cal-w', '80');
    await page.fill('#cal-age', '30');
    await page.selectOption('#cal-act', '1.55');
    await page.locator('button[onclick="runCal()"]').click();
    await page.waitForTimeout(200);
    // the figures carry a thousands separator, so compare digits only
    const digits = async (sel) => (((await page.locator(sel).textContent()) || '').replace(/[^0-9]/g, ''));
    const bmr = await digits('#cal-bmr');
    const tdee = await digits('#cal-tdee');
    const cut = await digits('#cal-cut');
    const bulk = await digits('#cal-bulk');
    report(bmr === '1780' && tdee === '2759' && cut === '2259' && bulk === '3009' && errs.length === 0,
      'calorie (bmr/tdee)', `bmr=${bmr} tdee=${tdee} cut=${cut} bulk=${bulk} errs=${errs.length}`);
    await page.close();
  } catch (e) { report(false, 'calorie (bmr/tdee)', e.message.split('\n')[0]); }

  // ---------- time zone: DST-aware, and across a day boundary ----------
  try {
    const { page, errs } = await newPage();
    await page.goto(nav('tools/time-zone-converter.html'), { waitUntil: 'load' });
    // January: New York is UTC-5, London UTC+0 -> 12:00 NY = 17:00 London, same day, 5 h apart
    await page.fill('#tz-date', '2026-01-15');
    await page.fill('#tz-time', '12:00');
    await page.selectOption('#tz-from', 'America/New_York');
    await page.selectOption('#tz-to', 'Europe/London');
    await page.locator('button[onclick="runTZ()"]').click();
    await page.waitForTimeout(250);
    const t1 = ((await page.locator('#tz-out').textContent()) || '').trim();
    const d1 = ((await page.locator('#tz-day').textContent()) || '').trim();
    const f1 = ((await page.locator('#tz-diff').textContent()) || '').trim();
    // 23:00 NY -> Tokyo (UTC+9) is +14 h, so 13:00 the NEXT day
    await page.fill('#tz-time', '23:00');
    await page.selectOption('#tz-to', 'Asia/Tokyo');
    await page.locator('button[onclick="runTZ()"]').click();
    await page.waitForTimeout(250);
    const t2 = ((await page.locator('#tz-out').textContent()) || '').trim();
    const d2 = ((await page.locator('#tz-day').textContent()) || '').trim();
    const f2 = ((await page.locator('#tz-diff').textContent()) || '').trim();
    report(t1 === '17:00' && d1 === 'Same day' && f1 === '5 h' &&
           t2 === '13:00' && d2 === '+1 day' && f2 === '14 h' && errs.length === 0,
      'time zone (dst)', `NY->London ${t1} ${d1} ${f1} | NY->Tokyo ${t2} ${d2} ${f2} errs=${errs.length}`);
    await page.close();
  } catch (e) { report(false, 'time zone (dst)', e.message.split('\n')[0]); }

  // ---------- affiliate links: the revenue path, end to end ----------
  // The static guard already proves the tag and disclosure are in the HTML. This proves the
  // links actually RENDER as working links a visitor can click, with the tag intact after any
  // JS has run — and that the disclosure is visible rather than merely present in the source.
  // The tag is read from the links rather than hardcoded, so this cannot drift from config.
  try {
    const { page, errs } = await newPage();
    await page.goto(nav('tools/bmi-calculator.html'), { waitUntil: 'load' });
    const links = await page.$$eval('.gear-list a.gear-link', as => as.map(a => ({
      href: a.getAttribute('href'),
      rel: a.getAttribute('rel') || '',
      target: a.getAttribute('target') || ''
    })));
    const disclosureVisible = await page.locator('.gear-disclosure').first().isVisible();
    const tags = links.map(l => (l.href.match(/[?&]tag=([^&]+)/) || [])[1] || '');
    const ok = links.length === 2 && tags.every(t => t && t === tags[0]) &&
               links.every(l => l.rel.includes('sponsored') && l.rel.includes('noopener') &&
                                l.target === '_blank' && /^https:\/\/www\.amazon\./.test(l.href)) &&
               disclosureVisible && errs.length === 0;
    report(ok, 'affiliate links', `n=${links.length} tag=${tags[0] || '(none)'} ` +
      `disclosure=${disclosureVisible} rel=${links[0] ? links[0].rel : '-'} errs=${errs.length}`);
    await page.close();
  } catch (e) { report(false, 'affiliate links', e.message.split('\n')[0]); }

  // ---------- static pages ----------
  for (const p of ['about.html', 'privacy.html', '404.html']) {
    try {
      const { page, errs } = await newPage();
      await page.goto(nav(p), { waitUntil: 'load' });
      const h1 = ((await page.locator('h1').first().textContent()) || '').trim();
      report(h1.length > 0 && errs.length === 0, p, `h1="${h1.slice(0, 28)}" errs=${errs.length}`);
      await page.close();
    } catch (e) { report(false, p, e.message.split('\n')[0]); }
  }

  await browser.close();
  console.log(`\n==== ${pass} passed, ${fail} failed ====`);
  process.exit(fail ? 1 : 0);
})();
