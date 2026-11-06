#!/usr/bin/env python3
"""Summarise what's selling on the user's own account, to steer the next batch.

Usage: python3 my_results.py my_posts.json <Slideshows folder> > my_results.md
- my_posts.json: parse_posts.py output for https://www.social1.ai/creators/<handle>
- Slideshows folder: earlier runs; each slideshow's _build/post.json holds its product link and format,
  so the user's posts can be matched to the format that was used (same product, posted 0-10 days after).

Writes a short Markdown report: best and worst posts by sales per 1,000 views, products worth repeating,
and (when matches exist) which formats sell best for this account.
"""
import glob, json, os, re, sys
from collections import defaultdict
from datetime import datetime, timedelta

def pid_from_url(u):
    m = re.search(r"(\d{15,20})", u or "")
    return m.group(1) if m else None

def day(s):
    try: return datetime.fromisoformat(str(s).replace(" ", "T")[:19])
    except Exception: return None

def main():
    posts = json.load(open(sys.argv[1], encoding="utf-8"))
    root = sys.argv[2]
    made = []  # (product_id, date, format, folder)
    for pj in glob.glob(os.path.join(root, "*", "*", "_build", "post.json")):
        try: p = json.load(open(pj, encoding="utf-8"))
        except Exception: continue
        folder = pj.split(os.sep)[-3]; date = pj.split(os.sep)[-4]
        pid = (p.get("product") or {}).get("id") or pid_from_url((p.get("product") or {}).get("url"))
        fmt = (p.get("source") or {}).get("format") or folder.rsplit(" - ", 1)[-1]
        made.append((pid, day(date), fmt, f"{date}/{folder}"))

    rows = []
    for p in posts:
        v = p.get("views") or 0; g = p.get("gmv") or 0
        pd = p.get("product_data") or {}
        pid = str(pd.get("product_id") or p.get("product_id") or "")
        t = day(p.get("time_posted"))
        match = next((m for m in made if m[0] == pid and m[1] and t and timedelta(0) <= t - m[1] <= timedelta(days=10)), None)
        rows.append({"date": (p.get("time_posted") or "")[:10], "views": v, "gmv": g,
                     "per1k": (g / v * 1000) if v else 0, "product": pd.get("name", "")[:70], "pid": pid,
                     "price": pd.get("price_value"), "format": match[2] if match else None,
                     "folder": match[3] if match else None, "url": p.get("video_url")})
    rows.sort(key=lambda r: -r["per1k"])

    print(f"# What's selling on your account ({len(rows)} recent posts on Social1)\n")
    print("| Posted | Views | Sales | £ per 1K views | Product | Our format |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['date']} | {r['views']:,} | £{r['gmv']:,.0f} | £{r['per1k']:.2f} | {r['product']} | {r['format'] or '-'} |")
    good = [r for r in rows if r["gmv"] >= 300 and r["per1k"] >= 2]
    print("\n## Products worth repeating (they sold for you)")
    for r in good or []:
        print(f"- {r['product']} — £{r['gmv']:,.0f} from {r['views']:,} views (£{r['per1k']:.2f} per 1K)")
    if not good: print("- none yet")
    weak = [r for r in rows if r["views"] >= 100000 and r["per1k"] < 1]
    print("\n## Views but few sales (hook works, product or offer doesn't)")
    for r in weak: print(f"- {r['product']} — {r['views']:,} views, £{r['gmv']:,.0f}")
    if not weak: print("- none")
    fm = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        if r["format"]: fm[r["format"]][0] += 1; fm[r["format"]][1] += r["views"]; fm[r["format"]][2] += r["gmv"]
    print("\n## Formats (only posts matched to our slideshows)")
    if fm:
        for f, (n, v, g) in sorted(fm.items(), key=lambda kv: -(kv[1][2] / kv[1][1] if kv[1][1] else 0)):
            print(f"- {f}: {n} posts, {v:,} views, £{g:,.0f} (£{(g / v * 1000) if v else 0:.2f} per 1K)")
    else:
        print("- no matches yet (needs posts made from these slideshows)")

if __name__ == "__main__":
    main()
