#!/usr/bin/env python3
"""Turn raw Social1 page data (from social1_capture.js) into a clean JSON list of posts.

Usage: python3 parse_posts.py raw.txt [more_raw.txt ...] > posts.json
Each post: video_id, handle, views, likes, comments, gmv, time_posted, is_slideshow, video_url,
product_data {product_id, name, price_value, units_sold, img_url, categories}. Duplicates are merged.
"""
import json, sys

def objects(text):
    """Yield every JSON object that contains "video_id", in plain or escaped (\\") form."""
    for src in (text, text.replace('\\\\"', '\\"').replace('\\"', '"')):
        i = 0
        while True:
            k = src.find('"video_id"', i)
            if k < 0:
                break
            start = src.rfind("{", 0, k)
            depth, j = 0, start
            while 0 <= j < len(src):
                c = src[j]
                if c == "{": depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0: break
                j += 1
            i = k + 10
            if start < 0 or depth != 0:
                continue
            try:
                yield json.loads(src[start:j + 1])
            except Exception:
                continue

def main():
    posts = {}
    for f in sys.argv[1:]:
        for d in objects(open(f, encoding="utf-8", errors="ignore").read()):
            vid = str(d.get("video_id") or "")
            if vid and (vid not in posts or len(json.dumps(d)) > len(json.dumps(posts[vid]))):
                posts[vid] = d
    out = sorted(posts.values(), key=lambda p: -(p.get("views") or 0))
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
