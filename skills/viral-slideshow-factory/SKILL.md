---
name: viral-slideshow-factory
description: Makes ready-to-post TikTok Shop photo slideshows using Social1 research and ChatGPT images. Modes - "make me 10 slideshows" remakes what is going viral on Social1 now (UK, or US on request) with the same product and format but new people and wording; a viral slideshow link plus the user's product applies that format to it; or the user's own products each get the best viral format. Saves slides with TikTok text, caption, sound, product link, price check and an original-vs-remake comparison. Use whenever the user wants TikTok Shop slideshows, carousels or photo posts, gives a TikTok slideshow link to copy, or mentions Social1, Kalodata or faceless TikTok Shop content.
---

# Viral slideshow factory

Turns what is selling on TikTok Shop right now into **new** slideshows the user only has to post. Claude does the research and the build. **Social1** (or Kalodata) is where the winners are found, and **ChatGPT image** makes the photos. The user posts by hand: never post, schedule or log into TikTok to upload. Automated posting gets accounts banned.

Each remake keeps the *idea* of a proven winner (hook angle, slide structure, selling point). It must look like a different post by a different creator, and the **product must be the real product**: same packaging, colours, shape, logo and label.

## MAIN MODE: remake a slideshow the user sends (user's choice, 9 Nov)

This is how the user works now. They send a TikTok slideshow (a link, often a vm.tiktok.com share link, or screenshots of the slides) and sometimes the product (a link or screenshots of the listing). You recreate it **pretty much the same**: same concept, same slide order and number of slides, same kind of photo on each slide (scene, framing, props, mood), same text placement, style and colour, and nearly the same words. Change it **slightly** so it reads as a different post: a different (AI) person, a slightly different angle, room and props, and lightly reworded text that still says the same thing. Don't "improve" the story, add slides or invent a new angle: the user wants the proven winner, not a new idea.

1. **Get the original.** Link: `scripts/run-chrome.sh tt_fetch.js --url <link> --out <run>/_research/orig` saves every slide, the caption, the sound and stats (meta.json). Screenshots: copy the uploaded images into the same folder. Look at every slide at full size.
2. **Get the product.** Use the product the user names or sends; otherwise the one tagged on the original (Social1 product page or `item.json` anchors). Save the listing photo as `_build/product/listing.jpg` (crop it from the user's screenshots if that's all you have). Note price, commission and sales from what the user sends.
3. **Write it down slide by slide** before generating anything: for each slide, what the photo shows (scene, framing, props, light, who's in it and how), the exact text, its position, style (classic / box / yellow / outline) and size. This is your copy sheet.
4. **Remake each slide.** Photos: ChatGPT prompts that describe the same scene with the small changes, with the product reference attached on every slide that shows the product. Never upload the original creator's images to ChatGPT, and never copy a real person's face: describe the scene instead. Screenshot-style slides (chats, emails, comments, Google, notifications, tweets, Instagram, Facebook): redraw them with `screens.py` / `screens2.py` with the same layout and the wording lightly changed. Text: TikTok Sans (the default), same position and style as the original.
5. **Keep it honest.** Swap anything you can't stand behind: exact prices (use "really cheap atm"), "sale ends Thursday" or "last few left" (unless true), invented reviews, copyrighted characters or film stills (use a similar original image), real people's photos. Say in the reply what you changed and why.
6. **Build, check, send**: make_slides.py, finish.py, look at every slide, then send the slides and post.txt as files. Put the original next to the remake (comparison.png) so the user can see it's the same idea.

## Settings (the user can override any of these in their request)

| Setting | Default |
|---|---|
| Slideshows per run | 3 (the user may say "10" or "20"; for more than 10, confirm they're happy with the run time first, roughly 3–5 minutes per slideshow) |
| Region | UK. Use US when the user says US, or "UK and US" to research both |
| Minimum commission per sale | £2.00 UK, $2.50 US |
| Minimum hook score | 4 out of 5 (see step 2) |
| Output folder | `Slideshows/<YYYY-MM-DD>/` in the current working directory |
| Research window | Last 7 days, falling back to 30 days if there are fewer than about 10 slideshows |

## Daily batch (scheduled morning runs)

**The user's standing rules (apply to every run):**
- **Slide format:** follow "THE STANDARD SLIDESHOW" in `references/recreate.md` (aesthetic hook photo + don't-miss-out product reveal with real sales numbers).
- **No exact prices on slides, titles or captions** (the user doesn't like it). End with a casual "it's cheap right now" line plus the basket, varied each time, e.g. "they're sooo cheap atm 😭 / it's in the basket ⬇️", "honestly such a good price rn", "bargain rn, grab it in the basket ⬇️". Still record the checked price in post.json for the user.
- **Never use Made by Mitchell products** (any product whose name or shop contains "Made By Mitchell" / "MBM"), even if they're top sellers.
- **Always include the P.Louise Christmas bundle** ("Obsessed For Bad Bitch Bundle Christmas Edition", product 1729946120903826144) while it's still selling on Social1: at least one slideshow a day, in a format not used for it the day before.

When this runs as the scheduled morning batch (the prompt says so), these override the settings above:
- **Count:** the number the prompt asks for (e.g. 20). Prefer screenshot formats (chat, email, comment reply) and memes where only one or two photos are needed, because ChatGPT Plus limits how many images can be made in a few hours. On `RATE_LIMITED`, stop generating, finish every slideshow whose images are done, and report how many were made and how many were planned.
- **Commission:** it can't be checked (not on Social1, and TikTok Shop pages block scripts), so don't wait for the user. Only pick products priced **£8 or more**, and in the report list every product with "commission: check in the affiliate app before posting".
- **Repeats of winners are allowed:** before picking, read the earlier runs' folders (`Slideshows/*/`, including each `_build/post.json`) on the `daily-slideshows` branch and on `main`. A product made before **may be picked again if it is still among this week's top sellers on Social1**. Each new slideshow for it must use a **different format** (folder label) and a **new hook** from every earlier one for that product, so the posts don't look the same. At most 2 slideshows per product in one batch, and spread the rest of the batch across other products.
- **Logins:** the saved logins don't survive between sessions, so expect to ask the user for the Social1 code and then the ChatGPT code. Ask in one short message each and keep the scripts waiting (they wait 10 minutes).
- **Learn from the user's own sales first (account: allterca):** before picking products, run `run-chrome.sh social1_capture.js --out <run>/_research/mine_raw.txt --url https://www.social1.ai/creators/allterca --scrolls 6`, then `python3 parse_posts.py <run>/_research/mine_raw.txt > <run>/_research/mine.json` and `python3 my_results.py <run>/_research/mine.json Slideshows > <run>/my_results.md`. Use it when choosing: products under "Products worth repeating" go first (if still selling on Social1), formats with the best £ per 1K views get more of the batch, and avoid products like those under "Views but few sales". Say in report.md how the results changed today's picks.
- **Posting page:** after all slideshows pass `finish.py`, build the phone page with `python3 posting_page.py Slideshows/<date> <scratch>/postpage --mine <run>/_research/mine.json`. Publish it to the **same** artifact every day: read `posting_page_url.txt`, call the Artifact tool with `action: "read"` on that URL first, then publish `<scratch>/postpage/index.html` with `url` set to it, `files` = the contents of `<scratch>/postpage/files.json`, and keep `capabilities: {"downloads": true}`. Remove the previous days' images in the same publish: list the artifact's files (`action: "list", scope: "files"`) and map every `img/<older date>/...` path to `null`. Give the user the page link first in the final message.
- **Send the slides as files too:** saving from the posting page doesn't work in the Claude phone app, so at the end send every slideshow's `slide-N.png` files plus its `post.txt` with the file-sending tool, about 5 slideshows per message in posting order, with a one-line caption naming them. On a phone the user opens a card, then Share → Save Image.
- **Output:** commit the finished folders (not `_research/` or `_build/original/`, which `.gitignore` already skips) and push to the `daily-slideshows` branch, then send the user each slideshow's `comparison.png` and the `report.md`.

## Pick the mode

- **A. Trending ("make me N slideshows")**: research Social1, pick N winners, remake each. This is the default.
- **B. Format from a link**: the user gives a TikTok slideshow link (or screenshots) and their product (TikTok Shop link, photo, or both). Read that slideshow, and apply its format to their product. Skip winner-picking; still run the hook and commission checks and tell the user if either fails, then do what they decide.
- **C. My products**: the user gives one or more of their own products. For each, find the best format (see step 3C) and make one slideshow per product unless they ask for more.

The user can mix them, for example "5 trending ones plus one for this product".

## 0. Setup (every run)

### Browser: choose one route and stick with it for the run

1. **Claude in Chrome (preferred when its tools are available).** It uses the user's own Chrome, which is already logged into Social1 and ChatGPT, so there are no login codes. Load the chrome-browser skill first if it exists. Work in a new tab and never close the user's tabs. Use it to browse Social1 and TikTok and to read pages. For ChatGPT image generation it must be able to attach the product photo and save the result to disk. If it can't do either, use the script below for that one step.
2. **Bundled Playwright scripts** (any computer, including cloud sessions). Scripts live in `scripts/` next to this file; call that folder `$S`.
   - First time: `cd $S && npm install && npx playwright install chromium`. If Google Chrome is installed, `BROWSER_CHANNEL=chrome` makes the sites less likely to block the browser.
   - **In a cloud session** Social1 and ChatGPT turn away a hidden (headless) browser. Run every browser script through the launcher, which uses real Chrome on a virtual screen: `skills/viral-slideshow-factory/scripts/run-chrome.sh <script.js> [args]` (from the repo root), for example `skills/viral-slideshow-factory/scripts/run-chrome.sh social1_login.js --shot /tmp/s1.png`. The repo's `.claude/settings.json` allows this launcher. If a session's safety check still refuses it, tell the user and let them decide; don't look for other ways round a site's bot check.
   - Only one browser script can use a site's saved profile at a time. Never run two scripts for the same site at once.
   - Credentials come only from environment variables: `SOCIAL1_EMAIL`, `CHATGPT_EMAIL`, `CHATGPT_PASSWORD`. Never write them into a file, report or chat. If they're missing, ask the user to set them.
   - Sessions are saved in `~/.tiktok-shop-slideshows/profiles/` (shared with the older tiktok-shop-slideshows skill), so logins only re-run when a session expires.
   - `node $S/social1_login.js --shot /tmp/s1.png` **in the background**. If it prints `NEEDS_CODE`, ask: "Social1 has just emailed you a login code. What is it?" and write it with `echo 123456 > ~/.tiktok-shop-slideshows/social1_code.txt` (or the whole link, if they got a link). Wait for `LOGGED_IN` or `NO_LOGIN_FORM`.
   - `node $S/chatgpt_login.js --shot /tmp/gpt.png` **in the background**. If it prints `NEEDS_CODE`, ask: "ChatGPT has just sent you a login code. What is it?" and write it to `~/.tiktok-shop-slideshows/chatgpt_code.txt`. Do Social1 first, then ChatGPT, so the user isn't juggling two codes. Codes expire quickly, so ask straight away.
   - Captchas, Cloudflare checks or Google/Apple sign-in can't be passed by a script. Say so plainly: the fix is to run once with `HEADED=1` on their own computer and log in by hand.
   - See pages with `node $S/snap.js --site <social1|tiktok> --url <url> --out <dir> [--scrolls 4] [--click "UK"]`, which saves screenshots, visible text, links and image URLs. Read the screenshots. Download images with `node $S/download.js --site <site> --out <dir> <url> ...`.

Python 3 with Pillow is needed for the text and comparison steps (`pip install pillow` if `import PIL` fails).

### Run folder

`Slideshows/<YYYY-MM-DD>/`, with one folder per slideshow named `NN - <Product short name> - <FORMAT>`, for example `01 - Rosemary hair spray - POV` or `04 - Fleece balaclava - SELFIE`. Inside each one:

```
NN - Product - FORMAT/
  slide-1.png … slide-N.png   finished slides to post (with text)
  post.txt                    title, caption, hashtags, sound, product link, price check
  comparison.png              viral original (top) vs our remake (bottom)
  preview.png                 our slides side by side
  _build/                     plan.md, slides.json, post.json, prompts, raw images, original slides
```

## 1. Research (modes A and C)

Read `references/social1.md` first. It has the page layout and the navigation notes from earlier runs. Follow them, and **update the Navigation notes** whenever the site differs, so the next run is faster.

Collect from Social1 **Videos** (set the region, the time range and the photo/slideshow filter if there is one):
- Top slideshows (photo posts, not videos) with: link, creator, product, views, likes, comments, Creator GMV, post date, and slide count.
- For each candidate's product: name, shop, current sale price, commission rate or £/$ per sale, units and GMV trend, product link, and the largest product images you can get.

If the user uses **Kalodata** instead, apply the same steps there and record its navigation in the notes file under a Kalodata heading.

## 2. The must-pass filters

Every winner (and every remake's new hook) must pass both. If fewer than N pass, make fewer and say why. Never lower the bar to fill the batch.

**Commission per sale ≥ the minimum** (£2.00 UK / $2.50 US). Commission = the price buyers actually pay (the sale price, not the crossed-out one) × the open-collaboration commission rate. If Social1 shows a £/$ amount, use it. If neither is shown, check the TikTok Shop product page. If you still can't find it, the product **fails**; don't guess. Filter products first, so you don't analyse posts for products that pay too little.

**Hook score ≥ 4 out of 5**, one point each for slide 1:
1. Stops the scroll in under a second: a short line (roughly 3–10 words) plus a striking image.
2. Speaks to a specific viewer, problem or desire, not a vague "check this out".
3. Opens a loop: curiosity, a reveal, a list, price shock, before and after, a comment reply.
4. Leads naturally to the product's selling point.
5. Works without that creator's face, fame, inside joke or an expired trend.

Reject on sight: "link in bio", "TikTok made me buy it" with nothing else, only the product name, clickbait the slides don't pay off, and anything relying on shock or mocking people. Views alone prove nothing, because posts can go viral off a sound or a big account.

Also skip restricted categories (supplements with health claims, weight loss, adult, weapons) unless the user insists, and products without a clean photo to copy.

Pick N winners. Prefer products that appear in several winning slideshows, products that are rising, and different products across the batch unless the user wants one product.

## 3. Get the original and break it down

**A (trending):** open each winner's TikTok post (Social1's open-in-new-tab icon on the card) and save every slide to `_build/original/`. These are for analysis and for the comparison image only.

**B (link):** open the user's link the same way. A TikTok photo post is a swipeable set of images; use `snap.js --site tiktok --scrolls 0` and the image URLs in `page.json`, or screenshots if the images won't download. If the link is a video rather than a photo post, say so and ask whether to turn its idea into a slideshow.

**C (my products):** for each product, search Social1 for top slideshows of **that product** first, then of similar products in the same category and price band. Score the candidates with step 2 and use the best one as the format. Read `references/formats.md` for common winning formats and pick the one that best fits the product if nothing suitable is trending. Say in the report which format was chosen and why.

For each original write down in `_build/plan.md`:
- **Hook**: slide 1 text and image, and *why* it stops the scroll.
- **Structure**: what each slide does (hook, problem, reveal, close-up, proof, offer, CTA).
- **Visual style**: phone photo or editorial, setting, lighting, how the product is held, the person's role (hands only, mirror selfie, face), and text style and position.
- **Selling angle** and the **sound** used (name and link, from the post page).
- **Format label** for the folder name: one word such as POV, SELFIE, LIST, COMMENT-REPLY, BEFORE-AFTER, GIFT, DUPE, ROUTINE or UNBOXING.

## 4. Plan the remake

Read `references/recreate.md` and follow it. In short:
- Keep the hook angle, slide count (±1) and each slide's job.
- Change **at least two** of: the person, the setting, props, palette and lighting, angle and framing. Rewrite every line of text. The original creator should recognise the format, not their post.
- **Never upload the original's slides to ChatGPT.** Describe the composition in words. The only image references are the product photo(s) and earlier slides of *your own* remake.
- Write 3 hook options, score them, use the best and list the other two in `plan.md`.
- Get a clean product photo into `_build/product/`, ideally a packshot from the TikTok Shop listing. For mode B/C, the user's photo is fine if it's clear.

Add a per-slide plan: the image prompt, the text, its position and style (`classic` or `box`, matching the original; `--color yellow` when the original uses TikTok yellow).

**The last slide always ends with a call to action**, even if the original didn't have one: a short line such as "linked in the basket", "tap the orange basket" or "it's in the basket below". Keep it soft: no fake urgency like "sale ends soon" unless the listing really shows an end date. `finish.py` refuses a slideshow whose last slide has none.

## 5. Make the images (ChatGPT)

Per slide (script route):
```
node $S/chatgpt_image.js --prompt-file _build/slide-1.prompt.txt --ref _build/product/packshot.jpg --out _build/raw/slide-1.png [--chat-url <chat_url from the previous slide>]
```
- Slide 1 starts a new chat; pass the returned `chat_url` to later slides so the same person and scene carry over.
- Ask for a **vertical 2:3 portrait**, real phone-photo look, with no text, captions, watermarks or other logos.
- `RATE_LIMITED`: stop, tell the user how far you got, and keep the plan so the run can continue later. `REFUSED_BY_CHATGPT`: rephrase within policy. `NOT_LOGGED_IN`: log in again. Other errors: read the `.error.png`.

**Get the product's real size first** and put a SIZE line in every prompt (see `references/recreate.md`). **Check every image yourself** (including scale against hands and everyday objects) against the product photo: shape, colours, label layout, logo, cap or pump, and realistic size. Also check hands, fake-looking text and anything uncanny. If the product is wrong, regenerate in the same chat with a short correction. After 3 tries, flag the slide instead of shipping a wrong product.

## 6. Add the text

No slide ships without on-screen text. Write `_build/slides.json`:
```json
{"style": "classic", "slides": [
  {"image": "raw/slide-1.png", "text": "POV: your hair finally grows", "position": "top", "size": 84},
  {"image": "raw/slide-2.png", "text": "2 sprays every morning"}
]}
```
Run `python3 $S/make_slides.py <slideshow>/_build`, then move the results up: `mv <slideshow>/_build/slide-*.png <slideshow>/_build/preview.png <slideshow>/`.
Open `preview.png` and check: text on every slide, readable, not covering the product, not cut off. If the text looks off compared with real TikTok text (the creator in the demo flagged this as a common weak spot), fix size, position or style and run it again.

## 7. The posting pack

Write `_build/post.json`:
```json
{
  "title": "short title for the post (TikTok photo posts have a title field)",
  "caption": "caption text, emoji welcome here",
  "hashtags": ["#tiktokshop", "#..."],
  "sound": {"name": "sound name", "url": "link", "why": "used on the original / currently trending"},
  "product": {"name": "...", "url": "TikTok Shop product link", "currency": "GBP",
              "price": 14.99, "was_price": 24.99, "commission_rate": 0.15, "commission_per_sale": 2.25,
              "checked_at": "YYYY-MM-DD HH:MM", "checked_on": "where you checked (product page / Social1)"},
  "source": {"mode": "A|B|C", "url": "original post link", "creator": "@...", "views": "1.2M", "gmv": "£45.3K", "format": "POV"},
  "hooks": {"used": "...", "score": 5, "alternatives": ["...", "..."]}
}
```
**Price check:** open the product page right before writing this and record the price you saw and when. Any price written on a slide or in the caption must match `price` (or `was_price` for a crossed-out price). If the listing had no sale, set `was_price` to null.

Then run:
```
python3 $S/finish.py <slideshow folder>
```
This checks the pack (price in the text matches the checked price, nothing missing, risky claims flagged), writes `post.txt` and builds `comparison.png` from `_build/original/` and the finished slides. Fix anything it reports as `ERROR`, and read each `WARN` before deciding.

## 8. Gallery and report

When all slideshows are done:
```
python3 $S/gallery.py Slideshows/<date>
```
This writes `Slideshows/<date>/index.html`, a page showing each original next to our remake, with the caption, sound and product link and copy buttons. Tell the user to open it in their browser.

Write `Slideshows/<date>/report.md`:
1. **What's winning**: a table of the slideshows and products looked at, with views, GMV, commission per sale and hook score, the patterns you noticed, and strong performers you rejected and why.
2. **Per slideshow**: folder, source and metrics, format, original hook and score, new hook and alternatives, what was kept and changed, and any flagged slides.
3. **Before posting**: the safety reminders below.

Finish with a short chat summary: the folder path, how many slideshows were made (and why any were skipped), and show each `comparison.png`.

## Safety rules (apply them, and remind the user in the report)

- **AI label:** TikTok requires realistic AI-generated images to be labelled. Tell the user to switch on "AI-generated content" when posting each one.
- **No health or medical claims** and no invented personal results ("cured my acne", "lost 5kg", fake before and after photos). Benefit claims come only from the product listing. UK ASA/CMA and US FTC rules treat the rest as misleading, and TikTok Shop removes it.
- **No fake prices:** only the checked price, and no invented discounts or "only 3 left" urgency.
- No real people's faces, celebrity lookalikes, or other brands' logos. Never upload the original creator's images to ChatGPT.
- The user posts manually. Don't post, schedule or automate TikTok in any way.

## Troubleshooting

- Social1 layout changed: screenshot, look, adjust the clicks, then update the navigation notes.
- ChatGPT layout changed: `chatgpt_image.js` has fallback selectors. If they fail, read the `.error.png`, update the selectors and tell the user.
- TikTok slide images won't download: take screenshots of each slide instead (crop to the image) for the comparison; they're only used for analysis.
