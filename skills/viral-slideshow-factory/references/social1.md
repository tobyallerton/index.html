# Social1: what to pull and how to get there

Social1 (social1.ai) is a TikTok Shop analytics site. Its sections and filter names change, so treat these notes as a starting point, confirm with a screenshot, and **update the Navigation notes whenever you learn something**.

## What "top performing" means
Rank in this order and say in the report which you used:
1. **GMV / sales** tied to the post or creator (it sells, not just entertains)
2. **Recent growth** (the purple "trend" number on cards, views gained in the period)
3. **Views** and engagement ((likes + comments + shares) / views)

Set every time: **region** (UK or US), **time range** (7 days, falling back to 30), and **content type = photo/slideshow** if the filter exists. If not, slideshows show a photo/carousel look rather than a video with a duration; check by opening the post.

## Product data to record
Name, shop, category, sale price and crossed-out price, commission rate and/or commission per sale (**required**), units and GMV with trend, how many creators promote it, product link, and the largest image URLs.

## Picking winners
- A product in more than one top slideshow points to the product, not one creator's luck.
- Rising beats huge-but-flat.
- Skip restricted categories (supplements with health claims, weight loss, adult, weapons) unless the user insists.
- Skip products whose only photos are tiny or heavily edited.

## Navigation notes (update these each run)
- Confirmed 2026-11-03 and 2026-11-06.
- **Cloud sessions:** Social1 (Vercel checkpoint) and ChatGPT block headless Chromium. Run every script as `HEADED=1 BROWSER_CHANNEL=chrome xvfb-run -a -s "-screen 0 1400x1000x24" node ...` (this is the same real Chrome a person uses, shown on a virtual screen).
- Login: /login is a 404. Sign-in is a pop-up from "Sign In" in the left sidebar of https://www.social1.ai/ : email box, then "Login", then a 6-digit emailed code (`social1_login.js` handles it). Logged in = the sidebar shows the user's first name instead of "Sign In".
- Home = Videos list; region selector top right (UK).
- Filters are URL params, so go straight to:
  `https://www.social1.ai/?tsStart=<YYYY-MM-DD, 7 days ago>&tsEnd=<today>&perf=topConverters&isSlideshow=true`
  - Date: Today / Last 3 / 7 / 30 days. Performance (`perf`): trending, biggestHits, recentlyPosted, topCreators, topConverters.
  - The funnel button (`button:has(svg.lucide-funnel)`) opens Ad Type / AI Content / Content Type (All, Videos only, Slideshows only = `isSlideshow=true`) / Sort By / Posted within. 12 cards per page.
- Best data: the page's own document response (RSC payload; capture with `page.on('response')` on the page URL) contains JSON per post: video_id, handle, views, likes, **gmv (per post)**, time_posted, is_slideshow, product_data {product_id, name, price_value, units_sold, img_url}, thumbnail, video_url. The card's "Creator GMV (30D)" is the creator's total, not the post's. **Commission isn't in this payload** — ask the user to confirm commission for the shortlisted products if it can't be found.
- Each card's external-link button opens the TikTok post.
- Product image: `https://social-listening-images.s3.us-east-2.amazonaws.com/products/<product_id>.jpg` (800x800 main listing image; can have text or infographics, so crop it).
- Slides: TikTok post HTML (`__UNIVERSAL_DATA_FOR_REHYDRATION__` → webapp.video-detail.itemInfo.itemStruct.imagePost.images[].imageURL.urlList) has every slide plus live stats; images are on `*.tiktokcdn-us.com` / `*.tiktokcdn-eu.com`.
- Top Products: https://www.social1.ai/products (price, 32-day GMV, views, videos, sold; all content types).
- TikTok Shop product pages (tiktok.com/shop/uk/pdp/<id>) show a "Security Check" captcha to scripts, so the price check may need the user.
- ChatGPT: `ws.chatgpt.com` may be blocked, so replies don't stream; reload the chat to pick up a finished image.
- Cloud network allowlist needed: social1.ai, www.social1.ai, d1lj461v9v7c81.cloudfront.net, social-listening-images.s3.us-east-2.amazonaws.com, tiktok.com hosts, tiktokcdn-eu.com / tiktokcdn-us.com hosts, chatgpt.com, oaistatic.com / oaiusercontent.com hosts, auth.openai.com.

## Kalodata (if the user uses it instead)
- _unknown, fill in on first use_
