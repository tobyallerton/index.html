// Shared browser helpers. One persistent Chrome profile per site keeps you
// logged in between runs, so the password is only typed when the session expires.
const path = require('path');
const os = require('os');
const fs = require('fs');

function loadPlaywright() {
  try { return require('playwright'); } catch (_) {}
  try { return require(path.join(__dirname, 'node_modules', 'playwright')); } catch (_) {}
  console.error('Playwright not found. Run: cd "' + __dirname + '" && npm install && npx playwright install chromium');
  process.exit(2);
}

const HOME = process.env.SLIDESHOW_HOME || path.join(os.homedir(), '.tiktok-shop-slideshows');

async function openProfile(site, { headed } = {}) {
  const { chromium } = loadPlaywright();
  const dir = path.join(HOME, 'profiles', site);
  fs.mkdirSync(dir, { recursive: true });
  const show = headed ?? (process.env.HEADED === '1');
  const opts = {
    headless: !show,
    viewport: { width: 1400, height: 1000 },
    locale: 'en-GB',
    timezoneId: 'Europe/London',
    acceptDownloads: true,
    args: ['--disable-blink-features=AutomationControlled'],
  };
  if (process.env.CHROME_PATH) opts.executablePath = process.env.CHROME_PATH;
  else opts.channel = process.env.BROWSER_CHANNEL || undefined; // e.g. "chrome" to use installed Chrome
  const ctx = await chromium.launchPersistentContext(dir, opts);
  const page = ctx.pages()[0] || (await ctx.newPage());
  return { ctx, page };
}

function arg(name, fallback) {
  const i = process.argv.indexOf('--' + name);
  return i > -1 ? process.argv[i + 1] : fallback;
}
function args(name) {
  const out = [];
  process.argv.forEach((a, i) => { if (a === '--' + name) out.push(process.argv[i + 1]); });
  return out;
}
function need(envName) {
  const v = process.env[envName];
  if (!v) { console.error(`Missing ${envName}. Set it as an environment variable / secret, never in a file in this skill.`); process.exit(2); }
  return v;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function firstVisible(page, selectors, timeout = 8000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    for (const s of selectors) {
      const loc = page.locator(s + ' >> visible=true').first();
      if (await loc.isVisible().catch(() => false)) return loc;
    }
    await sleep(250);
  }
  return null;
}

module.exports = { openProfile, arg, args, need, sleep, firstVisible, HOME };
