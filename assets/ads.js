/* ============================================================================
   LAZYTOOLS — AD CONFIGURATION
   ----------------------------------------------------------------------------
   This is the ONE file you edit to turn ads on.
   Nothing is sent anywhere until you paste real ad code here.

   HOW (Adsterra example — works from any country, payouts from $5, incl. crypto):
     1. Create a publisher account: https://adsterra.com  (Publishers → Sign up)
     2. Websites → Add your website → wait for approval (usually < 48h)
     3. Ad Units → Create 3 SEPARATE units (one per slot — see the warning below):
          - 728x90 / 320x50 banner        → copy the code → paste in "top"
          - 300x250 banner                → paste in "middle"
          - 300x250 or native banner      → paste in "bottom"
     4. Paste each code between the quotes below, save, redeploy. Done.

   ONE AD UNIT KEY = ONE SLOT.  Do NOT paste the same snippet into two slots.
   Adsterra's snippet works by assigning a GLOBAL variable, `atOptions`, and then loading
   a script that reads it back. Put the same snippet on a page twice and the second
   assignment overwrites the first, while invoke.js is initialised twice — the documented
   outcome is that only ONE of the two ever renders. So a duplicate costs you a slot and
   earns nothing. If you want three ads, create three ad units in the Adsterra dashboard.

   Google AdSense works too (create the units, paste the loader in headCode and
   each unit in its slot). Add your ads.txt line in /ads.txt as well.

   WHY AD CODE IS SOMETIMES RENDERED INSIDE AN IFRAME  (read this before "fixing" it)
   ------------------------------------------------------------------------------------
   Adsterra's banner codes load a cross-origin invoke.js that calls document.write.
   What that does depends entirely on WHEN the write lands. Both cases below were
   measured in headless Chrome against this exact file (see _tests/check_ads.js):

     readyState "interactive"  (deferred-script phase, i.e. a fast/instant script)
         document.write is silently SWALLOWED. The page survives, no error is
         logged anywhere — but nothing is written, so the ad never appears.
         You lose the revenue and have no symptom to debug.

     readyState "complete"  (page already loaded, i.e. any normal network fetch)
         document.write implicitly calls document.open(), which ERASES THE ENTIRE
         DOCUMENT. The visitor gets a blank tab. This is the severe one, and it is
         the case that actually happens on a cold cross-origin fetch.

   Neither is acceptable, and note the second one only appears once REAL ad code is
   pasted in — i.e. on launch day, for every visitor, with no test coverage unless
   this suite is run first.

   So: if a slot's code looks like it will write, it is rendered inside a same-origin
   iframe via srcdoc. srcdoc is parsed normally, so the write lands inside the iframe
   while a parser is active: the ad renders correctly AND the page is untouched.
   Isolation is therefore load-bearing for revenue, not just for safety.

   Detection cannot just look for the string "document.write", because the snippet
   you paste usually contains no such thing — the write is inside invoke.js, on
   another host. Hence needsIsolation() also matches the known ad-script hostnames.
   If you switch networks and see blank ad slots, add that network's host there.

   Slots whose code does not write (AdSense, most native units) are injected inline
   as before, because some networks require their tag to live in the top-level
   document and would mis-measure it inside an iframe.

   Set forceIsolate to true to push every slot through the iframe path.
============================================================================ */
window.LAZYTOOLS_ADS = {
  /* Optional global loader script — e.g. AdSense:
     "<script async src=\"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXX\" crossorigin=\"anonymous\"></script>" */
  headCode: "",

  slots: {
    top:    "",   /* banner above the tool  */
    middle:       /* unit below the tool    */
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
    bottom: ""    /* footer banner          */
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
  /* Every Adsterra snippet loads <host>/<key>/invoke.js, and Adsterra rotates that host
     over time — highperformanceformat.com, highrevenueformat.com and the
     profitabledisplay* / effectivegatecpm names are all the same product on different
     domains. Matching a fixed host list alone is therefore fragile, and the cost of a miss
     is asymmetric: over-isolating merely renders a banner in an iframe, while
     under-isolating hands the visitor a blank page. So this matches both the hosts seen in
     the wild AND the /invoke.js path itself, which is the one shape all of them share. */
  var AD_SCRIPT = new RegExp(
    'highperformanceformat\\.com' +
    '|highrevenueformat\\.com' +
    '|profitabledisplayformat\\.com' +
    '|profitabledisplaynetwork\\.com' +
    '|effectivegatecpm\\.com' +
    '|/invoke\\.js', 'i');

  function needsIsolation(code) {
    return /document\s*\.\s*write/i.test(code) || AD_SCRIPT.test(code);
  }

  function sizeOf(slot) {
    var w = parseInt(slot.getAttribute('data-w'), 10) || 300;
    var h = parseInt(slot.getAttribute('data-h'), 10) || 250;
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
      var code = cfg.slots && cfg.slots[name];
      if (code && code.trim()) {
        if (cfg.forceIsolate || needsIsolation(code)) {
          renderIsolated(slot, code, sizeOf(slot));
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
