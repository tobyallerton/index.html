// Download a TikTok photo slideshow the user wants remade: every slide image, the caption, the sound,
// the stats and whatever product data the post carries.
//
// Usage (from the repo root, through the Chrome wrapper):
//   skills/viral-slideshow-factory/scripts/run-chrome.sh tt_fetch.js --url <tiktok link> --out <folder>
// Works with full links (tiktok.com/@user/photo/123) and share links (vm.tiktok.com/XXXX/).
// Writes <folder>/01.jpg, 02.jpg, ... , meta.json (caption, sound, stats, author, product anchors) and item.json (raw data).
const fs = require('fs'); const path = require('path');
const { openProfile, sleep } = require('./lib');

function arg(name) { const i = process.argv.indexOf('--' + name); return i > 0 ? process.argv[i + 1] : null; }

(async () => {
  const url = arg('url'), out = arg('out');
  if (!url || !out) { console.log(JSON.stringify({ ok: false, error: 'usage: --url <link> --out <folder>' })); process.exit(1); }
  fs.mkdirSync(out, { recursive: true });
  const { ctx, page } = await openProfile('tiktok');
  let item = null;
  page.on('response', async r => {
    if (/api\/item\/detail/.test(r.url())) { try { const j = await r.json(); if (j.itemInfo) item = j.itemInfo.itemStruct; } catch (e) {} }
  });
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(8000);
    let final = page.url();
    // Share links land on /video/ for photo posts; the /photo/ page is what loads the slides.
    if (!item && /\/video\/\d+/.test(final)) { await page.goto(final.replace('/video/', '/photo/'), { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(8000); final = page.url(); }
    if (!item) {
      // Fall back to the data embedded in the page.
      item = await page.evaluate(() => {
        try { const s = document.querySelector('#__UNIVERSAL_DATA_FOR_REHYDRATION__'); const j = JSON.parse(s.textContent);
              return j.__DEFAULT_SCOPE__['webapp.video-detail'].itemInfo.itemStruct; } catch (e) { return null; }
      });
    }
    let imgs = [];
    if (item && item.imagePost) imgs = item.imagePost.images.map(i => i.imageURL.urlList[0]);
    else imgs = await page.evaluate(() => [...new Set([...document.querySelectorAll('img')].map(i => i.currentSrc || i.src).filter(u => /photomode/.test(u)))]);
    let k = 0;
    for (const u of imgs) { k++; const r = await ctx.request.get(u); if (r.ok()) fs.writeFileSync(path.join(out, String(k).padStart(2, '0') + '.jpg'), await r.body()); }
    const meta = item ? {
      url: final, id: item.id, author: item.author && item.author.uniqueId, desc: item.desc,
      music: item.music && { title: item.music.title, author: item.music.authorName, id: item.music.id, url: item.music.id ? `https://www.tiktok.com/music/x-${item.music.id}` : '' },
      stats: item.stats, slides: imgs.length, anchors: item.anchors || null,
    } : { url: final, slides: imgs.length, note: 'post data not found; slides taken from the page' };
    fs.writeFileSync(path.join(out, 'meta.json'), JSON.stringify(meta, null, 1));
    if (item) fs.writeFileSync(path.join(out, 'item.json'), JSON.stringify(item));
    console.log(JSON.stringify({ ok: imgs.length > 0, slides: imgs.length, out, author: meta.author || null, title: await page.title() }));
  } catch (e) {
    console.log(JSON.stringify({ ok: false, error: e.message.slice(0, 200) }));
  }
  await ctx.close();
})();
