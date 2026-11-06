#!/usr/bin/env python3
"""Build index.html for a run folder: every slideshow's viral original next to our remake,
with title, caption, sound, product link and price check, and copy buttons.

Usage: python gallery.py "Slideshows/<date>"
Open the resulting index.html in a browser (it uses relative paths, so keep it in the folder).
"""
import glob, html, json, os, re, sys
from urllib.parse import quote

def numkey(p):
    n = re.findall(r"\d+", os.path.basename(p))
    return (int(n[-1]) if n else 0, p)

def rel(run, p):
    return "/".join(quote(x) for x in os.path.relpath(p, run).split(os.sep))

def imgs(run, paths):
    return "".join(f'<a href="{rel(run, p)}" target="_blank"><img loading="lazy" src="{rel(run, p)}"></a>' for p in paths)

def main():
    run = os.path.abspath(sys.argv[1])
    cards = []
    for d in sorted(x for x in glob.glob(os.path.join(run, "*")) if os.path.isdir(x)):
        pj = os.path.join(d, "_build", "post.json")
        ours = sorted(glob.glob(os.path.join(d, "slide-*.png")), key=numkey)
        if not ours:
            continue
        post = json.load(open(pj, encoding="utf-8")) if os.path.exists(pj) else {}
        orig = sorted([p for p in glob.glob(os.path.join(d, "_build", "original", "*"))
                       if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))], key=numkey)
        e = lambda v: html.escape(str(v or ""))
        p, s, src = post.get("product", {}), post.get("sound", {}), post.get("source", {})
        sym = {"GBP": "£", "USD": "$"}.get(str(p.get("currency", "")).upper(), "")
        caption = (post.get("caption", "") + "\n\n" + " ".join(post.get("hashtags", []))).strip()
        price = f"{sym}{p.get('price', '?')}" + (f" (was {sym}{p['was_price']})" if p.get("was_price") else "")
        link = lambda u, t: f'<a href="{e(u)}" target="_blank" rel="noopener">{e(t)}</a>' if u else e(t)
        cards.append(f"""
<section class="card">
  <h2>{e(os.path.basename(d))}</h2>
  <div class="meta">{e(src.get('format'))} · inspired by {link(src.get('url'), src.get('creator') or 'link')} {e(('· ' + str(src.get('views')) + ' views') if src.get('views') else '')} {e(('· ' + str(src.get('gmv')) + ' GMV') if src.get('gmv') else '')}</div>
  {'<div class="label">Original</div><div class="row">' + imgs(run, orig) + '</div>' if orig else ''}
  <div class="label">Ours</div><div class="row">{imgs(run, ours)}</div>
  <div class="grid">
    <div><b>Title</b><pre>{e(post.get('title'))}</pre><button data-copy="{e(post.get('title'))}">Copy title</button></div>
    <div><b>Caption</b><pre>{e(caption)}</pre><button data-copy="{e(caption)}">Copy caption</button></div>
    <div><b>Sound</b><p>{link(s.get('url'), s.get('name') or '—')}<br><small>{e(s.get('why'))}</small></p>
         <b>Product</b><p>{link(p.get('url'), p.get('name') or '—')}<br>{e(price)} · checked {e(p.get('checked_at'))}</p>
         {f'<button data-copy="{e(p.get("url"))}">Copy product link</button>' if p.get('url') else ''}</div>
  </div>
  <p class="remind">Before posting: switch on the "AI-generated content" label, add the product link, re-check the price.</p>
</section>""")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Slideshows {html.escape(os.path.basename(run))}</title>
<style>
:root{{--bg:#fafafa;--fg:#111;--card:#fff;--muted:#666;--line:#e3e3e3;--accent:#fe2c55}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111;--fg:#eee;--card:#1b1b1b;--muted:#aaa;--line:#333}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;padding:16px}}
h1{{font-size:22px;margin:0 0 16px}} h2{{font-size:17px;margin:0 0 4px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:0 0 20px;max-width:1200px}}
.meta,small{{color:var(--muted)}} .meta{{margin-bottom:10px;font-size:13px}}
.label{{font-weight:700;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:10px 0 4px}}
.row{{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px}} .row img{{height:300px;border-radius:8px;display:block}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:14px}}
pre{{white-space:pre-wrap;font:inherit;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:8px;margin:4px 0}}
button{{background:var(--accent);color:#fff;border:0;border-radius:6px;padding:6px 10px;cursor:pointer}}
a{{color:inherit}} .remind{{font-size:13px;color:var(--muted);margin:12px 0 0}}
</style></head><body>
<h1>Slideshows — {html.escape(os.path.basename(run))} ({len(cards)})</h1>
{''.join(cards) or '<p>No finished slideshows found.</p>'}
<script>
document.addEventListener('click',e=>{{const b=e.target.closest('button[data-copy]');if(!b)return;
navigator.clipboard.writeText(b.dataset.copy).then(()=>{{const t=b.textContent;b.textContent='Copied';setTimeout(()=>b.textContent=t,1200)}})}});
</script></body></html>"""
    out = os.path.join(run, "index.html")
    open(out, "w", encoding="utf-8").write(page)
    print(json.dumps({"index": out, "slideshows": len(cards)}))

if __name__ == "__main__":
    main()
