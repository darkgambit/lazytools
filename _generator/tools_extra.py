# -*- coding: utf-8 -*-
"""LazyTools — tool definitions, part 2 of 2 (utilities / finance / text / business)."""

TOOLS_EXTRA = [

# ---------------------------------------------------------------- PASSWORD
{
"slug": "password-generator", "name": "Password Generator", "icon": "🔐", "cat": "Utilities", "popular": False,
"short": "Strong random passwords generated locally with crypto-grade randomness.",
"title": "Password Generator — Strong, Random & Secure Passwords",
"desc": "Free password generator: create strong random passwords with custom length and character sets. Generated locally with cryptographic randomness — nothing is transmitted or stored.",
"keywords": "password generator, strong password, random password, secure password generator, create password",
"lead": "Generate strong, random passwords in one click. Everything happens on your device using cryptographically secure randomness — generated passwords are never sent anywhere.",
"body": """
<div class="panel">
  <div class="output-box" id="pw-out">Click “Generate password”…</div>
  <div class="btn-row">
    <button class="btn-primary" type="button" onclick="genPw()">Generate password</button>
    <button class="btn-ghost" type="button" onclick="copyVal('pw-out', this)">Copy</button>
  </div>
  <div class="field" style="margin-top:20px">
    <label for="pw-len">Length: <span id="pw-len-val">16</span> characters</label>
    <input type="range" id="pw-len" min="6" max="64" value="16" oninput="$id('pw-len-val').textContent=this.value">
  </div>
  <div class="check"><input type="checkbox" id="pw-lower" checked><label for="pw-lower" style="margin:0">Lowercase (a–z)</label></div>
  <div class="check"><input type="checkbox" id="pw-upper" checked><label for="pw-upper" style="margin:0">Uppercase (A–Z)</label></div>
  <div class="check"><input type="checkbox" id="pw-num" checked><label for="pw-num" style="margin:0">Numbers (0–9)</label></div>
  <div class="check"><input type="checkbox" id="pw-sym" checked><label for="pw-sym" style="margin:0">Symbols (!@#$%…)</label></div>
  <div class="check"><input type="checkbox" id="pw-amb"><label for="pw-amb" style="margin:0">Exclude look-alikes (I, l, 1, O, 0)</label></div>
  <div class="strength-bar"><i id="pw-bar"></i></div>
  <p class="note" id="pw-str">Strength: —</p>
</div>
""",
"js": """
function genPw(){
  var len = parseInt($id('pw-len').value, 10);
  var sets = [];
  if($id('pw-lower').checked) sets.push('abcdefghijklmnopqrstuvwxyz');
  if($id('pw-upper').checked) sets.push('ABCDEFGHIJKLMNOPQRSTUVWXYZ');
  if($id('pw-num').checked) sets.push('0123456789');
  if($id('pw-sym').checked) sets.push('!@#$%^&*()-_=+[]{};:,.<>?/~');
  if(!sets.length){ alert('Select at least one character type.'); return; }
  var pool = sets.join('');
  if($id('pw-amb').checked) pool = pool.replace(/[Il1O0o]/g, '');
  if(!pool.length){ alert('That combination excludes every character — untick “look-alikes”.'); return; }
  var rnd = new Uint32Array(len);
  (window.crypto || window.msCrypto).getRandomValues(rnd);
  var out = '';
  for(var i = 0; i < len; i++) out += pool.charAt(rnd[i] % pool.length);
  $id('pw-out').textContent = out;
  var bits = len * Math.log2(pool.length);
  var label, pct, col;
  if(bits < 40){ label = 'Weak'; pct = 25; col = '#f87171'; }
  else if(bits < 60){ label = 'Fair'; pct = 50; col = '#fbbf24'; }
  else if(bits < 90){ label = 'Strong'; pct = 75; col = '#a3e635'; }
  else { label = 'Excellent'; pct = 100; col = '#4ade80'; }
  $id('pw-str').textContent = 'Strength: ' + label + ' (~' + Math.round(bits) + ' bits of entropy — ' + pool.length + ' possible characters)';
  $id('pw-bar').style.width = pct + '%';
  $id('pw-bar').style.background = col;
}
genPw();
""",
"faqs": [
("Are these passwords safe to use?", "Yes. They are generated on your device with the browser's cryptographic random number generator (the same API used for encryption keys) and are never transmitted, logged or stored. Close the tab and they are gone."),
("How long should a password be?", "At least 16 characters for anything important. Length matters more than weird symbols: a 20-character password of mixed case and digits is far harder to crack than a short one full of symbols."),
("Why not just use one tricky password everywhere?", "Because one breached site exposes every account you own. Pair unique generated passwords with a password manager, and turn on two-factor authentication wherever it is offered.")
],
"about": [
"Almost every large password leak comes from two causes: passwords chosen by humans (patterns, names, keyboard walks) and password reuse across sites. A random generator removes the first problem, and a password manager makes reuse unnecessary.",
"The strength meter shown here is based on real entropy — length multiplied by the information content of the character pool — rather than cosmetic rules, so adding length visibly moves the needle while swapping symbols for other symbols does not."
],
"gear": [
{"query": "hardware security key fido2", "label": "Hardware security key (FIDO2)", "why": "Phishing-proof second factor. A strong generated password plus a hardware key is the single biggest upgrade you can make to an account."},
{"query": "password manager", "label": "Password manager", "why": "This is what makes it practical to give every site a different generated password and actually remember none of them."}
]
},

# ---------------------------------------------------------------- TIP
{
"slug": "tip-calculator", "name": "Tip Calculator", "icon": "💵", "cat": "Finance", "popular": False,
"short": "Tip amount, total and per-person split in one tap.",
"title": "Tip Calculator — Tip Amount, Total & Bill Split",
"desc": "Free tip calculator: enter the bill, pick a tip percentage and split between friends to get the tip, total and each person's share instantly.",
"keywords": "tip calculator, gratuity calculator, bill splitter, how much to tip, split the bill",
"lead": "Enter the bill, choose a tip percentage, and say how many people are splitting — you'll get the tip, the total, and each person's share instantly.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="tip-bill">Bill amount</label><input type="number" id="tip-bill" placeholder="e.g. 84.50" min="0" step="any"></div>
    <div class="field"><label for="tip-pct">Tip (%)</label><input type="number" id="tip-pct" value="15" min="0" step="any"></div>
    <div class="field"><label for="tip-people">Split between (people)</label><input type="number" id="tip-people" value="1" min="1" step="1"></div>
  </div>
  <div class="btn-row">
    <button class="btn-ghost" type="button" onclick="tipQuick(10)">10%</button>
    <button class="btn-primary" type="button" onclick="tipQuick(15)">15%</button>
    <button class="btn-ghost" type="button" onclick="tipQuick(18)">18%</button>
    <button class="btn-ghost" type="button" onclick="tipQuick(20)">20%</button>
    <button class="btn-ghost" type="button" onclick="tipQuick(25)">25%</button>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runTip()">Calculate</button></div>
  <div class="results" id="tip-res">
    <div class="stat-grid">
      <div class="stat"><b id="tip-amt">—</b><span>Tip</span></div>
      <div class="stat"><b id="tip-total">—</b><span>Total bill</span></div>
      <div class="stat"><b id="tip-each">—</b><span>Per person (total)</span></div>
      <div class="stat"><b id="tip-eachtip">—</b><span>Tip per person</span></div>
    </div>
    <p class="note">Typical etiquette: 15–20% in the US, 10% or rounding up in much of Europe and the Middle East, and no tipping in Japan. When in doubt, ask a local.</p>
  </div>
</div>
""",
"js": """
function tipQuick(p){ $id('tip-pct').value = p; runTip(); }
function runTip(){
  var bill = readNum('tip-bill', 'bill amount');
  var pct = readNum('tip-pct', 'tip');
  var people = parseInt($id('tip-people').value, 10);
  if(bill === null || pct === null) return;
  if(isNaN(people) || people < 1){ alert('At least one person is paying!'); return; }
  var tip = bill * pct / 100;
  var total = bill + tip;
  $id('tip-amt').textContent = fmt(tip);
  $id('tip-total').textContent = fmt(total);
  $id('tip-each').textContent = fmt(total / people);
  $id('tip-eachtip').textContent = fmt(tip / people);
  showRes('tip-res');
}
""",
"faqs": [
("How much should I tip?", "It depends on the country. In the United States 15–20% of the pre-tax bill is standard for restaurants. In most of Europe a 10% service charge is either included or a small extra is appreciated. In many Asian countries tipping is not expected at all."),
("Should I tip on the pre-tax or post-tax amount?", "Convention is to tip on the pre-tax subtotal in countries that add sales tax at the register. In countries where prices include tax, the printed total is what you tip on."),
("How do I split a bill fairly?", "The simplest approach is to split the total evenly as this calculator does. For very uneven orders, have each person add roughly 120% of their own dish (to cover tax and tip).")
],
"about": [
"Tipping math is done at the worst possible moment: the bill has arrived, the waiter is hovering, and everyone at the table is suddenly a mathematician. A tip calculator removes the fumbling and the arguments.",
"The per-person figures make group meals painless, and the quick-percentage buttons cover the common etiquette standards so you can adapt quickly whether you are dining in New York, Berlin or Tripoli. If the bill also carries sales tax or VAT, the <a href=\"sales-tax-calculator.html\">sales tax calculator</a> separates the tax from the food so you can tip on the right number."
]
},

# ---------------------------------------------------------------- UNIT CONVERTER
{
"slug": "unit-converter", "name": "Unit Converter", "icon": "🔄", "cat": "Utilities", "popular": False,
"short": "Length, weight, volume, area, speed, data and temperature conversions.",
"title": "Unit Converter — Length, Weight, Volume, Temperature & More",
"desc": "Free unit converter for length, weight, volume, area, speed, data storage and temperature. Metric ↔ imperial, instant results, works offline.",
"keywords": "unit converter, metric to imperial, length converter, weight converter, temperature converter, data storage converter",
"lead": "Convert between metric, imperial and everyday units across seven categories — including the tricky one, temperature. Results update as you type.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="uc-cat">Category</label>
      <select id="uc-cat" onchange="ucFill()">
        <option value="length">Length</option>
        <option value="weight">Weight & mass</option>
        <option value="volume">Volume</option>
        <option value="area">Area</option>
        <option value="speed">Speed</option>
        <option value="data">Data storage</option>
        <option value="temperature">Temperature</option>
      </select>
    </div>
    <div class="field"><label for="uc-val">Value</label><input type="number" id="uc-val" value="1" step="any" oninput="runUC()"></div>
    <div class="field"><label for="uc-from">From</label><select id="uc-from" onchange="runUC()"></select></div>
    <div class="field"><label for="uc-to">To</label><select id="uc-to" onchange="runUC()"></select></div>
  </div>
  <div class="btn-row">
    <button class="btn-primary" type="button" onclick="runUC()">Convert</button>
    <button class="btn-ghost" type="button" onclick="ucSwap()">⇄ Swap units</button>
  </div>
  <div class="results show" id="uc-res"><p class="big-result" id="uc-out">—</p></div>
</div>
""",
"js": """
var UC = {
  length: { meter:1, kilometer:1000, centimeter:0.01, millimeter:0.001, micrometer:1e-6, mile:1609.344, yard:0.9144, foot:0.3048, inch:0.0254, 'nautical mile':1852 },
  weight: { kilogram:1, gram:0.001, milligram:1e-6, 'metric ton':1000, pound:0.45359237, ounce:0.028349523125, stone:6.35029318, 'US ton':907.18474 },
  volume: { liter:1, milliliter:0.001, 'cubic meter':1000, 'US gallon':3.785411784, 'US quart':0.946352946, 'US pint':0.473176473, 'US cup':0.2365882365, 'US fluid ounce':0.0295735295625, 'imperial gallon':4.54609 },
  area: { 'square meter':1, 'square kilometer':1e6, 'square centimeter':0.0001, 'square foot':0.09290304, 'square yard':0.83612736, acre:4046.8564224, hectare:10000, 'square mile':2589988.110336 },
  speed: { 'meter per second':1, 'kilometer per hour':0.2777777778, 'mile per hour':0.44704, knot:0.5144444444, 'foot per second':0.3048 },
  data: { byte:1, bit:0.125, kilobyte:1000, megabyte:1e6, gigabyte:1e9, terabyte:1e12, kibibyte:1024, mebibyte:1048576, gibibyte:1073741824 },
  temperature: { 'Celsius (°C)':1, 'Fahrenheit (°F)':1, 'Kelvin (K)':1 }
};
function ucFill(){
  var cat = $id('uc-cat').value;
  var units = Object.keys(UC[cat]);
  var from = $id('uc-from'), to = $id('uc-to');
  from.innerHTML = ''; to.innerHTML = '';
  units.forEach(function(u){
    from.appendChild(new Option(u, u));
    to.appendChild(new Option(u, u));
  });
  if(cat === 'temperature'){ to.value = 'Fahrenheit (°F)'; }
  else { if(units.indexOf('foot') > -1) to.value = 'foot'; else to.value = units[Math.min(1, units.length - 1)]; }
  runUC();
}
function ucSwap(){
  var f = $id('uc-from'), t = $id('uc-to');
  var tmp = f.value; f.value = t.value; t.value = tmp;
  runUC();
}
function toC(v, u){
  if(u.indexOf('Fahrenheit') === 0) return (v - 32) * 5 / 9;
  if(u.indexOf('Kelvin') === 0) return v - 273.15;
  return v;
}
function fromC(c, u){
  if(u.indexOf('Fahrenheit') === 0) return c * 9 / 5 + 32;
  if(u.indexOf('Kelvin') === 0) return c + 273.15;
  return c;
}
function runUC(){
  var cat = $id('uc-cat').value;
  var v = parseFloat($id('uc-val').value);
  var fu = $id('uc-from').value, tu = $id('uc-to').value;
  if(isNaN(v)){ $id('uc-out').textContent = '—'; return; }
  var r;
  if(cat === 'temperature'){
    r = fromC(toC(v, fu), tu);
  } else {
    r = v * UC[cat][fu] / UC[cat][tu];
  }
  $id('uc-out').textContent = fmt(v) + ' ' + fu + ' = ' + fmt(r) + ' ' + tu;
}
ucFill();
""",
"faqs": [
("How accurate are the conversions?", "Conversion factors are the exact internationally defined values (for example 1 inch = 2.54 cm exactly, 1 pound = 0.45359237 kg exactly). Results are shown to a sensible number of digits."),
("Why does temperature need special handling?", "Unlike length or weight, temperature scales have different zero points, not just different unit sizes. Converting °C to °F needs multiplication and addition — that's why “wind chill” and oven settings confuse everyone."),
("What's the difference between GB and GiB?", "A gigabyte (GB) is 1,000,000,000 bytes; a gibibyte (GiB) is 1,073,741,824 bytes (1024³). That ~7% gap is why a “500 GB” drive shows as ~465 GiB in your operating system.")
],
"about": [
"Unit conversion is a daily necessity in a world split between metric and imperial: recipes from another continent, fuel efficiency quotes in miles per gallon versus litres per 100 km, screen sizes in inches, body weight in kilograms versus stones, and data plans in megabytes.",
"This converter uses exact internationally-defined factors and handles the one category that doesn't convert by simple multiplication — temperature — with the correct offset formulas in both directions."
]
},

# ---------------------------------------------------------------- LOAN
{
"slug": "loan-calculator", "name": "Loan Calculator", "icon": "🏦", "cat": "Finance", "popular": False,
"short": "Monthly payment and total interest for any loan — plus extra-payment savings.",
"title": "Loan Calculator — Monthly Payment & Total Interest",
"desc": "Free loan calculator: estimate monthly payments and total interest for any loan, and see how much an extra monthly payment saves you. Works for car loans, personal loans and mortgages.",
"keywords": "loan calculator, monthly payment calculator, mortgage payment calculator, car loan calculator, extra payment savings, amortization",
"lead": "Enter a loan amount, interest rate and term to get the monthly payment and total interest — then see how much an extra monthly payment saves you and shortens the loan.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="ln-p">Loan amount</label><input type="number" id="ln-p" value="20000" min="1" step="any"></div>
    <div class="field"><label for="ln-r">Annual interest rate (%)</label><input type="number" id="ln-r" value="6" min="0" step="any"></div>
    <div class="field"><label for="ln-y">Term (years)</label><input type="number" id="ln-y" value="5" min="1" step="any"></div>
    <div class="field"><label for="ln-x">Extra monthly payment (optional)</label><input type="number" id="ln-x" value="0" min="0" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runLoan()">Calculate payment</button></div>
  <div class="results" id="ln-res">
    <div class="stat-grid">
      <div class="stat"><b id="ln-pay">—</b><span>Monthly payment</span></div>
      <div class="stat"><b id="ln-int">—</b><span>Total interest (with extra)</span></div>
      <div class="stat"><b id="ln-save">—</b><span>Interest saved by extra payments</span></div>
      <div class="stat"><b id="ln-time">—</b><span>Payoff time (with extra)</span></div>
    </div>
    <div class="bar-stack"><i id="ln-bar-p" style="background:#8fa4ff;width:50%"></i><i id="ln-bar-i" style="background:#f5b53f;width:50%"></i></div>
    <div class="legend"><span><i style="background:#8fa4ff"></i>Principal</span><span><i style="background:#f5b53f"></i>Interest</span></div>
    <p class="note">Principal & interest only — taxes, insurance and fees are not included. Even 25–50 extra per month can cut years off a long loan.</p>
  </div>
</div>
""",
"js": """
function runLoan(){
  var P = readNum('ln-p', 'loan amount'), R = readNum('ln-r', 'interest rate'), Y = readNum('ln-y', 'term');
  var X = parseFloat($id('ln-x').value) || 0;
  if(P === null || R === null || Y === null) return;
  if(P <= 0 || Y <= 0 || R < 0){ alert('Check the loan amount, rate and term.'); return; }
  var r = R / 100 / 12;
  var n = Math.round(Y * 12);
  var pay = (r === 0) ? P / n : P * r / (1 - Math.pow(1 + r, -n));
  var bal = P, months = 0, paid = 0;
  var capped = false;
  while(bal > 0.005 && months < 1200){
    var interest = bal * r;
    var principal = pay + X - interest;
    if(principal <= 0){ capped = true; break; }
    if(principal > bal) principal = bal;
    bal -= principal; paid += principal + interest; months++;
  }
  var baseInterest = pay * n - P;
  var saved = Math.max(0, baseInterest - (paid - P));
  $id('ln-pay').textContent = fmt(pay) + (X > 0 ? ' + ' + fmt(X) : '');
  $id('ln-int').textContent = fmt(Math.max(0, paid - P));
  $id('ln-save').textContent = fmt(saved);
  $id('ln-time').textContent = capped ? 'Never (extra too small)' : Math.floor(months / 12) + ' y ' + (months % 12) + ' m';
  var tp = Math.min(P / paid * 100, 100);
  $id('ln-bar-p').style.width = tp + '%';
  $id('ln-bar-i').style.width = (100 - tp) + '%';
  showRes('ln-res');
}
runLoan();
""",
"faqs": [
("What is the monthly payment formula?", "Payment = P · r / (1 − (1+r)^−n), where P is the loan amount, r the monthly rate (annual ÷ 12) and n the number of months. It is the standard amortization formula used by banks worldwide."),
("Why do extra payments help so much?", "Every extra unit of currency goes straight to principal, which reduces the balance interest is charged on for all remaining months. On long loans the effect compounds dramatically — often saving thousands in interest."),
("Does this work for mortgages?", "Yes for the principal-and-interest part. Full mortgage payments also include property taxes and insurance, and your bank may charge fees — add those separately.")
],
"about": [
"A loan is one of the few big financial decisions where five minutes with a calculator can save you thousands. The monthly payment formula is fixed, but the trade-offs — shorter term versus lower payment, extra payments versus investing the money — are yours to explore.",
"The extra-payment simulation on this page runs a real month-by-month amortization, the same way your bank does, so the interest saved and payoff time reflect what actually happens to your balance, not a rough approximation."
]
},

# ---------------------------------------------------------------- WATER
{
"slug": "water-intake-calculator", "name": "Water Intake Calculator", "icon": "💧", "cat": "Health", "popular": False,
"short": "Personalized daily water goal based on weight, activity and climate.",
"title": "Water Intake Calculator — How Much Water Should You Drink?",
"desc": "Free water intake calculator: get a personalized daily hydration goal based on your body weight, exercise minutes and climate — in litres, glasses and bottles.",
"keywords": "water intake calculator, how much water should i drink, daily water intake, hydration calculator, water per day",
"lead": "Get a personalized daily water goal based on your body weight, how much you exercise, and how hot your climate is — shown in litres, glasses and bottles.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="w-units">Units</label>
      <select id="w-units" onchange="wUnits()">
        <option value="metric">Metric (kg)</option>
        <option value="imperial">Imperial (lb)</option>
      </select>
    </div>
    <div class="field"><label for="w-kg" id="w-wlabel">Body weight (kg)</label><input type="number" id="w-kg" value="70" min="0" step="any"></div>
    <div class="field"><label for="w-ex">Exercise (minutes per day)</label><input type="number" id="w-ex" value="30" min="0" step="any"></div>
    <div class="field"><label for="w-climate">Climate</label>
      <select id="w-climate">
        <option value="0">Temperate / cool</option>
        <option value="0.35">Warm</option>
        <option value="0.7" selected>Hot (desert, summer)</option>
      </select>
    </div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runWater()">Calculate my goal</button></div>
  <div class="results" id="w-res">
    <div class="stat-grid">
      <div class="stat"><b id="w-liters">—</b><span>Litres per day</span></div>
      <div class="stat"><b id="w-glasses">—</b><span>250 ml glasses</span></div>
      <div class="stat"><b id="w-bottles">—</b><span>500 ml bottles</span></div>
    </div>
    <p class="note">Rule of thumb used: ~35 ml per kg of body weight, +350 ml per 30 min of exercise, + a climate adjustment. Food also supplies ~20% of your fluids. This is general guidance, not medical advice — kidney or heart conditions may require different limits.</p>
  </div>
</div>
""",
"js": """
function wUnits(){
  var imp = $id('w-units').value === 'imperial';
  $id('w-wlabel').textContent = imp ? 'Body weight (lb)' : 'Body weight (kg)';
}
function runWater(){
  var w = readNum('w-kg', 'body weight');
  var ex = parseFloat($id('w-ex').value) || 0;
  if(w === null || w <= 0){ alert('Enter a positive body weight.'); return; }
  var kg = $id('w-units').value === 'imperial' ? w * 0.45359237 : w;
  var climate = parseFloat($id('w-climate').value) || 0;
  var liters = (kg * 0.035) + (ex / 30) * 0.35 + climate;
  $id('w-liters').textContent = fmt(liters, 1) + ' L';
  $id('w-glasses').textContent = fmt(liters * 1000 / 250, 0);
  $id('w-bottles').textContent = fmt(liters * 1000 / 500, 1);
  showRes('w-res');
}
""",
"faqs": [
("How much water should I drink per day?", "A common guideline is about 35 ml per kilogram of body weight — roughly 2.5 litres for a 70 kg adult — plus more for exercise and hot weather. Around 20% of your fluid intake normally comes from food."),
("Do coffee and tea count?", "Yes. Despite their mild diuretic reputation, caffeinated drinks still hydrate you on balance. Water is still the cheapest and healthiest default."),
("Can I drink too much water?", "Rarely, but yes — extreme intake in a short time can dilute blood sodium (hyponatremia). Spread intake across the day and drink to thirst, especially if you have kidney or heart conditions.")
],
"about": [
"Hydration needs are not one-size-fits-all: they scale with body mass, sweat losses from activity, and climate — which is why a one-line “8 glasses a day” rule fails desert dwellers and office workers alike.",
"This calculator starts from the widely used weight-based guideline (about 35 ml per kg), adds sweat replacement for exercise, and layers on a climate adjustment — then translates the result into glasses and bottles, the units people actually track. Water is only half of the intake picture, though; the <a href=\"calorie-calculator.html\">calorie calculator</a> covers the energy side with your BMR and daily calorie needs."
],
"gear": [
{"query": "insulated water bottle 1 litre", "label": "Insulated 1 L water bottle", "why": "Keeping it visible and full on your desk does more for your intake than any reminder app."},
{"query": "reusable water bottle with time markers", "label": "Bottle with time markers", "why": "Turns a daily total into hourly checkpoints, which is the part people actually miss."}
]
},

# ---------------------------------------------------------------- INVOICE
{
"slug": "invoice-generator", "name": "Invoice Generator", "icon": "🧾", "cat": "Business", "popular": True,
"short": "Create a clean, professional invoice and save it as PDF — free, no signup.",
"title": "Free Invoice Generator — Create & Download Invoices as PDF",
"desc": "Free invoice generator: create professional invoices with line items and tax, then save as PDF straight from your browser. No signup, no watermark, nothing uploaded.",
"keywords": "invoice generator, free invoice maker, create invoice online, invoice pdf, invoice template",
"lead": "Fill in the fields, add your line items, and hit “Print / Save as PDF” for a clean, professional invoice. Free, no signup, no watermark — and it never leaves your browser.",
"body": """
<div class="panel no-print">
  <p class="panel-title" style="margin-bottom:6px">How it works</p>
  <p class="note" style="margin-top:0">Type directly into the invoice below — totals update live. When you're done, click <b>Print / Save as PDF</b> and choose “Save as PDF” as the printer destination. Everything stays on your device.</p>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="window.print()">🖨️ Print / Save as PDF</button></div>
</div>

<div id="invoice-sheet" class="invoice-sheet">
  <div class="inv-head">
    <div>
      <div class="inv-logo">INVOICE</div>
      <label>Invoice #</label><input id="inv-no" value="INV-001">
    </div>
    <div class="inv-dates">
      <label>Date</label><input type="date" id="inv-date">
      <label>Due date</label><input type="date" id="inv-due">
    </div>
  </div>

  <div class="inv-parties">
    <div>
      <label>From (your details)</label>
      <textarea id="inv-from" rows="4">Your Name&#10;Street Address&#10;City, Country&#10;you@example.com</textarea>
    </div>
    <div>
      <label>Bill to (client)</label>
      <textarea id="inv-to" rows="4">Client Name&#10;Street Address&#10;City, Country&#10;client@example.com</textarea>
    </div>
  </div>

  <table class="inv-table">
    <thead><tr><th style="width:52%">Description</th><th>Qty</th><th>Price</th><th>Amount</th><th class="no-print"></th></tr></thead>
    <tbody id="inv-items"></tbody>
  </table>
  <div class="btn-row no-print"><button class="btn-ghost" type="button" onclick="invAdd()">+ Add line item</button></div>

  <div class="inv-totals">
    <div><span>Subtotal</span><b id="inv-sub">0.00</b></div>
    <div><span>Tax % <input type="number" id="inv-tax" value="0" min="0" step="any" class="mini" oninput="invCalc()"></span><b id="inv-taxamt">0.00</b></div>
    <div class="inv-total"><span>Total</span><b id="inv-total">0.00</b></div>
  </div>

  <div class="inv-notes">
    <label>Notes / payment details</label>
    <textarea id="inv-notes" rows="3">Payment instructions, bank or wallet details, thank-you note…</textarea>
  </div>
</div>
""",
"js": """
function invCalc(){
  var rows = document.querySelectorAll('#inv-items tr');
  var sub = 0;
  rows.forEach(function(tr){
    var qty = parseFloat(tr.querySelector('.inv-qty').value) || 0;
    var price = parseFloat(tr.querySelector('.inv-price').value) || 0;
    var amt = qty * price;
    tr.querySelector('.inv-amt').textContent = amt.toFixed(2);
    sub += amt;
  });
  var taxPct = parseFloat($id('inv-tax').value) || 0;
  var tax = sub * taxPct / 100;
  $id('inv-sub').textContent = sub.toFixed(2);
  $id('inv-taxamt').textContent = tax.toFixed(2);
  $id('inv-total').textContent = (sub + tax).toFixed(2);
}
function invDel(btn){
  var tr = btn.parentNode.parentNode;
  tr.parentNode.removeChild(tr);
  invCalc();
}
function invAdd(desc, qty, price){
  var tr = document.createElement('tr');
  tr.innerHTML =
    '<td><input class="inv-desc" value="' + (desc || '') + '" placeholder="Description of work"></td>' +
    '<td><input type="number" class="inv-qty" value="' + (qty !== undefined ? qty : 1) + '" min="0" step="any"></td>' +
    '<td><input type="number" class="inv-price" value="' + (price !== undefined ? price : 0) + '" min="0" step="any"></td>' +
    '<td class="inv-amt">0.00</td>' +
    '<td class="no-print"><button class="inv-x" type="button" onclick="invDel(this)">✕</button></td>';
  $id('inv-items').appendChild(tr);
  tr.addEventListener('input', invCalc);
  invCalc();
}
(function(){
  $id('inv-date').value = localISO(new Date());
  var due = new Date(Date.now() + 14 * 86400000);
  $id('inv-due').value = localISO(due);
  invAdd('Website design — landing page', 1, 250);
  invAdd('Monthly maintenance', 1, 50);
})();
""",
"faqs": [
("Is this invoice generator really free?", "Yes — no signup, no watermark, no page limit, and no “upgrade to download” trap. The invoice is produced entirely in your browser; nothing is uploaded to any server."),
("How do I save the invoice as a PDF?", "Click “Print / Save as PDF”, then in the browser's print dialog choose “Save as PDF” as the destination. This works in Chrome, Edge, Firefox and Safari on desktop and mobile."),
("Are invoices made in a browser legally valid?", "In most countries an invoice is valid as long as it contains the required details — parties, date, unique number, description, amounts and tax. Check your local requirements (some places require a tax ID or specific numbering) and keep a copy of every invoice you send.")
],
"about": [
"Freelancers, small shops and consultants lose real money to invoicing friction: clunky templates, sign-up walls, watermarks, and subscriptions for something that should take two minutes. This generator keeps it simple — type, print, done.",
"Because everything renders locally, there is no account to create, no client data leaking to a third party, and no waiting: the invoice is a real document you can save as PDF and email. That also makes it work offline. If you bill by the hour, the <a href=\"hours-calculator.html\">hours calculator</a> turns a week of start and finish times into the decimal hours these line items need."
]
},

# ---------------------------------------------------------------- CASE CONVERTER
{
"slug": "case-converter", "name": "Case Converter", "icon": "🔤", "cat": "Text", "popular": False,
"short": "UPPERCASE, lowercase, Title, Sentence, camelCase, snake_case and more.",
"title": "Case Converter — UPPERCASE, lowercase, Title Case & More",
"desc": "Free case converter: switch text between UPPERCASE, lowercase, Title Case, Sentence case, camelCase, snake_case, kebab-case and aLtErNaTiNg case instantly.",
"keywords": "case converter, uppercase to lowercase, title case, sentence case, camelcase converter, snake case, kebab case",
"lead": "Paste your text and switch it between eight different letter cases with one click — the classics plus the programmer favourites.",
"body": """
<div class="panel">
  <div class="field">
    <label for="cc-in">Your text</label>
    <textarea id="cc-in" rows="6" placeholder="Paste or type your text here…"></textarea>
  </div>
  <div class="btn-row">
    <button class="btn-ghost" type="button" onclick="conv('upper')">UPPERCASE</button>
    <button class="btn-ghost" type="button" onclick="conv('lower')">lowercase</button>
    <button class="btn-primary" type="button" onclick="conv('title')">Title Case</button>
    <button class="btn-ghost" type="button" onclick="conv('sentence')">Sentence case</button>
    <button class="btn-ghost" type="button" onclick="conv('camel')">camelCase</button>
    <button class="btn-ghost" type="button" onclick="conv('snake')">snake_case</button>
    <button class="btn-ghost" type="button" onclick="conv('kebab')">kebab-case</button>
    <button class="btn-ghost" type="button" onclick="conv('alt')">aLtErNaTiNg</button>
  </div>
  <div class="field" style="margin-top:18px">
    <label>Result</label>
    <div class="output-box" id="cc-out" style="min-height:52px">—</div>
  </div>
  <div class="btn-row"><button class="btn-ghost" type="button" onclick="copyVal('cc-out', this)">Copy result</button></div>
</div>
""",
"js": r"""
function cap(s){ return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase(); }
var CC = {
  upper: function(t){ return t.toUpperCase(); },
  lower: function(t){ return t.toLowerCase(); },
  title: function(t){ return t.replace(/\S+/g, function(w){ return cap(w); }); },
  sentence: function(t){
    return t.toLowerCase().replace(/(^\s*[a-z])|([.!?]\s+[a-z])/g, function(m){ return m.toUpperCase(); });
  },
  camel: function(t){
    var parts = t.split(/[^a-zA-Z0-9]+/).filter(Boolean);
    return parts.map(function(p, i){ return i === 0 ? p.toLowerCase() : cap(p); }).join('');
  },
  snake: function(t){ return t.trim().toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, ''); },
  kebab: function(t){ return t.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); },
  alt: function(t){
    var i = 0;
    return t.split('').map(function(ch){
      if(!/[a-zA-Z]/.test(ch)) return ch;
      var out = (i % 2 === 0) ? ch.toLowerCase() : ch.toUpperCase();
      i++;
      return out;
    }).join('');
  }
};
function conv(kind){
  var t = $id('cc-in').value;
  if(!t.trim()){ alert('Type or paste some text first.'); return; }
  $id('cc-out').textContent = CC[kind](t);
}
""",
"faqs": [
("What is the difference between Title Case and Sentence case?", "Title Case Capitalizes The First Letter Of Every Word, while Sentence case only capitalizes the first letter of the sentence. Headlines usually use title case; body text uses sentence case."),
("When would I use camelCase, snake_case or kebab-case?", "They are programming and file-naming conventions: camelCase for JavaScript variables, snake_case for Python variables and database columns, kebab-case for URLs, CSS classes and file names."),
("Does the converter change my original text?", "No — your input stays in the box exactly as you typed it. Each button just produces a converted copy in the result area, which you can copy with one click.")
],
"about": [
"Accidentally typed three paragraphs with Caps Lock on? Need a URL-safe version of a product name? Turning a headline into proper title case for a blog post? Case conversion is a small job that shows up constantly in writing, coding and marketing.",
"This tool covers the eight cases people actually need — including the developer trio camelCase, snake_case and kebab-case, which most simple converters skip. When what you need is a random string rather than a tidied one, the <a href=\"password-generator.html\">password generator</a> builds strong ones at any length you choose."
]
},

# ---------------------------------------------------------------- HOURS / TIME CARD
{
"slug": "hours-calculator", "name": "Hours Calculator", "icon": "⏱️", "cat": "Business", "popular": True,
"short": "Hours between two times, plus a weekly time-card total in decimal hours for payroll.",
"title": "Hours Calculator — Time Card & Hours Between Two Times",
"desc": "Free hours calculator: work out the hours between two times, subtract unpaid breaks, and total a full week as decimal hours ready for payroll. Runs 100% in your browser.",
"keywords": "hours calculator, time card calculator, work hours calculator, hours between two times, decimal hours, payroll hours, timesheet calculator",
"lead": "Add up working hours the way payroll does — get the duration between two times, then total a full week in both hours:minutes and the decimal hours that timesheets actually use.",
"body": """
<div class="panel">
  <h3 class="panel-title">Hours between two times</h3>
  <div class="grid-2">
    <div class="field"><label for="hc-start">Start time</label><input type="time" id="hc-start" value="09:00"></div>
    <div class="field"><label for="hc-end">End time</label><input type="time" id="hc-end" value="17:30"></div>
    <div class="field"><label for="hc-break">Unpaid break (minutes)</label><input type="number" id="hc-break" value="30" min="0" step="1"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runHours()">Calculate hours</button></div>
  <div class="results" id="hc-res">
    <div class="stat-grid">
      <div class="stat"><b id="hc-hm">—</b><span>Hours &amp; minutes</span></div>
      <div class="stat"><b id="hc-dec">—</b><span>Decimal hours</span></div>
      <div class="stat"><b id="hc-mins">—</b><span>Total minutes</span></div>
      <div class="stat"><b id="hc-overnight">—</b><span>Crosses midnight</span></div>
    </div>
    <p class="note">If the end time is earlier than the start time the shift is counted as crossing midnight — useful for night work. Your times never leave this page.</p>
  </div>
</div>

<div class="panel" style="margin-top:18px">
  <h3 class="panel-title">Weekly time card</h3>
  <ul class="sleep-list" id="hc-week"></ul>
  <div class="results show" id="hc-wres">
    <div class="stat-grid">
      <div class="stat"><b id="hc-wtotal">0.00</b><span>Decimal hours</span></div>
      <div class="stat"><b id="hc-whm">0 h 0 m</b><span>Hours &amp; minutes</span></div>
      <div class="stat"><b id="hc-wdays">0</b><span>Days worked</span></div>
    </div>
    <p class="note">Payroll bills in decimal hours: 7 h 30 m = 7.50 h. Multiply by your hourly rate to get gross pay before deductions.</p>
  </div>
</div>
""",
"js": """
var HC_DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
function hcParse(t){ if(!t) return null; var p = t.split(':'); return (parseInt(p[0], 10) * 60) + parseInt(p[1], 10); }
function hcHM(m){ m = Math.max(0, Math.round(m)); return Math.floor(m / 60) + ' h ' + (m % 60) + ' m'; }
function hcSpan(startV, endV, brk){
  var s = hcParse(startV), e = hcParse(endV);
  if(s === null || e === null) return null;
  var overnight = false;
  if(e < s){ e += 1440; overnight = true; }
  var mins = e - s - (brk || 0);
  if(mins < 0) mins = 0;
  return { mins: mins, overnight: overnight };
}
function hcBuild(){
  var host = $id('hc-week');
  var html = '';
  HC_DAYS.forEach(function(d){
    html += '<li><b style="font-size:.95rem;min-width:84px;color:var(--text)">' + d + '</b>' +
            '<input type="time" class="hc-in" aria-label="' + d + ' start time" style="width:134px">' +
            '<input type="time" class="hc-out" aria-label="' + d + ' end time" style="width:134px">' +
            '<input type="number" class="hc-brk mini" value="0" min="0" step="1" title="Unpaid break (minutes)" aria-label="' + d + ' unpaid break minutes">' +
            '<span class="hc-day" style="margin-left:auto">—</span></li>';
  });
  host.innerHTML = html;
  host.addEventListener('input', hcWeek);
}
function runHours(){
  var brk = parseFloat($id('hc-break').value) || 0;
  var r = hcSpan($id('hc-start').value, $id('hc-end').value, brk);
  if(!r){ alert('Please enter both a start time and an end time.'); return; }
  $id('hc-hm').textContent = hcHM(r.mins);
  $id('hc-dec').textContent = (r.mins / 60).toFixed(2);
  $id('hc-mins').textContent = fmt(r.mins, 0) + ' min';
  $id('hc-overnight').textContent = r.overnight ? 'Yes (+1 day)' : 'No';
  showRes('hc-res');
}
function hcWeek(){
  var total = 0, days = 0;
  [].slice.call(document.querySelectorAll('#hc-week li')).forEach(function(li){
    var r = hcSpan(li.querySelector('.hc-in').value, li.querySelector('.hc-out').value,
                  parseFloat(li.querySelector('.hc-brk').value) || 0);
    var cell = li.querySelector('.hc-day');
    if(r){ total += r.mins; if(r.mins > 0) days++; cell.textContent = hcHM(r.mins) + ' · ' + (r.mins / 60).toFixed(2); }
    else { cell.textContent = '—'; }
  });
  $id('hc-wtotal').textContent = (total / 60).toFixed(2);
  $id('hc-whm').textContent = hcHM(total);
  $id('hc-wdays').textContent = String(days);
}
hcBuild();
runHours();
""",
"faqs": [
("How do I convert hours and minutes into decimal hours?", "Divide the minutes by 60. So 7 hours 30 minutes is 7 + 30/60 = 7.50 decimal hours. Payroll systems use decimal hours because they multiply straight into an hourly rate — 7.50 × 20 = 150."),
("Why does the calculator say my night shift crosses midnight?", "If the end time is earlier than the start time, the only sensible reading is that the shift ran past midnight: 22:00 to 06:00 is 8 hours, not a negative number. This tool adds 24 hours automatically and tells you it did."),
("Does it deduct unpaid breaks automatically?", "Only the break you enter. Some jurisdictions require a rest break to be unpaid, others require it to be paid, so the tool never assumes. Enter your unpaid break in minutes and it is deducted from the day and from the weekly total.")
],
"about": [
"An hours calculator is one of the most searched tools on the web because timesheets are still filled in by hand. The arithmetic is deceptively awkward: clock time is base-60, payroll is base-10, and any shift that crosses midnight breaks a naive subtraction.",
"This tool handles all three problems at once. It returns the duration between two times with unpaid breaks deducted, converts that answer into decimal hours, and then totals a whole week the way a payroll system would — overnight shifts included. If the people you bill or schedule are in different countries, the <a href=\"time-zone-converter.html\">time zone converter</a> settles what “09:00” actually means on each side."
]
},

# ---------------------------------------------------------------- DISCOUNT
{
"slug": "discount-calculator", "name": "Discount Calculator", "icon": "🏷️", "cat": "Everyday", "popular": False,
"short": "Percent off, the price you pay and what you saved — plus two reverse modes.",
"title": "Discount Calculator — Percent Off & Sale Price",
"desc": "Free discount calculator: work out the sale price after a percent-off discount, how much money you save, the discount between two prices, and the original price from a sale price. Instant and private.",
"keywords": "discount calculator, percent off calculator, sale price calculator, how much do i save, 20 percent off, original price calculator, percentage discount",
"lead": "Three ways to do discount maths: take a percentage off a price, work out the discount between an original and a sale price, and go backwards from a sale price to the original.",
"body": """
<div class="panel">
  <h3 class="panel-title">1. Take a percentage off a price</h3>
  <div class="grid-2">
    <div class="field"><label for="d1-price">Original price</label><input type="number" id="d1-price" placeholder="e.g. 120" min="0" step="any"></div>
    <div class="field"><label for="d1-pct">Discount (%)</label><input type="number" id="d1-pct" value="20" min="0" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runD1()">Calculate sale price</button></div>
  <div class="results" id="d1-res">
    <div class="stat-grid">
      <div class="stat"><b id="d1-final">—</b><span>You pay</span></div>
      <div class="stat"><b id="d1-save">—</b><span>You save</span></div>
    </div>
    <p class="big-result" id="d1-out">—</p>
  </div>
</div>

<div class="panel" style="margin-top:18px">
  <h3 class="panel-title">2. What discount did I actually get?</h3>
  <div class="grid-2">
    <div class="field"><label for="d2-orig">Original price</label><input type="number" id="d2-orig" placeholder="e.g. 120" min="0" step="any"></div>
    <div class="field"><label for="d2-sale">Price you paid</label><input type="number" id="d2-sale" placeholder="e.g. 84" min="0" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runD2()">Calculate discount</button></div>
  <div class="results" id="d2-res">
    <div class="stat-grid">
      <div class="stat"><b id="d2-pct">—</b><span>Discount</span></div>
      <div class="stat"><b id="d2-save">—</b><span>You saved</span></div>
    </div>
    <p class="big-result" id="d2-out">—</p>
  </div>
</div>

<div class="panel" style="margin-top:18px">
  <h3 class="panel-title">3. What was the original price?</h3>
  <div class="grid-2">
    <div class="field"><label for="d3-sale">Sale price</label><input type="number" id="d3-sale" placeholder="e.g. 84" min="0" step="any"></div>
    <div class="field"><label for="d3-pct">Discount (%)</label><input type="number" id="d3-pct" value="30" min="0" max="99" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runD3()">Find original price</button></div>
  <div class="results" id="d3-res">
    <div class="stat-grid">
      <div class="stat"><b id="d3-orig">—</b><span>Original price</span></div>
      <div class="stat"><b id="d3-save">—</b><span>You saved</span></div>
    </div>
    <p class="big-result" id="d3-out">—</p>
  </div>
</div>
""",
"js": """
function runD1(){
  var p = readNum('d1-price', 'the original price'); if(p === null) return;
  var pct = readNum('d1-pct', 'the discount percentage'); if(pct === null) return;
  var save = p * pct / 100;
  $id('d1-final').textContent = fmt(p - save);
  $id('d1-save').textContent = fmt(save);
  $id('d1-out').textContent = fmt(p) + ' less ' + fmt(pct, 2) + '% = ' + fmt(p - save);
  showRes('d1-res');
}
function runD2(){
  var o = readNum('d2-orig', 'the original price'); if(o === null) return;
  var s = readNum('d2-sale', 'the price you paid'); if(s === null) return;
  if(o <= 0){ alert('The original price must be greater than zero.'); return; }
  var save = o - s, pct = save / o * 100;
  $id('d2-pct').textContent = fmt(pct, 2) + '%';
  $id('d2-save').textContent = fmt(save);
  $id('d2-out').textContent = fmt(s) + ' is ' + fmt(pct, 2) + '% off ' + fmt(o);
  showRes('d2-res');
}
function runD3(){
  var s = readNum('d3-sale', 'the sale price'); if(s === null) return;
  var pct = readNum('d3-pct', 'the discount percentage'); if(pct === null) return;
  if(pct >= 100){ alert('A discount of 100% or more leaves no original price to find.'); return; }
  var o = s / (1 - pct / 100);
  $id('d3-orig').textContent = fmt(o);
  $id('d3-save').textContent = fmt(o - s);
  $id('d3-out').textContent = 'A price of ' + fmt(s) + ' after ' + fmt(pct, 2) + '% off started at ' + fmt(o);
  showRes('d3-res');
}
""",
"faqs": [
("How do I work out 20% off?", "Multiply the price by 0.20 to get the saving, then subtract it — or multiply by 0.80 to get the final price in one step. An item priced 120 with 20% off costs 96 and saves 24."),
("Is 20% off and then another 20% off the same as 40% off?", "No, and this is the trick that shop promotions rely on. Successive discounts multiply: 0.80 × 0.80 = 0.64, so the real total discount is 36%, not 40%. Run the first result back through the calculator to check any 'extra 20%' offer."),
("Why does the reverse mode need a discount below 100%?", "Because the original price is found by dividing by (1 − rate). At exactly 100% off that divisor is zero, so the original price is undefined; above 100% the formula returns a negative price. Real discounts are always below 100%.")
],
"about": [
"Discount maths is the most common piece of mental arithmetic people get wrong, and it is not the shopper's fault — the two-step version (find the saving, then subtract) is easy to muddle under time pressure, and 'extra 20% off sale prices' is genuinely not the same as 40%.",
"This calculator covers all three questions that actually come up: the sale price from a percentage, the percentage from two prices, and the original price when all you can see is the sale ticket. Results are plain numbers, so they work in any currency."
]
},

# ---------------------------------------------------------------- SALES TAX / VAT
{
"slug": "sales-tax-calculator", "name": "Sales Tax Calculator", "icon": "🧮", "cat": "Finance", "popular": False,
"short": "Add sales tax, VAT or GST to a price — or strip it back out of a tax-inclusive total.",
"title": "Sales Tax Calculator — Add or Reverse Tax (VAT & GST)",
"desc": "Free sales tax calculator: add sales tax, VAT or GST to a net price, or reverse a tax-inclusive total to find the pre-tax amount and the tax you paid. Any rate, any currency.",
"keywords": "sales tax calculator, reverse sales tax calculator, add tax to price, remove tax from total, vat calculator, gst calculator, tax inclusive price, pre-tax amount",
"lead": "Both directions, because both come up: add a tax rate to a net price, or pull the tax back out of a gross total to see what you actually paid for the goods.",
"body": """
<div class="panel">
  <h3 class="panel-title">Add tax to a price</h3>
  <div class="grid-2">
    <div class="field"><label for="st1-net">Price before tax</label><input type="number" id="st1-net" placeholder="e.g. 250" min="0" step="any"></div>
    <div class="field"><label for="st1-rate">Tax rate (%)</label><input type="number" id="st1-rate" value="8.25" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runST1()">Add tax</button></div>
  <div class="results" id="st1-res">
    <div class="stat-grid">
      <div class="stat"><b id="st1-tax">—</b><span>Tax</span></div>
      <div class="stat"><b id="st1-gross">—</b><span>Total with tax</span></div>
    </div>
    <p class="big-result" id="st1-out">—</p>
  </div>
</div>

<div class="panel" style="margin-top:18px">
  <h3 class="panel-title">Remove tax from a total (reverse)</h3>
  <div class="grid-2">
    <div class="field"><label for="st2-gross">Total including tax</label><input type="number" id="st2-gross" placeholder="e.g. 270.63" min="0" step="any"></div>
    <div class="field"><label for="st2-rate">Tax rate (%)</label><input type="number" id="st2-rate" value="8.25" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runST2()">Remove tax</button></div>
  <div class="results" id="st2-res">
    <div class="stat-grid">
      <div class="stat"><b id="st2-net">—</b><span>Price before tax</span></div>
      <div class="stat"><b id="st2-tax">—</b><span>Tax included</span></div>
    </div>
    <p class="big-result" id="st2-out">—</p>
    <p class="note">Reversing tax is not the same as subtracting the percentage — see the first FAQ for why.</p>
  </div>
</div>
""",
"js": """
function runST1(){
  var net = readNum('st1-net', 'the price before tax'); if(net === null) return;
  var rate = readNum('st1-rate', 'the tax rate'); if(rate === null) return;
  var tax = net * rate / 100;
  $id('st1-tax').textContent = fmt(tax);
  $id('st1-gross').textContent = fmt(net + tax);
  $id('st1-out').textContent = fmt(net) + ' + ' + fmt(rate, 3) + '% tax = ' + fmt(net + tax);
  showRes('st1-res');
}
function runST2(){
  var gross = readNum('st2-gross', 'the tax-inclusive total'); if(gross === null) return;
  var rate = readNum('st2-rate', 'the tax rate'); if(rate === null) return;
  if(rate <= -100){ alert('That tax rate is not a valid number.'); return; }
  var net = gross / (1 + rate / 100), tax = gross - net;
  $id('st2-net').textContent = fmt(net);
  $id('st2-tax').textContent = fmt(tax);
  $id('st2-out').textContent = fmt(gross) + ' including ' + fmt(rate, 3) + '% tax = ' + fmt(net) + ' before tax';
  showRes('st2-res');
}
""",
"faqs": [
("How do I remove sales tax from a total?", "Divide the total by (1 + rate/100) — do not subtract the percentage. At 8.25%, a 270.63 total is 270.63 / 1.0825 = 250.00 before tax. Subtracting 8.25% from the total instead would give 248.30, which is wrong: the tax was charged on the pre-tax amount, not on the total."),
("What is the difference between sales tax, VAT and GST?", "They are all consumption taxes collected at the point of sale. US sales tax is normally added on top of the displayed price, while VAT (Europe, UK) and GST (Australia, Canada, India, Singapore) are usually already included in the shelf price — which is exactly why the reverse mode matters more outside the US."),
("Can it handle compound tax or two rates at once?", "It handles one rate at a time. For compound tax, where a second tax is charged on top of the first, run the 'add tax' step and then feed the resulting total back in as the pre-tax price for the second rate.")
],
"about": [
"Sales tax, VAT and GST are all consumption taxes, and the single most common mistake is working backwards. People subtract the rate from the tax-inclusive total, which always understates the tax and overstates the pre-tax price, because the tax was charged on the smaller pre-tax amount rather than on the total.",
"This calculator does both directions properly: forward to add tax to a net price, and reverse to divide it back out of a gross total. Rates are free-form, so it works for a US state sales tax, UK VAT, Australian GST, or any other percentage."
]
},

# ---------------------------------------------------------------- GPA
{
"slug": "gpa-calculator", "name": "GPA Calculator", "icon": "🎓", "cat": "Everyday", "popular": True,
"short": "Credit-weighted GPA from your course grades and credit hours, on the 4.0 scale.",
"title": "GPA Calculator — Weighted Grade Point Average (4.0 Scale)",
"desc": "Free GPA calculator: enter each course's grade and credit hours for your weighted GPA on the 4.0 scale, then combine it with your previous record for a cumulative GPA.",
"keywords": "gpa calculator, weighted gpa, grade point average, cumulative gpa calculator, college gpa, 4.0 scale gpa, high school gpa",
"lead": "Enter your courses, grades and credit hours to get the credit-weighted GPA that actually goes on a transcript — then fold it into your cumulative GPA.",
"body": """
<div class="panel">
  <h3 class="panel-title">This term's courses</h3>
  <ul class="sleep-list" id="gpa-rows"></ul>
  <div class="btn-row">
    <button class="btn-primary" type="button" onclick="runGPA()">Calculate GPA</button>
    <button class="btn-ghost" type="button" onclick="gpaAddRow()">+ Add course</button>
    <button class="btn-ghost" type="button" onclick="gpaClear()">Clear all</button>
  </div>
  <div class="results" id="gpa-res">
    <div class="stat-grid">
      <div class="stat"><b id="gpa-val">—</b><span>Term GPA</span></div>
      <div class="stat"><b id="gpa-credits">—</b><span>Credit hours</span></div>
      <div class="stat"><b id="gpa-points">—</b><span>Quality points</span></div>
    </div>
    <p class="note">GPA is credit-weighted, not a plain average of your grades: a 3-credit course counts three times as much as a 1-credit one. Only graded courses count — pass/fail, credit/no-credit and withdrawn courses carry no grade points.</p>
  </div>
</div>

<div class="panel" style="margin-top:18px">
  <h3 class="panel-title">Cumulative GPA</h3>
  <div class="grid-2">
    <div class="field"><label for="cg-gpa">Current cumulative GPA</label><input type="number" id="cg-gpa" value="3.2" min="0" max="5" step="any"></div>
    <div class="field"><label for="cg-cr">Credits earned so far</label><input type="number" id="cg-cr" value="60" min="0" step="any"></div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runCGPA()">Combine with this term</button></div>
  <div class="results" id="cg-res">
    <div class="stat-grid">
      <div class="stat"><b id="cg-new">—</b><span>New cumulative GPA</span></div>
      <div class="stat"><b id="cg-total">—</b><span>Total credits</span></div>
      <div class="stat"><b id="cg-change">—</b><span>Change</span></div>
    </div>
    <p class="note">This uses the term result from above, so calculate the term first. Old grades never leave the average — which is why one weak semester is hard to undo late in a degree, and why adding credits is usually faster than chasing perfect grades.</p>
  </div>
</div>
""",
"js": """
var GPA_GRADES = [
  ['A+', 4.0], ['A', 4.0], ['A-', 3.7],
  ['B+', 3.3], ['B', 3.0], ['B-', 2.7],
  ['C+', 2.3], ['C', 2.0], ['C-', 1.7],
  ['D+', 1.3], ['D', 1.0], ['D-', 0.7],
  ['F', 0.0]
];
function gpaOpts(sel){
  return GPA_GRADES.map(function(g){
    return '<option value="' + g[1] + '"' + (g[0] === sel ? ' selected' : '') + '>' + g[0] + '</option>';
  }).join('');
}
function gpaAddRow(name, grade, credits){
  var li = document.createElement('li');
  li.innerHTML = '<input type="text" class="gpa-name" value="' + (name || '') +
    '" placeholder="Course name" aria-label="Course name" style="flex:1 1 130px;min-width:120px">' +
    '<select class="gpa-grade" aria-label="Grade">' + gpaOpts(grade === undefined ? 'A' : grade) + '</select>' +
    '<input type="number" class="gpa-cr mini" value="' + (credits === undefined ? 3 : credits) +
    '" min="0" step="any" aria-label="Credit hours" title="Credit hours">';
  $id('gpa-rows').appendChild(li);
}
function gpaClear(){
  $id('gpa-rows').innerHTML = '';
  gpaAddRow('', 'A', 3);
}
function gpaTotals(){
  var credits = 0, points = 0, n = 0;
  [].slice.call(document.querySelectorAll('#gpa-rows li')).forEach(function(li){
    var g = parseFloat(li.querySelector('.gpa-grade').value);
    var c = parseFloat(li.querySelector('.gpa-cr').value);
    if(isNaN(g) || isNaN(c) || c <= 0) return;
    credits += c; points += g * c; n++;
  });
  return { credits: credits, points: points, n: n, gpa: credits > 0 ? points / credits : 0 };
}
function runGPA(){
  var t = gpaTotals();
  if(t.n === 0){ alert('Enter at least one course with credit hours greater than zero.'); return; }
  $id('gpa-val').textContent = t.gpa.toFixed(2);
  $id('gpa-credits').textContent = fmt(t.credits, 2);
  $id('gpa-points').textContent = fmt(t.points, 2);
  showRes('gpa-res');
}
function runCGPA(){
  var t = gpaTotals();
  if(t.n === 0){ alert('Add your courses above first — this figure uses the term result.'); return; }
  var prev = readNum('cg-gpa', 'your current cumulative GPA'); if(prev === null) return;
  var prevCr = readNum('cg-cr', 'credits earned so far'); if(prevCr === null) return;
  if(prev < 0 || prevCr < 0){ alert('GPA and credit hours cannot be negative.'); return; }
  var totalCr = prevCr + t.credits;
  if(totalCr <= 0){ alert('Total credit hours must be greater than zero.'); return; }
  var combined = ((prev * prevCr) + t.points) / totalCr;
  var diff = combined - prev;
  $id('cg-new').textContent = combined.toFixed(2);
  $id('cg-total').textContent = fmt(totalCr, 2);
  $id('cg-change').textContent = (diff >= 0 ? '+' : '') + diff.toFixed(2);
  $id('cg-change').style.color = diff >= 0 ? '#4ade80' : '#f87171';
  showRes('cg-res');
}
gpaAddRow('Course 1', 'A', 3);
gpaAddRow('Course 2', 'B', 3);
gpaAddRow('Course 3', 'A-', 3);
gpaAddRow('Course 4', 'B+', 3);
runGPA();
""",
"faqs": [
("How is GPA calculated?", "Multiply each course's grade points by its credit hours, add all of those products together, then divide by the total credit hours. That sum of products is the 'quality points'. A 3-credit A (4.0) contributes 12 quality points and a 1-credit A contributes 4 — so credit hours, not the number of courses, decide the result."),
("What is the difference between weighted and unweighted GPA?", "An unweighted GPA puts every course on the same 4.0 scale. A weighted GPA adds extra points for honours, AP or IB classes, often out to 5.0, so a hard course can lift the number above 4.0. This calculator produces the unweighted, credit-weighted figure that most universities report; if your school weights honours classes, enter the adjusted grade points your registrar uses instead."),
("Does a pass/fail course affect my GPA?", "No. Pass/fail, credit/no-credit and withdrawn courses carry no grade points, so leave them out entirely. Entering them as an F or a 0 would drag the average down incorrectly."),
("How much can one bad semester lower my cumulative GPA?", "Less than you fear, as long as you keep earning credits. The cumulative average is credit-weighted, so 60 existing credits plus a weak 12-credit term moves the number only slightly. The same maths means recovery is slow and steady rather than instant.")
],
"about": [
"A grade point average is a credit-weighted mean of your grades. The weighting is the whole point: universities use it to stop a single hard 4-credit course from counting the same as a light 1-credit elective, and employers and graduate schools read it as a single comparable number across very different transcripts.",
"Working out the term figure by hand is where most people go wrong, because it is not an average of the letter grades you can see. You have to convert each grade to grade points, multiply by the credit hours, total both, and divide. That is exactly what this calculator does, and it then folds the result into your existing cumulative GPA — the number that actually appears on a transcript."
]
},

# ---------------------------------------------------------------- CALORIE / BMR / TDEE
{
"slug": "calorie-calculator", "name": "Calorie Calculator", "icon": "🔥", "cat": "Health", "popular": True,
"short": "Your BMR and daily calorie needs (TDEE), plus targets for losing or gaining weight.",
"title": "Calorie Calculator — BMR & Daily Calorie Needs (TDEE)",
"desc": "Free calorie calculator using the Mifflin-St Jeor equation. Get your BMR, your daily maintenance calories (TDEE) and safe targets for losing or gaining weight, in metric or imperial units.",
"keywords": "calorie calculator, bmr calculator, tdee calculator, daily calorie needs, maintenance calories, weight loss calories, mifflin st jeor",
"lead": "Work out how many calories you actually burn in a day — your BMR and your TDEE — and what that means for losing or gaining weight.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="cal-units">Units</label>
      <select id="cal-units" onchange="calUnits()">
        <option value="metric">Metric (cm, kg)</option>
        <option value="imperial">Imperial (ft/in, lb)</option>
      </select>
    </div>
    <div class="field"><label for="cal-sex">Sex</label>
      <select id="cal-sex">
        <option value="male">Male</option>
        <option value="female">Female</option>
      </select>
    </div>
  </div>
  <div class="grid-2" id="cal-metric" style="margin-top:14px">
    <div class="field"><label for="cal-h">Height (cm)</label><input type="number" id="cal-h" value="180" min="0" step="any"></div>
    <div class="field"><label for="cal-w">Weight (kg)</label><input type="number" id="cal-w" value="80" min="0" step="any"></div>
    <div class="field"><label for="cal-age">Age (years)</label><input type="number" id="cal-age" value="30" min="0" step="1"></div>
  </div>
  <div class="grid-2" id="cal-imperial" style="display:none;margin-top:14px">
    <div class="field"><label for="cal-ft">Height (feet)</label><input type="number" id="cal-ft" value="5" min="0" step="any"></div>
    <div class="field"><label for="cal-in">Height (inches)</label><input type="number" id="cal-in" value="11" min="0" step="any"></div>
    <div class="field"><label for="cal-lb">Weight (pounds)</label><input type="number" id="cal-lb" value="176" min="0" step="any"></div>
    <div class="field"><label for="cal-age-i">Age (years)</label><input type="number" id="cal-age-i" value="30" min="0" step="1"></div>
  </div>
  <div class="grid-2" style="margin-top:14px">
    <div class="field"><label for="cal-act">Activity level</label>
      <select id="cal-act">
        <option value="1.2">Sedentary — little or no exercise</option>
        <option value="1.375">Lightly active — 1–3 days a week</option>
        <option value="1.55" selected>Moderately active — 3–5 days a week</option>
        <option value="1.725">Very active — 6–7 days a week</option>
        <option value="1.9">Extra active — physical job or twice a day</option>
      </select>
    </div>
  </div>
  <div class="btn-row"><button class="btn-primary" type="button" onclick="runCal()">Calculate calories</button></div>
  <div class="results" id="cal-res">
    <div class="stat-grid">
      <div class="stat"><b id="cal-bmr">—</b><span>BMR (at rest)</span></div>
      <div class="stat"><b id="cal-tdee">—</b><span>Maintenance</span></div>
      <div class="stat"><b id="cal-cut">—</b><span>Lose ~0.5 kg/week</span></div>
      <div class="stat"><b id="cal-bulk">—</b><span>Gain ~0.25 kg/week</span></div>
    </div>
    <p class="note">BMR is what your body burns at complete rest. Maintenance (TDEE) multiplies that by how active you are. A deficit of about 500 kcal a day is the usual target for roughly 0.5 kg (1 lb) of fat loss a week — but do not eat below your BMR, and speak to a doctor before aggressive dieting.</p>
  </div>
</div>
""",
"js": """
function calUnits(){
  var imp = $id('cal-units').value === 'imperial';
  $id('cal-metric').style.display = imp ? 'none' : '';
  $id('cal-imperial').style.display = imp ? '' : 'none';
}
function runCal(){
  var unit = $id('cal-units').value;
  var male = $id('cal-sex').value === 'male';
  var hcm, wkg, age;
  if(unit === 'metric'){
    hcm = readNum('cal-h', 'height'); wkg = readNum('cal-w', 'weight');
    age = readNum('cal-age', 'age');
  } else {
    var ft = readNum('cal-ft', 'feet'); var inch = parseFloat($id('cal-in').value) || 0;
    wkg = readNum('cal-lb', 'weight'); age = readNum('cal-age-i', 'age');
    if(ft === null) return;
    hcm = (ft * 12 + inch) * 2.54;
    if(wkg !== null) wkg = wkg * 0.45359237;
  }
  if(hcm === null || wkg === null || age === null) return;
  if(hcm <= 0 || wkg <= 0 || age <= 0){ alert('Height, weight and age must all be positive numbers.'); return; }
  if(age < 15 || age > 100){ alert('This formula is validated for adults. Use a paediatric calculator for under-15s.'); return; }
  /* Mifflin-St Jeor: the most accurate simple BMR equation for the general population. */
  var bmr = (10 * wkg) + (6.25 * hcm) - (5 * age) + (male ? 5 : -161);
  var factor = parseFloat($id('cal-act').value);
  var tdee = bmr * factor;
  var cut = tdee - 500;
  var bulk = tdee + 250;
  /* never present a target below the floor of 1,200 kcal */
  if(cut < 1200) cut = 1200;
  $id('cal-bmr').textContent = fmt(bmr, 0) + ' kcal';
  $id('cal-tdee').textContent = fmt(tdee, 0) + ' kcal';
  $id('cal-cut').textContent = fmt(cut, 0) + ' kcal';
  $id('cal-bulk').textContent = fmt(bulk, 0) + ' kcal';
  showRes('cal-res');
}
runCal();
""",
"faqs": [
("What is the difference between BMR and TDEE?", "BMR (basal metabolic rate) is the energy you would burn lying still all day — it covers breathing, circulation, temperature control and cell repair. TDEE (total daily energy expenditure) is BMR multiplied by an activity factor, and it is the number that predicts whether you gain, lose or hold weight. If you eat roughly your TDEE, your weight stays put."),
("How many calories should I eat to lose weight?", "A deficit of about 500 kcal a day below your maintenance level is the standard target, and it produces roughly 0.5 kg (1 lb) of loss a week — which is also what this calculator's weight-loss figure shows. Larger deficits lose weight faster but cost muscle and are harder to sustain."),
("How accurate is the Mifflin-St Jeor equation?", "It is the equation most dietitians use, and studies find it lands within about 10% of measured resting energy expenditure for most adults. That still means a few hundred calories either way. Treat the result as a starting point, watch your weight over two to three weeks, and adjust."),
("Is it safe to eat only 1,200 calories a day?", "1,200 kcal is generally treated as the floor below which you should not go without medical supervision, because it becomes very hard to hit your protein, vitamin and mineral needs. This calculator will not show a weight-loss target below that level.")
],
"about": [
"Every calorie target starts with one number: how much energy your body uses in a day. That figure has two parts. The first is your basal metabolic rate, the cost of simply staying alive, which depends mostly on body size, sex and age. The second is everything you do on top of that — walking, working, training — expressed as a multiplier on the first.",
"Multiplying the two gives your total daily energy expenditure, or maintenance calories. Eat around that number and your weight holds steady; eat below it and you lose; eat above it and you gain. The arithmetic here uses the Mifflin-St Jeor equation, the formula most clinical dietitians default to because it is more accurate than the older Harris-Benedict equation across a wide range of body types. Both metric and imperial inputs are accepted — for anything else that needs converting between the two systems, the <a href=\"unit-converter.html\">unit converter</a> covers length, weight, volume and temperature."
]
},

# ---------------------------------------------------------------- TIME ZONE CONVERTER
{
"slug": "time-zone-converter", "name": "Time Zone Converter", "icon": "🌍", "cat": "Utilities", "popular": False,
"short": "Convert a date and time between any two time zones, with daylight saving handled.",
"title": "Time Zone Converter — Convert Time Between Any Two Zones",
"desc": "Free time zone converter: turn a date and time in one city into the local time in another, with daylight saving handled automatically and the day shift shown clearly.",
"keywords": "time zone converter, world clock, time difference calculator, meeting time converter, daylight saving converter, utc converter",
"lead": "Convert a meeting, a flight or a call between any two time zones — with daylight saving applied automatically and the day shift spelled out.",
"body": """
<div class="panel">
  <div class="grid-2">
    <div class="field"><label for="tz-date">Date</label><input type="date" id="tz-date"></div>
    <div class="field"><label for="tz-time">Time</label><input type="time" id="tz-time" value="12:00"></div>
  </div>
  <div class="grid-2" style="margin-top:14px">
    <div class="field"><label for="tz-from">From</label><select id="tz-from"></select></div>
    <div class="field"><label for="tz-to">To</label><select id="tz-to"></select></div>
  </div>
  <div class="btn-row">
    <button class="btn-primary" type="button" onclick="runTZ()">Convert</button>
    <button class="btn-ghost" type="button" onclick="tzSwap()">⇄ Swap zones</button>
    <button class="btn-ghost" type="button" onclick="tzNow()">Use current time</button>
  </div>
  <div class="results" id="tz-res">
    <div class="stat-grid">
      <div class="stat"><b id="tz-out">—</b><span>Local time at destination</span></div>
      <div class="stat"><b id="tz-day">—</b><span>Day shift</span></div>
      <div class="stat"><b id="tz-diff">—</b><span>Time difference</span></div>
    </div>
    <p class="note" id="tz-detail">—</p>
  </div>
</div>

<div class="panel" style="margin-top:18px">
  <h3 class="panel-title">The same moment around the world</h3>
  <table class="simple" id="tz-table">
    <thead><tr><th>City</th><th>Local time</th><th>Day</th></tr></thead>
    <tbody></tbody>
  </table>
  <p class="note">Daylight saving is applied from your browser's own time zone database, so summer and winter dates are handled correctly — no manual adjustment needed.</p>
</div>
""",
"js": """
var TZ_LIST = [
  ['UTC', 'UTC'],
  ['America/Los_Angeles', 'Los Angeles'],
  ['America/Denver', 'Denver'],
  ['America/Chicago', 'Chicago'],
  ['America/New_York', 'New York'],
  ['America/Sao_Paulo', 'São Paulo'],
  ['Europe/London', 'London'],
  ['Europe/Paris', 'Paris'],
  ['Europe/Berlin', 'Berlin'],
  ['Africa/Lagos', 'Lagos'],
  ['Africa/Cairo', 'Cairo'],
  ['Europe/Moscow', 'Moscow'],
  ['Asia/Dubai', 'Dubai'],
  ['Asia/Karachi', 'Karachi'],
  ['Asia/Kolkata', 'Kolkata'],
  ['Asia/Dhaka', 'Dhaka'],
  ['Asia/Bangkok', 'Bangkok'],
  ['Asia/Shanghai', 'Shanghai'],
  ['Asia/Singapore', 'Singapore'],
  ['Asia/Tokyo', 'Tokyo'],
  ['Australia/Sydney', 'Sydney'],
  ['Pacific/Auckland', 'Auckland']
];
function tzPad(n){ return (n < 10 ? '0' : '') + n; }
function tzParts(date, tz){
  var dtf = new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit' });
  var p = {};
  dtf.formatToParts(date).forEach(function(x){ if(x.type !== 'literal') p[x.type] = x.value; });
  return p;
}
function tzOffsetMin(date, tz){
  var p = tzParts(date, tz);
  var asUTC = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second);
  return Math.round((asUTC - date.getTime()) / 60000);
}
/* Build the exact instant that reads as this wall-clock time in tz. The second pass
   corrects the offset across a daylight-saving boundary. */
function tzInstant(y, mo, d, h, mi, tz){
  var guess = Date.UTC(y, mo - 1, d, h, mi, 0);
  var off = tzOffsetMin(new Date(guess), tz);
  var ts = guess - off * 60000;
  off = tzOffsetMin(new Date(ts), tz);
  return new Date(guess - off * 60000);
}
function tzTime(date, tz){
  var p = tzParts(date, tz);
  return p.hour + ':' + p.minute;
}
function tzDateLabel(date, tz){
  return new Intl.DateTimeFormat('en-GB', { timeZone: tz, weekday: 'short',
    day: 'numeric', month: 'short', year: 'numeric' }).format(date);
}
function tzDayDiff(date, fromTz, toTz){
  var a = tzParts(date, fromTz), b = tzParts(date, toTz);
  return Math.round((Date.UTC(+b.year, +b.month - 1, +b.day) - Date.UTC(+a.year, +a.month - 1, +a.day)) / 86400000);
}
function tzOffLabel(min){
  var sign = min < 0 ? '-' : '+', a = Math.abs(min);
  return 'UTC' + sign + tzPad(Math.floor(a / 60)) + ':' + tzPad(a % 60);
}
function tzName(code){
  for(var i = 0; i < TZ_LIST.length; i++){ if(TZ_LIST[i][0] === code) return TZ_LIST[i][1]; }
  return code;
}
function tzFillSelects(){
  var opts = TZ_LIST.map(function(z){ return '<option value="' + z[0] + '">' + z[1] + '</option>'; }).join('');
  $id('tz-from').innerHTML = opts;
  $id('tz-to').innerHTML = opts;
  $id('tz-from').value = 'America/New_York';
  $id('tz-to').value = 'Europe/London';
}
function tzSwap(){
  var a = $id('tz-from').value;
  $id('tz-from').value = $id('tz-to').value;
  $id('tz-to').value = a;
  runTZ();
}
function tzNow(){
  var now = new Date();
  $id('tz-date').value = localISO(now);
  $id('tz-time').value = tzPad(now.getHours()) + ':' + tzPad(now.getMinutes());
  runTZ();
}
function runTZ(){
  var dv = $id('tz-date').value, tv = $id('tz-time').value;
  if(!dv || !tv){ alert('Please choose both a date and a time.'); return; }
  var from = $id('tz-from').value, to = $id('tz-to').value;
  var dp = dv.split('-'), tp = tv.split(':');
  var instant = tzInstant(+dp[0], +dp[1], +dp[2], +tp[0], +tp[1], from);
  var shift = tzDayDiff(instant, from, to);
  var diff = tzOffsetMin(instant, to) - tzOffsetMin(instant, from);
  var hours = Math.abs(diff) / 60;
  var hoursTxt = (hours % 1 === 0) ? String(hours) : hours.toFixed(1).replace('.0', '');
  $id('tz-out').textContent = tzTime(instant, to);
  $id('tz-day').textContent = shift === 0 ? 'Same day' : (shift > 0 ? '+' + shift + ' day' : shift + ' day');
  $id('tz-diff').textContent = hoursTxt + ' h';
  $id('tz-detail').textContent = tzDateLabel(instant, from) + ' at ' + tzTime(instant, from) + ' in ' +
    tzName(from) + ' (' + tzOffLabel(tzOffsetMin(instant, from)) + ') is ' +
    tzDateLabel(instant, to) + ' at ' + tzTime(instant, to) + ' in ' + tzName(to) +
    ' (' + tzOffLabel(tzOffsetMin(instant, to)) + ').';
  var body = '';
  TZ_LIST.forEach(function(z){
    var s = tzDayDiff(instant, from, z[0]);
    var mark = s === 0 ? 'same day' : (s > 0 ? '+' + s + ' day' : s + ' day');
    body += '<tr><td>' + z[1] + '</td><td>' + tzTime(instant, z[0]) + '</td><td>' + mark + '</td></tr>';
  });
  $id('tz-table').querySelector('tbody').innerHTML = body;
  showRes('tz-res');
}
tzFillSelects();
$id('tz-date').value = localISO(new Date());
runTZ();
""",
"faqs": [
("How do I convert a time from one time zone to another?", "Find the offset of each zone from UTC at that exact date, then shift the time by the difference. A 12:00 meeting in New York on 15 January is 17:00 in London, because New York is UTC-5 in winter and London is UTC+0. This converter does that arithmetic for you and also shows the day shift when the two zones land on different calendar dates."),
("Does the converter handle daylight saving time?", "Yes, automatically. Offsets are read from your browser's own time zone database for the specific date you enter, so a July date and a January date give different answers for the same pair of cities. That is also why you should always enter a date rather than assuming a fixed number of hours' difference."),
("Why is the time difference sometimes not a whole number of hours?", "Because several zones use a half-hour or three-quarter-hour offset. India is UTC+5:30, Nepal is UTC+5:45, and parts of Australia are UTC+9:30. The converter shows fractional differences as decimals, so India against London reads as 5.5 h in winter."),
("What is UTC and why use it?", "UTC (Coordinated Universal Time) is the reference clock the whole world's time zones are defined against — a zone is described by how far it is ahead of or behind UTC. Aviation, shipping, servers and international contracts all use it precisely because it has no daylight saving and never shifts.")
],
"about": [
"Converting time between zones looks like simple subtraction and is almost never that. The gap between two cities is not fixed: it depends on the date, because each country switches to and from daylight saving on its own schedule, and a handful of zones sit on half-hour or quarter-hour offsets. A 12:00 call between New York and London is a five-hour difference in January and a five-hour difference in July, but only because the two countries change their clocks within a week of each other — shift the date to late March and the answer changes.",
"That is why a fixed 'hours apart' table is unreliable and why this converter asks for a date. It reads the real offset for both zones on the exact day you specify, from the time zone database your own browser ships with, so the daylight saving transition is handled without you thinking about it."
]
},
]
