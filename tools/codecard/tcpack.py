#!/usr/bin/env python3
# 🧡🖼️ ═══ WP-980 — صورةُ تجميعة حملات ترينديول: أقوى ٤ منتجات في صورةٍ واحدة 4:5 (قالب tp1) ═══
#   قولُه 2026-11-07 «ابني» بعد التصميم التجريبي بأرقام 6/11 (نايكي 116 بدل 525 · نيو بالانس 244 بدل 847 كانت مدفونة).
#   المصنعُ نفسُه (ty-cards.yml): tyrun.py يأخذ `pack` من /api/tycamp/cards/todo ⇐ هنا HTML بكروم ⇐ JPEG 2160×2700
#   ⇐ /api/tycamp/cards/upload (cid=pack · ببصمة اليوم وحدها). المقاسُ ثابت 1080×1350 ×2 (قراره 5/11: مقاسُ إكس 4:5 من أوّل مرّة).
#   كلُّ ما يُرسم يأتي من الخادم (الماركة · المنتج · الأسعار · الكود · كم ماركة باقية). أرقامٌ إنجليزيّة (قراره 16/10).
import base64, html, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
F400 = "file://" + os.path.join(HERE, "fonts", "plexfull-400.ttf")
F700 = "file://" + os.path.join(HERE, "fonts", "plexfull-700.ttf")
E = lambda s: html.escape(str(s if s is not None else ""))
W, H = 1080, 1350
MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

CSS = """
@font-face{font-family:Plex;src:url('%s');font-weight:400}
@font-face{font-family:Plex;src:url('%s');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden}
body{background:#f3f2ef;font-family:Plex,sans-serif;color:#1c1c1c;padding:38px 40px 26px}
.top{display:flex;justify-content:space-between;align-items:center}
.logo{font-size:30px;font-weight:700} .logo b{color:#f27a1a;margin-left:8px}
.pill{background:#1c1c1c;color:#fff;border-radius:40px;padding:12px 28px;font-weight:700;font-size:24px} .pill b{color:#f27a1a}
h1{font-weight:700;font-size:76px;line-height:1.15;margin-top:20px;white-space:nowrap} h1 em{color:#f27a1a;font-style:normal}
.sub{font-size:25px;color:#666;margin-top:4px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:24px}
.card{background:#fff;border-radius:26px;padding:20px 22px 18px;position:relative;border:3px solid #fff;height:454px;display:flex;flex-direction:column}
.card.hl{border-color:#f27a1a}
.off{position:absolute;top:16px;left:16px;background:#e0302e;color:#fff;font-weight:700;font-size:26px;border-radius:30px;padding:4px 16px;direction:ltr}
.tag{position:absolute;top:16px;right:16px;background:#fde3cc;color:#c4560a;font-weight:700;font-size:21px;border-radius:30px;padding:4px 14px}
.pic{height:165px;flex-shrink:0;display:flex;justify-content:center;align-items:center;margin-top:34px}
.pic img{max-height:165px;max-width:330px;object-fit:contain;border-radius:12px;mix-blend-mode:multiply}
.brand{flex-shrink:0;line-height:1.3;font-weight:700;font-size:34px;margin-top:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.name{font-size:21px;line-height:1.5;flex-shrink:0;color:#777;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.price{flex-shrink:0;background:#f3f3f1;border-radius:16px;display:flex;justify-content:space-between;align-items:baseline;padding:6px 18px;margin-top:8px}
.now{font-weight:700;font-size:44px;color:#1f9a3c} .now small{font-size:22px}
.was{font-size:26px;color:#9a9a9a;text-decoration:line-through;font-weight:700}
.code{flex-shrink:0;margin-top:auto;padding-top:10px;display:flex;justify-content:space-between;align-items:center;font-size:19px;color:#555}
.code b{background:#f27a1a;color:#fff;border-radius:12px;padding:3px 14px;font-size:24px;letter-spacing:1px;direction:ltr}
.code i{font-style:normal;background:#eaf6ed;color:#1f7a34;border-radius:12px;padding:3px 14px;font-weight:700}
.bar{background:#1c1c1c;color:#fff;border-radius:26px;margin-top:22px;padding:18px 30px;display:flex;justify-content:space-between;align-items:center;font-size:24px;font-weight:700}
.bar b{color:#f27a1a}
.foot{display:flex;justify-content:space-between;color:#8a8a8a;font-size:19px;margin-top:12px}
""" % (F400, F700)


def num(x):
    x = float(x)
    if x >= 1000: return "{:,.0f}".format(x)
    return ("%.2f" % x).rstrip("0").rstrip(".")


def day_ar(d):
    try:
        y, m, dd = [int(v) for v in str(d).split("-")]
        return "%d %s %d" % (dd, MONTHS[m - 1], y)
    except Exception:
        return str(d)


def img_uri(im):
    """PIL ⇒ data URI بعد قصّ الحواف الفاضية (لون الزاوية) — صورُ ترينديول فيها بياضٌ كثير (نايكي 6/11 صغيرة في الوسط)."""
    if im is None: return ""
    from PIL import Image, ImageChops
    im = im.convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
    bb = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > 18 else 0).getbbox()
    if bb:
        pad = 20
        im = im.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad)))
    im.thumbnail((700, 700))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def pack_html(it, pics):
    items = it.get("items") or []
    best = max(range(len(items)), key=lambda i: items[i].get("off") or 0) if items else -1
    cells = []
    for i, p in enumerate(items):
        hl = " hl" if i == best else ""
        tag = '<div class="tag">الأقوى خصم</div>' if i == best else ""
        code = ('<span>🎟️ وبالكود ينزل أكثر</span><b>%s</b>' % E(p.get("code"))) if p.get("code") else '<span></span><i>🛒 الخصم يطلع في السلة</i>'
        cells.append('<div class="card%s">%s<div class="off">-%s%%</div><div class="pic"><img src="%s"></div>'
                     '<div class="brand">%s</div><div class="name">%s</div>'
                     '<div class="price"><span class="now">%s<small> ريال</small></span><span class="was">%s</span></div>'
                     '<div class="code">%s</div></div>'
                     % (hl, tag, E(p.get("off")), pics[i] if i < len(pics) else "", E(p.get("brand")), E(p.get("title")),
                        E(num(p.get("now"))), E(num(p.get("was"))), code))
    more = int(it.get("more") or 0)
    bar = ('<span>➕ %d ماركة ثانية بأكوادها <b>في النص</b> ⬇️</span><span>الروابط في النص</span>' % more) if more else '<span>الروابط والأكواد <b>في النص</b> ⬇️</span><span></span>'
    import re
    hl = re.sub(r"(\d+%)", r'<span dir="ltr">\1</span>', E(it.get("hl")))   # «78%» لا «%78» داخل العربي
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>'
            '<div class="top"><div class="logo"><b>✓</b>العروض أول بأول</div><div class="pill">ترينديول · <b>اليوم بس</b></div></div>'
            '<h1>ماركات معروفة <em>%s</em></h1><div class="sub">%s</div><div class="grid">%s</div>'
            '<div class="bar">%s</div>'
            '<div class="foot"><span>الأسعار من ترينديول %s · تتغير بأي لحظة</span><span dir="ltr">@awalbawal_sa</span></div>'
            '</body></html>') % (CSS, hl, E(it.get("sub")), "".join(cells), bar, E(day_ar(it.get("date"))))


def render_pack(it, fetch, scale=2):
    """⇒ (jpg, مشكلة أو None). المشكلة = ما يمنع الرفع: صورةُ منتجٍ ما نزلت · نصٌّ يطلع برّا · الصفحةُ أطول من 4:5."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    items = it.get("items") or []
    pics = [img_uri(fetch(p.get("img"))) for p in items]
    if any(not u for u in pics):
        return None, "صورةُ منتجٍ ما نزلت (%d من %d)" % (sum(1 for u in pics if not u), len(pics))
    path = os.path.join(HERE, "_tcpack.html")
    open(path, "w", encoding="utf-8").write(pack_html(it, pics))
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=scale)
        pg.goto("file://" + path, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(800)
        # ✂️ العنوانُ يصغر حتى 72% ليدخل سطرًا واحدًا (درسُ WP-973: «1199 على 996 ⇒ انقصّ الرقم») — وإن ما دخل يمسكه الفحص تحت
        pg.evaluate("""() => { const h = document.querySelector('h1'); let f = 76;
          while (h.scrollWidth > h.clientWidth + 2 && f > 55) { f -= 2; h.style.fontSize = f + 'px'; } }""")
        chk = pg.evaluate("""() => {
          const foot = document.querySelector('.foot').getBoundingClientRect().bottom;
          const h1 = document.querySelector('h1'); const wide = h1.scrollWidth > h1.clientWidth + 2;
          const cut = [...document.querySelectorAll('.card')].filter(c => { const r = c.getBoundingClientRect(), k = c.querySelector('.code').getBoundingClientRect(); return k.bottom > r.bottom - 4; }).length;
          const broken = [...document.images].filter(i => !i.complete || !i.naturalWidth).length;
          return {foot, wide, cut, broken};
        }""")
        png = pg.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()
    why = None
    if chk["foot"] > H: why = "الصفحةُ أطول من 1350 (%d)" % chk["foot"]
    elif chk["wide"]: why = "العنوانُ أعرض من الصفحة"
    elif chk["cut"]: why = "%d بطاقة كودها طالع برّا" % chk["cut"]
    elif chk["broken"]: why = "%d صورة ما انرسمت" % chk["broken"]
    im = Image.open(io.BytesIO(png)).convert("RGB")
    if im.size != (W * scale, H * scale): why = why or "المقاس %dx%d لا %dx%d" % (im.size[0], im.size[1], W * scale, H * scale)
    for q in (86, 80, 72, 64):
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
        if buf.tell() <= 1000000: break
    return buf.getvalue(), why
