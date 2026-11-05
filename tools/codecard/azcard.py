#!/usr/bin/env python3
# 🏷️🖼️ ═══ WP-962 (D-259) — تصميمُ تجميعة ماركات أمازون (قالب «ماركات رياضية» الفاتح · اعتمده صالح 5/11 «نعم اعتمد») ═══
#   azrun.py يسأل /api/azbrands/card/todo ⇐ هنا تُرسم كلُّ صفحة HTML بكروم (Playwright) بخطّ IBM Plex Sans Arabic من fonts/
#   ⇐ JPEG بمقاس إكس 4:5 بالضبط (1080×1350 ×2 = 2160×2700 — قراره 5/11 «انتبه المره الثانيه لاتغلط في المقاس»)
#   ⇐ /api/azbrands/card/upload (ببصمة القائمة المحسومة وحدها). لا رابطَ ولا سعرَ مكتوبٌ هنا: كلُّ ما يُرسم من الخادم.
import html, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
F400 = "file://" + os.path.join(HERE, "fonts", "plexfull-400.ttf")
F700 = "file://" + os.path.join(HERE, "fonts", "plexfull-700.ttf")
W, H = 1080, 1350
E = lambda s: html.escape(str(s if s is not None else ""))

CSS = """
@font-face{font-family:Plex;src:url('%s');font-weight:400}
@font-face{font-family:Plex;src:url('%s');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%dpx;height:%dpx;overflow:hidden}
body{background:#f4f2ee;font-family:Plex,sans-serif;color:#1c1c1c;padding:40px 42px 26px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center}
.logo{font-size:30px;font-weight:700} .logo b{color:#e0a91a;margin-left:8px}
.pill{background:#1c1c1c;color:#fff;border-radius:40px;padding:12px 28px;font-size:22px;font-weight:700} .pill span{color:#f2b628}
h1{font-size:76px;font-weight:700;margin:20px 0 4px;line-height:1.12;white-space:nowrap} h1 .g{color:#e0a91a} h1 .pg{color:#9a948a;font-size:40px;margin-right:12px}
.subt{font-size:24px;color:#6b6b6b;margin-bottom:24px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.grid{flex:1;display:grid;gap:18px;min-height:0}
.g2{grid-template-columns:1fr 1fr}
.card{background:#fff;border:2px solid #ece8e1;border-radius:24px;padding:20px 22px;display:flex;gap:14px;min-height:0;overflow:hidden}
.pic{width:170px;flex:none;display:flex;align-items:center;justify-content:center;order:2}
.pic img{max-width:170px;max-height:100%%;object-fit:contain}
.info{flex:1;display:flex;flex-direction:column;min-width:0;order:1}
.nm{font-size:25px;font-weight:700;line-height:1.28;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.sub{font-size:19px;color:#7a7a7a;margin:3px 0 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pr{display:flex;align-items:center;gap:8px;flex-wrap:nowrap;white-space:nowrap}
.now{font-size:34px;font-weight:700} .bd{font-size:20px;color:#555} .was{font-size:22px;text-decoration:line-through;color:#9a9a9a}
.off{background:#d62f2f;color:#fff;border-radius:10px;padding:2px 10px;font-weight:700;font-size:21px}
.sz{background:#f4f2ee;border-radius:12px;padding:4px 12px;font-size:17px;color:#555;margin-top:9px;align-self:flex-start;max-width:100%%;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.sz bdi{unicode-bidi:isolate}
.box{background:#fdf3d6;border-radius:16px;text-align:center;padding:6px 0 4px;margin-top:auto}
.bl{font-size:18px;color:#a07c11;font-weight:700} .bv{font-size:36px;font-weight:700;color:#a07c11;line-height:1.15}
.span2{grid-column:1 / -1}
.rows .card{padding:22px 28px} .rows .pic{width:300px} .rows .pic img{max-width:300px} .rows .box{margin-top:auto}
.tip{background:#fdf3d6;border:2px solid #f0dc9c;border-radius:20px;padding:18px 26px;font-size:24px;margin-top:18px}
.foot{display:flex;justify-content:space-between;margin-top:16px;font-size:19px;color:#8a8a8a}
""" % (F400, F700, W, H)


def cell(p, span=False):
    # المقاساتُ بكسورها (43⅓) تنقلب في سطرٍ عربيّ («⅓43») ⇒ كلُّ مقاسٍ معزولٌ يسارًا بترتيبه
    sz = ('<div class="sz">📏 <span dir="ltr">%s</span></div>' % " · ".join('<bdi dir="ltr">%s</bdi>' % E(x) for x in str(p["sizes"]).split(" · "))) if p.get("sizes") else ""
    img = ('<img src="%s">' % E(p["img"])) if p.get("img") else ""
    return ('<div class="card%s"><div class="pic">%s</div><div class="info">'
            '<div class="nm">%s</div><div class="sub">%s</div>'
            '<div class="pr"><span class="now">%s</span><span class="bd">بدل</span><span class="was">%s</span>'
            '<span class="off" dir="ltr">-%s%%</span></div>%s'
            '<div class="box"><div class="bl">السعر</div><div class="bv">%s</div></div></div></div>'
            % (" span2" if span else "", img, E(p.get("name")), E(p.get("sub")), E(p.get("price")), E(p.get("was")),
               E(p.get("pct")), sz, E(p.get("price"))))


def page_html(it, pg):
    items = pg.get("items") or []
    k = len(items)
    if k <= 3 and pg.get("of", 1) > 1:
        grid = '<div class="grid rows" style="grid-template-rows:repeat(%d,1fr)">%s</div>' % (max(k, 1), "".join(cell(p) for p in items))
        grid += '<div class="tip">💡 الروابط في التغريدة · الأسعار من أمازون السعودية نفسها</div>'
    else:
        rows = (k + 1) // 2
        cells = [cell(p, span=(k % 2 == 1 and i == k - 1)) for i, p in enumerate(items)]
        grid = '<div class="grid g2" style="grid-template-rows:repeat(%d,1fr)">%s</div>' % (max(rows, 1), "".join(cells))
    of = pg.get("of", 1)
    mark = ('<span class="pg" dir="ltr">(%d/%d)</span>' % (pg["page"], of)) if of > 1 and pg["page"] > 1 else ""
    sub = it.get("sub2") if pg["page"] > 1 else it.get("sub")
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>'
            '<div class="top"><div class="logo"><b>✓</b>العروض أول بأول</div><div class="pill">أمازون · <span>%s</span></div></div>'
            '<h1>%s <span class="g">بخصم</span> يوصل <span dir="ltr">%s%%</span>%s</h1>'
            '<div class="subt">%s</div>%s'
            '<div class="foot"><div>الأسعار%s من أمازون %s · تتغير بأي لحظة</div><div dir="ltr">@awalbawal_sa</div></div>'
            '</body></html>') % (CSS, E(it.get("pill")), E(it.get("hl")), E(it.get("pct")), mark, E(sub), grid,
                                 " والمقاسات" if it.get("sized") else "", E(it.get("date")))


def render_az(it, scale=2):
    """كلُّ صفحة ⇒ JPEG 2160×2700 بالضبط. يعيد [(page, jpg, broken_imgs, overflow_px)]."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pgw = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=scale)
        for pg in it.get("pages") or []:
            path = os.path.join(HERE, "_azcard_%d.html" % pg["page"])
            open(path, "w", encoding="utf-8").write(page_html(it, pg))
            pgw.goto("file://" + path, wait_until="networkidle", timeout=60000)
            pgw.wait_for_timeout(700)
            broken = pgw.evaluate("[...document.images].filter(i=>!i.complete||!i.naturalWidth).length")
            over = pgw.evaluate("Math.max(0,document.body.scrollHeight-%d)+[...document.querySelectorAll('.card')].filter(c=>c.scrollHeight>c.clientHeight+2).length" % H)
            png = pgw.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})
            im = Image.open(io.BytesIO(png)).convert("RGB")
            assert im.size == (W * scale, H * scale), im.size
            for q in (86, 80, 72, 64):
                buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
                if buf.tell() <= 1150000: break
            out.append((pg["page"], buf.getvalue(), broken, over))
        b.close()
    return out
