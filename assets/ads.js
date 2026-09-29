/* ============================================================================
   LAZYTOOLS — AD CONFIGURATION
   ----------------------------------------------------------------------------
   This is the ONE file you edit to turn ads on.
   Nothing is sent anywhere until you paste real ad code here.

   WHAT IS ALLOWED HERE — read before adding a code
   ----------------------------------------------------------------------------
   **Banner and Native Banner only.** Deliberately excluded:
     - Popunder / Social Bar  — site-wide tags that hijack clicks and open tabs.
       They wreck the experience on a tool page (a visitor came to do arithmetic),
       they are a common cause of "this site opened something" complaints, and they
       put the whole domain at risk with search engines.
     - Direct Link / Smartlink — a bare URL for traffic arbitrage, not a placement.
       There is nowhere on the page for it to live.
   If you want those formats, that is a product decision, not a paste: they need
   their own review, and the site currently has no place to put them.

   HOW (Adsterra — works from any country, payouts from $5, incl. crypto)
     1. Publisher account: https://adsterra.com  (Publishers → Sign up)
     2. Websites → Add your website → wait for approval (usually < 48h)
     3. Ad Units → create ONE UNIT PER SLOT (see the warning below):
          - 728x90  banner  → "top"    (wide screens)
          - 320x50  banner  → "top"    (narrow screens — the mobile half of the pair)
          - 300x250 banner  → "middle"
          - Native Banner   → "bottom"
     4. Paste each code below, save, redeploy with: python _generator/deploy.py

   ONE AD UNIT KEY = ONE SLOT.  Do NOT paste the same snippet into two slots.
   Adsterra's banner snippet works by assigning a GLOBAL variable, `atOptions`, and then
   loading a script that reads it back. Put the same snippet on a page twice and the second
   assignment overwrites the first while invoke.js is initialised twice — the documented
   outcome is that only ONE of the two ever renders. A duplicate therefore costs you a slot
   and earns nothing. Three ads means three ad units in the Adsterra dashboard.

   WHY AD CODE IS SOMETIMES RENDERED INSIDE AN IFRAME  (read this before "fixing" it)
   ------------------------------------------------------------------------------------
   Adsterra's tags load a cross-origin invoke.js that calls document.write. What that does
   depends entirely on WHEN the write lands. Both cases were measured in headless Chrome
   against this exact file (see _tests/check_ads.js):

     readyState "interactive"  (deferred-script phase, i.e. a fast/instant script)
         document.write is silently SWALLOWED. The page survives, no error is logged
         anywhere — but nothing is written, so the ad never appears. Revenue lost with
         no symptom to debug.

     readyState "complete"  (page already loaded, i.e. any normal network fetch)
         document.write implicitly calls document.open(), which ERASES THE ENTIRE
         DOCUMENT. The visitor gets a blank tab. This is the severe one, and it is the
         case that actually happens on a cold cross-origin fetch.

   So: if a slot's code looks like it will write, it is rendered inside a same-origin iframe
   via srcdoc. srcdoc is parsed normally, so the write lands inside the iframe while a parser
   is active: the ad renders correctly AND the page is untouched. Isolation is load-bearing
   for revenue, not just for safety.

   Detection cannot just look for the string "document.write", because the snippet you paste
   usually contains no such thing — the write is inside invoke.js, on another host. Hence
   needsIsolation() also matches the known ad-script hostnames and the /invoke.js path.

   Slots whose code does not write (AdSense, most native units) are injected inline, because
   some networks require their tag in the top-level document. Set forceIsolate to true to push
   every slot through the iframe path.
============================================================================ */
window.LAZYTOOLS_ADS = {
  /* Optional global loader script — e.g. AdSense:
     "<script async src=\"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXX\" crossorigin=\"anonymous\"></script>" */
  headCode: "",

  slots: {
    /* `top` carries a PAIR: Adsterra sells the 728x90 leaderboard and the 320x50 mobile
       banner as two units of the same product, so the slot picks one by viewport width.
       A slot value is either a plain code string, or { wide, narrow } where each entry is
       { w, h, code }.

       The width/height travel WITH the code on purpose: the isolation iframe is sized from
       them, and the slot markup's own data-w/data-h can only describe one of the two. A
       728x90 unit rendered into a 320x50 frame — or the reverse — clips. Selection happens
       once, at load; resizing the window afterwards does not re-pick. */
    top: {
      wide: {
        w: 728, h: 90,
        code: "<script>\n" +
          "atOptions = {\n" +
          "'key' : 'c4f9202cd24dc97dcd2503e53680b762',\n" +
          "'format' : 'iframe',\n" +
          "'height' : 90,\n" +
          "'width' : 728,\n" +
          "'params' : {}\n" +
          "};\n" +
          "</script>\n" +
          "<script src=\"https://www.highrevenueformat.com/c4f9202cd24dc97dcd2503e53680b762/invoke.js\"></script>"
      },
      narrow: {
        w: 320, h: 50,
        code: "<script>\n" +
          "atOptions = {\n" +
          "'key' : '5631c5d7f76b01de548b1c9a339d9b92',\n" +
          "'format' : 'iframe',\n" +
          "'height' : 50,\n" +
          "'width' : 320,\n" +
          "'params' : {}\n" +
          "};\n" +
          "</script>\n" +
          "<script src=\"https://www.highrevenueformat.com/5631c5d7f76b01de548b1c9a339d9b92/invoke.js\"></script>"
      }
    },

    middle:   /* 300x250 banner, in-content below the tool */
      "<script>\n" +
      "atOptions = {\n" +
      "'key' : '0bab55ec2855e74946a5c24ac4862018',\n" +
      "'format' : 'iframe',\n" +
      "'height' : 250,\n" +
      "'width' : 300,\n" +
      "'params' : {}\n" +
      "};\n" +
      "</script>\n" +
      "<script src=\"https://www.highrevenueformat.com/0bab55ec2855e74946a5c24ac4862018/invoke.js\"></script>",

    /* Native Banner. Unlike the banner units this has no atOptions and no fixed size — the
       Adsterra script finds #container-<hash> and renders an ad that fits it, so it is safe
       in the existing 300x250 slot without pinning a height. Keep the script/div order and
       the container id exactly as Adsterra issues them; the id is what the script looks for. */
    bottom:
      "<script async=\"async\" data-cfasync=\"false\" src=\"https://pl31559854.profitableratecpmnetwork.com/0c1cdb3f8eac447dfc4b82a0243e3fda/invoke.js\"></script>\n" +
      "<div id=\"container-0c1cdb3f8eac447dfc4b82a0243e3fda\"></div>"
  },

  /* true  = always render slots in an isolation iframe
     false = only when the code actually needs it (document.write present)  */
  forceIsolate: false,

  /* true  = an unfilled slot shows a dashed "add code in assets/ads.js" box.
     Leave false in production: that box is a note to YOU, not to a visitor, and with
     two of three slots still empty it would otherwise appear on every page of the site.
     Turn it on locally when you want to see where the ads will land.  */
  showPlaceholders: false
};

/* ---- injector: replaces placeholder boxes with your code, safely re-running scripts ---- */
(function () {
  /* Every Adsterra tag loads a script from a rotating host on the same family of domains:
     the highperformanceformat / highrevenueformat names for banners, and the
     profitableratecpmnetwork / profitabledisplay* names for native and popunder units.
     Matching a fixed host list alone is fragile, and the cost of a miss is asymmetric:
     over-isolating merely renders an ad in an iframe, while under-isolating hands the
     visitor a blank page. So this matches the hosts seen in the wild AND the /invoke.js
     path, which the banner and native tags share. */
  var AD_SCRIPT = new RegExp(
    'highperformanceformat\\.com' +
    '|highrevenueformat\\.com' +
    '|profitableratecpmnetwork\\.com' +
    '|profitabledisplayformat\\.com' +
    '|profitabledisplaynetwork\\.com' +
    '|effectivegatecpm\\.com' +
    '|/invoke\\.js', 'i');

  function needsIsolation(code) {
    return /document\s*\.\s*write/i.test(code) || AD_SCRIPT.test(code);
  }

  /* Which of a slot's variants applies here. A plain string slot has only one. */
  function pick(slotCfg) {
    if (!slotCfg) return null;
    if (typeof slotCfg === 'string') return { code: slotCfg };
    var wide = true;
    try {
      wide = window.matchMedia('(min-width: 768px)').matches;
    } catch (e) { /* no matchMedia: prefer the wide unit, it degrades by clipping */ }
    return wide ? slotCfg.wide : slotCfg.narrow;
  }

  /* A variant may carry its own size; fall back to the slot markup's declared size. */
  function sizeOf(slot, variant) {
    var w = (variant && variant.w) || parseInt(slot.getAttribute('data-w'), 10) || 300;
    var h = (variant && variant.h) || parseInt(slot.getAttribute('data-h'), 10) || 250;
    return { w: w, h: h };
  }

  /* Render in a same-origin iframe. srcdoc is parsed normally, so scripts inside run
     during parsing and document.write stays legal. */
  function renderIsolated(slot, code, size) {
    var f = document.createElement('iframe');
    f.setAttribute('title', 'Advertisement');
    f.setAttribute('scrolling', 'no');
    f.setAttribute('loading', 'lazy');
    f.style.display = 'block';
    f.style.border = '0';
    f.style.width = size.w + 'px';
    f.style.height = size.h + 'px';
    f.style.maxWidth = '100%';
    f.style.margin = '0 auto';
    f.srcdoc = '<!DOCTYPE html><html><head><meta charset="utf-8">' +
               '<style>html,body{margin:0;padding:0;overflow:hidden;background:transparent}' +
               'body{display:flex;align-items:center;justify-content:center}</style>' +
               '</head><body>' + code + '</body></html>';
    slot.appendChild(f);
  }

  function reviveScripts(container) {
    var scripts = [].slice.call(container.querySelectorAll('script'));
    scripts.forEach(function (old) {
      var s = document.createElement('script');
      [].slice.call(old.attributes).forEach(function (a) { s.setAttribute(a.name, a.value); });
      s.text = old.text;
      old.parentNode.replaceChild(s, old);
    });
  }

  function loadHead(code) {
    var tmp = document.createElement('div');
    tmp.innerHTML = code;
    while (tmp.firstChild) {
      var node = tmp.firstChild;
      tmp.removeChild(node);
      if (node.tagName === 'SCRIPT') {
        var s = document.createElement('script');
        [].slice.call(node.attributes).forEach(function (a) { s.setAttribute(a.name, a.value); });
        s.text = node.text;
        document.head.appendChild(s);
      } else {
        document.head.appendChild(node);
      }
    }
  }

  function init() {
    var cfg = window.LAZYTOOLS_ADS || {};
    if (cfg.headCode) loadHead(cfg.headCode);
    var slots = document.querySelectorAll('.ad-slot[data-slot]');
    [].slice.call(slots).forEach(function (slot) {
      var name = slot.getAttribute('data-slot');
      var variant = pick(cfg.slots && cfg.slots[name]);
      var code = variant && variant.code;
      if (code && code.trim()) {
        if (cfg.forceIsolate || needsIsolation(code)) {
          renderIsolated(slot, code, sizeOf(slot, variant));
        } else {
          slot.innerHTML = code;
          reviveScripts(slot);
        }
        slot.classList.add('live');
      } else if (cfg.showPlaceholders) {
        /* Local development only — see showPlaceholders above. */
        slot.innerHTML = '<span class="ad-demo">Ad space — add code in assets/ads.js</span>';
      } else {
        /* Unfilled slot: collapse it, so it leaves no gap and no marker on the page. */
        slot.classList.add('empty');
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
