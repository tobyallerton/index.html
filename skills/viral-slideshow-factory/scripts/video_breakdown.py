#!/usr/bin/env python3
"""Break a TikTok video down into the stills a slideshow can be built from.

Usage:
  python3 video_breakdown.py <video.mp4> <out folder> [--max 12] [--threshold 0.30]

Finds every cut (scene change) with ffmpeg, then keeps the sharpest frame from each shot.
Long shots with no cut get an extra frame every few seconds so nothing is missed.

Writes to <out folder>:
  shots/01.jpg ...      one sharp still per shot, full resolution
  contact.jpg           all the stills on one sheet with their times (look at this first)
  audio.m4a             the sound, so you can tell the user what it is / whether there's voiceover
  breakdown.json        duration, size, and per shot: start, end, length and still file

The stills are for working out the video's story, text and look. Like an original slideshow,
they are never uploaded to ChatGPT; the remake photos are described in words.
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, '..', 'fonts', 'TikTokSans-Bold.ttf')


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(video):
    r = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
             'stream=width,height:format=duration', '-of', 'json', video])
    j = json.loads(r.stdout or '{}')
    s = (j.get('streams') or [{}])[0]
    return float(j.get('format', {}).get('duration') or 0), s.get('width'), s.get('height')


def cuts(video, threshold):
    r = run(['ffmpeg', '-hide_banner', '-i', video, '-an', '-vf',
             f"select='gt(scene,{threshold})',showinfo", '-f', 'null', '-'])
    return [float(t) for t in re.findall(r'pts_time:([0-9.]+)', r.stderr)]


def grab(video, t, path):
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', f'{t:.3f}', '-i', video,
         '-frames:v', '1', '-q:v', '2', path])
    return os.path.exists(path)


def sharpness(path):
    im = Image.open(path).convert('L')
    im.thumbnail((360, 360))
    return ImageStat.Stat(im.filter(ImageFilter.FIND_EDGES)).var[0]


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__); sys.exit(1)
    video, out = a[0], a[1]
    mx = int(a[a.index('--max') + 1]) if '--max' in a else 12
    th = float(a[a.index('--threshold') + 1]) if '--threshold' in a else 0.30
    os.makedirs(os.path.join(out, 'shots'), exist_ok=True)
    tmp = os.path.join(out, '_tmp'); os.makedirs(tmp, exist_ok=True)

    dur, w, h = probe(video)
    if not dur:
        print(json.dumps({'ok': False, 'error': 'could not read the video'})); sys.exit(1)

    # Shot boundaries: cuts, ignoring ones closer than 0.4s together; split shots longer than 4s.
    b = [0.0]
    for t in cuts(video, th):
        if t - b[-1] >= 0.4 and dur - t >= 0.4:
            b.append(t)
    b.append(dur)
    shots = []
    for s, e in zip(b, b[1:]):
        n = max(1, int((e - s) // 4))
        for i in range(n):
            shots.append((s + (e - s) * i / n, s + (e - s) * (i + 1) / n))
    # Too many? merge the shortest neighbours until within the cap.
    while len(shots) > mx:
        i = min(range(len(shots) - 1), key=lambda k: (shots[k][1] - shots[k][0]) + (shots[k + 1][1] - shots[k + 1][0]))
        shots[i:i + 2] = [(shots[i][0], shots[i + 1][1])]

    result = []
    for n, (s, e) in enumerate(shots, 1):
        best, score = None, -1
        L = e - s
        for k, f in enumerate((0.2, 0.5, 0.8)):
            p = os.path.join(tmp, f'{n}_{k}.jpg')
            if grab(video, min(s + L * f, dur - 0.05), p):
                sc = sharpness(p)
                if sc > score:
                    best, score = p, sc
        if not best:
            continue
        dst = os.path.join(out, 'shots', f'{n:02d}.jpg')
        os.replace(best, dst)
        result.append({'shot': n, 'start': round(s, 2), 'end': round(e, 2), 'seconds': round(L, 2),
                       'still': f'shots/{n:02d}.jpg'})
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)

    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', video, '-vn', '-c:a', 'aac',
         os.path.join(out, 'audio.m4a')])

    # Contact sheet: 4 across, each still labelled with its number and time.
    cols, tw = 4, 300
    ims = [Image.open(os.path.join(out, r['still'])).convert('RGB') for r in result]
    th_ = int(tw * (ims[0].height / ims[0].width)) if ims else 530
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw + (cols + 1) * 10, rows * (th_ + 10) + 10), 'white')
    try:
        font = ImageFont.truetype(FONT, 26)
    except Exception:
        font = ImageFont.load_default()
    for i, (im, r) in enumerate(zip(ims, result)):
        im = im.resize((tw, th_))
        x, y = 10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th_ + 10)
        sheet.paste(im, (x, y))
        d = ImageDraw.Draw(sheet)
        label = f"{r['shot']}  {r['start']:.1f}-{r['end']:.1f}s"
        d.rectangle((x, y, x + d.textlength(label, font=font) + 16, y + 38), fill='black')
        d.text((x + 8, y + 4), label, font=font, fill='white')
    sheet.save(os.path.join(out, 'contact.jpg'), quality=88)

    info = {'video': os.path.abspath(video), 'seconds': round(dur, 2), 'width': w, 'height': h,
            'shots': result}
    with open(os.path.join(out, 'breakdown.json'), 'w') as f:
        json.dump(info, f, indent=1)
    print(json.dumps({'ok': True, 'seconds': round(dur, 2), 'shots': len(result), 'out': out}))


if __name__ == '__main__':
    main()
