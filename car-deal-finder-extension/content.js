// Runs on eBay and Facebook Marketplace pages. Saves the car listings you scroll past and tags deals on the page.
(function () {
  'use strict';
  var SRC = /facebook\./.test(location.hostname) ? 'facebook' : 'ebay';
  var SEL = SRC === 'facebook' ? 'a[href*="/marketplace/item/"]' : 'a[href*="/itm/"]';
  var MARK = '◆';
  var sent = {}, boxes = {}, timer = null, alive = true, totalHere = 0, dealsHere = 0, savedTotal = 0;

  function normal(href) {
    try {
      var u = new URL(href, location.href);
      if (SRC === 'facebook') { var m = u.pathname.match(/\/marketplace\/item\/(\d+)/); return m ? 'https://www.facebook.com/marketplace/item/' + m[1] + '/' : null; }
      var e = u.pathname.match(/\/itm\/(?:[^/]+\/)?(\d{9,})/); return e ? u.origin + '/itm/' + e[1] : null;
    } catch (err) { return null; }
  }
  function boxOf(a) {
    if (SRC === 'facebook') return a;
    return a.closest('li.s-item, li.s-card, .s-item, .s-card') || a.closest('li') || a.parentElement;
  }
  function textOf(box) {
    var t = box.innerText || '';
    if (t.split('\n').filter(function (l) { return l.trim(); }).length < 3) {
      // layout put everything on one line: fall back to one line per text node
      var w = document.createTreeWalker(box, NodeFilter.SHOW_TEXT), parts = [], n;
      while ((n = w.nextNode())) { var v = n.nodeValue.trim(); if (v && !(n.parentElement && n.parentElement.closest('.cdf-tag'))) parts.push(v); }
      t = parts.join('\n');
    }
    return t.split('\n').filter(function (l) { return l.trim().charAt(0) !== MARK; }).join('\n').trim();
  }

  function scan() {
    if (!alive) return;
    var out = [], found = {};
    document.querySelectorAll(SEL).forEach(function (a) {
      var url = normal(a.href); if (!url || found[url]) return;
      var box = boxOf(a); if (!box) return;
      var t = textOf(box);
      if (!/(£|GBP)\s?\d/.test(t)) return;
      found[url] = box;
      if (sent[url] !== t) { sent[url] = t; out.push({ src: SRC, url: url, text: t.slice(0, 700) }); }
    });
    boxes = found;
    var urls = Object.keys(found);
    if (!urls.length) { chip(); return; }
    try {
      chrome.runtime.sendMessage({ type: 'listings', items: out, urls: urls }, function (res) {
        if (chrome.runtime.lastError || !res) return;
        savedTotal = res.total || savedTotal;
        paint(res.verdicts || {});
      });
    } catch (e) { alive = false; } // extension was reloaded; this page needs a refresh
  }

  var STYLE = {
    steal: ['#24683a', '#ffffff'], good: ['#e6f3e9', '#1d5a30'], fair: ['#eee8de', '#4a4038'],
    pricey: ['#fbe9e2', '#a3321a'], check: ['#fdf3e1', '#8a5408'], none: ['#f2f0ec', '#6b625a']
  };
  function label(v) {
    var pct = v.disc != null ? Math.round(Math.abs(v.disc) * 100) + '%' : '';
    if (v.verdict === 'none') return 'No value yet · need more of this model';
    if (v.verdict === 'sold') return 'Sold · used as a comparison';
    var core = v.disc >= 0 ? pct + ' under (' + gbp(v.value * v.disc) + ')' : pct + ' over market';
    var bits = [core, 'worth ~' + gbp(v.value)];
    if (v.profit > 0) bits.push('profit ~' + gbp(v.profit));
    if (v.verdict === 'check') bits.unshift(v.flags.join(', '));
    if (v.auction) bits.push('current bid');
    return bits.join(' · ');
  }
  function gbp(n) { return n == null ? '–' : (n < 0 ? '−£' : '£') + Math.round(Math.abs(n)).toLocaleString('en-GB'); }

  function paint(verdicts) {
    totalHere = 0; dealsHere = 0;
    Object.keys(boxes).forEach(function (url) {
      var v = verdicts[url], box = boxes[url];
      var tag = box.querySelector(':scope > .cdf-tag');
      if (!v) { if (tag) tag.remove(); return; }
      totalHere++;
      if (v.verdict === 'steal' || v.verdict === 'good') dealsHere++;
      var txt = MARK + ' ' + (v.verdict === 'steal' ? 'STEAL · ' : v.verdict === 'good' ? 'DEAL · ' : '') + label(v);
      if (!tag) { tag = document.createElement('div'); tag.className = 'cdf-tag'; box.appendChild(tag); }
      if (tag.textContent !== txt) {
        tag.textContent = txt;
        var c = STYLE[v.verdict] || STYLE.none;
        tag.style.cssText = 'display:block;margin:4px 0 2px;padding:3px 7px;border-radius:6px;font:600 12px/1.35 system-ui,sans-serif;white-space:normal;background:' + c[0] + ';color:' + c[1] + ';';
      }
      var big = v.verdict === 'steal' || v.verdict === 'good';
      box.style.outline = big ? '3px solid ' + (v.verdict === 'steal' ? '#24683a' : '#6fbf86') : '';
      box.style.outlineOffset = big ? '2px' : '';
      box.style.borderRadius = big ? '8px' : box.style.borderRadius;
    });
    chip();
  }

  var chipEl = null;
  function chip() {
    if (!totalHere) { if (chipEl) chipEl.remove(); chipEl = null; return; }
    if (!chipEl) {
      chipEl = document.createElement('button');
      chipEl.type = 'button';
      chipEl.title = 'Open Car Deal Finder';
      chipEl.style.cssText = 'position:fixed;z-index:2147483646;right:16px;bottom:16px;padding:9px 14px;border-radius:999px;border:0;background:#1a1714;color:#f5f0e8;font:600 13px system-ui,sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.3);cursor:pointer';
      chipEl.onclick = function () { try { chrome.runtime.sendMessage({ type: 'open-dashboard' }); } catch (e) {} };
      document.body.appendChild(chipEl);
    }
    chipEl.textContent = MARK + ' ' + totalHere + ' cars on this page · ' + dealsHere + ' deal' + (dealsHere === 1 ? '' : 's') + ' · ' + savedTotal + ' saved';
  }

  function soon() { clearTimeout(timer); timer = setTimeout(scan, 900); }
  new MutationObserver(function (muts) {
    for (var i = 0; i < muts.length; i++) {
      var t = muts[i].target;
      if (!(t.classList && t.classList.contains('cdf-tag')) && t !== chipEl) { soon(); return; }
    }
  }).observe(document.documentElement, { childList: true, subtree: true });
  window.addEventListener('scroll', soon, { passive: true });
  setTimeout(scan, 1200);
})();
