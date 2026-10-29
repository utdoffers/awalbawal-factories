#!/usr/bin/env python3
# 👻🖼️ ═══ WP-814 — رسمُ ستوري سناب (1080×1920) بأربعة قوالب ═══
# قرارُه 2026-10-22 بعد النماذج الثلاثة لكود سبورتر: «حلوووو جدا التصاميم الثلاث» ثمّ «ابني كل شي بشكل جذري».
#   today ⇐ 🎟️ كود اليوم   — ثيمُ «أول بأول» الفاتح: الشعار · الخصم كبيرًا · شريطُ الكود الفحمي
#   store ⇐ 🛍️ من المتجر   — صورةُ المتجر بطلةُ البطاقة · شريطُ الكود بلون المتجر
#   bold  ⇐ ⚡ سؤال جريء   — نصفٌ علويٌّ بلون المتجر وسؤالٌ يشدّ · نصفٌ سفليٌّ فحميٌّ والكود
#   live  ⇐ 🔥 عرض حي      — العرضُ الحيّ بهويّتنا (لا نعيد صورَ حسابات غيرنا) · بلا شارة «منقول/متحقَّق» (قرارُه)
# ⚖️ كلُّ نصٍّ من البيانات حرفًا. الأرقامُ إنجليزيّة. والمهمُّ كلُّه داخل منطقة سناب الآمنة (225…1425).
import io, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features
assert features.check("raqm"), "لا raqm ⇒ لن يتشكّل العربي"

HERE = os.path.dirname(os.path.abspath(__file__))
F700 = os.path.join(HERE, "fonts", "plexfull-700.ttf")
F400 = os.path.join(HERE, "fonts", "plexfull-400.ttf")
MARK = os.path.join(HERE, "mark.png")
W, H = 1080, 1920
SAFE_TOP, SAFE_BOT = 225, 1425
GOLD, GD, WW, CH, GR, LINE = (212, 175, 55), (154, 123, 18), (249, 248, 244), (26, 26, 26), (107, 107, 107), (234, 227, 211)
WHITE, RED, GREEN, AMBER = (255, 255, 255), (232, 72, 52), (34, 150, 90), (176, 120, 20)
PROMISE = "أول بأول · تحقّق، انسخ، وفّر"

_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍⬀-⯿]")
def plain(t): return _EMOJI.sub("", str(t or "")).replace("  ", " ").strip()
def west(t):
    t = "".join(str("٠١٢٣٤٥٦٧٨٩".index(c)) if c in "٠١٢٣٤٥٦٧٨٩" else c for c in str(t or ""))
    # «10%» تبقى «10%» داخل سطرٍ عربيّ — عزلٌ يساريٌّ للرقم ونسبته (وإلّا قُلبت «%10»)
    t = t.replace("٪", "%")
    return re.sub(r"(\d+(?:[.,]\d+)?)\s*%", "\u2066\\1%\u2069", t)
def font(bold, size): return ImageFont.truetype(F700 if bold else F400, size, layout_engine=ImageFont.Layout.RAQM)
def is_rtl(t): return bool(re.search(r"[؀-ۿ]", t))

def fit(d, text, bold, size, maxw, min_size=26):
    rtl = is_rtl(text)
    while size > min_size:
        f = font(bold, size)
        if d.textlength(text, font=f, direction="rtl" if rtl else "ltr") <= maxw: return f
        size -= 2
    return font(bold, min_size)

def txt(d, xy, text, bold, size, fill, anchor="mm", maxw=900, min_size=26):
    text = west(plain(text))
    if not text: return
    f = fit(d, text, bold, size, maxw, min_size)
    d.text(xy, text, font=f, fill=fill, anchor=anchor, direction="rtl" if is_rtl(text) else "ltr")

def wrap(d, text, bold, size, maxw, max_lines=3):
    """أسطرٌ تناسب العرض — وما زاد يُختم بنقاط."""
    text = west(plain(text)); f = font(bold, size)
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f, direction="rtl" if is_rtl(t) else "ltr") <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    if len(lines) > max_lines: lines = lines[:max_lines]; lines[-1] = lines[-1].rstrip("،,.") + "…"
    return lines, f

def para(d, x, y, text, bold, size, fill, maxw, max_lines=3, gap=1.35, anchor="ma"):
    lines, f = wrap(d, text, bold, size, maxw, max_lines)
    for i, ln in enumerate(lines):
        d.text((x, y + i * size * gap), ln, font=f, fill=fill, anchor=anchor, direction="rtl" if is_rtl(ln) else "ltr")
    return y + len(lines) * size * gap

def contain(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def flat(im, bg=WHITE):
    im = im.convert("RGBA"); b = Image.new("RGBA", im.size, bg + (255,)); b.alpha_composite(im); return b.convert("RGB")

def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

def shadow(img, box, r, alpha=38, blur=24):
    sh = Image.new("L", img.size, 0); ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + 18, box[2], box[3] + 18), r, fill=alpha)
    img.paste(Image.new("RGB", img.size, (0, 0, 0)), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)))

def accent_of(*ims):
    """لونُ المتجر من شعاره/صورته: أكثرُ لونٍ مشبَعٍ ظهورًا — وإلّا ذهبُنا."""
    best, score = None, 0
    for im in ims:
        if im is None: continue
        sm = flat(im).resize((64, 64))
        q = sm.quantize(colors=8).convert("RGB")
        for n, c in sorted(q.getcolors(64 * 64) or [], reverse=True):
            r, g, b = c; mx, mn = max(c), min(c)
            sat = (mx - mn) / (mx or 1)
            if sat < 0.35 or mx < 70 or mx > 252 and mn > 230: continue
            if n * sat > score: best, score = c, n * sat
    return best or GOLD

def ink_on(c):
    r, g, b = c; return CH if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else WHITE

def header(img, d, y=262, color=CH, align="center"):
    try:
        mk = Image.open(MARK).convert("RGBA").resize((76, 76), Image.LANCZOS)
    except Exception: mk = None
    f = font(True, 50); tw = d.textlength("أول بأول", font=f, direction="rtl")
    total = tw + (88 if mk else 0)
    right = (W + total) / 2 if align == "center" else W - 70
    d.text((right, y), "أول بأول", font=f, fill=color, anchor="rm", direction="rtl")
    if mk: img.paste(mk, (int(right - tw - 88), int(y - 40)), mk)

def code_pill(d, box, code, bg, fg, size=120):
    d.rounded_rectangle(box, (box[3] - box[1]) // 2, fill=bg)
    txt(d, ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2 + 4), code, True, size, fg, maxw=box[2] - box[0] - 80)

def cta(d, y, fill, has_code=True):
    txt(d, (540, y), "صوّرها واحفظ الكود" if has_code else "صوّرها وشاركها", True, 44, fill, maxw=800)

def footer(d, fill):
    txt(d, (540, 1720), PROMISE, True, 34, fill, maxw=900)

def jpg(img):
    out = io.BytesIO(); img.save(out, "JPEG", quality=88, optimize=True, progressive=True); return out.getvalue()

# ═══════════ 🎟️ كود اليوم ═══════════
def r_today(it, logo=None, poster=None):
    img = Image.new("RGB", (W, H), WW); d = ImageDraw.Draw(img)
    header(img, d, 262)
    box = (70, 380, 1010, 1390)
    shadow(img, box, 56); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 56, fill=WHITE, outline=GOLD, width=5)
    f = font(True, 38); tag = "كود اليوم"; tw = d.textlength(tag, font=f, direction="rtl")
    d.rounded_rectangle((540 - tw / 2 - 40, 430, 540 + tw / 2 + 40, 500), 35, fill=(255, 244, 204))
    d.text((540, 466), tag, font=f, fill=(138, 109, 0), anchor="mm", direction="rtl")
    y = 545
    if logo is not None:
        lg = contain(flat(logo), 600, 190); img.paste(lg, (540 - lg.width // 2, y + (190 - lg.height) // 2)); y += 190 + 70
        txt(d, (540, y), it["store"], True, 50, CH, maxw=820); y += 110
    else:
        txt(d, (540, y + 90), it["store"], True, 110, CH, maxw=840); y += 230
    txt(d, (540, y + 20), it["value"], True, 96, CH, maxw=840, min_size=44); y += 120
    txt(d, (540, y + 10), "كود الخصم", True, 44, GD, maxw=500); y += 50
    code_pill(d, (150, y, 930, y + 150), it["code"], CH, GOLD, 124); y += 185
    if it.get("terms"): para(d, 540, y, it["terms"], False, 34, GR, 820, max_lines=2)
    cta(d, 1462, CH, True); footer(d, (179, 154, 74))
    return jpg(img)

# ═══════════ 🛍️ من المتجر ═══════════
def r_store(it, logo=None, poster=None):
    img = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(img)
    acc = accent_of(logo, poster)
    header(img, d, 262, align="right")
    if logo is not None:
        lg = contain(flat(logo), 300, 92); img.paste(lg, (70, 262 - lg.height // 2))
    # البطلة: صورةُ المتجر على هالةٍ دافئة
    glow = Image.new("RGB", (W, 760), WHITE); gd = ImageDraw.Draw(glow)
    tint = tuple(int(c * 0.18 + 255 * 0.82) for c in acc)
    for i in range(40, 0, -1):
        r = 14 * i; gd.ellipse((540 - r, 380 - r * 0.8, 540 + r, 380 + r * 0.8), fill=tuple(int(t + (255 - t) * (i / 40)) for t in tint))
    img.paste(glow, (0, 340))
    if poster is not None:
        p = contain(flat(poster), 940, 700)
        m = rmask(p.width, p.height, 28); img.paste(p, (540 - p.width // 2, 370 + (700 - p.height) // 2), m)
    d = ImageDraw.Draw(img)
    txt(d, (540, 1135), it["store"], True, 58, CH, maxw=900)
    txt(d, (540, 1205), it["value"], False, 42, GR, maxw=900)
    bx = (80, 1250, 1000, 1400)
    d.rounded_rectangle(bx, 75, fill=CH)
    d.rounded_rectangle((80, 1250, 380, 1400), 75, fill=acc); d.rectangle((300, 1250, 380, 1400), fill=acc)
    txt(d, (230, 1328), "الكود", True, 46, ink_on(acc), maxw=240)
    txt(d, (690, 1330), it["code"], True, 104, GOLD if acc == GOLD else WHITE, maxw=560)
    if it.get("terms"): txt(d, (540, 1450), it["terms"], False, 30, GR, maxw=920)
    cta(d, 1510, CH, True); footer(d, (179, 154, 74))
    return jpg(img)

# ═══════════ ⚡ سؤال جريء ═══════════
def r_bold(it, logo=None, poster=None):
    img = Image.new("RGB", (W, H), CH); d = ImageDraw.Draw(img)
    acc = accent_of(logo, poster); ink = ink_on(acc)
    d.polygon([(0, 0), (W, 0), (W, 1000), (0, 1130)], fill=acc)
    header(img, d, 262, color=ink, align="right")
    y = para(d, W - 70, 340, it.get("hook1") or "ناوي تشتري؟", True, 84, ink, 940, max_lines=2, gap=1.2, anchor="ra")
    para(d, W - 70, y + 4, it.get("hook2") or "لا تدفع السعر كامل", True, 70, ink, 940, max_lines=1, anchor="ra")
    pic = poster if poster is not None else logo
    if pic is not None:
        card = Image.new("RGB", (430, 430), WHITE)
        p = contain(flat(pic), 380, 380); card.paste(p, ((430 - p.width) // 2, (430 - p.height) // 2))
        cm = rmask(430, 430, 36); card.putalpha(cm)
        card = card.rotate(6, resample=Image.BICUBIC, expand=True)
        img.paste(card, (60, 600), card)
        d = ImageDraw.Draw(img)
        txt(d, (790, 790), it["value"], True, 120, ink, maxw=500, min_size=44)
        txt(d, (790, 900), it["store"], True, 54, ink, maxw=500)
    else:
        txt(d, (540, 790), it["value"], True, 150, ink, maxw=940, min_size=48)
        txt(d, (540, 920), it["store"], True, 60, ink, maxw=900)
    txt(d, (540, 1185), "كود الخصم", True, 44, WHITE, maxw=500)
    code_pill(d, (150, 1215, 930, 1355), it["code"], acc, ink, 116)
    if it.get("terms"): txt(d, (540, 1398), it["terms"], False, 30, (190, 190, 190), maxw=900)
    cta(d, 1462, WHITE, True); footer(d, acc if acc != CH else GOLD)
    return jpg(img)

# ═══════════ 🔥 عرض حي ═══════════
def r_live(it, logo=None, poster=None):
    img = Image.new("RGB", (W, H), (255, 250, 245)); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 205), fill=RED); d.rectangle((0, 1640, W, H), fill=CH)
    header(img, d, 262)
    # 🚫 بلا شارات «عرض حي» ولا «منقول» ولا «متحقَّق منه» — قرارُه 2026-10-22:
    #    «كلمه عرض حي او منقول غير مناسبه في التصاميم … هو طبيعي منقول لاني كاتب اسم المتجر»
    def block(d, y, real=True):
        y = para(d, W - 80, y, it.get("name") or "", True, 78, CH, 920, max_lines=3, gap=1.25, anchor="ra")
        d.rectangle((W - 80 - 160, y + 18, W - 80, y + 26), fill=RED)
        y += 70
        if it.get("detail"): y = para(d, W - 80, y, it["detail"], False, 46, (60, 60, 60), 920, max_lines=3, anchor="ra") + 20
        if it.get("terms"):
            lines, ff = wrap(d, it["terms"], False, 34, 860, 3)
            bh = 40 + len(lines) * 46 + 50
            d.rounded_rectangle((70, y, 1010, y + bh), 28, fill=WHITE, outline=LINE, width=3)
            d.text((W - 110, y + 28), "الشروط", font=font(True, 34), fill=GD, anchor="ra", direction="rtl")
            for i, ln in enumerate(lines):
                d.text((W - 110, y + 78 + i * 46), ln, font=ff, fill=GR, anchor="ra", direction="rtl" if is_rtl(ln) else "ltr")
            y += bh + 24
        if it.get("ends"):
            txt(d, (W - 80, y + 26), "ينتهي: " + it["ends"], True, 38, RED, anchor="rm", maxw=920); y += 80
        code = (it.get("code") or "").strip()
        if code:
            y += 30
            txt(d, (540, y + 10), "كود الخصم", True, 40, GD, maxw=500)
            code_pill(d, (170, y + 40, 910, y + 175), code, CH, GOLD, 112); y += 190
        return y
    scratch = ImageDraw.Draw(Image.new("RGB", (W, H)))
    h = block(scratch, 0)
    top, bot = 360, 1420
    block(d, top + max(0, (bot - top - h) // 2))
    code = (it.get("code") or "").strip()
    cta(d, 1475, CH, bool(code))
    footer(d, GOLD)
    return jpg(img)

RENDER = {"today": r_today, "store": r_store, "bold": r_bold, "live": r_live}

def render_snap(fields, logo=None, poster=None):
    return RENDER[fields.get("tpl") or "today"](fields, logo=logo, poster=poster)
