// Logs in to chatgpt.com with CHATGPT_EMAIL / CHATGPT_PASSWORD and keeps the session in a saved profile.
// After the password, OpenAI may ask for a code (sent by WhatsApp, SMS, email or an authenticator app).
// If it does, the script prints NEEDS_CODE and waits (up to 10 min) for the code
// to be written to <SLIDESHOW_HOME>/chatgpt_code.txt. Run it in the background, ask the user for the
// code, write it to that file, and the script carries on.
// Usage: node chatgpt_login.js [--shot out.png]
const fs = require('fs');
const path = require('path');
const { openProfile, arg, need, firstVisible, sleep, HOME } = require('./lib');

async function isLoggedIn(page) {
  // Logged out pages show a "Log in" button; logged-in pages show the account menu / Library / Projects.
  const loginBtn = await page.locator('[data-testid="login-button"], button:has-text("Log in") >> visible=true').first().isVisible().catch(() => false);
  if (loginBtn) return false;
  return await page.locator('[data-testid="profile-button"], [data-testid="accounts-profile-button"], nav :text("Library"), nav :text("Projects"), #prompt-textarea').first().isVisible().catch(() => false);
}

(async () => {
  const email = need('CHATGPT_EMAIL');
    const codeFile = path.join(HOME, 'chatgpt_code.txt');
  try { fs.unlinkSync(codeFile); } catch {}
  const { ctx, page } = await openProfile('chatgpt');
  try {
    await page.goto('https://chatgpt.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(4000);
    if (await isLoggedIn(page)) { console.log('ALREADY_LOGGED_IN'); return; }
    const loginBtn = await firstVisible(page, ['[data-testid="login-button"]', 'button:has-text("Log in")', 'a:has-text("Log in")'], 15000);
    if (!loginBtn) throw new Error('No "Log in" button. Possibly a Cloudflare check, see screenshot.');
    await loginBtn.click();
    const emailBox = await firstVisible(page, ['input[type=email]', 'input[name=email]', 'input[name=username]', 'input[autocomplete=email]'], 30000);
    if (!emailBox) throw new Error('Email box never appeared (Cloudflare/captcha?).');
    await emailBox.fill(email);
    await emailBox.press('Enter');
    await sleep(4000);
    // If Enter didn't move on, click the dialog's own Continue (a bare button[type=submit] can hit the chat box and close the dialog).
    if (await emailBox.isVisible().catch(() => false)) await (await firstVisible(page, ['[role=dialog] button:has-text("Continue")', 'button:has-text("Continue")'], 3000))?.click();
    // Some accounts get a password box, others go straight to an emailed code.
    const CODES = ['input[autocomplete="one-time-code"]', 'input[name=code]', 'input[name*=code i]', 'input[placeholder*=code i]', 'input[inputmode=numeric]', 'input[maxlength="1"]'];
    const next = await firstVisible(page, ['input[type=password]', ...CODES], 40000);
    await page.screenshot({ path: path.join(HOME, 'chatgpt_step.png') }).catch(() => {});
    if (!next) throw new Error('Neither a password box nor a code box appeared. The account may use Google/Apple/Microsoft sign-in, which needs a real person.');
    if (await next.evaluate((e) => e.type === 'password')) {
      if (!process.env.CHATGPT_PASSWORD) throw new Error('ChatGPT asked for a password but CHATGPT_PASSWORD is not set.');
      await next.fill(process.env.CHATGPT_PASSWORD);
      await (await firstVisible(page, ['button[type=submit]', 'button:has-text("Continue")'], 5000))?.click();
    }
    // Possible email-code step.
    const codeBox = await firstVisible(page, ['input[autocomplete="one-time-code"]', 'input[name=code]', 'input[name*=code i]', 'input[placeholder*=code i]', 'input[inputmode=numeric]', 'input[maxlength="1"]'], 25000);
    if (codeBox) {
      console.log('NEEDS_CODE: ask the user for the ChatGPT login code just sent to them (by email, WhatsApp or SMS), then write it to ' + codeFile);
      const end = Date.now() + 10 * 60 * 1000;
      let code = '';
      while (Date.now() < end && !code) { await sleep(2000); try { code = fs.readFileSync(codeFile, 'utf8').trim(); } catch {} }
      if (!code) throw new Error('Timed out waiting for the ChatGPT login code.');
      if ((await page.locator('input[maxlength="1"]').count()) > 1) { await codeBox.click(); await page.keyboard.type(code, { delay: 80 }); }
      else await codeBox.fill(code);
      await (await firstVisible(page, ['button[type=submit]', 'button:has-text("Continue")'], 5000))?.click();
      try { fs.unlinkSync(codeFile); } catch {}
    }
    const end = Date.now() + 45000;
    while (Date.now() < end && !(await isLoggedIn(page))) await sleep(1500);
    console.log((await isLoggedIn(page)) ? 'LOGGED_IN' : 'LOGIN_NOT_CONFIRMED, see screenshot');
  } finally {
    const shot = arg('shot');
    if (shot) await page.screenshot({ path: shot }).catch(() => {});
    await ctx.close();
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
