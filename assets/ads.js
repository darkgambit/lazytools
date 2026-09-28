/* ============================================================================
   LAZYTOOLS — AD CONFIGURATION
   ----------------------------------------------------------------------------
   This is the ONE file you edit to turn ads on.
   Nothing is sent anywhere until you paste real ad code here.

   HOW (Adsterra example — works from any country, payouts from $5, incl. crypto):
     1. Create a publisher account: https://adsterra.com  (Publishers → Sign up)
     2. Websites → Add your website → wait for approval (usually < 48h)
     3. Ad Units → Create 3 units, e.g.:
          - 728x90 / 320x50 banner        → copy the code → paste in "top"
          - 300x250 banner                → paste in "middle"
          - 300x250 or native banner      → paste in "bottom"
     4. Paste each code between the quotes below, save, redeploy. Done.

   Google AdSense works too (create the units, paste the loader in headCode and
   each unit in its slot). Add your ads.txt line in /ads.txt as well.
============================================================================ */
window.LAZYTOOLS_ADS = {
  /* Optional global loader script — e.g. AdSense:
     "<script async src=\"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXX\" crossorigin=\"anonymous\"></script>" */
  headCode: "",

  slots: {
    top:    "",   /* banner above the tool  */
    middle: "",   /* unit below the tool    */
    bottom: ""    /* footer banner          */
  }
};

/* ---- injector: replaces placeholder boxes with your code, safely re-running scripts ---- */
(function () {
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
        slot.innerHTML = code;
        slot.classList.add('live');
        reviveScripts(slot);
      } else {
        slot.innerHTML = '<span class="ad-demo">Ad space — add code in assets/ads.js</span>';
      }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
