// Shared listing parser and valuation model. Used by the background worker and the dashboard.
(function (g) {
'use strict';
var NOW_YEAR = new Date().getFullYear();
var DEFAULTS = { prep: 250, fees: 60, disc: 7, thresh: 12, notify: true, minProfit: 300 };

var MAKES = [
  ['alfa romeo','Alfa Romeo'],['aston martin','Aston Martin'],['land rover','Land Rover'],['range rover','Land Rover'],['mercedes-benz','Mercedes-Benz'],['mercedes benz','Mercedes-Benz'],['mercedes','Mercedes-Benz'],['merc','Mercedes-Benz'],
  ['abarth','Abarth'],['audi','Audi'],['bentley','Bentley'],['bmw','BMW'],['chevrolet','Chevrolet'],['citroen','Citroen'],['citroën','Citroen'],['cupra','Cupra'],['dacia','Dacia'],['ds','DS'],['fiat','Fiat'],['ford','Ford'],
  ['honda','Honda'],['hyundai','Hyundai'],['jaguar','Jaguar'],['jeep','Jeep'],['kia','Kia'],['lexus','Lexus'],['lotus','Lotus'],['mazda','Mazda'],['mg','MG'],['mini','Mini'],['mitsubishi','Mitsubishi'],
  ['nissan','Nissan'],['peugeot','Peugeot'],['polestar','Polestar'],['porsche','Porsche'],['renault','Renault'],['saab','Saab'],['seat','SEAT'],['skoda','Skoda'],['škoda','Skoda'],['smart','Smart'],['ssangyong','SsangYong'],
  ['subaru','Subaru'],['suzuki','Suzuki'],['tesla','Tesla'],['toyota','Toyota'],['vauxhall','Vauxhall'],['volkswagen','Volkswagen'],['vw','Volkswagen'],['volvo','Volvo']
];
var MULTI = ['range rover sport','range rover evoque','range rover velar','discovery sport','grand c-max','c-max','s-max','b-max','golf plus','grand scenic','grand picasso','c4 picasso','grandland x','crossland x','mokka x','tiguan allspace','model 3','model y','model s','cx-5','cx-3','mx-5','cr-v','hr-v'];
var SKIP = /^(\d(\.\d)?l?|\d{3,4}cc|tdi|tsi|tfsi|crdi|dci|hdi|vti|tdci|ecoboost|hybrid|diesel|petrol|auto|manual|\d+dr|\d-door|\d+v|turbo|new|used|for|sale|the|a|in|uk|cheap|reg|plate|\(?\d{2}\)?)$/i;
function tcase(s) { return s.replace(/(^|[\s-])([a-z])/g, function (m, a, b) { return a + b.toUpperCase(); }); }
function num(s) { return parseFloat(String(s).replace(/,/g, '')); }

function findMake(t) {
  var low = ' ' + String(t).toLowerCase().replace(/[^a-z0-9šë!\-\s]/g, ' ') + ' ';
  var best = null;
  MAKES.forEach(function (m) {
    var i = low.indexOf(' ' + m[0] + ' ');
    if (i >= 0 && (!best || i < best.i || (i === best.i && m[0].length > best.k.length))) best = { i: i, k: m[0], name: m[1] };
  });
  if (!best) return null;
  best.rest = low.slice(best.i + best.k.length + 2).trim();
  if (best.k === 'range rover') best.rest = 'range rover ' + best.rest;
  return best;
}
function findModel(mk) {
  var rest = mk.rest, name = mk.name;
  for (var j = 0; j < MULTI.length; j++) if (rest.indexOf(MULTI[j]) === 0) return tcase(MULTI[j]);
  if (name === 'Land Rover' && /^range rover/.test(rest)) return 'Range Rover';
  var toks = rest.split(/\s+/).filter(function (x) { return x && !SKIP.test(x); });
  var t = toks[0] || '';
  if (!t) return '';
  if (name === 'BMW') {
    var b = t.match(/^(\d)(\d{2})[a-z]*$/); if (b) return b[1] + ' Series';
    if (/^\d$/.test(t) && toks[1] === 'series') return t + ' Series';
    return t.toUpperCase();
  }
  if (name === 'Mercedes-Benz') {
    var c = t.match(/^(gla|glc|gle|cla|cls|slk|ml|[abcesv])-?(?:class)?(\d{0,3})[a-z]*$/);
    if (c) return /^(gla|glc|gle|cla|cls|slk|ml)$/.test(c[1]) ? c[1].toUpperCase() : c[1].toUpperCase() + '-Class';
  }
  if (name === 'Mini') { var mm = rest.match(/countryman|clubman|paceman|convertible|roadster/); return mm ? tcase(mm[0]) : 'Hatch'; }
  if (/^[a-z]+\d+$|^[a-z]\d$/i.test(t) && t.length <= 4) return t.toUpperCase();
  return tcase(t.replace(/[^a-z0-9!\-]/g, ''));
}
function parseMiles(t) {
  var m, re = /(?:mileage|odometer)\s*[:\-]?\s*([\d][\d,.]*)\s*(k)?/i;
  if ((m = t.match(re))) { var v = num(m[1]) * (m[2] ? 1000 : 1); if (v < 1000 && !m[2]) v *= 1000; if (v >= 100 && v < 400000) return Math.round(v); }
  re = /([\d][\d,.]*)\s*(k)?\s*(miles|mi|mls|km)\b(?!\s*away)/gi;
  while ((m = re.exec(t))) {
    var n = num(m[1]) * (m[2] ? 1000 : 1);
    if (/km/i.test(m[3])) n *= 0.621;
    if (n >= 500 && n < 400000) return Math.round(n);
  }
  return null;
}
function parseYear(t) {
  var m = t.match(/\b(19[89]\d|20[0-3]\d)\b/);
  if (m && +m[1] <= NOW_YEAR + 1) return +m[1];
  m = t.match(/\b(\d{2})\s?(?:plate|reg)\b|\((\d{2})\)/i);
  if (m) { var p = +(m[1] || m[2]); if (p >= 51 && p <= 99) return 2000 + p - 50; if (p >= 2 && p <= NOW_YEAR - 2000) return 2000 + p; }
  return null;
}
var FLAGS = [
  [/\bcat(egory)?[\s\-]?([sncd])\b/i, function (m) { return 'Cat ' + m[2].toUpperCase(); }],
  [/spares?\s*(or|\/|&)\s*repairs?|for spares/i, 'Spares or repair'],
  [/non[\s\-]?runner|not running|doesn'?t start|won'?t start/i, 'Non-runner'],
  [/\bno mot\b|mot (fail|expired)|without mot/i, 'No MOT'],
  [/head gasket|gearbox (issue|fault|problem)|engine (issue|fault|problem|knock)|clutch (gone|slipping)|timing (chain|belt) (gone|issue|noise)|dpf (issue|fault)/i, 'Mechanical fault'],
  [/write[\s\-]?off|written off|salvage|flood|fire damage|accident damaged|\bdamaged\b/i, 'Damaged / write-off'],
  [/\bbreaking\b|for parts/i, 'Breaking for parts'],
  [/\bswaps?\b|\bpx\b|part[\s\-]?ex/i, 'Swap / PX'],
  [/deposit|finance|monthly|per month|\bpcp\b/i, 'Finance or deposit price'],
  [/\blhd\b|left hand drive|\bexport only\b/i, 'LHD / export'],
  [/project|needs work|needs tlc|easy fix/i, 'Needs work']
];
var JUNK = /^(new listing|sponsored|opens in a new window or tab|buy it now|or best offer|best offer accepted|collection in person|free postage|free delivery|\+?£[\d,.]+ (postage|delivery)|watch|save this|\d+ watchers?|\d+ sold|top rated.*|brand new|pre-owned|used|.*private seller|.*trade seller)$/i;

function parseItem(raw) {
  var text = String(raw.text || '').replace(/\r/g, '').replace(/opens in a new (window or tab|tab|window)/gi, '\n').replace(/\n{2,}/g, '\n');
  var lines = text.split('\n').map(function (s) { return s.trim().replace(/^new listing\s*/i, ''); }).filter(Boolean);
  var pm = text.match(/(?:£|GBP)\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?/);
  var price = pm ? Math.round(num(pm[1])) : null;
  var cands = lines.filter(function (l) { return !JUNK.test(l) && !/^(£|GBP)?\s?[\d,.]+$/.test(l) && !/^(£|GBP)\s?[\d,]/.test(l) && /[a-z]{2}/i.test(l); });
  var title = '';
  for (var i = 0; i < cands.length; i++) if (findMake(cands[i])) { title = cands[i]; break; }
  if (!title) title = cands.slice().sort(function (a, b) { return b.length - a.length; })[0] || 'Untitled listing';
  title = title.slice(0, 140);
  var mk = findMake(title) || findMake(text);
  var flags = [];
  FLAGS.forEach(function (f) { var m = text.match(f[0]); if (m) { var l = typeof f[1] === 'function' ? f[1](m) : f[1]; if (flags.indexOf(l) < 0) flags.push(l); } });
  if (price != null && price < 300) flags.push('Placeholder price?');
  var sold = /\bsold\s+\d{1,2}\s+[a-z]{3}\b/i.test(text);
  var auction = !sold && /\b\d+\s+bids?\b|time left|\b\d+[dh]\s+\d+[hm]\s+left\b/i.test(text);
  return {
    id: raw.url || raw.id || ('m' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7)),
    src: raw.src === 'ebay' || raw.src === 'facebook' ? raw.src : 'manual',
    url: /^https?:\/\//.test(raw.url || '') ? raw.url : '',
    text: text.slice(0, 700), title: title, price: price,
    year: parseYear(title) || parseYear(text), miles: parseMiles(text),
    make: mk ? mk.name : '', model: mk ? findModel(mk) : '',
    flags: flags, sold: sold, auction: auction,
    added: raw.added || Date.now(), seen: Date.now(), userValue: raw.userValue || null
  };
}
// Does a parsed item look like a car? (drops phone cases, sofas, etc.)
function isCar(it) { return it.price != null && it.price >= 100 && !!it.make && (it.year != null || it.miles != null); }

function keyOf(it) { return (it.make + ' ' + it.model).trim().toLowerCase(); }
function wmedian(vals) {
  vals.sort(function (a, b) { return a.v - b.v; });
  var tot = vals.reduce(function (s, x) { return s + x.w; }, 0), acc = 0;
  for (var i = 0; i < vals.length; i++) { acc += vals[i].w; if (acc >= tot / 2) return vals[i].v; }
  return vals[vals.length - 1].v;
}
// Adds est, n, conf, value, disc, profit and verdict to every item. Returns groups by model.
function valueAll(items, s) {
  s = Object.assign({}, DEFAULTS, s || {});
  var groups = {};
  items.forEach(function (it) { var k = keyOf(it); if (it.model) (groups[k] = groups[k] || []).push(it); });
  items.forEach(function (it) {
    it.est = null; it.n = 0; it.conf = '';
    var g = groups[keyOf(it)] || [];
    var comps = g.filter(function (c) { return c !== it && c.price >= 300 && !c.flags.length && !c.auction; });
    if (comps.length >= 3) {
      comps = comps.map(function (c) {
        var dy = it.year && c.year ? it.year - c.year : null, dm = it.miles != null && c.miles != null ? it.miles - c.miles : null;
        var d = (dy == null ? 2 : Math.abs(dy)) + (dm == null ? 1.5 : Math.abs(dm) / 15000);
        var adj = c.price * Math.exp(0.09 * Math.max(-5, Math.min(5, dy || 0)) - 0.012 * Math.max(-10, Math.min(10, (dm || 0) / 10000)));
        return { d: d, v: adj, w: c.sold ? 2 : 1 };
      }).sort(function (a, b) { return a.d - b.d; }).slice(0, 8);
      it.est = Math.round(wmedian(comps.slice()) / 10) * 10;
      it.n = comps.length;
      var vs = comps.map(function (c) { return c.v; }).sort(function (a, b) { return a - b; });
      var spread = (vs[Math.floor(vs.length * 0.75)] - vs[Math.floor(vs.length * 0.25)]) / it.est;
      it.conf = it.n >= 6 && spread < 0.3 ? 'high' : it.n >= 4 ? 'medium' : 'low';
    }
    var value = it.userValue || it.est;
    it.value = value;
    it.disc = value && it.price ? (value - it.price) / value : null;
    it.profit = value && it.price ? Math.round(value * (1 - (+s.disc || 0) / 100) - it.price - (+s.prep || 0) - (+s.fees || 0)) : null;
    var th = (+s.thresh || 12) / 100;
    it.verdict = it.sold ? 'sold' : it.disc == null ? 'none' : it.flags.length ? 'check' : it.disc >= th * 2 ? 'steal' : it.disc >= th ? 'good' : it.disc >= -0.05 ? 'fair' : 'pricey';
  });
  return groups;
}
function isDeal(it) { return it.verdict === 'steal' || it.verdict === 'good'; }
function gbp(n) { return n == null ? '–' : (n < 0 ? '−£' : '£') + Math.abs(n).toLocaleString('en-GB'); }

g.CDF = { DEFAULTS: DEFAULTS, parseItem: parseItem, isCar: isCar, valueAll: valueAll, isDeal: isDeal, findMake: findMake, findModel: findModel, tcase: tcase, num: num, gbp: gbp, keyOf: keyOf };
})(typeof self !== 'undefined' ? self : window);
