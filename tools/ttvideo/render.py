#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 القالبُ — سيناريو ثلاثِ لقطات (WP-087)

═══ لماذا تغيّر (قرارُ صالح 2026-08-13) ═══
كان القالبُ **بطاقةً ساكنة**: اسمٌ ورقمٌ وكود، تظهر وتبقى — بقراره في ١١ أغسطس
(«الفيديو يكفي اسم المتجر وقيمة الخصم والكود»). ثمّ خرج أوّلُ مقطعين آليّين
فقال: **«مقطع نون كان جميل بس فكرة وبرفيوم كو ما عجبني»**.

وقِيس الفرقُ فكان **كلامًا لا تصميمًا**: مقطعُ نون كان سيناريو ثلاثِ لقطات فيه
«قبل ما تطلب من نون» و«احفظ الكود»، والقالبُ الجديدُ بلا جملةٍ واحدة. فسحب
قرارَه القديمَ وطلب **تنويعَ العبارات**.

═══ الشكلُ الآن ═══
  ٠  → ٤٫٢ث   الخطّاف   — سطران من بنك العبارات (حسب فئة المتجر)
  ٤٫٢→ ٨٫٨ث   الجسم    — اسمُ المتجر ثمّ الكود، ومعه الرقمُ **إن وُجد**
  ٨٫٨→ ١٣ث    الأمر    — ماذا يفعل الآن + توقيعُ «أول بأول»

واسمُ المتجر يُرسم في اللقطة الثانية **دائمًا** — لأنّ بعضَ العبارات لا تذكره
(«بيتك يستاهل / وجيبك بعد»)، ومنشورٌ بلا اسمِ متجرٍ لا معنى له.

  OFFER_JSON='{"store":"…","code":"…","value":"…","h1":"…","h2":"…","cta":"…"}'
  python3 render.py a 1 out.mp4        الشكل: a|b|c|d|e|f   ·   الصوت: 1|2|3
"""
import os, sys, json, math, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features

assert features.check("raqm"), "لا raqm ⇒ لن يتشكّل العربي"
W, H, FPS = 1080, 1920, 30
TMPDIR = os.environ.get("TTVID_TMP", "/tmp")
# 📁 مساراتٌ نسبيةٌ للمستودع — لا مسارَ مطلقٌ لجهازٍ بعينه
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
FB = os.path.join(FD, "plex-ar-700.ttf")
FR = os.path.join(FD, "plex-ar-400.ttf")
# الخطُّ اللاتينيّ من النظام — يُثبَّت في الـworkflow، ويُبحث عنه في أماكنه المعروفة
_LAT = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf"]
FL = next((p for p in _LAT if os.path.exists(p)), _LAT[0])

GOLD, CREAM, DIM = (212, 175, 55), (251, 249, 244), (154, 150, 142)
INK, YEL = (24, 24, 24), (254, 224, 0)

_c = json.loads(os.environ.get("OFFER_JSON") or "{}")
STORE = _c.get("store") or "نون"
CODE = (_c.get("code") or "").strip()
# 🛡️ لا كودَ مزروع: كودٌ افتراضي في الرسّام يطبع كودًا متقاعدًا على الشاشة
#    (كان "BAWAL" — أُزيل 2026-08-13). بلا كودٍ لا مقطعَ، ويُقال السبب.
if not CODE:
    raise SystemExit("⛔ لا كودَ في OFFER_JSON — لا يُزرع كودٌ افتراضي")
# لا رقمَ مزروع: إن لم تُعطَ قيمةٌ معلومة لا تُخترع
VALUE = (_c.get("value") or "").strip()   # فارغٌ ⇒ لا سطرَ رقمٍ (قرار «لا تكرار»)
HAS_V = bool(VALUE)

# 🗣️ العبارة — سطرا الخطّاف والأمر. ويُستبدل {S} باسم المتجر عند المشغّل لا هنا،
#    فيبقى هذا الملفُّ رسّامًا لا مؤلِّفًا: من غيّر الكلامَ غيّره في `phrases.json`.
H1 = (_c.get("h1") or "قبل ما تدفع").strip()
H2 = (_c.get("h2") or ("في " + STORE)).strip()
CTA = (_c.get("cta") or "احفظ الكود").strip()

# 🎨 فئةُ المتجر (من run.py) — لونُ الأشكال الجديدة يتبعها (WP-628)
CAT = (_c.get("cat") or "none").strip()
CAT_COL = {"fashion": (176, 58, 98), "home": (46, 110, 94), "food": (196, 92, 38),
           "beauty": (150, 70, 140), "health": (40, 130, 90), "travel": (30, 100, 170),
           "tech": (52, 72, 140), "auto": (96, 96, 104), "ride": (190, 140, 20),
           "service": (60, 90, 150), "none": (130, 100, 40)}
CC = CAT_COL.get(CAT, CAT_COL["none"])

# ⏱ السيناريو: ثلاثُ لقطات — ومدّتُها **لكلِّ شكلٍ مدّتُه** (WP-628: كانت ١٣ ثانيةً للجميع).
#    الخطّافُ ظاهرٌ عند 1.2ث في كلِّ شكل — وهي لحظةُ غلاف تيك توك (THUMB_OFFSET_MS).
T1, T2, T3, DUR = 0.0, 4.2, 8.8, 13.0
TIMELINE = {"a": (4.2, 8.8, 13.0), "b": (4.2, 8.8, 13.0), "c": (4.2, 8.8, 13.0),
            "d": (3.0, 7.4, 10.0), "e": (5.0, 11.0, 16.0), "f": (2.2, 5.4, 7.5)}


f = lambda p, s: ImageFont.truetype(p, s)

# ═══ 🔤 اختيارُ الخطِّ بالقياس لا بالظنّ (عطبُ 2026-08-11) ═══
# خطُّ العلامة عربيٌّ **بلا حروفٍ لاتينية**، واسمُ المتجر قد يكون «DKNY».
# فالخطُّ يُختار بفحص التغطية الفعلية: أيُّهما يرسم كلَّ حرفٍ في النصّ.
from fontTools.ttLib import TTFont as _TT
_CMAP = {}
def _cov(path):
    if path not in _CMAP:
        _CMAP[path] = set(_TT(path).getBestCmap().keys())
    return _CMAP[path]

_AR = lambda t: any("\u0600" <= c <= "\u06FF" for c in t)
_IND = str.maketrans("0123456789%,;?", "٠١٢٣٤٥٦٧٨٩٪،؛؟")

def norm(t):
    """نصٌّ عربيٌّ فيه رقمٌ لاتينيّ يخرج من خطِّ العلامة (لا يحوي 0-9).
       فتُحوَّل أرقامُه إلى العربية بدل أن يهبط النصُّ كلُّه لخطٍّ أضعف."""
    return t.translate(_IND) if _AR(t) else t


def pick(txt, ar_path):
    """يُعيد مسارَ الخطِّ الذي يغطّي النصَّ كلَّه — والعربيُّ مقدَّمٌ عند التعادل."""
    need = {ord(c) for c in txt if not c.isspace()}
    for path in (ar_path, FL):
        if need <= _cov(path):
            return path
    # لا خطَّ يغطّي الكلَّ ⇒ الأكثرُ تغطيةً، ولا يُرسم مربّعٌ فارغٌ صامتًا
    best = max((ar_path, FL), key=lambda q: len(need & _cov(q)))
    miss = "".join(chr(c) for c in sorted(need - _cov(best)))
    print(f"⚠️ حروفٌ لا يغطّيها أيُّ خط: «{miss}» في «{txt}»")
    return best
ez = lambda t: 1 - (1 - max(0.0, min(1.0, t))) ** 3


def ctr(d, y, s, fo, fill, a=1.0, rtl=True):
    kw = dict(direction="rtl", language="ar") if rtl else {}
    bb = d.textbbox((0, 0), s, font=fo, **kw)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y), s, font=fo,
           fill=fill + (int(255 * max(0, min(1, a))),), **kw)


def spaced(d, y, s, fo, fill, track, a=1.0):
    ws = [d.textlength(c, font=fo) for c in s]
    x = (W - (sum(ws) + track * (len(s) - 1))) / 2
    top = d.textbbox((0, 0), s, font=fo)[1]
    for c, w in zip(s, ws):
        d.text((x, y - top), c, font=fo, fill=fill + (int(255 * max(0, min(1, a))),))
        x += w + track


def fit(d, s, fo_path, start, maxw):
    """يصغّر الخطَّ حتى يتّسع — فلا يُقصّ اسمُ متجرٍ طويل. والخطُّ يُختار بالتغطية."""
    fo_path = pick(norm(s), fo_path)
    sz = start
    while sz > 40:
        fo = f(fo_path, sz)
        bb = d.textbbox((0, 0), s, font=fo, direction="rtl", language="ar")
        if bb[2] - bb[0] <= maxw:
            return fo
        sz -= 6
    return f(fo_path, 40)


def grad(c0, c1):
    im = Image.new("RGB", (W, H)); dr = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        dr.line([(0, y), (W, y)], fill=tuple(int(p + (q - p) * t) for p, q in zip(c0, c1)))
    return im


def glow(base, cx, cy, rx, ry, col, amt):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=amt)
    return Image.composite(Image.new("RGB", (W, H), col),
                           base, m.filter(ImageFilter.GaussianBlur(180)))


def sign(d):
    ctr(d, H - 195, "أول بأول", f(FB, 56), (198, 164, 62), 0.92)


# ═══ 🎬 مشتركاتُ السيناريو — ثلاثُ لقطاتٍ لكلِّ شكل ═══
# والانتقالُ **قطعٌ لا ذوبان**: القطعُ يوقظ العين، والذوبانُ في ثمانِ ثوانٍ يميّعها.
# ولكلِّ لقطةٍ نصفُ ثانيةٍ دخولًا ونصفٌ خروجًا فلا يقفز النصُّ قفزةً حادّة.

def phase(t):
    """أيُّ لقطةٍ الآن، وكم مضى فيها، وشفافيّتُها (دخولٌ وخروج)."""
    if t < T2:   k, t0, t1 = 1, T1, T2
    elif t < T3: k, t0, t1 = 2, T2, T3
    else:        k, t0, t1 = 3, T3, DUR
    u = t - t0
    a = min(ez(u / 0.45), ez((t1 - t) / 0.35))
    return k, u, max(0.0, min(1.0, a))


def hook(d, a, col=None):
    """① الخطّاف — سطران كبيران. وهو وحدَه ما يوقف الإبهام."""
    col = col or CREAM
    ctr(d, 700, norm(H1), fit(d, H1, FB, 132, 940), col, a)
    ctr(d, 880, norm(H2), fit(d, H2, FB, 132, 940), col, a)


def body(d, a, box, txt, sub=None):
    """② الجسم — اسمُ المتجر فوق، والكودُ في إطاره، والرقمُ تحته إن وُجد.
       واسمُ المتجر **يُرسم دائمًا**: بعضُ العبارات لا تذكره."""
    ctr(d, 540, norm(STORE), fit(d, STORE, FB, 96, 900), sub or DIM, a)
    y = 700
    d.rounded_rectangle([110, y, W - 110, y + 300], 36, **box)
    spaced(d, y + 86, CODE, f(FL, 150), txt, 14, a)
    if HAS_V:
        ctr(d, y + 360, norm(VALUE), fit(d, VALUE, FB, 92, 900), txt, a)


def order(d, a, col=None):
    """③ الأمر — ماذا يفعل الآن. وبعده التوقيع."""
    ctr(d, 780, norm(CTA), fit(d, CTA, FB, 128, 940), col or CREAM, a)


# ══ أ · الهادئ — خلفيةٌ داكنةٌ وتوهّجٌ ذهبيٌّ يتنفّس ══
def A(t, dur):
    cy = H * 0.36 + math.sin(t * 0.45) * 110
    im = glow(grad((13, 13, 15), (27, 25, 29)), W / 2, cy, W * .85, 620, (88, 72, 25), 74)
    im = glow(im, W / 2, H * 1.02, W * .8, 500, (58, 48, 20), 38)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k, u, a = phase(t)
    if k == 1:
        hook(d, a)
    elif k == 2:
        pu = 1 + 0.02 * math.sin(max(0.0, u - 0.6) * 3.0)
        body(d, a, dict(outline=GOLD + (int(255 * a),), width=6), CREAM)
    else:
        order(d, a)
    sign(d)
    return Image.alpha_composite(im.convert("RGBA"), ov)


# ══ ب · السريع — نبضٌ وبطاقةُ كودٍ ذهبيةٌ ممتلئة ══
def B(t, dur):
    pl = 0.5 + 0.5 * math.sin(t * 4.4)
    im = glow(grad((10, 10, 12), (31, 27, 18)), W / 2, H * .42, W * .95, 700,
              (112, 90, 27), int(38 + 40 * pl))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k, u, a = phase(t)
    if k == 1:
        hook(d, a, GOLD)
    elif k == 2:
        body(d, a, dict(fill=GOLD + (int(255 * a),)), (16, 14, 8), CREAM)
    else:
        order(d, a, GOLD)
    sign(d)
    return Image.alpha_composite(im.convert("RGBA"), ov)


# ══ ج · هوية المتجر — خلفيةٌ فاتحةٌ وشريطٌ أصفر ══
def C(t, dur):
    im = grad((252, 250, 245), (236, 232, 222))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k, u, a = phase(t)
    hb = ez(t / 0.5)
    d.rectangle([0, 0, W, 240 * hb], fill=YEL + (255,))
    if hb > 0.6:                                   # الشريطُ يحمل اسمَ المتجر طولَ المقطع
        ctr(d, 78, norm(STORE), fit(d, STORE, FB, 92, 880), INK, ez((t - 0.3) / 0.4))
    if k == 1:
        hook(d, a, INK)
    elif k == 2:
        body(d, a, dict(fill=(255, 255, 255, int(255 * a)),
                        outline=INK + (int(190 * a),), width=5), INK, (120, 116, 108))
    else:
        order(d, a, INK)
    ctr(d, H - 195, "أول بأول", f(FB, 56), (150, 122, 40), 0.95)
    return Image.alpha_composite(im.convert("RGBA"), ov)


# ══ د · كشفُ الكود — حرفًا حرفًا على ليلٍ أزرق (WP-628 · ١٠ ثوانٍ) ══
def D(t, dur):
    im = glow(grad((8, 12, 26), (20, 26, 48)), W / 2, H * 0.45, W * .9, 640, tuple(int(c * .55) for c in CC), 60)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k, u, a = phase(t)
    if k == 1:
        hook(d, a)
    elif k == 2:
        ctr(d, 560, norm(STORE), fit(d, STORE, FB, 92, 900), DIM, a)
        fo = f(FL, 150)
        n = max(0, min(len(CODE), int(u / 0.22) + 1))
        ws = [d.textlength(c, font=fo) for c in CODE]
        x = (W - (sum(ws) + 18 * (len(CODE) - 1))) / 2
        top = d.textbbox((0, 0), CODE, font=fo)[1]
        y = 760
        d.line([(110, y + 220), (W - 110, y + 220)], fill=CC + (int(255 * a),), width=8)
        cur = None
        for i, (c, w) in enumerate(zip(CODE, ws)):
            if i < n:
                d.text((x, y - top), c, font=fo, fill=CREAM + (int(255 * a),))
            elif cur is None:
                cur = x
            x += w + 18
        if cur is not None and int(t * 4) % 2 == 0:          # مؤشّرٌ يرمش حتى يكتمل
            d.rectangle([cur, y + 10, cur + 14, y + 170], fill=GOLD + (int(255 * a),))
        if HAS_V and n >= len(CODE):
            ctr(d, y + 300, norm(VALUE), fit(d, VALUE, FB, 88, 900), GOLD, a)
    else:
        order(d, a, GOLD)
    sign(d)
    return Image.alpha_composite(im.convert("RGBA"), ov)


# ══ هـ · سؤالٌ وجواب — لونُ الفئة وعلامةُ سؤالٍ ضخمة (WP-628 · ١٦ ثانية) ══
def E(t, dur):
    dark = tuple(int(c * .32) for c in CC)
    im = grad(dark, tuple(int(c * .55) for c in CC))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    qa = 0.14 + 0.05 * math.sin(t * 1.3)
    ctr(d, 90, "؟", f(FB, 420), CREAM, qa)                  # فوق النصّ لا خلفَه
    k, u, a = phase(t)
    if k == 1:
        hook(d, a)
    elif k == 2:
        ctr(d, 560, norm(STORE), fit(d, STORE, FB, 96, 900), CREAM, a)
        d.rounded_rectangle([110, 720, W - 110, 1020], 36, fill=CREAM + (int(240 * a),))
        csz = 150
        while csz > 70:                                        # الكودُ الطويلُ لا يلمس الحافّة
            fo = f(FL, csz)
            if sum(d.textlength(c, font=fo) for c in CODE) + 14 * (len(CODE) - 1) <= W - 300: break
            csz -= 8
        spaced(d, 806 + (150 - csz) // 2, CODE, f(FL, csz), dark, 14, a)
        if HAS_V:
            ctr(d, 1090, norm(VALUE), fit(d, VALUE, FB, 92, 900), CREAM, a)
    else:
        order(d, a)
    sign(d)
    return Image.alpha_composite(im.convert("RGBA"), ov)


# ══ و · التذكرة — خلفيةٌ فاتحةٌ بلون الفئة وكودٌ على تذكرةٍ مثقوبة (WP-628 · ٧٫٥ ثانية) ══
def F(t, dur):
    pale = tuple(int(255 - (255 - c) * .16) for c in CC)
    im = grad(pale, tuple(int(255 - (255 - c) * .30) for c in CC))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k, u, a = phase(t)
    if k == 1:
        hook(d, a, INK)
    elif k == 2:
        ctr(d, 520, norm(STORE), fit(d, STORE, FB, 92, 900), (90, 86, 80), a)
        y0, y1 = 690, 1050
        s_in = ez(u / 0.5)
        dx = int((1 - s_in) * 260)
        d.rounded_rectangle([110 + dx, y0, W - 110 + dx, y1], 30, fill=CC + (int(255 * a),))
        for cx in (110 + dx, W - 110 + dx):                    # ثقبا التذكرة
            d.ellipse([cx - 44, (y0 + y1) / 2 - 44, cx + 44, (y0 + y1) / 2 + 44], fill=pale + (255,))
        for xx in range(190 + dx, W - 190 + dx, 46):           # خطُّ القصّ
            d.line([(xx, y1 - 70), (xx + 22, y1 - 70)], fill=(255, 255, 255, int(160 * a)), width=4)
        csz = 140
        while csz > 70:                                        # الكودُ لا يلمس ثقبَي التذكرة
            fo = f(FL, csz)
            if sum(d.textlength(c, font=fo) for c in CODE) + 10 * (len(CODE) - 1) <= W - 420: break
            csz -= 8
        spaced(d, y0 + 110 - (csz - 100) // 2, CODE, f(FL, csz), (255, 255, 255), 10, a)
        if HAS_V:
            ctr(d, y1 + 60, norm(VALUE), fit(d, VALUE, FB, 84, 900), INK, a)
    else:
        order(d, a, INK)
    ctr(d, H - 195, "أول بأول", f(FB, 56), (120, 96, 30), 0.95)
    return Image.alpha_composite(im.convert("RGBA"), ov)


# 🕒 لكلِّ شكلٍ مدّتُه (TIMELINE) — والغلافُ لحظةَ ظهور الكود.
FNS = {"a": A, "b": B, "c": C, "d": D, "e": E, "f": F}
FORMS = {k: (FNS[k], TIMELINE[k][2], TIMELINE[k][0] + 0.6) for k in FNS}
# لحظةُ الكشف التي يُبنى عليها جرسُ الصوت
REVEAL = {k: TIMELINE[k][0] for k in FNS}


def build(form, snd, out):
    global T2, T3, DUR
    T2, T3, DUR = TIMELINE[form]
    fn, dur, cover = FORMS[form]
    tmp = os.path.join(TMPDIR, f"fin_{form}")
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for i in range(int(dur * FPS)):
        fn(i / FPS, dur).convert("RGB").save(f"{tmp}/f{i:05d}.jpg", quality=94)
    subprocess.run([sys.executable, os.path.join(HERE, "sound.py"),
                    str(dur), str(REVEAL[form])], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", f"{tmp}/f%05d.jpg", "-i", os.path.join("/tmp", f"s{snd}.wav"),
                    "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
                    "-crf", os.environ.get("CRF", "26"), "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    n = os.path.getsize(out)
    print(f"✓ شكل {form} · صوت {snd} · {dur}ث · الغلاف {cover}ث · "
          f"{n/1e6:.2f}MB (b64 {n*1.37/1e6:.2f})")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3])
