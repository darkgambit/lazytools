# -*- coding: utf-8 -*-
"""LazyTools — tool definitions, part 1 of 2 (everyday / finance / health / text).
Each tool is a dict. Keys:
  slug, name, icon, cat, popular(bool), short, title, desc, keywords, lead,
  body (HTML), js (inline JS for this page), faqs [(q, a)...], about [paragraphs]
"""

TOOLS_CORE = [

# ---------------------------------------------------------------- AGE
{
"slug": "age-calculator", "name": "Age Calculator", "icon": "🎂", "cat": "Everyday", "popular": True,
"short": "Your exact age in years, months and days — plus a countdown to your next birthday.",
"title": "Age Calculator — Exact Age in Years, Months & Days",
"desc": "Free age calculator: find your exact age in years, months and days, the day of the week you were born, and a countdown to your next birthday. Runs 100% in your browser.",
"keywords": "age calculator, how old am i, calculate age from date of birth, age in days, next birthday countdown",
"lead": "Enter a date of birth to get an exact age breakdown — in years, months and days — plus the day of the week you were born and a live countdown to your next birthday.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="dob">Date of birth</label><input type="date" id="dob"></div>
    <div class="field"><label for="asof">Age at date (optional — defaults to today)</label><input type="date" id="asof"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runAge()">Calculate my age</button></div>
  <div class="results" id="age-res">
    <div class="stat-grid">
      <div class="stat"><b id="age-main">—</b><span>Exact age</span></div>
      <div class="stat"><b id="age-total">—</b><span>Total days alive</span></div>
      <div class="stat"><b id="age-born">—</b><span>Day you were born</span></div>
      <div class="stat"><b id="age-next">—</b><span>Until next birthday</span></div>
    </div>
    <p class="note">Total days includes leap years. Your date of birth never leaves this page — the calculation runs locally in your browser.</p>
  </div>
</div>
""",
"js": """
function runAge(){
  var dobV = $id('dob').value;
  if(!dobV){ alert('Please pick your date of birth.'); return; }
  var dob = new Date(dobV + 'T00:00:00');
  var asofV = $id('asof').value;
  var end = asofV ? new Date(asofV + 'T00:00:00') : new Date();
  if(dob > end){ alert('The date of birth must be before the target date.'); return; }
  var y = end.getFullYear() - dob.getFullYear();
  var m = end.getMonth() - dob.getMonth();
  var d = end.getDate() - dob.getDate();
  if(d < 0){ m--; d += new Date(end.getFullYear(), end.getMonth(), 0).getDate(); }
  if(m < 0){ y--; m += 12; }
  var totalDays = Math.floor((end - dob) / 86400000);
  var days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  var nb = new Date(end.getFullYear(), dob.getMonth(), dob.getDate());
  if(nb <= end) nb.setFullYear(nb.getFullYear() + 1);
  var toBday = Math.ceil((nb - end) / 86400000);
  $id('age-main').textContent = y + ' y ' + m + ' m ' + d + ' d';
  $id('age-total').textContent = fmt(totalDays, 0) + ' days';
  $id('age-born').textContent = days[dob.getDay()];
  $id('age-next').textContent = toBday + ' day' + (toBday === 1 ? '' : 's') + ' · ' + days[nb.getDay()];
  showRes('age-res');
}
(function(){ $id('asof').value = localISO(new Date()); })();
""",
"faqs": [
("How is my exact age calculated?", "Age is counted the same way you would count it by hand: first full years, then full months, then the remaining days. If the remaining days are negative, one month is borrowed; if the months are negative, one year is borrowed. This gives the standard “years, months and days” result."),
("Why is the total number of days different on some websites?", "Some calculators ignore leap years or use a fixed 365.25-day year. This calculator counts real calendar days between the two dates, including February 29 in leap years, which is the accurate figure."),
("Is my date of birth uploaded anywhere?", "No. Everything on LazyTools runs locally in your browser. Nothing you type here is sent to, or stored on, any server.")
],
"about": [
"An age calculator looks simple, but it is one of the most useful everyday utilities on the web. People use it to fill official forms that ask for age in years, months and days, to check school admission cut-offs, to calculate ages for exams, visas, insurance and pensions, or simply to settle a friendly argument about who is older.",
"This tool counts real calendar time, so leap years and months of different lengths are handled correctly. It also tells you the weekday you were born on and exactly how many days remain until your next birthday — the two extras people look up most often."
]
},

# ---------------------------------------------------------------- PERCENTAGE
{
"slug": "percentage-calculator", "name": "Percentage Calculator", "icon": "💯", "cat": "Everyday", "popular": True,
"short": "Percent of a number, what percent X is of Y, and percentage increase or decrease.",
"title": "Percentage Calculator — Percent Of, Percent Change & More",
"desc": "Free percentage calculator: find X% of a number, work out what percent one number is of another, and calculate percentage increase or decrease. Instant and private.",
"keywords": "percentage calculator, percent of a number, percentage change, percent increase, percent decrease, what percent of",
"lead": "Three quick calculators for the three percentage questions everyone asks: a percent of a number, “X is what percent of Y?”, and percentage change between two values.",
"body": """
<div class="panel">
  <p class="panel-title">1 · Find a percentage of a number</p>
  <div class="grid-2">
    <div class="field"><label for="p1a">Percentage (%)</label><input type="number" id="p1a" placeholder="e.g. 15" step="any"></div>
    <div class="field"><label for="p1b">of number</label><input type="number" id="p1b" placeholder="e.g. 200" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runP1()">Calculate</button></div>
  <div class="results" id="p1-res"><p class="big-result" id="p1-out"></p></div>
</div>

<div class="panel">
  <p class="panel-title">2 · X is what percent of Y?</p>
  <div class="grid-2">
    <div class="field"><label for="p2a">Number (X)</label><input type="number" id="p2a" placeholder="e.g. 30" step="any"></div>
    <div class="field"><label for="p2b">of number (Y)</label><input type="number" id="p2b" placeholder="e.g. 150" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runP2()">Calculate</button></div>
  <div class="results" id="p2-res"><p class="big-result" id="p2-out"></p></div>
</div>

<div class="panel">
  <p class="panel-title">3 · Percentage change from X to Y</p>
  <div class="grid-2">
    <div class="field"><label for="p3a">From (original)</label><input type="number" id="p3a" placeholder="e.g. 80" step="any"></div>
    <div class="field"><label for="p3b">To (new)</label><input type="number" id="p3b" placeholder="e.g. 100" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runP3()">Calculate change</button></div>
  <div class="results" id="p3-res"><p class="big-result" id="p3-out"></p></div>
</div>
""",
"js": """
function runP1(){
  var a = readNum('p1a', 'percentage'), b = readNum('p1b', 'number');
  if(a === null || b === null) return;
  var r = a / 100 * b;
  $id('p1-out').textContent = fmt(a) + '% of ' + fmt(b) + ' = ' + fmt(r);
  showRes('p1-res');
}
function runP2(){
  var a = readNum('p2a', 'X'), b = readNum('p2b', 'Y');
  if(a === null || b === null) return;
  if(b === 0){ alert('The second number cannot be zero.'); return; }
  var r = a / b * 100;
  $id('p2-out').textContent = fmt(a) + ' is ' + fmt(r) + '% of ' + fmt(b);
  showRes('p2-res');
}
function runP3(){
  var a = readNum('p3a', 'original'), b = readNum('p3b', 'new');
  if(a === null || b === null) return;
  if(a === 0){ alert('The original number cannot be zero.'); return; }
  var r = (b - a) / Math.abs(a) * 100;
  var dir = r >= 0 ? 'increase' : 'decrease';
  $id('p3-out').textContent = fmt(Math.abs(r)) + '% ' + dir + ' (' + fmt(a) + ' → ' + fmt(b) + ')';
  showRes('p3-res');
}
""",
"faqs": [
("How do I calculate a percentage of a number?", "Multiply the number by the percentage and divide by 100. For example, 15% of 200 = 200 × 15 ÷ 100 = 30. Calculator 1 above does this for you."),
("How is percentage change calculated?", "Subtract the original from the new value, divide by the absolute value of the original, and multiply by 100. Going from 80 to 100 is a 25% increase; from 100 to 80 is a 20% decrease."),
("Where are percentage calculations actually used?", "Everywhere: discounts and sales tax while shopping, tips at restaurants, interest on savings and loans, exam scores, body-fat targets, battery levels, and reading business reports.")
],
"about": [
"Percentages are the most-used bit of school maths in adult life — and the easiest to get wrong under pressure. A discount that says “30% off, plus an extra 20% off the reduced price” is not 50% off, and percentage increases and decreases do not cancel out symmetrically.",
"Having the three standard formulas in one place — percent of a number, the reverse “what percent is X of Y”, and percentage change — covers almost every everyday case, from splitting a restaurant bill to checking whether your salary raise beat inflation. For shopping in particular, the <a href=\"discount-calculator.html\">discount calculator</a> handles the sale-price, “what discount did I actually get” and original-price versions in a single step."
]
},

# ---------------------------------------------------------------- COMPOUND INTEREST
{
"slug": "compound-interest-calculator", "name": "Compound Interest Calculator", "icon": "📈", "cat": "Finance", "popular": True,
"short": "See how savings grow with compound interest and monthly deposits — with a year-by-year table.",
"title": "Compound Interest Calculator — Savings Growth Projection",
"desc": "Free compound interest calculator with monthly contributions. Project savings growth year by year, see total interest earned, and understand the power of compounding.",
"keywords": "compound interest calculator, savings calculator, investment growth calculator, monthly contribution calculator, future value calculator",
"lead": "See how a starting balance, monthly deposits and compound interest grow over time — including a year-by-year breakdown of contributions versus interest.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="ci-p">Starting amount</label><input type="number" id="ci-p" value="1000" min="0" step="any"></div>
    <div class="field"><label for="ci-m">Monthly deposit</label><input type="number" id="ci-m" value="100" min="0" step="any"></div>
    <div class="field"><label for="ci-r">Annual interest rate (%)</label><input type="number" id="ci-r" value="7" min="0" step="any"></div>
    <div class="field"><label for="ci-y">Years</label><input type="number" id="ci-y" value="20" min="0" step="any"></div>
    <div class="field"><label for="ci-n">Compounding</label>
      <select id="ci-n">
        <option value="12">Monthly</option>
        <option value="4">Quarterly</option>
        <option value="1" selected>Annually</option>
        <option value="365">Daily</option>
      </select>
    </div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runCI()">Calculate growth</button></div>
  <div class="results" id="ci-res">
    <div class="stat-grid">
      <div class="stat"><b id="ci-final">—</b><span>Future balance</span></div>
      <div class="stat"><b id="ci-contrib">—</b><span>Total deposits</span></div>
      <div class="stat"><b id="ci-int">—</b><span>Interest earned</span></div>
    </div>
    <div class="bar-stack"><i id="ci-bar-c" style="background:#8fa4ff;width:50%"></i><i id="ci-bar-i" style="background:#f5b53f;width:50%"></i></div>
    <div class="legend"><span><i style="background:#8fa4ff"></i>Deposits</span><span><i style="background:#f5b53f"></i>Interest</span></div>
    <table class="simple"><thead><tr><th>Year</th><th>Balance</th><th>Deposited so far</th><th>Interest so far</th></tr></thead><tbody id="ci-table"></tbody></table>
    <p class="note">Projection only — real returns vary. Interest is compounded at the selected frequency and deposits are added monthly.</p>
  </div>
</div>
""",
"js": """
function runCI(){
  var P = readNum('ci-p', 'starting amount'), M = readNum('ci-m', 'monthly deposit');
  var R = readNum('ci-r', 'interest rate'), Y = readNum('ci-y', 'years');
  if(P === null || M === null || R === null || Y === null) return;
  if(P < 0 || M < 0 || R < 0 || Y < 0){ alert('Please use non-negative numbers.'); return; }
  var n = parseInt($id('ci-n').value, 10);
  var monthlyRate = Math.pow(1 + (R / 100) / n, n / 12) - 1;
  var months = Math.round(Y * 12);
  var bal = P, contrib = P, rowYear = 0;
  var rows = '';
  for(var i = 1; i <= months; i++){
    bal = bal * (1 + monthlyRate) + M;
    contrib += M;
    if(i % 12 === 0){
      rowYear++;
      if(months <= 480 || rowYear % 5 === 0 || rowYear === 1){
        rows += '<tr><td>' + rowYear + '</td><td>' + fmt(bal) + '</td><td>' + fmt(contrib) + '</td><td>' + fmt(bal - contrib) + '</td></tr>';
      }
    }
  }
  $id('ci-final').textContent = fmt(bal);
  $id('ci-contrib').textContent = fmt(contrib);
  $id('ci-int').textContent = fmt(bal - contrib);
  var pc = bal > 0 ? (contrib / bal * 100) : 0;
  $id('ci-bar-c').style.width = pc + '%';
  $id('ci-bar-i').style.width = (100 - pc) + '%';
  $id('ci-table').innerHTML = rows || '<tr><td colspan="4">Add at least a full year to see the table.</td></tr>';
  showRes('ci-res');
}
runCI();
""",
"faqs": [
("What is compound interest?", "Compound interest is interest earned on interest. Each period, your interest is added to the balance, and the next period's interest is calculated on the bigger balance. Over decades this snowball effect can outgrow your own deposits."),
("Which compounding frequency should I choose?", "Pick the one your bank or investment actually uses — savings accounts usually compound monthly or daily, many bonds annually. More frequent compounding yields slightly more at the same nominal rate."),
("Is this the same as my real investment return?", "No — it is a smooth projection at a constant rate. Real markets go up and down. Use it to compare scenarios (for example, 5% vs 8%, or 10 vs 20 years), not as a promise.")
],
"about": [
"Compound interest is the engine of long-term wealth: at a 7% annual return, money roughly doubles every 10 years, and the majority of a 30-year saver's final balance comes from interest, not deposits. The best way to feel that is to move the sliders and numbers yourself.",
"This calculator converts your nominal annual rate into an equivalent monthly rate based on the compounding frequency you choose, adds your deposit every month, and tracks the balance year by year so you can see exactly when interest starts doing the heavy lifting."
]
},

# ---------------------------------------------------------------- SLEEP
{
"slug": "sleep-cycle-calculator", "name": "Sleep Cycle Calculator", "icon": "😴", "cat": "Health", "popular": False,
"short": "Best bedtimes to wake up refreshed, based on 90-minute sleep cycles.",
"title": "Sleep Cycle Calculator — Best Time to Sleep & Wake Up",
"desc": "Free sleep cycle calculator: find the best bedtime to wake up refreshed, or the ideal wake-up time if you go to bed now. Based on 90-minute sleep cycles.",
"keywords": "sleep cycle calculator, best bedtime, what time should i sleep, 90 minute sleep cycle, wake up refreshed, sleep calculator",
"lead": "You wake up feeling groggy when your alarm interrupts deep sleep. Sleep happens in ~90-minute cycles — this calculator finds bedtimes and wake times that land at the end of a cycle.",
"body": """
<div class="panel">
  <p class="panel-title">I want to wake up at…</p>
  <div class="grid-2">
    <div class="field"><label for="wake-time">Wake-up time</label><input type="time" id="wake-time" value="07:00"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runWake()">Show best bedtimes</button></div>
  <div class="results" id="wake-res">
    <ul class="sleep-list" id="wake-list"></ul>
    <p class="note">Assumes ~15 minutes to fall asleep. 6 cycles = 9 h · 5 cycles = 7.5 h · 4 cycles = 6 h.</p>
  </div>
</div>

<div class="panel">
  <p class="panel-title">I'm going to bed now…</p>
  <div class="grid-2">
    <div class="field"><label for="bed-time">Bedtime (leave empty for “right now”)</label><input type="time" id="bed-time"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runBed()">Show ideal wake times</button></div>
  <div class="results" id="bed-res">
    <ul class="sleep-list" id="bed-list"></ul>
    <p class="note">Wake up at the end of a cycle and you avoid sleep inertia — that heavy, groggy feeling.</p>
  </div>
</div>
""",
"js": """
function fmtT(mins){
  mins = ((mins % 1440) + 1440) % 1440;
  var h = Math.floor(mins / 60), m = mins % 60;
  var ap = h < 12 ? 'AM' : 'PM';
  var h12 = h % 12; if(h12 === 0) h12 = 12;
  return h12 + ':' + (m < 10 ? '0' : '') + m + ' ' + ap;
}
function runWake(){
  var t = $id('wake-time').value;
  if(!t){ alert('Pick a wake-up time.'); return; }
  var p = t.split(':');
  var target = (+p[0]) * 60 + (+p[1]);
  var html = '';
  for(var c = 6; c >= 3; c--){
    var bed = target - c * 90 - 15;
    html += '<li><b>' + fmtT(bed) + '</b><span>' + c + ' cycles · ' + (c * 1.5) + ' h of sleep</span></li>';
  }
  $id('wake-list').innerHTML = html;
  showRes('wake-res');
}
function runBed(){
  var t = $id('bed-time').value;
  var base;
  if(t){ var p = t.split(':'); base = (+p[0]) * 60 + (+p[1]); }
  else { var now = new Date(); base = now.getHours() * 60 + now.getMinutes(); }
  var html = '';
  for(var c = 3; c <= 6; c++){
    var w = base + 15 + c * 90;
    html += '<li><b>' + fmtT(w) + '</b><span>' + c + ' cycles · ' + (c * 1.5) + ' h of sleep</span></li>';
  }
  $id('bed-list').innerHTML = html;
  showRes('bed-res');
}
""",
"faqs": [
("How long is a sleep cycle?", "A full cycle from light sleep through deep sleep to REM sleep lasts about 90 minutes in adults, though it varies from person to person and through the night (typically 80–120 minutes)."),
("Why do I feel worse after 9 hours of sleep than after 7.5?", "Waking mid-cycle — especially during deep sleep — causes sleep inertia, the heavy groggy feeling. 7.5 hours is five complete cycles, while 9 hours of fragmented sleep may still cut a cycle in half."),
("Is 6 hours of sleep enough?", "For most adults, no — 6 hours is the bare minimum and most people do best on 7–9 hours. Use the 4-cycle (6 h) option only when you must, and catch up the next night.")
],
"about": [
"Alarm clocks don't know where you are in your sleep cycle. If they ring during deep (slow-wave) sleep you wake up groggy even after a long night; if they ring between cycles you can feel fine after less sleep. That mismatch is called sleep inertia.",
"This calculator works backwards from your wake-up time in 90-minute steps and adds ~15 minutes of falling-asleep time, giving you several bedtimes that should end a cycle right as your alarm rings. It's a simple heuristic — but a genuinely useful one that millions of people search for every week."
]
},

# ---------------------------------------------------------------- DATE
{
"slug": "date-calculator", "name": "Date Calculator", "icon": "📅", "cat": "Everyday", "popular": False,
"short": "Days between two dates (with business days), or add / subtract days, weeks, months and years.",
"title": "Date Calculator — Days Between Dates & Date Add/Subtract",
"desc": "Free date calculator: count days, weeks, months and business days between two dates, or add and subtract days, weeks, months and years from any date.",
"keywords": "date calculator, days between dates, date difference, add days to date, business days calculator, working days",
"lead": "Two tools in one: find the exact time between two dates (including business days), or add and subtract days, weeks, months and years from a starting date.",
"body": """
<div class="panel">
  <div class="btn-row" style="margin-top:0">
    <button class="btn-primary" type="button" id="tab-diff-btn" onclick="dtTab('diff')">Difference between dates</button>
    <button class="btn-ghost" type="button" id="tab-add-btn" onclick="dtTab('add')">Add / subtract from a date</button>
  </div>

  <div id="dt-diff">
    <div class="grid-2" style="margin-top:16px">
      <div class="field"><label for="d1">Start date</label><input type="date" id="d1"></div>
      <div class="field"><label for="d2">End date</label><input type="date" id="d2"></div>
    </div>
    <div class="btn-row"><button class="btn-primary" type="button" onclick="runDiff()">Calculate difference</button></div>
    <div class="results" id="diff-res">
      <div class="stat-grid">
        <div class="stat"><b id="dif-days">—</b><span>Total days</span></div>
        <div class="stat"><b id="dif-weeks">—</b><span>Weeks & days</span></div>
        <div class="stat"><b id="dif-ymd">—</b><span>Years, months, days</span></div>
        <div class="stat"><b id="dif-biz">—</b><span>Business days</span></div>
      </div>
      <p class="note">Both dates are counted as included. Business days = Monday to Friday, ignoring public holidays.</p>
    </div>
  </div>

  <div id="dt-add" style="display:none">
    <div class="grid-2" style="margin-top:16px">
      <div class="field"><label for="ad-start">Start date</label><input type="date" id="ad-start"></div>
      <div class="field"><label for="ad-n">Amount</label><input type="number" id="ad-n" value="30" step="any"></div>
      <div class="field"><label for="ad-unit">Unit</label>
        <select id="ad-unit"><option value="days">Days</option><option value="weeks">Weeks</option><option value="months">Months</option><option value="years">Years</option></select>
      </div>
      <div class="field"><label for="ad-sign">Direction</label>
        <select id="ad-sign"><option value="add">Add (future)</option><option value="sub">Subtract (past)</option></select>
      </div>
    </div>
    <div class="btn-row"><button class="btn-primary" type="button" onclick="runAdd()">Calculate new date</button></div>
    <div class="results" id="add-res">
      <p class="big-result" id="add-out"></p>
      <p class="note">Adding months handles overflow like a calendar: Jan 31 + 1 month lands on Mar 3 (or Feb 28/29 in some libraries) — this tool uses the “keep the day number, roll over” behaviour of most calendar apps.</p>
    </div>
  </div>
</div>
""",
"js": """
function dtTab(which){
  var diff = which === 'diff';
  $id('dt-diff').style.display = diff ? '' : 'none';
  $id('dt-add').style.display = diff ? 'none' : '';
  $id('tab-diff-btn').className = diff ? 'btn-primary' : 'btn-ghost';
  $id('tab-add-btn').className = diff ? 'btn-ghost' : 'btn-primary';
}
function bizDays(a, b){
  if(b < a){ var t = a; a = b; b = t; }
  var total = Math.round((b - a) / 86400000) + 1;
  if(total > 200000) return null;
  var full = Math.floor(total / 7) * 5, rem = total % 7;
  for(var i = 0; i < rem; i++){
    var dow = new Date(a.getTime() + (Math.floor(total / 7) * 7 + i) * 86400000).getDay();
    if(dow > 0 && dow < 6) full++;
  }
  return full;
}
function runDiff(){
  var v1 = $id('d1').value, v2 = $id('d2').value;
  if(!v1 || !v2){ alert('Please choose both dates.'); return; }
  var a = new Date(v1 + 'T00:00:00'), b = new Date(v2 + 'T00:00:00');
  if(b < a){ var t = a; a = b; b = t; }
  var days = Math.round((b - a) / 86400000);
  $id('dif-days').textContent = fmt(days, 0);
  $id('dif-weeks').textContent = Math.floor(days / 7) + ' w ' + (days % 7) + ' d';
  var y = b.getFullYear() - a.getFullYear(), m = b.getMonth() - a.getMonth(), d = b.getDate() - a.getDate();
  if(d < 0){ m--; d += new Date(b.getFullYear(), b.getMonth(), 0).getDate(); }
  if(m < 0){ y--; m += 12; }
  $id('dif-ymd').textContent = y + 'y ' + m + 'm ' + d + 'd';
  var bd = bizDays(a, b);
  $id('dif-biz').textContent = bd === null ? '—' : fmt(bd, 0);
  showRes('diff-res');
}
function runAdd(){
  var v = $id('ad-start').value;
  if(!v){ alert('Please choose a start date.'); return; }
  var n = parseFloat($id('ad-n').value);
  if(isNaN(n)){ alert('Please enter an amount.'); return; }
  var d = new Date(v + 'T00:00:00');
  var unit = $id('ad-unit').value;
  var sign = $id('ad-sign').value === 'sub' ? -1 : 1;
  if(unit === 'days') d.setDate(d.getDate() + sign * n);
  else if(unit === 'weeks') d.setDate(d.getDate() + sign * 7 * n);
  else if(unit === 'months') d.setMonth(d.getMonth() + sign * n);
  else d.setFullYear(d.getFullYear() + sign * n);
  var days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  $id('add-out').textContent = d.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  showRes('add-res');
}
(function(){
  var t = new Date();
  $id('d1').value = localISO(t);
  $id('ad-start').value = localISO(t);
  var next = new Date(t.getTime() + 30 * 86400000);
  $id('d2').value = localISO(next);
})();
""",
"faqs": [
("Does the day count include the start and end dates?", "The total days shown is the pure difference (end minus start). The business-days figure counts both endpoints as included — the standard working-days convention for deadlines."),
("What are business days?", "Monday through Friday. Public holidays are not subtracted because they differ by country and year — check your local holiday calendar if precision matters."),
("Why would I need to add months to a date?", "Contract deadlines, visa and notice periods, subscription renewals, pregnancy due dates and loan terms are almost always expressed as “+ 3 months” or “+ 6 months” rather than a day count.")
],
"about": [
"Date math sounds trivial until you try it: months have different lengths, leap years add a day every four years (except most century years), and “one month from January 31” has no single right answer. Calendars are genuinely hard, which is why date calculators are among the most-searched utilities on the web.",
"Typical uses: counting days until a deadline or trip, checking a notice period, computing someone's exact age at a future date, or finding what weekday a project milestone will land on."
]
},

# ---------------------------------------------------------------- BMI
{
"slug": "bmi-calculator", "name": "BMI Calculator", "icon": "⚖️", "cat": "Health", "popular": True,
"short": "Body Mass Index in metric or imperial units, with your healthy weight range.",
"title": "BMI Calculator — Body Mass Index (Metric & Imperial)",
"desc": "Free BMI calculator in metric and imperial units. Get your Body Mass Index, WHO category, and the healthy weight range for your height — instantly and privately.",
"keywords": "bmi calculator, body mass index, healthy weight range, metric imperial bmi, who bmi categories",
"lead": "Enter your height and weight to get your Body Mass Index, your WHO weight category, and the weight range that is considered healthy for your height.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="bmi-units">Units</label>
      <select id="bmi-units" onchange="bmiUnits()">
        <option value="metric">Metric (cm, kg)</option>
        <option value="imperial">Imperial (ft/in, lb)</option>
      </select>
    </div>
  </div>
  <div class="grid-2" id="bmi-metric" style="margin-top:14px">
    <div class="field"><label for="bmi-h">Height (cm)</label><input type="number" id="bmi-h" value="170" min="0" step="any"></div>
    <div class="field"><label for="bmi-w">Weight (kg)</label><input type="number" id="bmi-w" value="70" min="0" step="any"></div>
  </div>
  <div class="grid-2" id="bmi-imperial" style="display:none;margin-top:14px">
    <div class="field"><label for="bmi-ft">Height (feet)</label><input type="number" id="bmi-ft" value="5" min="0" step="any"></div>
    <div class="field"><label for="bmi-in">Height (inches)</label><input type="number" id="bmi-in" value="7" min="0" step="any"></div>
    <div class="field"><label for="bmi-lb">Weight (pounds)</label><input type="number" id="bmi-lb" value="154" min="0" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runBMI()">Calculate BMI</button></div>
  <div class="results" id="bmi-res">
    <div class="stat-grid">
      <div class="stat"><b id="bmi-val">—</b><span>Your BMI</span></div>
      <div class="stat"><b id="bmi-cat">—</b><span>Category</span></div>
      <div class="stat"><b id="bmi-range">—</b><span>Healthy weight range</span></div>
    </div>
    <div class="gauge"><i id="bmi-mark"></i></div>
    <div class="gauge-labels"><span>12</span><span>18.5</span><span>25</span><span>30</span><span>40</span></div>
    <p class="note">BMI is a rough screening tool, not a diagnosis. It does not distinguish muscle from fat and is less reliable for athletes, children, pregnancy and older adults. Talk to a doctor about your individual situation.</p>
  </div>
</div>
""",
"js": """
function bmiUnits(){
  var imp = $id('bmi-units').value === 'imperial';
  $id('bmi-metric').style.display = imp ? 'none' : '';
  $id('bmi-imperial').style.display = imp ? '' : 'none';
}
function runBMI(){
  var hcm, wkg, unit = $id('bmi-units').value;
  if(unit === 'metric'){
    hcm = readNum('bmi-h', 'height'); wkg = readNum('bmi-w', 'weight');
  } else {
    var ft = readNum('bmi-ft', 'feet'), inch = parseFloat($id('bmi-in').value) || 0;
    var lb = readNum('bmi-lb', 'weight');
    if(ft === null || lb === null) return;
    hcm = (ft * 12 + inch) * 2.54;
    wkg = lb * 0.45359237;
  }
  if(hcm === null || wkg === null || hcm <= 0 || wkg <= 0){ alert('Height and weight must be positive numbers.'); return; }
  var h = hcm / 100;
  var bmi = wkg / (h * h);
  var cat, col;
  if(bmi < 18.5){ cat = 'Underweight'; col = '#60a5fa'; }
  else if(bmi < 25){ cat = 'Healthy'; col = '#4ade80'; }
  else if(bmi < 30){ cat = 'Overweight'; col = '#fbbf24'; }
  else { cat = 'Obese'; col = '#f87171'; }
  var lo = 18.5 * h * h, hi = 24.9 * h * h;
  var range = (unit === 'metric')
    ? fmt(lo, 1) + ' – ' + fmt(hi, 1) + ' kg'
    : fmt(lo / 0.45359237, 1) + ' – ' + fmt(hi / 0.45359237, 1) + ' lb';
  $id('bmi-val').textContent = fmt(bmi, 1);
  $id('bmi-cat').textContent = cat;
  $id('bmi-cat').style.color = col;
  $id('bmi-range').textContent = range;
  var pct = Math.min(Math.max((bmi - 12) / (40 - 12) * 100, 0), 100);
  $id('bmi-mark').style.left = pct + '%';
  showRes('bmi-res');
}
""",
"faqs": [
("What is a healthy BMI?", "The WHO classifies 18.5–24.9 as the healthy range for adults. Below 18.5 is underweight, 25–29.9 is overweight, and 30+ falls into obesity classes."),
("Is BMI accurate?", "As a population-level screening tool, yes. For individuals it has well-known blind spots: it can flag muscular athletes as overweight and miss unhealthy fat distribution. Waist size and body composition tell a more complete story."),
("What BMI should children use?", "Children and teenagers need age- and sex-specific percentile charts, not the adult cut-offs used here. Consult a paediatrician or a child-specific calculator.")
],
"about": [
"BMI (Body Mass Index) divides your weight by the square of your height (kg/m²). It was designed in the 1830s as a population statistic, and it remains the fastest universal screening number for weight-related health risk — which is exactly why doctors, insurers, gyms and diet apps still ask for it.",
"The healthy-weight range shown alongside your BMI is simply your height multiplied by the healthy BMI band (18.5–24.9), converted back into your chosen units — the number most people are actually looking for when they search for a BMI calculator."
]
},

# ---------------------------------------------------------------- WORD COUNTER
{
"slug": "word-counter", "name": "Word Counter", "icon": "✍️", "cat": "Text", "popular": True,
"short": "Live word, character, sentence and paragraph counts with reading time.",
"title": "Word Counter — Words, Characters, Sentences & Reading Time",
"desc": "Free word counter: live counts of words, characters, sentences and paragraphs, plus estimated reading and speaking time. Nothing is uploaded — works fully offline.",
"keywords": "word counter, character count, letter count, sentence counter, reading time calculator, words per page",
"lead": "Paste or type text and get live counts of words, characters, sentences and paragraphs — plus estimated reading and speaking time. Your text never leaves the page.",
"body": """
<div class="panel">
  <div class="field">
    <label for="wc-text">Your text</label>
    <textarea id="wc-text" rows="9" placeholder="Paste or type your text here — counts update as you type…"></textarea>
  </div>
  <div class="btn-row"><button class="btn-ghost" type="button" onclick="$id('wc-text').value='';runWC()">Clear</button></div>
  <div class="results show" id="wc-res">
    <div class="stat-grid">
      <div class="stat"><b id="wc-words">0</b><span>Words</span></div>
      <div class="stat"><b id="wc-chars">0</b><span>Characters</span></div>
      <div class="stat"><b id="wc-nospace">0</b><span>Without spaces</span></div>
      <div class="stat"><b id="wc-sent">0</b><span>Sentences</span></div>
      <div class="stat"><b id="wc-para">0</b><span>Paragraphs</span></div>
      <div class="stat"><b id="wc-read">0 sec</b><span>Reading time</span></div>
      <div class="stat"><b id="wc-speak">0 sec</b><span>Speaking time</span></div>
    </div>
    <p class="note">Reading time assumes ~200 words per minute; speaking time ~130 wpm (average presentation pace).</p>
  </div>
</div>
""",
"js": r"""
function dur(mins){
  if(mins <= 0) return '0 sec';
  var s = Math.round(mins * 60);
  if(s < 60) return s + ' sec';
  var m = Math.floor(s / 60), r = s % 60;
  if(m < 60) return m + ' min' + (r ? ' ' + r + ' sec' : '');
  var h = Math.floor(m / 60);
  return h + ' hr ' + (m % 60) + ' min';
}
function runWC(){
  var t = $id('wc-text').value;
  var words = (t.match(/\S+/g) || []).length;
  var sentences = (t.match(/[.!?]+(?=\s|$)/g) || []).length;
  if(words > 0 && sentences === 0) sentences = 1;
  var paras = t.split(/\n+/).filter(function(p){ return p.trim().length > 0; }).length;
  $id('wc-words').textContent = fmt(words, 0);
  $id('wc-chars').textContent = fmt(t.length, 0);
  $id('wc-nospace').textContent = fmt(t.replace(/\s/g, '').length, 0);
  $id('wc-sent').textContent = fmt(sentences, 0);
  $id('wc-para').textContent = fmt(paras, 0);
  $id('wc-read').textContent = dur(words / 200);
  $id('wc-speak').textContent = dur(words / 130);
}
(function(){
  var el = $id('wc-text');
  el.addEventListener('input', runWC);
  runWC();
})();
""",
"faqs": [
("How are words counted?", "A word is any run of characters separated by whitespace — so “state-of-the-art” counts as one word and “don't” as one word. Hyphenated compounds and numbers attached to text follow the same rule."),
("How many words is a page?", "A single-spaced page in a typical 12 pt font holds roughly 500 words; double-spaced about 250. Universities usually quote 250–275 words per double-spaced page."),
("Is my text uploaded anywhere?", "No. The counter runs entirely in your browser — you can even disconnect from the internet while typing and it keeps counting.")
],
"about": [
"Word counts gate a surprising amount of life: essays and dissertations have hard limits, X/Twitter posts have character caps, meta descriptions live around 155 characters, LinkedIn posts decay after ~1,300, and medium-form articles are judged by estimated reading time.",
"Reading and speaking time estimates are the underrated half of this tool: they tell you whether your blog post is a 3-minute skim or a 12-minute commitment, and whether your speech fits the 5-minute slot on the conference agenda."
]
},
]
