(function () {
'use strict';
var $ = function (id) { return document.getElementById(id); };
var items = [], settings = Object.assign({}, CDF.DEFAULTS), meta = {};
var editing = null, valEditing = null;
var send = function (msg) { return new Promise(function (res) { chrome.runtime.sendMessage(msg, res); }); };
var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); };
var gbp = CDF.gbp;
var VLABEL = { steal: 'Steal', good: 'Good deal', fair: 'Fair', pricey: 'Over market', check: 'Check flags', none: 'Need comps', sold: 'Sold comp' };
function toast(m, err) { var t = $('toast'); t.textContent = m; t.className = 'toast' + (err ? ' err' : ''); }
function ago(t) { if (!t) return 'never'; var s = (Date.now() - t) / 1000; return s < 60 ? 'just now' : s < 3600 ? Math.round(s / 60) + ' min ago' : s < 86400 ? Math.round(s / 3600) + ' h ago' : Math.round(s / 86400) + ' days ago'; }

async function load() {
  var s = await chrome.storage.local.get(['items', 'settings', 'search', 'lastCapture']);
  items = s.items || [];
  settings = Object.assign({}, CDF.DEFAULTS, s.settings || {});
  meta = s;
  if (!load.done) {
    load.done = true;
    $('sPrep').value = settings.prep; $('sFees').value = settings.fees; $('sDisc').value = settings.disc; $('sThresh').value = settings.thresh;
    $('sNotify').value = settings.notify ? '1' : ''; $('sMinProfit').value = settings.minProfit;
    if (s.search) Object.keys(s.search).forEach(function (k) { if ($(k) && s.search[k] != null) $(k).value = s.search[k]; });
    if (!items.length) $('fVerdict').value = '';
    links();
  }
  render();
}

function render() {
  var groups = CDF.valueAll(items, settings);
  var deals = items.filter(CDF.isDeal);
  $('tListings').textContent = items.length;
  $('tModels').textContent = Object.keys(groups).length;
  $('tDeals').textContent = deals.length;
  var fb = items.filter(function (i) { return i.src === 'facebook'; }).length, eb = items.filter(function (i) { return i.src === 'ebay'; }).length, sold = items.filter(function (i) { return i.sold; }).length;
  var lc = meta.lastCapture;
  $('status').innerHTML = items.length
    ? '<span><b>' + items.length + '</b> cars saved: ' + eb + ' from eBay (' + sold + ' sold), ' + fb + ' from Facebook.</span><span>Last capture ' + ago(lc && lc.at) + (lc ? ', ' + lc.added + ' new.' : '.') + '</span>'
    : 'No cars saved yet. Open a search from step 1 and scroll through the results. A dark “◆ cars on this page” button appears at the bottom right when it’s working.';

  var ft = $('fText').value.trim().toLowerCase(), fs = $('fSrc').value, fv = $('fVerdict').value, hide = $('fFlags').checked, sort = $('fSort').value;
  var list = items.filter(function (i) {
    if (fs && i.src !== fs) return false;
    if (hide && i.flags.length) return false;
    if (fv === 'deals' && !CDF.isDeal(i)) return false;
    if (fv === 'check' && i.verdict !== 'check') return false;
    if (fv === 'sold' && !i.sold) return false;
    if (fv === '' && i.sold) return false;
    if (ft && (i.title + ' ' + i.make + ' ' + i.model + ' ' + (i.year || '')).toLowerCase().indexOf(ft) < 0) return false;
    return true;
  });
  var nz = function (v, d) { return v == null ? d : v; };
  list.sort(function (a, b) {
    if (sort === 'profit') return nz(b.profit, -1e9) - nz(a.profit, -1e9);
    if (sort === 'price') return nz(a.price, 1e9) - nz(b.price, 1e9);
    if (sort === 'new') return b.added - a.added;
    return nz(b.disc, -9) - nz(a.disc, -9);
  });
  if (!list.length) {
    var msg = items.length ? (fv === 'deals' ? 'No deals at your threshold yet. Switch “Show” to Everything, or browse more listings of the same model so there are more to compare with.' : 'Nothing matches these filters.') : 'Nothing saved yet. Browse an eBay or Facebook Marketplace car search and cars appear here.';
    $('rows').innerHTML = '<tr><td colspan="7" class="empty">' + msg + '</td></tr>';
    return;
  }
  $('rows').innerHTML = list.slice(0, 400).map(function (i) {
    var id = esc(i.id);
    var keyCell = editing === i.id
      ? '<input class="valin" style="width:200px" data-key="' + id + '" value="' + esc((i.make + ' ' + i.model).trim()) + '" aria-label="Make and model">'
      : '<button class="key" data-act="edit" data-id="' + id + '" title="Fix make and model">' + esc((i.make + ' ' + i.model).trim() || 'set model') + '</button>';
    var bits = [i.year, i.miles != null ? Math.round(i.miles / 1000) + 'k mi' : null].filter(Boolean).join(' · ');
    var valCell = valEditing === i.id
      ? '<input class="valin" type="number" inputmode="numeric" data-uv="' + id + '" value="' + (i.userValue || '') + '" placeholder="£" aria-label="Your valuation">'
      : (i.value ? gbp(i.value) + '<span class="sub">' + (i.userValue ? 'your value' : i.n + ' comps · ' + i.conf) + '</span>' : '<span class="sub">needs 3+ of model</span>');
    var q = encodeURIComponent([i.year, i.make, i.model].filter(Boolean).join(' '));
    return '<tr>' +
      '<td class="car"><div>' + (i.url ? '<a href="' + esc(i.url) + '" target="_blank" rel="noopener">' + esc(i.title) + '</a>' : '<b>' + esc(i.title) + '</b>') + '</div>' +
        '<div class="meta"><span class="src">' + (i.src === 'facebook' ? 'FB' : i.src === 'ebay' ? 'eBay' : 'Manual') + '</span>' + (bits ? '<span>' + bits + '</span>' : '') + keyCell +
        '<span>seen ' + ago(i.added) + '</span>' + (i.auction ? '<span class="flag">Auction · current bid</span>' : '') + '</div>' +
        (i.flags.length ? '<div class="flags">' + i.flags.map(function (f) { return '<span class="flag">' + esc(f) + '</span>'; }).join('') + '</div>' : '') + '</td>' +
      '<td class="num"><b>' + gbp(i.price) + '</b>' + (i.dropped ? '<span class="sub drop">was ' + gbp(i.dropped) + '</span>' : '') + '</td>' +
      '<td class="num">' + valCell + '</td>' +
      '<td class="num">' + (i.disc == null ? '–' : '<span class="' + (i.disc > 0 ? 'pos' : 'neg') + '">' + Math.round(i.disc * 100) + '%</span><span class="sub">' + gbp(i.value - i.price) + '</span>') + '</td>' +
      '<td class="num">' + (i.profit == null ? '–' : '<span class="' + (i.profit > 0 ? 'pos' : 'neg') + '">' + gbp(i.profit) + '</span>') + '</td>' +
      '<td><span class="pill v-' + i.verdict + '">' + VLABEL[i.verdict] + '</span></td>' +
      '<td><div class="acts">' +
        '<button data-act="val" data-id="' + id + '">' + (i.userValue ? 'Edit value' : 'Set value') + '</button>' +
        '<a href="https://www.ebay.co.uk/sch/9801/i.html?_nkw=' + q + '&LH_Sold=1&LH_Complete=1&LH_PrefLoc=1" target="_blank" rel="noopener">Sold prices</a>' +
        '<button data-act="del" data-id="' + id + '">Remove</button>' +
      '</div></td></tr>';
  }).join('');
  var f = document.querySelector('[data-key],[data-uv]'); if (f) { f.focus(); if (f.select) f.select(); }
}

/* table actions */
$('rows').addEventListener('click', function (e) {
  var b = e.target.closest('button[data-act]'); if (!b) return;
  var id = b.getAttribute('data-id'), act = b.getAttribute('data-act');
  if (act === 'del') { items = items.filter(function (x) { return x.id !== id; }); send({ type: 'remove', ids: [id] }); }
  if (act === 'edit') { editing = id; valEditing = null; }
  if (act === 'val') { valEditing = id; editing = null; }
  render();
});
function commit(el) {
  var id = el.getAttribute('data-key') || el.getAttribute('data-uv');
  var it = items.find(function (x) { return x.id === id; }); if (!it) return;
  var patch;
  if (el.hasAttribute('data-key')) {
    var v = el.value.trim(), mk = CDF.findMake(v);
    if (mk) patch = { make: mk.name, model: CDF.findModel(mk) || CDF.tcase(mk.rest), edited: true };
    else if (v) { var p = v.split(/\s+/); patch = { make: CDF.tcase(p.shift()), model: CDF.tcase(p.join(' ')), edited: true }; }
    editing = null;
  } else { var n = Math.round(CDF.num(el.value)); patch = { userValue: n > 0 ? n : null }; valEditing = null; }
  if (patch) { Object.assign(it, patch); send({ type: 'patch', id: id, patch: patch }); }
  render();
}
$('rows').addEventListener('keydown', function (e) {
  if (!e.target.matches('[data-key],[data-uv]')) return;
  if (e.key === 'Enter') commit(e.target);
  if (e.key === 'Escape') { editing = valEditing = null; render(); }
});
$('rows').addEventListener('focusout', function (e) { if (e.target.matches('[data-key],[data-uv]')) commit(e.target); });

/* filters + settings */
['fText', 'fSrc', 'fVerdict', 'fSort', 'fFlags'].forEach(function (id) { $(id).addEventListener('input', render); });
var SET = { prep: 'sPrep', fees: 'sFees', disc: 'sDisc', thresh: 'sThresh', minProfit: 'sMinProfit', notify: 'sNotify' };
var st = null;
Object.keys(SET).forEach(function (k) {
  $(SET[k]).addEventListener('input', function () {
    settings[k] = k === 'notify' ? !!this.value : +this.value || 0;
    render();
    clearTimeout(st); st = setTimeout(function () { send({ type: 'settings', settings: settings }); }, 500);
  });
});

/* search links */
function links() {
  var q = $('q').value.trim(), mn = $('minP').value, mx = $('maxP').value, pc = $('pc').value.trim().replace(/\s+/g, ''), r = $('rad').value || 50;
  var city = ($('city').value.trim().toLowerCase().replace(/\s+/g, '') || 'london'), y = $('minY').value, mm = $('maxM').value;
  var e = 'https://www.ebay.co.uk/sch/9801/i.html?_nkw=' + encodeURIComponent(q) + '&LH_PrefLoc=1' + (mn ? '&_udlo=' + mn : '') + (mx ? '&_udhi=' + mx : '') + (pc ? '&_stpos=' + encodeURIComponent(pc) + '&_sadis=' + r + '&_fspt=1' : '');
  $('lnEbay').href = e + '&_sop=10&_ipg=240';
  $('lnSold').href = e + '&LH_Sold=1&LH_Complete=1&_sop=13&_ipg=240';
  $('lnFb').href = 'https://www.facebook.com/marketplace/' + encodeURIComponent(city) + '/vehicles?query=' + encodeURIComponent(q) + (mn ? '&minPrice=' + mn : '') + (mx ? '&maxPrice=' + mx : '') + (y ? '&minYear=' + y : '') + (mm ? '&maxMileage=' + mm : '') + '&sortBy=creation_time_descend&exact=false';
  chrome.storage.local.set({ search: { q: q, minP: mn, maxP: mx, pc: $('pc').value, rad: $('rad').value, city: $('city').value, minY: y, maxM: mm } });
}
$('searchForm').addEventListener('input', links);
$('searchForm').addEventListener('submit', function (e) { e.preventDefault(); });

/* backup / restore / manual add */
function copy(text, ok) {
  navigator.clipboard.writeText(text).then(function () { toast(ok); }, function () { $('paste').value = text; $('paste').select(); toast('Copy was blocked. The backup is selected in the box below: press Ctrl+C.', true); });
}
$('backup').onclick = function () {
  var slim = items.map(function (i) { return { id: i.id, src: i.src, url: i.url, text: i.text, added: i.added, userValue: i.userValue, edited: i.edited, make: i.make, model: i.model }; });
  copy(JSON.stringify({ cdfBackup: 1, items: slim, settings: settings }), 'Backup copied (' + items.length + ' cars). Paste it into a note or file to keep it.');
};
$('importBtn').onclick = async function () {
  var txt = $('paste').value.trim(); if (!txt) return;
  try {
    var j = JSON.parse(txt);
    if (j && j.cdfBackup) { var r = await send({ type: 'restore', items: j.items, settings: j.settings }); load.done = false; toast('Backup restored: ' + r.total + ' cars.'); $('paste').value = ''; return load(); }
  } catch (e) {}
  var raws = txt.split(/\n\s*\n/).filter(function (b) { return /(£|GBP)\s?\d/.test(b); }).map(function (b) { return { src: 'manual', text: b, url: (b.match(/https?:\/\/\S+/) || [''])[0] }; });
  if (!raws.length) return toast('Nothing to import. Each car needs a £ price.', true);
  var res = await send({ type: 'import', items: raws });
  toast(res.added ? res.added + ' car' + (res.added === 1 ? '' : 's') + ' added.' : 'Nothing added. Include a make, a £ price and the year or mileage.', !res.added);
  $('paste').value = '';
};
function clearHandler() {
  $('clearWrap').innerHTML = '<span class="confirm">Delete all ' + items.length + ' cars? <button class="btn sm red" id="yesClear" type="button">Delete</button><button class="btn sm ghost" id="noClear" type="button">Keep</button></span>';
  $('yesClear').onclick = function () { send({ type: 'clear' }); items = []; render(); resetClear(); toast('All cars cleared.'); };
  $('noClear').onclick = resetClear;
}
function resetClear() { $('clearWrap').innerHTML = '<button class="btn ghost" id="clearAll" type="button">Clear all listings</button>'; $('clearAll').onclick = clearHandler; }
$('clearAll').onclick = clearHandler;

/* live updates while you browse in another tab */
var lt = null;
chrome.storage.onChanged.addListener(function (ch, area) {
  if (area !== 'local' || !(ch.items || ch.lastCapture)) return;
  if (editing || valEditing) return;
  clearTimeout(lt); lt = setTimeout(load, 400);
});
setInterval(function () { if (!editing && !valEditing) render(); }, 60000);
load();
})();
