# -*- coding: utf-8 -*-
"""🎟️▶️ WP-931 — شورتات الأكواد ليوتيوب (قوله 2026-11-02 «ابي ٦ مقاطع في اليوم وزعها زي ما تشوف»)

شكلان جديدان بجانب مقطع المنتج — كلاهما **بلا صيد ولا تابلت** (صورةٌ تُرسم هنا ثمّ تتحرّك):
  codes ⇐ «أكواد خصم اليوم»: نون أوّلُها ثمّ أربعةُ متاجر من تصنيفٍ واحد — الأسطرُ تظهر واحدًا واحدًا
  card  ⇐ بطاقةُ كود متجرٍ واحد بقوالب ستوري سناب نفسِها (tools/codecard/snap.py) بتقريبٍ بطيء

الأكوادُ لا تُكتب هنا: تأتي من الخادم (yt/state ⇐ جدار الأكواد)، والنصُّ يُحجز منه (yt/claim بالمفاتيح).
"""
import os, io, re, sys, subprocess, importlib.util, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP_PATH = os.path.join(HERE, "..", "codecard", "snap.py")
DUR = 8.75
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

_snap = None
def snap():
    """قوالبُ سناب باسمٍ خاصّ — في المجلد الآخر ملفٌّ اسمه run.py أيضًا، فلا نضيفه لمسار الاستيراد."""
    global _snap
    if _snap is None:
        spec = importlib.util.spec_from_file_location("awb_snap_tpl", SNAP_PATH)
        _snap = importlib.util.module_from_spec(spec); spec.loader.exec_module(_snap)
    return _snap

def short_store(s):
    """«فوغا كلوسيت VOGACLOSET» ⇐ «فوغا كلوسيت» — الاسمُ العربيُّ وحده إن وُجد (السطرُ يتّسع للكود)."""
    s = str(s or "").strip()
    t = re.sub(r"\s+[A-Za-z][A-Za-z0-9 .&'’-]*$", "", s).strip() if re.search(r"[\u0600-\u06FF]", s) else s
    return t or s

_img = {}
def fetch_img(url):
    if not url: return None
    if url in _img: return _img[url]
    im = None
    try:
        from PIL import Image
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/png,image/jpeg,image/webp,*/*"})
        with urllib.request.urlopen(req, timeout=30) as r: b = r.read(6_000_000)
        im = Image.open(io.BytesIO(b)); im.load()
    except Exception: im = None   # بلا شعار ⇒ الاسمُ مكتوبًا (لا يقف المقطع)
    _img[url] = im
    return im

def codes_frames(items, cat):
    """صورٌ متتالية: العنوانُ ثمّ سطرٌ يُضاف كلَّ مرّة — آخرُها القائمةُ كاملة. items[0] نون."""
    S = snap(); from PIL import Image, ImageDraw
    frames = []
    for upto in range(1, len(items) + 1):
        img = Image.new("RGB", (S.W, S.H), S.WW); d = ImageDraw.Draw(img)
        S.header(img, d, 262)
        S.txt(d, (540, 378), "أكواد خصم اليوم", True, 76, S.CH, maxw=940)
        if cat == "منوّعة": S.txt(d, (540, 448), "نون ومتاجر منوّعة", False, 40, S.GR, maxw=900)   # WP-933: القائمةُ تمزج الأنواع
        elif cat and cat != "عام": S.txt(d, (540, 448), "نون وأكواد " + cat, False, 40, S.GR, maxw=900)
        y = 500
        for i, it in enumerate(items[:upto]):
            box = (70, y, 1010, y + 150)
            S.shadow(img, box, 40, alpha=26, blur=18); d = ImageDraw.Draw(img)
            d.rounded_rectangle(box, 40, fill=S.WHITE, outline=S.GOLD if i == 0 else S.LINE, width=5 if i == 0 else 3)
            # الاسمُ مكتوبٌ دائمًا — الشعارُ وحده لا يُقرأ (قِيس في محاكاة 2/11: «B» وتاجٌ صغير بلا اسم) ⇒ الشعارُ صغيرٌ يمينَ الاسم
            lg = fetch_img(it.get("logo")) if i else None
            nx = 960
            if lg is not None:
                p = S.contain(S.flat(lg), 96, 96); img.paste(p, (970 - p.width, y + (150 - p.height) // 2)); d = ImageDraw.Draw(img)
                nx = 970 - p.width - 22
            S.txt(d, (nx, y + 78), short_store(it["store"]), True, 52, S.CH, anchor="rm", maxw=nx - 575)
            S.code_pill(d, (105, y + 28, 540, y + 122), it["code"], S.CH, S.GOLD, 66)
            y += 168
        S.cta(d, y + 40, S.CH, True); S.footer(d, (179, 154, 74))
        frames.append(S.jpg(img))
    return frames

def card_jpg(fields):
    S = snap()
    return S.render_snap(fields, logo=fetch_img(fields.get("logo")), poster=fetch_img(fields.get("poster")))

def _ff(cmd):
    r = subprocess.run(cmd, capture_output=True)
    return (r.returncode == 0), r.stderr.decode("utf-8", "replace")[-300:]

def frames_mp4(frames, wav, out, tmp):
    """القائمة: كلُّ سطرٍ يظهر بعد ٠٫٩ ثانية، والقائمةُ الكاملةُ تبقى للآخر."""
    step = 0.9
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        for i, b in enumerate(frames):
            pth = os.path.join(tmp, f"f{i}.jpg"); open(pth, "wb").write(b)
            dur = step if i < len(frames) - 1 else max(2.0, DUR - step * (len(frames) - 1))
            f.write(f"file '{pth}'\nduration {dur:.2f}\n")
        f.write(f"file '{pth}'\n")
    ok, err = _ff(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                   "-vf", "scale=1080:1920,fps=30,format=yuv420p", "-t", f"{DUR}", "-map", "0:v", "-map", "1:a",
                   "-c:v", "libx264", "-preset", "slow", "-b:v", "3000k", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out])
    return (out if ok and os.path.exists(out) else None), (None if ok else err)

def still_mp4(jpg, wav, out, tmp):
    """البطاقة: تقريبٌ بطيءٌ ٦٪ على مدى المقطع."""
    pth = os.path.join(tmp, "card.jpg"); open(pth, "wb").write(jpg)
    n = int(DUR * 30)
    vf = (f"scale=2160:3840,zoompan=z='1+0.06*on/{n}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p")
    ok, err = _ff(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", pth, "-i", wav, "-vf", vf, "-t", f"{DUR}",
                   "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-b:v", "3000k",
                   "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out])
    return (out if ok and os.path.exists(out) else None), (None if ok else err)
