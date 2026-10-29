#!/usr/bin/env python3
# 🎟️🖼️ ═══ WP-699 — رسمُ بطاقة الكود (ثيم «أول بأول» الفاتح · AB-DOC-002) ═══
# التصميمُ الذي اعتمده صالح 2026-10-13 («هذا التصور جميل»): صورةُ المتجر الرسمية داخل إطارنا،
# تحتها اسمُ المتجر والعرض، ثمّ شريطُ الكود الفحمي. وثلاثةُ أشكالٍ بحسب ما في يدنا:
#   poster ⇐ صورةُ إعلان المتجر (og:image) · logo ⇐ الشعارُ وحدَه · name ⇐ لا صورة: الاسمُ كبيرًا.
# ⚖️ الكودُ والقيمةُ يُكتبان من البيانات حرفًا. العربيُّ بـraqm (تشكيلٌ ووصلٌ واتجاه) — وكلُّ سطرٍ باتجاهٍ واحد.
import io, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features
assert features.check("raqm"), "لا raqm ⇒ لن يتشكّل العربي"

HERE = os.path.dirname(os.path.abspath(__file__))
F700 = os.path.join(HERE, "fonts", "plexfull-700.ttf")
F400 = os.path.join(HERE, "fonts", "plexfull-400.ttf")
MARK = os.path.join(HERE, "mark.png")
GOLD, GD, WW, CH2, GR, LINE = (212, 175, 55), (138, 109, 30), (251, 249, 244), (26, 26, 26), (107, 107, 107), (234, 227, 211)
S = 1080
AR = "٠١٢٣٤٥٦٧٨٩"

def ar_digits(t): return "".join(AR[int(c)] if c.isdigit() else c for c in str(t))
def font(bold, size): return ImageFont.truetype(F700 if bold else F400, size, layout_engine=ImageFont.Layout.RAQM)

def fit(draw, text, bold, size, maxw, rtl=True, min_size=22):
    while size > min_size:
        f = font(bold, size)
        w = draw.textlength(text, font=f, direction="rtl" if rtl else "ltr")
        if w <= maxw: return f
        size -= 2
    return font(bold, min_size)

def txt(draw, xy, text, bold, size, fill, anchor="ms", rtl=True, maxw=820):
    f = fit(draw, text, bold, size, maxw, rtl)
    draw.text(xy, text, font=f, fill=fill, anchor=anchor, direction="rtl" if rtl else "ltr")

def contain(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im2 = im.resize((max(1, int(im.width * r + 1)), max(1, int(im.height * r + 1))), Image.LANCZOS)
    x, y = (im2.width - w) // 2, (im2.height - h) // 2
    return im2.crop((x, y, x + w, y + h))

def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

def flat(im, bg=(255, 255, 255)):
    im = im.convert("RGBA"); b = Image.new("RGBA", im.size, bg + (255,)); b.alpha_composite(im); return b.convert("RGB")

def frame():
    img = Image.new("RGB", (S, S), WW)
    # ظلٌّ ناعمٌ تحت البطاقة
    sh = Image.new("L", (S, S), 0); ImageDraw.Draw(sh).rounded_rectangle((100, 197, 980, 957), 40, fill=40)
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    img.paste(Image.new("RGB", (S, S), (0, 0, 0)), (0, 0), sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((100, 185, 980, 945), 40, fill=(255, 255, 255), outline=GOLD, width=4)
    # الترويسة: الرمز ✓ + «أول بأول»
    try:
        mk = Image.open(MARK).convert("RGBA").resize((100, 100), Image.LANCZOS); img.paste(mk, (610, 38), mk)
    except Exception: pass
    txt(d, (600, 118), "أول بأول", True, 64, CH2, anchor="rs", maxw=500)
    # القدم
    txt(d, (540, 1012), "نختار لك الأفضل… أول بأول", False, 30, GR)
    txt(d, (540, 1052), "awalbawal.com", False, 24, GR, rtl=False)
    return img, d

def code_bar(img, d, code, y, h, label=True):
    d.rounded_rectangle((150 if label else 190, y, 930 if label else 890, y + h), h // 2, fill=CH2)
    if label:
        txt(d, (870, y + h // 2), "الكود", True, 36, (245, 242, 233), anchor="rm", maxw=150)
        txt(d, (470, y + h // 2), code, True, 84, GOLD, anchor="mm", rtl=False, maxw=560)
    else:
        txt(d, (540, y + h // 2), code, True, 112, GOLD, anchor="mm", rtl=False, maxw=640)

def render(item, poster=None, logo=None):
    """item: {code, store, value} · poster/logo: PIL Images أو None ⇒ JPEG bytes"""
    img, d = frame()
    code, store = str(item["code"]).strip(), str(item["store"]).strip()
    value = ar_digits(str(item.get("value") or "").strip())
    if poster is not None:
        W, H, X, Y = 820, 430, 130, 215
        p = flat(poster)
        bg = cover(p, W, H).filter(ImageFilter.GaussianBlur(28))
        bg = Image.blend(bg, Image.new("RGB", (W, H), (255, 255, 255)), 0.35)
        fg = contain(p, W, H); bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
        img.paste(bg, (X, Y), rounded_mask(W, H, 26))
        d.rounded_rectangle((X, Y, X + W, Y + H), 26, outline=LINE, width=2)
        txt(d, (930, 712), store, True, 52, CH2, anchor="rs", maxw=780)
        txt(d, (930, 762), value, False, 30, GR, anchor="rs", maxw=780)
        code_bar(img, d, code, 790, 120, label=True)
    elif logo is not None:
        lg = contain(flat(logo), 500, 190)
        img.paste(lg, (540 - lg.width // 2, 335 - lg.height // 2))
        txt(d, (540, 515), store, True, 62, CH2, maxw=760)
        txt(d, (540, 575), value, False, 32, GR, maxw=760)
        txt(d, (540, 665), "كود الخصم", True, 42, GD, maxw=400)
        code_bar(img, d, code, 700, 160, label=False)
    else:
        txt(d, (540, 410), store, True, 120, CH2, maxw=780)
        txt(d, (540, 500), value, False, 36, GR, maxw=760)
        d.line((420, 550, 660, 550), fill=GOLD, width=3)
        txt(d, (540, 665), "كود الخصم", True, 42, GD, maxw=400)
        code_bar(img, d, code, 700, 160, label=False)
    out = io.BytesIO(); img.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return out.getvalue()

def load_image(data, url=""):
    """bytes ⇒ PIL · SVG بـcairosvg · أو None"""
    if not data: return None
    try:
        if url.split("?")[0].lower().endswith(".svg") or data[:200].lstrip().startswith((b"<svg", b"<?xml")):
            import cairosvg
            data = cairosvg.svg2png(bytestring=data, output_width=900)
        im = Image.open(io.BytesIO(data)); im.load(); return im
    except Exception:
        return None

# ═══════════ 🖼️ WP-732(٨) — بطاقةُ حملة ترينديول «قبل وبعد» ═══════════
# قراره 2026-10-16: «كل الماركات: صورة قبل وبعد من ترينديول» (بعد ٣ تصوّرات: أيوا · ديفاكتو · يارجيجي).
# رأسٌ باسم الماركة · صورةُ المنتج كما في ترينديول · «في ترينديول» كبيرًا · السعرُ الأصلي مشطوبًا · شريطُ الخصم والكود.
# الأرقامُ من بطاقة ترينديول حرفًا (قرأها التابلت) — لا رقمَ يُحسب هنا إلّا الفرق.
# 🔢 قراره 2026-10-16: «ليش الارقام عربيه المفروض انجليزيه» ⇒ أرقامٌ إنجليزيّة (0-9) في هذه البطاقة.
def _num(x):
    return ("%.2f" % float(x)).rstrip("0").rstrip(".")

def render_ty(item, product=None):
    S = 1080
    im = Image.new("RGB", (S, S), WW); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, S, 300), fill=CH2)
    txt(d, (540, 185), str(item.get("brand") or item.get("store") or ""), True, 118, (255, 255, 255), rtl=False, maxw=920)
    d.rectangle((0, 300, S, 308), fill=GOLD)
    box = Image.new("RGB", (470, 640), (255, 255, 255))
    if product is not None:
        p = contain(flat(product), 440, 600); box.paste(p, ((470 - p.width) // 2, (640 - p.height) // 2))
    im.paste(box, (570, 335), rounded_mask(470, 640, 28)); d.rounded_rectangle((570, 335, 1040, 975), 28, outline=LINE, width=3)
    title = str(item.get("title") or "").strip()
    if title: txt(d, (295, 395), title, True, 44, CH2, maxw=480)
    txt(d, (295, 450), str(item.get("store") or ""), False, 30, GR, maxw=480)
    d.rounded_rectangle((60, 490, 530, 660), 24, fill=(255, 247, 226), outline=GOLD, width=3)
    txt(d, (295, 552), "في ترينديول", False, 34, GD, maxw=430)
    txt(d, (295, 638), _num(item["now"]) + " ر.س", True, 78, CH2, maxw=430)
    was = "السعر الأصلي  " + _num(item["was"]) + " ر.س"
    f = fit(d, was, False, 34, 480)
    txt(d, (295, 735), was, False, 34, GR, maxw=480)
    w = d.textlength(was, font=f, direction="rtl"); d.line((295 - w / 2, 723, 295 + w / 2, 723), fill=(190, 60, 60), width=3)
    save = float(item["was"]) - float(item["now"])
    txt(d, (295, 805), "توفّر " + _num(round(save)) + " ريال", True, 40, GD, maxw=480)
    pill = "خصم " + str(int(item.get("off") or 0)) + "%" + ((" · الكود " + item["code"]) if item.get("code") else "")
    d.rounded_rectangle((60, 880, 530, 965), 42, fill=CH2)
    txt(d, (295, 936), pill, True, 34, (255, 255, 255), maxw=440)
    d.rectangle((0, 1000, S, S), fill=CH2)
    try:
        mk = contain(Image.open(MARK).convert("RGBA"), 60, 60); im.paste(mk, (1000, 1010), mk)
    except Exception: pass
    txt(d, (540, 1052), "من العروض أول بأول", True, 34, GOLD, maxw=700)
    out = io.BytesIO(); im.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return out.getvalue()
