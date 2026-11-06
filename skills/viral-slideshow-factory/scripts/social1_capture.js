// Captures the post data behind Social1 pages (videos list, creator profile) and saves it raw.
// Social1 sends each post as JSON inside its page payload: video_id, handle, views, likes, comments,
// gmv (per post), time_posted, is_slideshow, product_data {product_id, name, price_value, ...}, video_url.
// Usage (cloud: through run-chrome.sh):
//   run-chrome.sh social1_capture.js --out raw.txt --url "<social1 url>" [--url "<another>"] [--pages 4] [--scrolls 4]
// Then: python3 parse_posts.py raw.txt > posts.json
const fs = require('fs');
const { openProfile, arg, args, sleep } = require('./lib');

(async () => {
  const urls = args('url');
  const out = arg('out', 'raw.txt');
  const pages = parseInt(arg('pages', '1'), 10);
  const scrolls = parseInt(arg('scrolls', '3'), 10);
  if (!urls.length) { console.error('--url required'); process.exit(2); }
  const { ctx, page } = await openProfile('social1');
  let buf = '';
  page.on('response', async (r) => {
    if (!/social1\.ai/.test(r.url())) return;
    try { const b = await r.text(); if (b.includes('video_id')) buf += b + '\n'; } catch (e) {}
  });
  try {
    for (const u of urls) {
      await page.goto(u, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await sleep(9000);
      for (let i = 0; i < scrolls; i++) { await page.mouse.wheel(0, 2500); await sleep(2000); }
      for (let p = 2; p <= pages; p++) {
        const b = page.getByRole('button', { name: String(p), exact: true }).last();
        if (!(await b.isVisible().catch(() => false))) break;
        await b.click().catch(() => {}); await sleep(6000);
      }
    }
    fs.writeFileSync(out, buf);
    console.log(JSON.stringify({ ok: true, out, bytes: buf.length }));
  } finally { await ctx.close(); }
})().catch((e) => { console.log(JSON.stringify({ ok: false, error: e.message })); process.exit(1); });
