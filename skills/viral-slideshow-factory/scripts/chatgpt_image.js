// Generates one image in ChatGPT (chatgpt.com) with optional reference images, then saves it.
// Usage:
//   node chatgpt_image.js --prompt-file p.txt --ref product.jpg [--ref style.jpg] --out slide1.png
//                         [--chat-url https://chatgpt.com/c/...] [--timeout 300]
// Prints JSON: {"ok":true,"out":"slide1.png","chat_url":"https://chatgpt.com/c/..."}
// Pass the returned chat_url to the next slide of the same slideshow so the same person/scene carries over.
const fs = require('fs');
const path = require('path');
const { openProfile, arg, args, sleep, firstVisible } = require('./lib');

(async () => {
  const promptFile = arg('prompt-file');
  const prompt = promptFile ? fs.readFileSync(promptFile, 'utf8') : arg('prompt');
  const out = arg('out', 'image.png');
  const refs = args('ref').map((r) => path.resolve(r));
  const chatUrl = arg('chat-url', 'https://chatgpt.com/?model=gpt-4o');
  const timeout = parseInt(arg('timeout', '300'), 10) * 1000;
  if (!prompt) { console.error('--prompt-file or --prompt required'); process.exit(2); }
  for (const r of refs) if (!fs.existsSync(r)) { console.error('Missing ref ' + r); process.exit(2); }
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });

  const { ctx, page } = await openProfile('chatgpt');
  const fail = async (msg) => {
    const shot = out.replace(/\.\w+$/, '') + '.error.png';
    await page.screenshot({ path: shot }).catch(() => {});
    console.log(JSON.stringify({ ok: false, error: msg, screenshot: shot }));
    await ctx.close(); process.exit(1);
  };
  try {
    await page.goto(chatUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    const box = await firstVisible(page, ['#prompt-textarea', 'div[contenteditable="true"]', 'textarea'], 30000);
    if (!box) return fail('No prompt box: not logged in? Run chatgpt_login.js.');
    if (await page.locator('[data-testid="login-button"]').first().isVisible().catch(() => false)) return fail('NOT_LOGGED_IN');

    const before = new Set(await page.$$eval('img', (els) => els.map((e) => e.currentSrc || e.src)));

    if (refs.length) {
      const input = page.locator('input[type=file]').first();
      await input.setInputFiles(refs);
      // wait for upload thumbnails to finish
      await sleep(3000 + refs.length * 2500);
    }
    await box.click();
    await page.keyboard.insertText(prompt);
    await sleep(800);
    const send = await firstVisible(page, ['[data-testid="send-button"]', 'button[aria-label*="Send" i]'], 30000);
    if (send) { for (let i = 0; i < 40 && !(await send.isEnabled()); i++) await sleep(500); await send.click(); }
    else await page.keyboard.press('Enter');

    // Wait for a new, finished generated image in the last assistant turn.
    const end = Date.now() + timeout;
    let src = null, lastSrc = null, stable = 0;
    while (Date.now() < end) {
      await sleep(3000);
      const bodyText = await page.locator('main').innerText().catch(() => '');
      if (/you've hit the (plus|free) plan limit|image generation limit|reached your limit|try again (later|in)/i.test(bodyText.slice(-1500))) return fail('RATE_LIMITED');
      if (/(can't|cannot|unable to) (help|create|generate)|violat(e|es) our content polic/i.test(bodyText.slice(-1200))) return fail('REFUSED_BY_CHATGPT: ' + bodyText.slice(-400).replace(/\s+/g, ' '));
      const cands = await page.$$eval('img', (els) => els
        .filter((e) => e.naturalWidth >= 512 && !e.closest('[data-message-author-role="user"]'))
        .map((e) => ({ src: e.currentSrc || e.src, alt: e.alt || '', blur: getComputedStyle(e).filter })));
      const fresh = cands.filter((c) => !before.has(c.src) && !/blur/.test(c.blur));
      const gen = fresh.filter((c) => /generated/i.test(c.alt)).pop() || fresh.pop();
      const stillWorking = await page.locator('[data-testid="stop-button"], button[aria-label*="Stop" i]').first().isVisible().catch(() => false);
      if (gen) {
        if (gen.src === lastSrc && !stillWorking) stable++; else stable = 0;
        lastSrc = gen.src;
        if (stable >= 2) { src = gen.src; break; }
      }
    }
    if (!src) return fail('TIMEOUT waiting for image');
    let buf;
    if (src.startsWith('data:')) buf = Buffer.from(src.split(',')[1], 'base64');
    else {
      const res = await ctx.request.get(src, { timeout: 60000 });
      if (!res.ok()) return fail('Download failed ' + res.status());
      buf = await res.body();
    }
    fs.writeFileSync(out, buf);
    console.log(JSON.stringify({ ok: true, out, chat_url: page.url() }));
  } catch (e) { return fail(e.message); }
  await ctx.close();
})();
