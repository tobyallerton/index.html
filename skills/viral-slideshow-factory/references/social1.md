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

Seen in a screen recording from November 2026; confirm on first run:
- Site: https://www.social1.ai/ . Login: https://www.social1.ai/login (emailed code).
- Left sidebar: **Videos**, **Products**, **Creators**.
- **Videos** page: header filters "Viral content from", "Performance", "Filter by category", "Filter by product", and a region/flag selector top right (UK/US).
- Each video card shows: rank (#1, #2 …) with views gained, a "$ Ad" badge on some, product thumbnail and name with "Save Product", creator handle and age of post, **Creator GMV (30D)**, then views / likes / comments / growth, and buttons **AI Insights** and **Transcribe**. Top-right icons on the card: bookmark, **open in new tab** (goes to the TikTok post), share.
- Results are paged (1, 2 … 5) at the bottom.
- Where to filter to slideshows only: _unknown, fill in_
- Where full-size product images are: _unknown, fill in_ (fallback: open the TikTok Shop product page)
- Gotchas: from a cloud server (Playwright, headless) Social1 shows a "Vercel Security Checkpoint — Failed to verify your browser (Code 29)" page instead of the login form. Social1 research needs Claude in Chrome on the user's own computer; in the cloud, only mode B (user gives the slideshow link) can run.

## Kalodata (if the user uses it instead)
- _unknown, fill in on first use_
