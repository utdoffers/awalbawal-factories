#!/usr/bin/env python3
# 🏷️🖼️ ═══ WP-960 — تصميمُ تجميعة ماركات ترينديول (قالب نوفمبر الفاتح · اعتمده صالح 5/11 «اعتمد») ═══
#   المصنعُ نفسُه (ty-cards.yml): tyrun.py يسأل /api/tybrands/card/todo ⇐ هنا يُرسم HTML بكروم (Playwright)
#   بخطّ IBM Plex Sans Arabic من fonts/ ⇐ JPEG ⇐ /api/tybrands/card/upload (ببصمة اليوم وحدها).
#   لا رابطَ ولا كودَ مكتوبٌ هنا: كلُّ ما يُرسم يأتي من الخادم (الكودُ والأسعارُ والصور).
import html, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
F400 = "file://" + os.path.join(HERE, "fonts", "plexfull-400.ttf")
F700 = "file://" + os.path.join(HERE, "fonts", "plexfull-700.ttf")
E = lambda s: html.escape(str(s if s is not None else ""))

CSS = """
@font-face{font-family:Plex;src:url('%s');font-weight:400}
@font-face{font-family:Plex;src:url('%s');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;background:#f4f2ee;font-family:Plex,sans-serif;color:#1c1c1c;padding:34px 36px 26px}
.top{display:flex;justify-content:space-between;align-items:center}
.logo{font-size:30px;font-weight:700} .logo b{color:#e3a51c}
.pill{background:#1c1c1c;color:#fff;border-radius:40px;padding:12px 26px;font-size:20px;font-weight:700} .pill span{color:#f2b628}
h1{font-size:70px;font-weight:700;margin:22px 0 4px;line-height:1.15} h1 .hl{color:#f27a1a}
.subt{font-size:23px;color:#6b6b6b;margin-bottom:22px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card{background:#fff;border:2px solid #ece8e1;border-radius:22px;padding:18px;display:flex;gap:14px;min-height:262px}
.pic{width:150px;flex:none;display:flex;align-items:center;justify-content:center}
.pic img{max-width:150px;max-height:215px;object-fit:contain;border-radius:10px}
.noimg{width:130px;height:170px;border-radius:14px;background:#f6f3ee;display:flex;align-items:center;justify-content:center;font-size:54px}
.info{flex:1;display:flex;flex-direction:column;min-width:0}
.nm{font-size:23px;font-weight:700;line-height:1.25} .sub{font-size:17px;color:#7a7a7a;margin:2px 0 8px;min-height:6px}
.pr{font-size:19px;color:#555;white-space:nowrap} .now{font-size:27px;font-weight:700;color:#1c1c1c}
.was{text-decoration:line-through;color:#9a9a9a} .off{background:#d62f2f;color:#fff;border-radius:9px;padding:2px 9px;font-weight:700;font-size:18px;margin-right:4px}
.sz{background:#f4f2ee;border-radius:12px;padding:4px 12px;font-size:15px;color:#555;margin:9px 0;align-self:flex-start}
.box{background:#fdf3d6;border-radius:14px;text-align:center;padding:6px 0 4px;margin-top:auto}
.bl{font-size:16px;color:#a07c11;font-weight:700} .bv{font-size:32px;font-weight:700;color:#a07c11;line-height:1.1}
.dark{background:#1c1c1c;border-color:#1c1c1c;color:#fff;align-items:center;justify-content:center}
.wide{grid-column:1 / -1;min-height:200px}
.cd{text-align:center} .cdrow{display:flex;gap:16px;align-items:center;justify-content:center;margin-bottom:16px}
.key{font-size:28px;font-weight:700} .code{background:#f2b628;color:#1c1c1c;font-size:38px;font-weight:700;letter-spacing:3px;border-radius:14px;padding:6px 22px;direction:ltr}
.cdt{font-size:20px;line-height:1.6;color:#ddd} .cdt b{color:#f2b628}
.foot{display:flex;justify-content:space-between;margin-top:18px;font-size:17px;color:#8a8a8a}
""" % (F400, F700)


def card_html(it):
    items = it.get("items") or []
    cells = []
    for p in items:
        sub = E(p.get("brand") or "")
        sz = ('<div class="sz">📏 %s</div>' % E(p["sizes"])) if p.get("sizes") else ""
        # 🛡️ WP-990: صورةُ المنتج الحسّاس غيرُ المناسبة تُفرَّغ ⇒ مربّعٌ هادئ بدل صورةٍ مكسورة
        pic = ('<img src="%s">' % E(p.get("img"))) if p.get("img") else '<div class="noimg">🏷️</div>'
        cells.append(
            '<div class="card"><div class="pic">%s</div><div class="info">'
            '<div class="nm">%s</div><div class="sub">%s</div>'
            '<div class="pr"><span class="now">%s</span> <span class="bd">بدل</span> <span class="was">%s</span> '
            '<span class="off" dir="ltr">-%s%%</span></div>%s'
            '<div class="box"><div class="bl">السعر</div><div class="bv">%s</div></div></div></div>'
            % (pic, E(p.get("title")), sub, E(p.get("price")), E(p.get("was")), E(p.get("pct")), sz, E(p.get("price"))))
    if it.get("code"):
        wide = " wide" if len(items) % 2 == 0 else ""
        cells.append('<div class="card dark%s"><div class="cd"><div class="cdrow"><span class="key">🔑 الكود</span>'
                     '<span class="code">%s</span></div><div class="cdt">كود الخصم يشتغل من <b>تطبيق ترينديول</b><br>'
                     'ورابط كل منتج في التغريدة</div></div></div>' % (wide, E(it["code"])))
    lead = (E(it.get("lead")) + " ") if it.get("lead") else ""
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>'
            '<div class="top"><div class="logo"><b>✓</b> العروض أول بأول</div><div class="pill">ترينديول · <span>تجميعة اليوم</span></div></div>'
            '<h1>%s<span class="hl">%s</span> بخصم يوصل <span dir="ltr">%s%%</span></h1>'
            '<div class="subt">%s</div><div class="grid">%s</div>'
            '<div class="foot"><div>الأسعار والمقاسات من ترينديول %s · تتغير بأي لحظة</div><div dir="ltr">@awalbawal_sa</div></div>'
            '</body></html>') % (CSS, lead, E(it.get("hl")), E(it.get("pct")), E(it.get("sub")), "".join(cells), E(it.get("date")))


def render_tb(it, scale=2):
    """HTML ⇒ JPEG بكروم. يصغّر الجودة حتى يدخل سقفَ الخادم (~1.4MB)."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    path = os.path.join(HERE, "_tbcard.html")
    open(path, "w", encoding="utf-8").write(card_html(it))
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1000}, device_scale_factor=scale)
        pg.goto("file://" + path, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(800)
        broken = pg.evaluate("[...document.images].filter(i=>!i.complete||!i.naturalWidth).length")
        png = pg.screenshot(full_page=True)
        b.close()
    im = Image.open(io.BytesIO(png)).convert("RGB")
    for q in (86, 80, 72, 64):
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
        if buf.tell() <= 1400000: break
    return buf.getvalue(), broken
