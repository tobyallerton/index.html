// Logs in to Social1, which emails a one-time code (or a magic link) instead of using a password.
// Needs SOCIAL1_EMAIL. SOCIAL1_PASSWORD is used only if the site shows a password box.
// When the code is sent the script prints NEEDS_CODE and waits (up to 10 min) for it to be written to
// <SLIDESHOW_HOME>/social1_code.txt. Run it in the background, ask the user for the code from their
// email, write it to that file, and the script carries on. If Social1 emails a link instead,
// write the whole link to the same file.
// Session is saved in the profile, so this is only needed when the login expires.
// Usage: node social1_login.js [--url https://www.social1.ai/login] [--shot out.png]
const fs = require('fs');
const path = require('path');
const { openProfile, arg, need, firstVisible, sleep, HOME } = require('./lib');

const CODE_BOXES = ['input[autocomplete="one-time-code"]', 'input[name*=code i]', 'input[placeholder*=code i]', 'input[inputmode=numeric]', 'input[maxlength="1"]'];

(async () => {
  const email = need('SOCIAL1_EMAIL');
  const url = arg('url', process.env.SOCIAL1_LOGIN_URL || 'https://www.social1.ai/login');
  const codeFile = path.join(HOME, 'social1_code.txt');
  try { fs.unlinkSync(codeFile); } catch {}
  const { ctx, page } = await openProfile('social1');
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(2500);
    const emailBox = await firstVisible(page, ['input[type=email]', 'input[name*=email i]', 'input[placeholder*=email i]', 'input[autocomplete=username]', 'input[autocomplete=email]']);
    if (!emailBox) { console.log('NO_LOGIN_FORM: probably already logged in. Current URL: ' + page.url()); return; }
    await emailBox.fill(email);
    const send = await firstVisible(page, ['button:has-text("Send code")', 'button:has-text("Get code")', 'button:has-text("Continue")', 'button:has-text("Next")', 'button:has-text("Log in")', 'button:has-text("Sign in")', 'button[type=submit]'], 3000);
    if (send) await send.click(); else await emailBox.press('Enter');
    await sleep(3000);

    const pw = await firstVisible(page, ['input[type=password]'], 2000);
    if (pw && process.env.SOCIAL1_PASSWORD) {
      await pw.fill(process.env.SOCIAL1_PASSWORD);
      await pw.press('Enter');
    } else {
      const codeBox = await firstVisible(page, CODE_BOXES, 15000);
      console.log((codeBox ? 'NEEDS_CODE' : 'NEEDS_CODE_OR_LINK') + ': ask the user for the code (or link) Social1 just emailed, then write it to ' + codeFile);
      const end = Date.now() + 10 * 60 * 1000;
      let code = '';
      while (Date.now() < end && !code) { await sleep(2000); try { code = fs.readFileSync(codeFile, 'utf8').trim(); } catch {} }
      try { fs.unlinkSync(codeFile); } catch {}
      if (!code) throw new Error('Timed out waiting for the Social1 email code.');
      if (/^https?:\/\//.test(code)) {
        await page.goto(code, { waitUntil: 'domcontentloaded', timeout: 60000 });
      } else {
        const box = codeBox || (await firstVisible(page, CODE_BOXES, 5000));
        if (!box) throw new Error('Code box not found, see screenshot.');
        const singleDigitBoxes = await page.locator('input[maxlength="1"]').count();
        if (singleDigitBoxes > 1) { await box.click(); await page.keyboard.type(code, { delay: 80 }); }
        else await box.fill(code);
        const verify = await firstVisible(page, ['button:has-text("Verify")', 'button:has-text("Confirm")', 'button:has-text("Continue")', 'button:has-text("Log in")', 'button:has-text("Sign in")', 'button[type=submit]'], 3000);
        if (verify) await verify.click().catch(() => {});
      }
    }
    await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
    await sleep(3000);
    const stillForm = await firstVisible(page, ['input[type=email]', 'input[type=password]', ...CODE_BOXES], 1000);
    console.log(stillForm ? 'LOGIN_NOT_CONFIRMED (wrong/expired code or captcha), see screenshot' : 'LOGGED_IN: ' + page.url());
  } finally {
    const shot = arg('shot');
    if (shot) await page.screenshot({ path: shot }).catch(() => {});
    await ctx.close();
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
