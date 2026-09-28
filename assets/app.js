/* LazyTools — shared behaviour: theme, filtering, small helpers used by tool pages. */
(function () {
  var root = document.documentElement;

  /* ---- theme (dark by default) ---- */
  var saved = null;
  try { saved = localStorage.getItem('lt-theme'); } catch (e) {}
  var prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
  if (saved === 'light' || (!saved && prefersLight)) root.classList.add('light');

  window.toggleTheme = function () {
    var light = root.classList.toggle('light');
    try { localStorage.setItem('lt-theme', light ? 'light' : 'dark'); } catch (e) {}
    var b = document.getElementById('theme-btn');
    if (b) b.textContent = light ? '🌙' : '☀️';
  };

  document.addEventListener('DOMContentLoaded', function () {
    var b = document.getElementById('theme-btn');
    if (b) b.textContent = root.classList.contains('light') ? '🌙' : '☀️';
    var y = document.getElementById('year');
    if (y) y.textContent = new Date().getFullYear();

    /* ---- home page tool filter ---- */
    var search = document.getElementById('tool-search');
    var cards = [].slice.call(document.querySelectorAll('.tool-card[data-slug]'));
    var chips = [].slice.call(document.querySelectorAll('.chip[data-cat]'));
    var activeCat = 'all';

    function apply() {
      var q = (search && search.value ? search.value : '').toLowerCase().trim();
      var anyVisible = false;
      cards.forEach(function (c) {
        var okCat = activeCat === 'all' || c.getAttribute('data-cat') === activeCat;
        var hay = (c.getAttribute('data-name') + ' ' + (c.getAttribute('data-keywords') || '')).toLowerCase();
        var okQ = !q || hay.indexOf(q) > -1;
        var show = okCat && okQ;
        c.style.display = show ? '' : 'none';
        if (show) anyVisible = true;
      });
      var none = document.getElementById('no-results');
      if (none) none.style.display = anyVisible ? 'none' : 'block';
    }
    if (search) search.addEventListener('input', apply);
    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        chips.forEach(function (x) { x.classList.remove('active'); });
        ch.classList.add('active');
        activeCat = ch.getAttribute('data-cat');
        apply();
      });
    });
  });

  /* ---- helpers available to every tool page ---- */
  window.$id = function (i) { return document.getElementById(i); };

  window.fmt = function (n, d) {
    if (typeof n !== 'number' || !isFinite(n)) return '—';
    if (d === undefined) d = 2;
    return n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: d });
  };

  window.showRes = function (id) {
    var el = $id(id);
    if (el) el.classList.add('show');
  };

  window.localISO = function (dt) {
    var p = function (n) { return (n < 10 ? '0' : '') + n; };
    return dt.getFullYear() + '-' + p(dt.getMonth() + 1) + '-' + p(dt.getDate());
  };

  window.copyVal = function (id, btn) {
    var el = $id(id);
    if (!el) return;
    var v = (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') ? el.value : el.textContent;
    var done = function () {
      if (!btn) return;
      var t = btn.textContent;
      btn.textContent = 'Copied ✓';
      setTimeout(function () { btn.textContent = t; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(v).then(done, done);
    } else {
      var ta = document.createElement('textarea');
      ta.value = v; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta); done();
    }
  };

  window.readNum = function (id, label) {
    var v = parseFloat($id(id).value);
    if (isNaN(v)) { alert('Please enter a number for “' + (label || id) + '”.'); return null; }
    return v;
  };
})();
