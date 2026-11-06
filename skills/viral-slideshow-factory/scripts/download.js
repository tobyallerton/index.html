// Downloads image URLs using the logged-in profile's cookies (works for Social1/TikTok CDN links).
// Usage: node download.js --site social1 --out <dir> <url1> <url2> ...   (or --list urls.txt)
const fs = require('fs');
const path = require('path');
const { openProfile, arg } = require('./lib');

(async () => {
  const site = arg('site', 'social1');
  const out = arg('out', 'downloads');
  const list = arg('list');
  let urls = process.argv.slice(2).filter((a, i, all) => /^https?:/.test(a) && !['--out', '--site', '--list'].includes(all[i - 1]));
  if (list) urls = urls.concat(fs.readFileSync(list, 'utf8').split(/\s+/).filter((u) => /^https?:/.test(u)));
  fs.mkdirSync(out, { recursive: true });
  const { ctx } = await openProfile(site);
  try {
    let n = 0;
    for (const u of urls) {
      n++;
      const res = await ctx.request.get(u, { timeout: 60000 }).catch((e) => ({ ok: () => false, status: () => e.message }));
      if (!res.ok()) { console.log(`FAIL ${res.status()} ${u}`); continue; }
      const type = (res.headers()['content-type'] || '').split(';')[0];
      const ext = { 'image/png': '.png', 'image/webp': '.webp', 'image/jpeg': '.jpg', 'image/avif': '.avif', 'image/heic': '.heic' }[type] || path.extname(new URL(u).pathname) || '.jpg';
      const file = path.join(out, String(n).padStart(2, '0') + ext);
      fs.writeFileSync(file, await res.body());
      console.log(`OK ${file}`);
    }
  } finally { await ctx.close(); }
})().catch((e) => { console.error(e.message); process.exit(1); });
