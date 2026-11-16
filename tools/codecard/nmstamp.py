#!/usr/bin/env python3
# 🏷️🖼️ ═══ WP-1110 — صورةُ صيدة نمشي بشريط الكود تحتها (قالب nm1 · ثيم «أول بأول» الفاتح) ═══
# قولُه 16/11: «الصور اللي تجي مع نون ونمشي ينكتب عليها الكود - العين كذا تشوف ان المنتج مرتبط بالكود» ثمّ «١» (نمشي وحدَها).
# صورةُ المنتج كاملةً داخل إطارٍ أبيض، وتحتها شريطٌ فحميٌّ: «كود الخصم في نمشي» + الكودُ في كبسولةٍ ذهبيّة.
# المقاس: 4:5 لإكس بالضبط (1080×1350 ×2 = 2160×2700 — قراره 5/11 «انتبه المره الثانيه لاتغلط في المقاس»).
# ⚖️ الكودُ والعبارةُ من البيانات حرفًا (todo) — لا كودَ مكتوبٌ هنا. كلُّ سطرٍ باتجاهٍ واحد (العربيُّ بـraqm · الكودُ لاتينيّ وحدَه).
import io
from PIL import Image, ImageDraw
from render import txt, contain, flat, rounded_mask, WW, CH2, GOLD, LINE

W, H = 2160, 2700
PANEL = (60, 60, 2100, 2240)          # إطارُ صورة المنتج
STRIP = (60, 2290, 2100, 2640)        # شريطُ الكود
PILL = (130, 2350, 1000, 2580)        # كبسولةُ الكود (يسار الشريط)

def render_nm(item, product=None):
    """item: {code, label} · product: PIL Image أو None ⇒ JPEG bytes بمقاس 2160×2700 بالضبط."""
    code = str(item["code"]).strip()
    label = str(item.get("label") or "كود الخصم").strip()
    im = Image.new("RGB", (W, H), WW); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = PANEL; pw, ph = x1 - x0, y1 - y0
    panel = Image.new("RGB", (pw, ph), (255, 255, 255))
    if product is not None:
        p = contain(flat(product), pw - 160, ph - 160)
        panel.paste(p, ((pw - p.width) // 2, (ph - p.height) // 2))
    im.paste(panel, (x0, y0), rounded_mask(pw, ph, 60))
    d.rounded_rectangle(PANEL, 60, outline=LINE, width=4)
    d.rounded_rectangle(STRIP, 80, fill=CH2)
    cy = (STRIP[1] + STRIP[3]) // 2
    txt(d, (STRIP[2] - 90, cy), label, True, 88, (255, 255, 255), anchor="rm", maxw=STRIP[2] - 90 - PILL[2] - 60)
    d.rounded_rectangle(PILL, (PILL[3] - PILL[1]) // 2, fill=GOLD)
    txt(d, ((PILL[0] + PILL[2]) // 2, cy), code, True, 150, CH2, anchor="mm", rtl=False, maxw=PILL[2] - PILL[0] - 120)
    out = io.BytesIO(); im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    return out.getvalue()
