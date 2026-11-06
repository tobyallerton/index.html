// Opens a page with a saved logged-in profile and dumps what Claude needs to read it:
// screenshot(s), visible text, links, and image/video URLs. Optional actions run first.
// Usage:
//   node snap.js --site social1 --url <url> --out <dir> [--scrolls 4] [--click "Text"] [--click "css=.selector"] [--wait 3000]
const fs = require('fs');
const path = require('path');
const { openProfile, arg, args, sleep } = require('./lib');

(async () => {
  const site = arg('site', 'social1');
  const url = arg('url');
  const out = arg('out', 'snap');
  const scrolls = parseInt(arg('scrolls', '3'), 10);
  const wait = parseInt(arg('wait', '3000'), 10);
  if (!url) { console.error('--url required'); process.exit(2); }
  fs.mkdirSync(out, { recursive: true });
  const { ctx, page } = await openProfile(site);
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
    await sleep(wait);
    for (const c of args('click')) {
      // Prefer clickable things (buttons, tabs, links, options) whose name matches, then exact text, then partial text.
      let loc = null;
      if (c.startsWith('css=')) loc = page.locator(c.slice(4)).first();
      else {
        for (const cand of [
          page.getByRole('button', { name: c }), page.getByRole('tab', { name: c }), page.getByRole('link', { name: c }),
          page.getByRole('option', { name: c }), page.getByRole('menuitem', { name: c }),
          page.getByText(c, { exact: true }), page.getByText(c),
        ]) { if (await cand.first().isVisible().catch(() => false)) { loc = cand.first(); break; } }
        loc = loc || page.getByText(c).first();
      }
      await loc.click({ timeout: 10000 }).catch((e) => console.log('CLICK_FAILED ' + c + ': ' + e.message.split('\n')[0]));
      await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
      await sleep(1500);
    }
    await page.screenshot({ path: path.join(out, 'shot-0.png') });
    for (let i = 1; i <= scrolls; i++) {
      await page.mouse.wheel(0, 900);
      await sleep(1500);
      await page.screenshot({ path: path.join(out, `shot-${i}.png`) });
    }
    const data = await page.evaluate(() => {
      const abs = (u) => { try { return new URL(u, location.href).href; } catch { return u; } };
      const links = [...document.querySelectorAll('a[href]')].map((a) => ({ text: a.innerText.trim().slice(0, 120), href: abs(a.getAttribute('href')) })).filter((l) => l.text || l.href);
      const imgs = [...document.querySelectorAll('img')].map((i) => ({ src: abs(i.currentSrc || i.src), alt: (i.alt || '').slice(0, 120), w: i.naturalWidth, h: i.naturalHeight })).filter((i) => i.src && i.w >= 120);
      const media = [...document.querySelectorAll('video, video source')].map((v) => abs(v.src || v.getAttribute('src') || '')).filter(Boolean);
      return { url: location.href, title: document.title, text: document.body.innerText, links, imgs, media };
    });
    fs.writeFileSync(path.join(out, 'page.txt'), data.text);
    fs.writeFileSync(path.join(out, 'page.json'), JSON.stringify({ ...data, text: undefined }, null, 2));
    const loginWall = /log ?in|sign ?in/i.test(data.title) || (await page.locator('input[type=password]').first().isVisible().catch(() => false));
    console.log(JSON.stringify({ url: data.url, title: data.title, links: data.links.length, images: data.imgs.length, loginWall, out }));
  } finally { await ctx.close(); }
})().catch((e) => { console.error(e.message); process.exit(1); });
