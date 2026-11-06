#!/usr/bin/env python3
"""Build the phone posting page for one day's slideshows (published as a private Artifact).

Usage: python3 posting_page.py "Slideshows/<date>" <out_dir> [--mine my_posts.json]
Writes <out_dir>/index.html and <out_dir>/img/<date>/NN-k.jpg, plus <out_dir>/files.json:
the {published path: local path} map to pass as the Artifact tool's `files`.
Publish with capabilities {"downloads": true} (the Save buttons use it).

Order = best bets first: the source post's GMV, a bonus for the hook score, and a big bonus when
the product already sold well on the user's own account (--mine, parse_posts.py output).
"""
import glob, html, json, os, re, sys
from PIL import Image

def num(s):
    """'£24.4K' -> 24400"""
    m = re.search(r"([\d.]+)\s*([KkMm]?)", str(s or ""))
    if not m: return 0.0
    v = float(m.group(1)); return v * {"k": 1e3, "m": 1e6}.get(m.group(2).lower(), 1)

def pid(u):
    m = re.search(r"(\d{15,20})", u or ""); return m.group(1) if m else ""

def main():
    run = os.path.abspath(sys.argv[1]); out = os.path.abspath(sys.argv[2])
    date = os.path.basename(run.rstrip("/"))
    mine = {}
    if "--mine" in sys.argv:
        for p in json.load(open(sys.argv[sys.argv.index("--mine") + 1], encoding="utf-8")):
            v = p.get("views") or 0; g = p.get("gmv") or 0
            k = str((p.get("product_data") or {}).get("product_id") or p.get("product_id") or "")
            if k and v: mine[k] = max(mine.get(k, 0), g / v * 1000)
    os.makedirs(os.path.join(out, "img", date), exist_ok=True)
    files, items = {}, []
    for d in sorted(glob.glob(os.path.join(run, "*", ""))):
        slides = sorted(glob.glob(os.path.join(d, "slide-*.png")), key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[-1]))
        pj = os.path.join(d, "_build", "post.json")
        if not slides or not os.path.exists(pj): continue
        post = json.load(open(pj, encoding="utf-8"))
        folder = os.path.basename(d.rstrip("/")); n = folder.split(" - ")[0]
        imgs = []
        for k, s in enumerate(slides, 1):
            rel = f"img/{date}/{n}-{k}.jpg"; dst = os.path.join(out, rel)
            Image.open(s).convert("RGB").save(dst, "JPEG", quality=88, optimize=True)
            files[rel] = dst; imgs.append(rel)
        p = post.get("product", {}); src = post.get("source", {})
        own = mine.get(p.get("id") or pid(p.get("url")), 0)
        score = num(src.get("gmv")) + 2000 * (post.get("hooks", {}).get("score") or 0) + (50000 if own >= 2 else 0)
        items.append({"folder": folder, "title": post.get("title", ""), "caption": post.get("caption", ""),
                      "hashtags": " ".join(post.get("hashtags", [])), "sound": post.get("sound", {}),
                      "product": {"name": p.get("name", ""), "url": p.get("url", ""), "price": p.get("price"),
                                  "checked": p.get("checked_at", "")},
                      "format": src.get("format") or folder.rsplit(" - ", 1)[-1], "inspired": src.get("gmv") or "",
                      "own": round(own, 2), "slides": imgs, "score": score})
    items.sort(key=lambda i: -i["score"])
    data = json.dumps({"date": date, "items": items}, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.replace("__DATA__", data).replace("__DATE__", html.escape(date))
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)
    json.dump(files, open(os.path.join(out, "files.json"), "w"), indent=1)
    print(json.dumps({"index": os.path.join(out, "index.html"), "slideshows": len(items), "images": len(files)}))

TEMPLATE = r"""<title>Slideshow Posting List</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600&display=swap">
<style>
/* Layout: one column of posting cards in order, each a slide strip plus the copy you paste into TikTok. */
:root{
  --bg:#f3f5f4; --card:#ffffff; --ink:#121a18; --muted:#5b6865; --line:#dde3e1;
  --accent:#e2365b; --accent-ink:#ffffff; --chip:#e8eeec; --done:#2f7d5b;
  --display:"Bricolage Grotesque", "Helvetica Neue", Arial, sans-serif;
  --body:"Figtree", -apple-system, "Segoe UI", Roboto, sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0e1312; --card:#171e1c; --ink:#eef3f1; --muted:#9aa7a3; --line:#27302d;
  --accent:#ff5a7a; --accent-ink:#1a0b10; --chip:#222b28; --done:#5cc79a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0e1312; --card:#171e1c; --ink:#eef3f1; --muted:#9aa7a3; --line:#27302d;
  --accent:#ff5a7a; --accent-ink:#1a0b10; --chip:#222b28; --done:#5cc79a; color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:15px/1.5 var(--body);
  padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px));padding-block:20px 48px}
.wrap{max-width:640px;margin:0 auto;display:grid;gap:18px}
header h1{font:800 30px/1.05 var(--display);margin:0;text-wrap:balance;letter-spacing:-.01em}
header p{margin:6px 0 0;color:var(--muted)}
.progress{display:flex;align-items:center;gap:10px;margin-top:12px;font-size:13px;color:var(--muted)}
.bar{flex:1;height:6px;background:var(--chip);border-radius:3px;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:var(--done);transition:width .3s}
.rules{font-size:13px;color:var(--muted);margin:0;padding:10px 12px;border:1px dashed var(--line);border-radius:10px}
article{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;display:grid;gap:12px;min-width:0}
article.posted{opacity:.55}
.top{display:flex;gap:12px;align-items:flex-start}
.rank{font:800 26px/1 var(--display);color:var(--accent);min-width:2ch;font-variant-numeric:tabular-nums}
.top h2{font:600 19px/1.2 var(--display);margin:0;text-wrap:balance}
.meta{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.chip{font-size:12px;font-weight:600;padding:2px 8px;border-radius:999px;background:var(--chip);color:var(--muted);letter-spacing:.02em}
.chip.hot{background:var(--accent);color:var(--accent-ink)}
.strip{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:4px}
.slide{flex:0 0 auto;width:132px;display:grid;gap:6px;scroll-snap-align:start}
.slide img{width:132px;aspect-ratio:9/16;object-fit:cover;border-radius:10px;display:block;max-width:100%;background:var(--chip)}
button{font:600 14px/1 var(--body);border-radius:10px;border:1px solid var(--line);background:var(--chip);color:var(--ink);padding:10px 12px;cursor:pointer}
button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
button.primary{background:var(--accent);color:var(--accent-ink);border-color:transparent}
.slide button{padding:7px 8px;font-size:12px}
.field{display:grid;gap:6px;min-width:0}
.field label{font-size:12px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.copy{display:flex;gap:8px;align-items:flex-start}
.copy pre{flex:1;min-width:0;margin:0;white-space:pre-wrap;word-break:break-word;font:15px/1.45 var(--body);background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
a{color:var(--ink)}
.done{display:flex;gap:10px;align-items:center;font-weight:600}
.done input{width:22px;height:22px;accent-color:var(--done)}
.note{font-size:13px;color:var(--muted);margin:0}
.toast{position:fixed;left:50%;bottom:calc(20px + env(safe-area-inset-bottom, 0px));transform:translateX(-50%);background:var(--ink);color:var(--bg);padding:10px 14px;border-radius:10px;font-weight:600}
@media (prefers-reduced-motion: reduce){.bar i{transition:none}}
</style>
<div class="wrap">
  <header>
    <h1>Today's slideshows</h1>
    <p id="sub"></p>
    <div class="progress"><div class="bar"><i id="bar"></i></div><span id="count"></span></div>
  </header>
  <p class="rules">For each one: save the slides, post them in order, paste the caption, add the product link and sound, and switch on <b>AI-generated content</b>. Check the price and commission in your affiliate app first.</p>
  <div id="list" class="wrap"></div>
</div>
<div class="toast" id="toast" hidden></div>
<script>
const DATA = __DATA__;
const $ = (s, el=document) => el.querySelector(s);
let downloads = null;
const KEY = "posted-" + DATA.date;
function getPosted(){ try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch(e) { return {}; } }
function setPosted(v){ try { localStorage.setItem(KEY, JSON.stringify(v)); } catch(e) {} }
function toast(t){ const el=$("#toast"); el.textContent=t; el.hidden=false; clearTimeout(toast.t); toast.t=setTimeout(()=>el.hidden=true, 1800); }
async function copy(text, btn){
  try { await navigator.clipboard.writeText(text); toast("Copied"); }
  catch(e){ const pre = btn.closest(".copy")?.querySelector("pre"); if (pre){ const r=document.createRange(); r.selectNodeContents(pre); const s=getSelection(); s.removeAllRanges(); s.addRange(r); toast("Selected: tap Copy"); } }
}
async function saveOne(path, name){
  if (!downloads) { toast("Press and hold the slide to save it"); return false; }
  const blob = await (await fetch(path)).blob();
  try { await downloads.save({ filename: name, data: blob }); return true; }
  catch(e){ if (e && e.code === "declined") return false; if (e && e.code === "rate_limited") { toast("One at a time: try again"); return false; } toast("Saving isn't available here: press and hold the slide"); return false; }
}
function el(tag, attrs={}, kids=[]){ const e=document.createElement(tag); for (const [k,v] of Object.entries(attrs)) { if (k==="text") e.textContent=v; else e.setAttribute(k,v); } for (const k of kids) e.append(k); return e; }
function render(){
  const posted = getPosted(); const list = $("#list"); list.textContent="";
  DATA.items.forEach((it, i) => {
    const art = el("article", {id:"s"+(i+1)});
    if (posted[it.folder]) art.classList.add("posted");
    const meta = el("div",{class:"meta"},[el("span",{class:"chip",text:it.format})]);
    if (it.own >= 2) meta.append(el("span",{class:"chip hot",text:"Sold well for you"}));
    if (it.inspired) meta.append(el("span",{class:"chip",text:"Original: "+it.inspired+" sales"}));
    art.append(el("div",{class:"top"},[el("div",{class:"rank",text:String(i+1)}), el("div",{},[el("h2",{text:it.product.name}), meta])]));
    const strip = el("div",{class:"strip"});
    it.slides.forEach((s, k) => {
      const b = el("button",{type:"button",text:"Save "+(k+1)});
      b.onclick = () => saveOne(s, `${String(i+1).padStart(2,"0")}-slide-${k+1}.jpg`).then(ok => ok && toast("Saved slide "+(k+1)));
      strip.append(el("div",{class:"slide"},[el("img",{src:s,alt:"Slide "+(k+1)+" of "+it.slides.length,loading:"lazy"}), b]));
    });
    art.append(strip);
    const all = el("button",{type:"button",class:"primary",text:`Save all ${it.slides.length} slides`});
    all.onclick = async () => { for (let k=0;k<it.slides.length;k++){ const ok = await saveOne(it.slides[k], `${String(i+1).padStart(2,"0")}-slide-${k+1}.jpg`); if (!ok) return; } toast("All slides saved"); };
    art.append(el("div",{class:"row"},[all]));
    const field = (label, text) => { const btn = el("button",{type:"button",text:"Copy"}); btn.onclick = () => copy(text, btn); return el("div",{class:"field"},[el("label",{text:label}), el("div",{class:"copy"},[el("pre",{text}), btn])]); };
    if (it.title) art.append(field("Title", it.title));
    art.append(field("Caption", (it.caption + "\n\n" + it.hashtags).trim()));
    const prod = el("div",{class:"field"},[el("label",{text:"Product link"})]);
    const prow = el("div",{class:"row"});
    if (it.product.url) { prow.append(el("a",{href:it.product.url,target:"_blank",rel:"noopener",text:"Open product"})); const cb=el("button",{type:"button",text:"Copy link"}); cb.onclick=()=>copy(it.product.url, cb); prow.append(cb); }
    prow.append(el("span",{class:"note",text:(it.product.price!=null?"£"+Number(it.product.price).toFixed(2)+" · ":"")+"check price & commission"}));
    prod.append(prow); art.append(prod);
    const snd = el("div",{class:"field"},[el("label",{text:"Sound"})]);
    snd.append(it.sound && it.sound.url ? el("a",{href:it.sound.url,target:"_blank",rel:"noopener",text:it.sound.name||"Open sound"}) : el("span",{text:(it.sound&&it.sound.name)||"Any trending sound"}));
    art.append(snd);
    const cb = el("input",{type:"checkbox",id:"done-"+(i+1)}); cb.checked = !!posted[it.folder];
    cb.onchange = () => { const p=getPosted(); if (cb.checked) p[it.folder]=1; else delete p[it.folder]; setPosted(p); render(); };
    art.append(el("label",{class:"done",for:"done-"+(i+1)},[cb, document.createTextNode("Posted")]));
    list.append(art);
  });
  const n = DATA.items.length, d = DATA.items.filter(it => posted[it.folder]).length;
  $("#sub").textContent = `${new Date(DATA.date+"T12:00:00").toLocaleDateString("en-GB",{weekday:"long",day:"numeric",month:"long"})} · ${n} slideshows, best bets first`;
  $("#count").textContent = `${d} of ${n} posted`;
  $("#bar").style.width = (n ? d/n*100 : 0) + "%";
}
render();
(async () => { try { downloads = await window.claude?.use?.("downloads") ?? null; } catch(e) { downloads = null; } })();
</script>
"""

if __name__ == "__main__":
    main()
