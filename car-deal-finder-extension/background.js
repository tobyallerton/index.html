// Background worker: stores listings, values them, sets the badge and sends deal notifications.
importScripts('core.js');

var chain = Promise.resolve();
function queued(fn) { var p = chain.then(fn); chain = p.catch(function () {}); return p; }

async function getState() {
  var s = await chrome.storage.local.get(['items', 'settings', 'notified']);
  return { items: s.items || [], settings: Object.assign({}, CDF.DEFAULTS, s.settings || {}), notified: s.notified || {} };
}
async function finish(st, extra) {
  CDF.valueAll(st.items, st.settings);
  var deals = st.items.filter(CDF.isDeal);
  chrome.action.setBadgeText({ text: deals.length ? String(deals.length) : '' });
  chrome.action.setBadgeBackgroundColor({ color: '#c8401a' });
  var fresh = st.settings.notify ? deals.filter(function (i) { return !st.notified[i.id] && !i.auction && i.profit >= (+st.settings.minProfit || 0); }) : [];
  fresh.forEach(function (i) { st.notified[i.id] = Date.now(); });
  await chrome.storage.local.set(Object.assign({ items: st.items, notified: st.notified, updated: Date.now() }, extra || {}));
  notify(fresh);
  return st;
}
function notify(list) {
  if (!list.length) return;
  list.sort(function (a, b) { return b.profit - a.profit; });
  if (list.length > 3) {
    var best = list[0];
    chrome.notifications.create('summary-' + Date.now(), {
      type: 'basic', iconUrl: 'icons/icon128.png', priority: 2,
      title: list.length + ' new car deals found',
      message: 'Best: ' + best.title + ' at ' + CDF.gbp(best.price) + ', about ' + CDF.gbp(best.profit) + ' profit. Click to see them all.'
    });
    return;
  }
  list.forEach(function (i) {
    chrome.notifications.create('item|' + i.id + '|' + Date.now(), {
      type: 'basic', iconUrl: 'icons/icon128.png', priority: 2,
      title: Math.round(i.disc * 100) + '% under: ' + i.title,
      message: CDF.gbp(i.price) + ' asking · worth about ' + CDF.gbp(i.value) + ' · est. profit ' + CDF.gbp(i.profit) + (i.src === 'facebook' ? ' · Facebook' : ' · eBay')
    });
  });
}
chrome.notifications.onClicked.addListener(function (id) {
  var parts = id.split('|');
  var url = parts[0] === 'item' && /^https?:/.test(parts[1]) ? parts[1] : chrome.runtime.getURL('dashboard.html');
  chrome.tabs.create({ url: url });
  chrome.notifications.clear(id);
});
chrome.action.onClicked.addListener(function () { chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') }); });

function verdictsFor(items, urls) {
  var by = {}, out = {};
  items.forEach(function (i) { by[i.id] = i; });
  (urls || []).forEach(function (u) {
    var i = by[u]; if (!i) return;
    out[u] = { verdict: i.verdict, disc: i.disc, value: i.value, profit: i.profit, n: i.n, flags: i.flags, auction: i.auction };
  });
  return out;
}

async function addListings(raws) {
  var st = await getState();
  var byId = {}; st.items.forEach(function (i) { byId[i.id] = i; });
  var added = 0;
  raws.forEach(function (r) {
    var it = CDF.parseItem(r);
    if (!CDF.isCar(it)) return;
    var old = byId[it.id];
    if (old) {
      it.added = old.added; it.userValue = old.userValue;
      if (old.edited) { it.make = old.make; it.model = old.model; it.edited = true; }
      if (old.price && it.price && it.price < old.price) it.dropped = old.price; else if (old.dropped) it.dropped = old.dropped;
      Object.assign(old, it);
    } else { st.items.push(it); byId[it.id] = it; added++; }
  });
  await finish(st, { lastCapture: { at: Date.now(), added: added, seen: raws.length } });
  return added;
}

chrome.runtime.onMessage.addListener(function (msg, sender, reply) {
  var job;
  if (msg.type === 'listings') {
    job = queued(async function () {
      var added = msg.items && msg.items.length ? await addListings(msg.items) : 0;
      var st = await getState();
      CDF.valueAll(st.items, st.settings);
      return { added: added, total: st.items.length, verdicts: verdictsFor(st.items, msg.urls) };
    });
  } else if (msg.type === 'import') {
    job = queued(async function () { return { added: await addListings(msg.items) }; });
  } else if (msg.type === 'restore') {
    job = queued(async function () {
      var st = await getState();
      st.items = (msg.items || []).map(function (i) { var p = CDF.parseItem(i); Object.assign(p, { id: i.id || p.id, added: i.added || p.added, edited: i.edited, userValue: i.userValue || null }); if (i.edited) { p.make = i.make; p.model = i.model; } return p; });
      if (msg.settings) { st.settings = Object.assign({}, CDF.DEFAULTS, msg.settings); await chrome.storage.local.set({ settings: st.settings }); }
      st.notified = {}; st.items.forEach(function (i) { st.notified[i.id] = 1; });
      await finish(st);
      return { total: st.items.length };
    });
  } else if (msg.type === 'patch') {
    job = queued(async function () {
      var st = await getState();
      var it = st.items.find(function (i) { return i.id === msg.id; });
      if (it) Object.assign(it, msg.patch);
      await finish(st); return { ok: true };
    });
  } else if (msg.type === 'remove') {
    job = queued(async function () {
      var st = await getState();
      st.items = st.items.filter(function (i) { return msg.ids.indexOf(i.id) < 0; });
      await finish(st); return { ok: true };
    });
  } else if (msg.type === 'settings') {
    job = queued(async function () {
      var st = await getState();
      st.settings = Object.assign(st.settings, msg.settings);
      await chrome.storage.local.set({ settings: st.settings });
      // re-valuing with new thresholds shouldn't fire a flood of alerts
      CDF.valueAll(st.items, st.settings);
      st.items.filter(CDF.isDeal).forEach(function (i) { st.notified[i.id] = st.notified[i.id] || 1; });
      await finish(st); return { ok: true };
    });
  } else if (msg.type === 'clear') {
    job = queued(async function () { await chrome.storage.local.set({ items: [], notified: {} }); chrome.action.setBadgeText({ text: '' }); return { ok: true }; });
  } else if (msg.type === 'open-dashboard') {
    chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') }); return false;
  } else return false;
  job.then(reply, function (e) { reply({ error: String(e) }); });
  return true;
});

chrome.runtime.onInstalled.addListener(function (d) {
  queued(async function () { await finish(await getState()); });
  if (d.reason === 'install') chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') });
});
chrome.runtime.onStartup.addListener(function () { queued(async function () { await finish(await getState()); }); });
