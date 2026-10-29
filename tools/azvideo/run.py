# -*- coding: utf-8 -*-
"""🎬 مصنعُ مقاطع أمازون لإكس — WP-781 (2026-10-20)

قراره: «حط لي خطه عمل ومهام انت تبنيها وتنفذها ( نبدا في اكس )».

  ① GET  /api/az/video/jobs   ← منتجاتٌ قرأ التابلتُ صفحاتِها فوجد فيها فيديو طوليًّا
  ② ينزّل نسخةَ 720×1280 من شبكة توزيع أمازون (m.media-amazon.com) — لا صفحةَ أمازون
  ③ يقصّ ١٠ ثوانٍ + شريطٌ صغير «أول بأول · الرابط في التغريدة» + صوتُ المقطع الأصليّ
  ④ يضغطه تحت سقف الخادم (~١ ميغا) ⇒ POST /api/az/video/put   (أو سببُ التعذّر)

قواعدُه: لا يكتب سعرًا ولا خصمًا على المقطع (السعرُ يتغيّر والتغريدةُ تحمله) · كلُّ تعذّرٍ يُرفع بسببه.
"""
import os, re, sys, json, base64, argparse, subprocess, tempfile, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "ttproduct", "fonts")
BASE = os.environ.get("OS_BASE", "https://os.awalbawal.com").rstrip("/")
TT_KEY = os.environ.get("TT_BOT_KEY", "")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36 AwalbawalAzVideo/1.0"
W, H = 720, 1280
CLIP = 10.0                 # ثوانٍ
MAX_B64 = 1_350_000         # سقفُ الخادم 1.4 مليون حرف (lib/azvideo.js) — وهامش
PILL = "أول بأول · الرابط في التغريدة"

def say(*a): print(" ".join(str(x) for x in a), flush=True)

def _req(path, body=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method="POST" if data is not None else "GET")
    req.add_header("User-Agent", UA); req.add_header("Accept", "application/json")
    if data is not None: req.add_header("Content-Type", "application/json")
    if TT_KEY: req.add_header("x-tt-key", TT_KEY)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        b = ""
        try: b = e.read().decode("utf-8", "replace")[:300]
        except Exception: pass
        raise RuntimeError(f"HTTP {e.code} على {path} — {b}") from None

def api(path): return _req(path)
def api_post(path, body): return _req(path, body)

def variant(m3u8, want=720):
    """قائمةُ الجودات (مقيسة 2026-10-20: 360/480/720/1080) ⇒ الأقربُ بضلعه الأقصر إلى 720 (العرضيُّ 1280×720)."""
    req = urllib.request.Request(m3u8, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        txt = r.read().decode("utf-8", "replace")
    best = None
    lines = txt.splitlines()
    for i, ln in enumerate(lines):
        m = re.search(r"RESOLUTION=(\d+)x(\d+)", ln)
        if m and i + 1 < len(lines):
            w, h = int(m.group(1)), int(m.group(2))
            uri = lines[i + 1].strip()
            score = abs(min(w, h) - want)
            if best is None or score < best[0]: best = (score, w, h, uri)
    if not best: return m3u8, None
    uri = best[3] if best[3].startswith("http") else m3u8.rsplit("/", 1)[0] + "/" + best[3]
    return uri, (best[1], best[2])

def pill(png):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(os.path.join(FONTS, "plexfull-700.ttf"), 46)
    tw = d.textlength(PILL, font=f, direction="rtl", language="ar") + 80
    d.rounded_rectangle((540 - tw / 2, 90, 540 + tw / 2, 176), 43, fill=(16, 16, 16, 225))
    d.text((540, 133), PILL, font=f, fill=(254, 190, 16), anchor="mm", direction="rtl", language="ar")
    im.resize((W, H), Image.LANCZOS).save(png)

def render(src, png, out, start, clip, horiz=False):
    if horiz:
        # 🎬 WP-782 («ضف العرضي اعتمد»): العرضيُّ كاملًا بعرض الشاشة وسطَها، وخلفه نسختُه مغبّشةً تملأ الطول
        vf = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=20:2,eq=brightness=-0.18[bg];"
              f"[b]scale={W}:-2[fg];[bg][fg]overlay=0:(H-h)/2,fps=30[v];")
    else:
        vf = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30[v];"
    fc = (vf + f"[v][1:v]overlay=0:0,format=yuv420p[o];[0:a]afade=t=out:st={max(0.0, clip - 1.0):.2f}:d=1.0[a]")
    for br in ("720k", "580k", "450k", "340k"):
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.2f}", "-t", f"{clip:.2f}", "-i", src, "-i", png,
               "-filter_complex", fc, "-map", "[o]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-b:v", br, "-maxrate", br, "-bufsize", "1400k",
               "-c:a", "aac", "-b:a", "64k", "-ac", "2", "-movflags", "+faststart", out]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0:
            # مقطعٌ بلا صوت: نعيد بلا مسار الصوت
            if b"matches no streams" in r.stderr or b"Stream specifier ':a'" in r.stderr or b"0:a" in r.stderr:
                fc2 = fc.split(";[0:a]")[0]
                cmd2 = [c for c in cmd]
                i = cmd2.index("-filter_complex"); cmd2[i + 1] = fc2
                j = cmd2.index("[a]"); del cmd2[j - 1:j + 1]
                for k in ("-c:a", "-b:a", "-ac"):
                    if k in cmd2: x = cmd2.index(k); del cmd2[x:x + 2]
                cmd2.insert(cmd2.index("-movflags"), "-an")
                r = subprocess.run(cmd2, capture_output=True)
            if r.returncode != 0: return None, r.stderr.decode("utf-8", "replace")[-300:]
        b64 = base64.b64encode(open(out, "rb").read()).decode()
        say(f"   🎞️ {br}: {len(b64)//1000}k حرف")
        if len(b64) <= MAX_B64: return b64, None
    return None, "المقطعُ أكبرُ من سقف الخادم حتى بأقلّ جودة"

def one(job, dry=False):
    a, m3u8 = job["asin"], job["m3u8"]
    dur = float(job.get("dur") or 0)
    say(f"🎯 {a} · {dur or '?'}ث")
    tmp = tempfile.mkdtemp(prefix="azv")
    src, png, out = (os.path.join(tmp, n) for n in ("src.mp4", "pill.png", "out.mp4"))
    try:
        # 🔴 WP-802: علي إكسبريس يعطي mp4 مباشرًا لا قائمةَ جودات — يُنزَّل كما هو ويُقاس بعده
        uri, wh = (m3u8, None) if not re.search(r"\.m3u8(\?|$)", m3u8) else variant(m3u8)
        say(f"   ⬇️ {wh[0]}x{wh[1]}" if wh else "   ⬇️ (بلا قائمة جودات)")
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-user_agent", UA, "-i", uri, "-t", "40", "-c", "copy", src],
                           capture_output=True, timeout=240)
        if r.returncode != 0 or not os.path.exists(src) or os.path.getsize(src) < 100_000:
            raise RuntimeError("ما نزل المقطع: " + r.stderr.decode("utf-8", "replace")[-160:])
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True)
        real = float((p.stdout.decode().strip() or "0").split("\n")[0] or 0)
        if real < 4: raise RuntimeError(f"المقطعُ قصيرٌ جدًّا ({real:.1f}ث)")
        start = 1.0 if real >= CLIP + 2 else 0.0      # ثانيةُ البداية غالبًا شاشةٌ فارغة أو شعار
        clip = min(CLIP, real - start)
        pill(png)
        probed = False
        if not wh:
            q = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", src], capture_output=True)
            try:
                pw, ph = (int(x) for x in q.stdout.decode().strip().split("\n")[0].split(",")[:2]); wh = (pw, ph); probed = True; say(f"   📐 {pw}x{ph}")
            except Exception: pass
        # مربّعُ علي إكسبريس (المقيس بـffprobe) يُعامَل كالعرضيّ: كاملًا وسطَ الشاشة بخلفيّةٍ مغبّشة — وأمازون كما كان حرفًا
        horiz = bool(wh and (wh[0] > wh[1] or (probed and wh[0] == wh[1]))) or (int(job.get("w") or 0) > int(job.get("h") or 0))
        if horiz: say("   ↔️ عرضيّ — وسطَ شاشةٍ طوليّة بخلفيّةٍ مغبّشة")
        b64, err = render(src, png, out, start, clip, horiz)
        if not b64: raise RuntimeError(err)
        if dry:
            say(f"   🧪 جافّ: {len(b64)//1000}k حرف · {clip:.1f}ث"); return True
        res = api_post("/api/az/video/put", {"asin": a, "mp4": "data:video/mp4;base64," + b64})
        say("   ✅ رُفع" if res.get("ok") else f"   ⚠️ رفضه الخادم: {res}")
        return bool(res.get("ok"))
    except Exception as e:
        why = str(e)[:200]
        say("   ⚠️", why)
        if not dry:
            try: api_post("/api/az/video/put", {"asin": a, "error": why})
            except Exception as e2: say("   ⚠️ وما وصل سببُ التعذّر:", e2)
        return False

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); ap.add_argument("--max", type=int, default=6)
    a = ap.parse_args()
    if not TT_KEY: say("⛔ لا مفتاحَ مقاطع (TT_BOT_KEY)"); sys.exit(1)
    jobs = (api("/api/az/video/jobs?limit=" + str(a.max)).get("jobs") or [])
    if not jobs: say("✅ لا مقطعَ ينتظر"); return
    ok = sum(1 for j in jobs if one(j, a.dry))
    say(f"🏁 {ok} من {len(jobs)}")

if __name__ == "__main__":
    main()
