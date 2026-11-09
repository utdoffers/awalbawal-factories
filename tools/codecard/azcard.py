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
h1{font-size:76px;font-weight:700;margin:20px 0 4px;line-height:1.12;white-space:nowrap} h1 .g{color:#e0a91a} h1 .pg{color:#9a948a;font-size:.53em;margin-right:12px}
h1 .nw{white-space:nowrap}
.subt{font-size:24px;color:#6b6b6b;margin-bottom:24px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.grid{flex:1;display:grid;gap:18px;min-height:0}
.g2{grid-template-columns:1fr 1fr}
.card{background:#fff;border:2px solid #ece8e1;border-radius:24px;padding:20px 22px;display:flex;gap:14px;min-height:0;overflow:hidden}
.pic{width:170px;flex:none;display:flex;align-items:center;justify-content:center;order:2}
.pic img{max-width:170px;max-height:100%%;object-fit:contain}
.info{flex:1;display:flex;flex-direction:column;min-width:0;order:1}
.nm{font-size:25px;font-weight:700;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.sub{font-size:19px;color:#7a7a7a;margin:3px 0 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pr{display:flex;align-items:center;gap:8px;flex-wrap:nowrap;white-space:nowrap}
.now{font-size:34px;font-weight:700} .bd{font-size:20px;color:#555} .was{font-size:22px;text-decoration:line-through;color:#9a9a9a}
.off{background:#d62f2f;color:#fff;border-radius:10px;padding:2px 10px;font-weight:700;font-size:21px}
.sz{background:#f4f2ee;border-radius:12px;padding:4px 12px;font-size:17px;color:#555;margin-top:9px;align-self:flex-start;max-width:100%%;line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.sz bdi{unicode-bidi:isolate}
.box{background:#fdf3d6;border-radius:16px;text-align:center;padding:6px 0 4px;margin-top:auto}
.bl{font-size:18px;color:#a07c11;font-weight:700} .bv{font-size:36px;font-weight:700;color:#a07c11;line-height:1.15}
.span2{grid-column:1 / -1}
.rows .card{padding:22px 28px} .rows .pic{width:300px} .rows .pic img{max-width:300px} .rows .box{margin-top:auto}
.tip{background:#fdf3d6;border:2px solid #f0dc9c;border-radius:20px;padding:18px 26px;font-size:24px;margin-top:18px}
.foot{display:flex;justify-content:space-between;margin-top:16px;font-size:19px;color:#8a8a8a}
.info>*{flex-shrink:0}
body.t1 .nm{font-size:22px} body.t1 .sub{font-size:17px;margin:2px 0 5px} body.t1 .now{font-size:30px} body.t1 .sz{font-size:15px;margin-top:6px} body.t1 .bv{font-size:30px} body.t1 .bl{font-size:16px} body.t1 .card{padding:16px 20px} body.t1 .was{font-size:20px} body.t1 .off{font-size:19px;padding:2px 8px} body.t1 .bd{font-size:18px} body.t1 .pr{gap:6px}
body.t2 .nm{font-size:20px} body.t2 .sub{font-size:16px;margin:1px 0 4px} body.t2 .now{font-size:27px} body.t2 .was{font-size:18px} body.t2 .off{font-size:17px;padding:1px 7px} body.t2 .bd{font-size:16px} body.t2 .pr{gap:5px} body.t2 .sz{font-size:14px;margin-top:4px;-webkit-line-clamp:1} body.t2 .bv{font-size:26px} body.t2 .bl{font-size:14px} body.t2 .box{padding:3px 0 2px} body.t2 .card{padding:14px 18px} body.t2 .grid{gap:14px}
""" % (F400, F700, W, H)


# 🛒 WP-966: قالبُ «بقالة اليوم» (ag1) — نفسُ الترتيب بألوان البقالة: أخضرُ زيتونيّ بدل الذهبيّ · سلّةٌ بدل الماركة · الحجمُ سطرُه الثاني
CSS_AG = CSS + """
body{background:#f1f5ee}
.logo b{color:#2f8f4e}
.pill{background:#1f5f36} .pill span{color:#b8f0c8}
h1{font-size:70px} h1 .g{color:#2f8f4e}
.card{border-color:#dfe9db}
.sub{color:#3f7a52;font-weight:700}
.off{background:#e0662a}
.box{background:#e3f3e6} .bl,.bv{color:#1f6b3c}
body{--acc:#1f6b3c}
.tip{background:#e3f3e6;border-color:#bfe0c6}
"""


# 🏷️ WP-967: قالبُ «ماركات علي إكسبريس» (ae1) — ترتيبُ ab1 نفسُه بأحمر علي إكسبريس · السطرُ الثاني المواصفة
CSS_AE = CSS + """
body{background:#f7f1ef}
.logo b{color:#e5372b}
.pill{background:#b0201a} .pill span{color:#ffd2cc}
h1 .g{color:#e5372b}
.card{border-color:#eedbd7}
.sub{color:#9a3a32;font-weight:700}
.off{background:#e5372b}
.box{background:#fde6e2} .bl,.bv{color:#b0201a}
body{--acc:#b0201a}
.tip{background:#fde6e2;border-color:#f3c4bd}
"""
LAYOUT_CSS = {"ag1": CSS_AG, "ae1": CSS_AE}

# 📺 ═══ WP-991 — قالبُ «دليل الشراء» (gd1) ═══
#   بعد قوله 2026-11-08 «الصور معجبتك كذا ؟»: في ae1 كانت صورةُ المنتج بنرَ المتجر (شعار وكود وNEW) مصغّرةً لسدس الكرت،
#   ونصُّ الكرت فاضي، والسعرُ مكتوبٌ مرّتين، والسطرُ الثاني مقصوص («السعر ح...»). هنا: الصورةُ البطل فوق (صورةٌ بلا كتابة يختارها Claude ويقصّ الجهاز — prep_guide_imgs)
#   · الاسم · «👈 لمين» · سعرٌ واحد «من 1,805 ريال» ومقاسُه · «بدل» · المقاساتُ المتوفّرة · ووسمُ الموديل شارةٌ في زاويته.
#   4 موديلات ⇒ 2×2 · 5–6 ⇒ 3×2. المقاسُ 1080×1350 (×2) كما هو.
CSS_GD = CSS + """
body{background:#f7f1ef}
.logo b{color:#e5372b}
.pill{background:#b0201a} .pill span{color:#ffd2cc}
h1 .g{color:#e5372b}
.grid{gap:16px}
.gcard{background:#fff;border:2px solid #eedbd7;border-radius:26px;padding:16px 18px 16px;display:flex;flex-direction:column;min-height:0;overflow:hidden;position:relative}
.gcard .tg{position:absolute;top:12px;right:12px;background:#b0201a;color:#fff;border-radius:30px;padding:5px 14px;font-size:19px;font-weight:700;z-index:2}
.gcard .tg.lo{background:#1f7a45} .gcard .tg.hot{background:#e5372b} .gcard .tg.top{background:#1c1c1c;color:#f2c94c}
.gpic{flex:1;min-height:0;position:relative;margin:34px 0 10px;border-radius:16px;overflow:hidden}
.gpic img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}
.info{display:flex;flex-direction:column;min-width:0;flex:none}
.nm{font-size:26px;font-weight:700;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.fr{font-size:20px;color:#b0201a;font-weight:700;line-height:1.5;margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.sub{font-size:17px;color:#8a8a8a;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.5}
.gpr{display:flex;align-items:baseline;gap:7px;margin-top:8px;white-space:nowrap}
.gpr .fm{font-size:20px;color:#555;font-weight:700} .gpr .now{font-size:40px;font-weight:700;color:#b0201a;line-height:1.1} .gpr .cur{font-size:19px;color:#555}
.gpr2{display:flex;align-items:center;gap:7px;margin-top:4px;white-space:nowrap;min-height:30px}
.gpr2 .szc{background:#fde6e2;color:#9a3a32;border-radius:10px;padding:2px 10px;font-size:17px;font-weight:700}
.gpr2 .bd{font-size:17px;color:#777} .gpr2 .was{font-size:19px;text-decoration:line-through;color:#9a9a9a}
.gpr2 .off{background:#e5372b;color:#fff;border-radius:9px;padding:1px 8px;font-weight:700;font-size:17px}
.sz{background:#f4f2ee;border-radius:12px;padding:3px 12px;font-size:16px;color:#555;margin-top:8px;align-self:flex-start;max-width:100%;line-height:1.5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.c3 .nm{font-size:22px} .c3 .fr{font-size:17px} .c3 .sub{font-size:15px} .c3 .gpr .now{font-size:33px} .c3 .gpr .fm,.c3 .gpr .cur{font-size:16px}
.c3 .gpr2 .szc,.c3 .gpr2 .off{font-size:14px} .c3 .gpr2 .was{font-size:16px} .c3 .gpr2 .bd{font-size:14px} .c3 .sz{font-size:14px} .c3 .gcard .tg{font-size:16px;padding:4px 11px}
.c3 .gcard{padding:14px 14px} .c3 .gpic{margin:32px 0 8px}
body.t1 .nm{-webkit-line-clamp:1} body.t1 .fr{-webkit-line-clamp:1} body.t1 .gpr .now{font-size:34px}
body.t2 .sub{display:none} body.t2 .sz{display:none}
.foot{margin-top:14px}
"""


def gcell(p):
    tag = str(p.get("tag") or "")
    cls = "lo" if "الأرخص" in tag else "top" if "الأفخم" in tag else "hot" if "طلب" in tag else ""
    tg = ('<div class="tg %s">%s</div>' % (cls, E(tag))) if tag else ""
    img = ('<img src="%s">' % E(p["img"])) if p.get("img") else ""
    fr = ('<div class="fr">👈 %s</div>' % E(p["for"])) if p.get("for") else ""
    sub = ('<div class="sub">%s</div>' % E(p["sub"])) if p.get("sub") else ""
    fm = '<span class="fm">من</span>' if p.get("from") else ""
    szc = ('<span class="szc">%s</span>' % E(p["size"])) if p.get("size") else ""
    was = ('<span class="bd">بدل</span><span class="was">%s</span><span class="off" dir="ltr">-%s%%</span>' % (E(p.get("was")), E(p.get("pct")))) if p.get("was") not in (None, "") else ""
    # المقاساتُ بترتيبها من اليمين (55 أوّلًا) — بلا عزلٍ يساريّ (كان يقلبها 85 · 75 · 65 · 55)
    sz = ('<div class="sz">📏 المتوفر: %s%s</div>' % (E(p["sizes"]), (" " + E(p["unit"])) if p.get("unit") else "")) if p.get("sizes") else ""
    return ('<div class="card gcard">%s<div class="gpic">%s</div><div class="info">'
            '<div class="nm">%s</div>%s%s'
            '<div class="gpr">%s<span class="now">%s</span><span class="cur">ريال</span></div>'
            '<div class="gpr2">%s%s</div>%s</div></div>'
            % (tg, img, E(p.get("name")), fr, sub, fm, E(p.get("price")), szc, was, sz))


def guide_html(it, pg):
    items = pg.get("items") or []
    k = len(items)
    cols = 2 if k <= 4 else 3
    rows = max(1, (k + cols - 1) // cols)
    grid = '<div class="grid %s" style="grid-template-columns:repeat(%d,1fr);grid-template-rows:repeat(%d,1fr)">%s</div>' % (
        "c3" if cols == 3 else "c2", cols, rows, "".join(gcell(p) for p in items))
    h1 = '<h1>%s <span class="g">%s</span></h1>' % (E(it.get("hl_pre") or "دليل شراء"), E(it.get("hl")))
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>'
            '<div class="top"><div class="logo"><b>✓</b>العروض أول بأول</div><div class="pill">%s · <span>%s</span></div></div>'
            '%s<div class="subt">%s</div>%s'
            '<div class="foot"><div>الأسعار%s %s %s · تتغير بأي لحظة</div><div dir="ltr">@awalbawal_sa</div></div>'
            '</body></html>') % (CSS_GD, E(it.get("store") or "علي إكسبريس"), E(it.get("pill")), h1, E(it.get("sub")), grid,
                                 " والمقاسات" if it.get("sized") else "", E(it.get("foot") or ""), E(it.get("date")))


# 🖼️ WP-991: صورةُ الموديل — يختارها Claude (sonnet) في الخادم لحظةَ الحسم: رقمُ الصورة بلا كتابة + مربّعُ الجهاز (pic).
#   جُرّب قبله «أكثرُها بياضًا» على صور TCL فاختار إنفوجرافيك الضمان (أبيضُ بكتابةٍ حمراء) للأربع ⇒ شيل. بلا اختيار Claude ⇒ الصورةُ الأولى كما كانت.
def _img_get(url, timeout=12):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def crop_white(im, pad=0.04):
    """يقصّ الحوافَّ البيضاء حول المنتج (مع هامشٍ صغير) — المنتجُ يملأ مكانه. نقيّة."""
    from PIL import ImageChops, Image
    rgb = im.convert("RGB")
    bg = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, bg).convert("L").point(lambda x: 255 if x > 22 else 0)
    box = diff.getbbox()
    if not box: return rgb
    w, h = rgb.size; px, py = int(w * pad), int(h * pad)
    box = (max(0, box[0] - px), max(0, box[1] - py), min(w, box[2] + px), min(h, box[3] + py))
    if (box[2] - box[0]) * (box[3] - box[1]) < 0.15 * w * h: return rgb
    return rgb.crop(box)


def crop_box(im, box, pad=0.03):
    """يقصّ مربّعَ الجهاز (نسبٌ مئوية من Claude) بهامشٍ صغير — مربّعُه تقريبيّ فالهامشُ يحمي الأطراف. نقيّة."""
    rgb = im.convert("RGB"); w, h = rgb.size
    x0, y0, x1, y1 = [float(v) / 100 for v in box]
    x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(1, x1 + pad), min(1, y1 + pad)
    if (x1 - x0) < 0.2 or (y1 - y0) < 0.2: return rgb
    return rgb.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))


def _uri(im):
    import base64
    im = im.convert("RGB"); im.thumbnail((900, 900))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def prep_guide_imgs(it, get=_img_get, say=print):
    """لكلِّ موديل: اختيارُ Claude (pic: صورة + مربّع) يُقصّ · وإلّا الأولى كما هي."""
    from PIL import Image
    for pg in it.get("pages") or []:
        for p in pg.get("items") or []:
            pic = p.get("pic") or {}
            if pic.get("u"):
                try:
                    im = Image.open(io.BytesIO(get(pic["u"]))); im.load()
                    p["img"] = _uri(crop_box(im, pic["box"]) if pic.get("box") else crop_white(im))
                    say("   🖼️", str(p.get("name"))[:30], "⇐ اختيار Claude", "بمربّع" if pic.get("box") else "بلا مربّع"); continue
                except Exception as e:
                    say("   🖼️", str(p.get("name"))[:30], "⇐ صورة Claude ما نزلت:", repr(e)[:60])
            say("   🖼️", str(p.get("name"))[:30], "⇐ الصورة الأولى (بلا اختيار Claude)")



def prep_card_imgs(it, get=_img_get, say=print):
    """🖼️ WP-1004: صورُ التجميعات (ab1 · ag1 · ae1) — الحوافُّ البيضاء تُقصّ فيملأ المنتجُ مكانه (صورُ أمازون 500×500 والجزمةُ في ثلثها).
    تعذّر التحميلُ أو القصّ ⇒ الرابطُ كما هو (كروم يحمّله كما كان) والسببُ في السجلّ. نفسُ الرابط ⇒ تحميلٌ واحد."""
    from PIL import Image
    seen = {}
    for pg in it.get("pages") or []:
        for p in pg.get("items") or []:
            u = p.get("img") or ""
            if not u.startswith("http"): continue
            if u not in seen:
                try:
                    im = Image.open(io.BytesIO(get(u))); im.load()
                    seen[u] = _uri(crop_white(im))
                except Exception as e:
                    seen[u] = u; say("   🖼️", str(p.get("name"))[:30], "⇐ ما انقصّت (الرابط كما هو):", repr(e)[:60])
            p["img"] = seen[u]


def cell(p, span=False):
    # 🖼️ WP-1004 (قوله 9/11 «اعتمد ونفذ بشكل جذري» بعد «ليش صور المنتجات صغار»): كانت الصورةُ عمودًا جانبيًّا عرضُه 170 من ~490
    #   (الجزمة 170×85 في بطاقةٍ طولُها ~450) والسعرُ مكتوبٌ مرّتين (جنب الاسم + مربّع «السعر» الأصفر).
    #   الآن: الصورةُ تملأ ما بقي من البطاقة (فوق أو جنب — يختار LAYOUT_PICK_JS الأكبرَ للمنتج) · حوافُّها البيضاء مقصوصة (prep_card_imgs)
    #   · والسعرُ مرّةً واحدة «114.85 ريال بدل 335 -66%». المقاساتُ بكسورها (43⅓) معزولةٌ يسارًا بترتيبها كما كانت.
    sz = ('<div class="sz">📏 <span dir="ltr">%s</span></div>' % " · ".join('<bdi dir="ltr">%s</bdi>' % E(x) for x in str(p["sizes"]).split(" · "))) if p.get("sizes") else ""
    img = ('<img src="%s">' % E(p["img"])) if p.get("img") else ""
    was = ('<span class="bd">بدل</span><span class="was">%s</span><span class="off" dir="ltr">-%s%%</span>' % (E(p.get("was")), E(p.get("pct")))) if p.get("was") not in (None, "") else ""
    tag = ('<div class="ctg">%s</div>' % E(p["tag"])) if p.get("tag") else ""
    return ('<div class="card%s">%s<div class="pic">%s</div><div class="info">'
            '<div class="nm">%s</div><div class="sub">%s</div>'
            '<div class="pr"><span class="now">%s</span><span class="cur">ريال</span>%s</div>%s</div></div>'
            % (" span2" if span else "", tag, img, E(p.get("name")), E(p.get("sub")), E(p.get("price")), was, sz))


# 🖼️ WP-1004: قالبُ البطاقة — الصورةُ هي البطل. يُلحق بعد قالب الطبقة (ab1 · ag1 · ae1) فيعلو عليه، ولونُ السعر من --acc لكلِّ طبقة.
CSS_CELL = """
:root{--acc:#a07c11}
.card{flex-direction:column;gap:8px;padding:14px 18px;position:relative}
.card .pic{order:0;width:auto;flex:1 1 auto;min-height:0;position:relative}
.card .pic img{position:absolute;inset:0;width:100%;height:100%;max-width:none;max-height:none;object-fit:contain}
.card .info{order:1;flex:none}
body.ph .card,.rows .card,.card.span2{flex-direction:row;gap:18px}
body.ph .card .pic,.rows .card .pic,.card.span2 .pic{order:2;flex:0 0 44%;width:auto}
body.ph .card .info,.rows .card .info,.card.span2 .info{flex:1;justify-content:center}
.pr{align-items:baseline;margin-top:4px}
.now{color:var(--acc);font-size:36px;line-height:1.15} .cur{font-size:19px;color:#666;font-weight:700}
.pr .bd{margin-inline-start:6px}
.box{display:none}
.ctg{position:absolute;top:12px;right:12px;background:#1c1c1c;color:#f2c94c;border-radius:30px;padding:4px 14px;font-size:18px;font-weight:700;z-index:2}
body.t1 .now{font-size:31px} body.t1 .cur{font-size:17px} body.t1 .card{gap:6px}
body.t2 .now{font-size:27px} body.t2 .cur{font-size:15px} body.t2 .card{gap:4px;padding:12px 16px}
"""


def page_html(it, pg):
    items = pg.get("items") or []
    k = len(items)
    if k <= 3 and pg.get("of", 1) > 1:
        grid = '<div class="grid rows" style="grid-template-rows:repeat(%d,1fr)">%s</div>' % (max(k, 1), "".join(cell(p) for p in items))
        grid += '<div class="tip">%s</div>' % E(it.get("tip") or "💡 الروابط في التغريدة · الأسعار من أمازون السعودية نفسها")
    else:
        rows = (k + 1) // 2
        cells = [cell(p, span=(k % 2 == 1 and i == k - 1)) for i, p in enumerate(items)]
        grid = '<div class="grid g2" style="grid-template-rows:repeat(%d,1fr)">%s</div>' % (max(rows, 1), "".join(cells))
    of = pg.get("of", 1)
    mark = ('<span class="pg" dir="ltr">(%d/%d)</span>' % (pg["page"], of)) if of > 1 and pg["page"] > 1 else ""
    sub = it.get("sub2") if pg["page"] > 1 else it.get("sub")
    # 📺 WP-969: الدليلُ عنوانُه «دليل شراء <الفئة>» · والتجميعاتُ كما كانت حرفًا «<الماركة> بخصم يوصل X%»
    if it.get("guide"):
        h1 = '<h1>%s <span class="g">%s</span>%s</h1>' % (E(it.get("hl_pre") or "دليل شراء"), E(it.get("hl")), mark)
    else:
        h1 = '<h1>%s <span class="g">بخصم</span> <span class="nw">يوصل <span dir="ltr">%s%%</span></span>%s</h1>' % (E(it.get("hl")), E(it.get("pct")), mark)
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>'
            '<div class="top"><div class="logo"><b>✓</b>العروض أول بأول</div><div class="pill">%s · <span>%s</span></div></div>'
            '%s'
            '<div class="subt">%s</div>%s'
            '<div class="foot"><div>الأسعار%s %s %s · تتغير بأي لحظة</div><div dir="ltr">@awalbawal_sa</div></div>'
            '</body></html>') % (LAYOUT_CSS.get(it.get("layout"), CSS) + CSS_CELL, E(it.get("store") or "أمازون"), E(it.get("pill")), h1, E(sub), grid,
                                 " والمقاسات" if it.get("sized") else "", E(it.get("foot") or "من أمازون"), E(it.get("date")))



# ➕ ═══ WP-995 — قالبُ «المرافق» (cp1): الصيدةُ كبيرةً فوق · «+ ويكمّلها» · ما يكمّلها تحت · «الاثنين معًا / توفّر» ═══
#   بعد التصوّر الذي أرسله Claude 8/11 (حفاضات بيبي جوي + مناديلها · مكواة براون + طاولة كي) وقوله «اعتمد وابني».
#   ألوانُ قالب ab1 نفسُها وخطُّه · لا رابطَ ولا سعرَ يُكتب هنا: كلُّه من الخادم (lib/companion.js · cpCardItem).
CSS_CP = CSS + """
.cp-main{margin-top:28px;padding:30px 34px;flex:1.35;gap:22px}
.cp-main .pic{width:400px}.cp-main .pic img{max-width:400px;max-height:430px}
.cp-comp{padding:22px 30px;flex:.8;gap:22px}
.cp-comp .pic{width:250px}.cp-comp .pic img{max-width:250px;max-height:260px}
.card.cp-main,.card.cp-comp{display:flex}
.cp .info{justify-content:center}
.cp .tag{align-self:flex-start;background:#fdf3d6;color:#a07c11;font-weight:700;font-size:21px;border-radius:12px;padding:4px 14px;margin-bottom:14px}
.cp .nm{font-size:36px;-webkit-line-clamp:3} .cp-comp .nm{font-size:30px;-webkit-line-clamp:2}
.cp .now{font-size:58px} .cp-comp .now{font-size:46px} .cp .cur{font-size:26px;font-weight:700}
.cp .was{font-size:28px} .cp .off{font-size:28px;padding:3px 14px;border-radius:12px}
.plus{display:flex;align-items:center;gap:16px;margin:18px 6px}
.plus .c{width:58px;height:58px;border-radius:50%;background:#e0a91a;color:#fff;font-size:44px;font-weight:700;display:flex;align-items:center;justify-content:center;line-height:1}
.plus .t{font-size:30px;font-weight:700;white-space:nowrap}.plus .t span{color:#a07c11}
.plus .ln{flex:1;border-top:3px dashed #ddd5c6}
.cbox{background:#fdf3d6;border-radius:20px;display:flex;justify-content:space-around;padding:14px 0;margin-top:20px}
.cbox div{text-align:center}.cbox .bl{font-size:20px}.cbox .bv{font-size:40px;line-height:1.2}
"""


def cp_cell(p, cls, tag=""):
    img = ('<img src="%s">' % E(p["img"])) if p.get("img") else ""
    was = ('<span class="was">%s</span><span class="off" dir="ltr">-%s%%</span>' % (E(p.get("was")), E(p.get("pct")))) if p.get("was") not in (None, "") else ""
    return ('<div class="card %s"><div class="pic">%s</div><div class="info">%s<div class="nm">%s</div>'
            '<div class="pr"><span class="now">%s</span><span class="cur">ريال</span>%s</div></div></div>'
            % (cls, img, ('<div class="tag">%s</div>' % E(tag)) if tag else "", E(p.get("name")), E(p.get("price")), was))


def comp_html(it, pg):
    items = pg.get("items") or []
    main = next((x for x in items if x.get("role") == "main"), items[0] if items else {})
    comp = next((x for x in items if x.get("role") == "comp"), items[1] if len(items) > 1 else {})
    box = "".join('<div><div class="bl">%s</div><div class="bv">%s</div></div>' % (E(a), E(b)) for a, b in (it.get("box") or []))
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body class="cp">'
            '<div class="top"><div class="logo"><b>✓</b>العروض أول بأول</div><div class="pill">%s · <span>%s</span></div></div>'
            '%s<div class="plus"><div class="c">+</div><div class="t">%s <span>%s</span></div><div class="ln"></div></div>%s'
            '%s<div class="foot"><div>الأسعار %s · تتغير بأي لحظة</div><div dir="ltr">@awalbawal_sa</div></div>'
            '</body></html>') % (CSS_CP, E(it.get("pill") or "صيدة اليوم"), E(it.get("store") or "أمازون"),
                                 cp_cell(main, "cp-main", "🔥 الصيدة"), E(it.get("lead")), E(it.get("why") or ""), cp_cell(comp, "cp-comp"),
                                 ('<div class="cbox">%s</div>' % box) if box else "", E(it.get("date")))

# 🖼️ ═══ WP-1005 (D-295) — بطاقةُ التجميعة المخلوطة (قالب mx1 · نوفمبر الفاتح) ═══
#   قوله 9/11 «الوضع المهم ليس ما فيهم صور» ثمّ «طيب طبق الشعار وعطني تصور» ثمّ «ابني» على التصوّر:
#   لكلِّ متجرٍ خانة — شعارُه (أوّلُ مصدرٍ يتحمّل بحجمٍ يُقرأ) وإلّا الحرفُ بلونه · الاسم · الوصف · الكودُ بشريطٍ أسود
#   أو «بدون كود — ادخل من رابطه في التغريدة». كلُّ نصٍّ هنا من الخادم (lib/mixcard.js · mxCardItem).
CSS_MX = """
@font-face{font-family:Plex;src:url('%s');font-weight:400}
@font-face{font-family:Plex;src:url('%s');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%dpx;height:%dpx;overflow:hidden}
body{background:#f3f2ef;font-family:Plex,sans-serif;direction:rtl;color:#141414;padding:36px 40px 0;position:relative}
.top{display:flex;justify-content:space-between;align-items:center;height:62px}
.brand{font-size:30px;font-weight:700} .brand b{color:#e3a521;margin-left:10px}
.pill{background:#151515;color:#fff;border-radius:40px;padding:12px 28px;font-size:23px;font-weight:700} .pill span{color:#e3a521}
h1{font-size:60px;font-weight:700;line-height:1.15;margin-top:22px;white-space:nowrap} h1 .g{color:#e3a521} h1 .pg{color:#9a948a;font-size:.5em;margin-right:12px}
.subt{font-size:23px;color:#6d6b66;margin-top:10px;display:flex;gap:18px;align-items:center;white-space:nowrap}
.subt i{width:12px;height:12px;border-radius:50%%;display:inline-block;margin-left:8px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:28px}
.card{background:#fff;border-radius:28px;height:318px;padding:26px 26px 22px;display:flex;flex-direction:column;position:relative;overflow:hidden}
.n4 .card{height:480px} .n4 .lg{height:150px} .n4 .lg img{max-height:130px} .n4 .lg img.wide{max-height:80px;max-width:330px}
.tag{position:absolute;top:22px;left:22px;font-size:18px;font-weight:700;border-radius:30px;padding:5px 16px}
.tag.c{background:#fdecc4;color:#9a6a00} .tag.l{background:#e4f2e7;color:#1f6b3c}
.lg{height:96px;display:flex;align-items:center;justify-content:flex-start;padding-left:120px}
.lg img{max-height:84px;max-width:220px;object-fit:contain;display:block}
.lg img.wide{max-height:52px;max-width:250px} .lg img.sq{border-radius:20px}
.mono{width:84px;height:84px;border-radius:22px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:44px;font-weight:700;padding-bottom:6px}
.nm{font-size:30px;font-weight:700;line-height:1.6;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ds{font-size:21px;color:#6d6b66;line-height:1.45;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar{margin-top:auto;border-radius:20px;height:84px;display:flex;align-items:center;justify-content:space-between;padding:0 18px 0 14px;flex:none}
.bar.c{background:#151515} .bar.c .lb{color:#cfcac0;font-size:20px;line-height:1.3;min-width:0;overflow:hidden}
.bar.c .lb b{color:#fff;font-size:22px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.code{background:#e3a521;color:#151515;font-weight:700;font-size:38px;border-radius:14px;padding:4px 22px;letter-spacing:2px;direction:ltr;white-space:nowrap;flex:none;margin-right:12px}
.bar.l{background:#f1f0ec;justify-content:flex-start;padding:0 22px}
.bar.l .lb{font-size:22px;color:#1f6b3c;font-weight:700;display:flex;align-items:center;gap:10px;line-height:1.35}
.bar.l .lb small{display:block;font-size:18px;color:#6d6b66;font-weight:400}
.foot{position:absolute;bottom:26px;right:40px;left:40px;display:flex;justify-content:space-between;font-size:19px;color:#8a877f}
""" % (F400, F700, W, H)
MX_LINK = '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1" stroke="#1f6b3c" stroke-width="2.4" fill="none" stroke-linecap="round"/></svg>'


def mx_tile(t):
    import json as _j
    c = t.get("k") == "c"
    mono = '<div class="mono" style="background:%s">%s</div>' % (E(t.get("col") or "#1d1d1f"), E(t.get("ini") or "؟"))
    lg = '<div class="lg" data-logos="%s">%s</div>' % (E(_j.dumps(t.get("logos") or [])), mono)
    ds = ('<div class="ds">%s</div>' % E(t.get("desc"))) if t.get("desc") else ""
    if c:
        import re as _re
        off = _re.sub(r"(\d+(?:[.,]\d+)?\s*%)", r'<bdi dir="ltr">\1</bdi>', E(t.get("off") or "كود خصم"))   # «خصم 10%» لا «%10 خصم»
        bar = '<div class="bar c"><div class="lb"><b><bdi>%s</bdi></b>انسخه عند الدفع</div><div class="code">%s</div></div>' % (off, E(t.get("code")))
    else:
        bar = '<div class="bar l"><div class="lb">%s<span>بدون كود<small>ادخل من رابطه في التغريدة</small></span></div></div>' % MX_LINK
    return '<div class="card"><span class="tag %s">%s</span>%s<div class="nm">%s</div>%s%s</div>' % (
        "c" if c else "l", "كود" if c else "رابط مباشر", lg, E(t.get("name")), ds, bar)


def mix_html(it, pg):
    items = pg.get("items") or []
    sub = []
    if it.get("n_code"): sub.append('<span><i style="background:#e3a521"></i>%s أكواد متحقَّقة اليوم</span>' % E(it.get("n_code")))
    if it.get("n_link"): sub.append('<span><i style="background:#1f6b3c"></i>%s متاجر برابط مباشر</span>' % E(it.get("n_link")))
    pgn = ('<span class="pg">(%d/%d)</span>' % (pg["page"], pg["of"])) if pg.get("of", 1) > 1 else ""
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body class="%s">'
            '<div class="top"><div class="brand"><b>✓</b>العروض أول بأول</div><div class="pill">%s · <span>%s</span></div></div>'
            '<h1>%s <span class="g">%s</span>%s</h1><div class="subt">%s</div><div class="grid">%s</div>'
            '<div class="foot"><span>%s</span><span dir="ltr">@awalbawal_sa</span></div></body></html>') % (
        CSS_MX, "n4" if len(items) <= 4 else "", E(it.get("pill")), E(it.get("theme")), E(it.get("hl")), E(it.get("gold")), pgn,
        "".join(sub), "".join(mx_tile(t) for t in items), E(it.get("foot")))


def mx_trim(im, pad=0.03):
    """يقصّ الحوافَّ الفاضية (شفّافة أو بيضاء) حول الشعار — أيقونةُ ليفل شوز 225×225 شعارُها في وسطها الصغير. نقيّة."""
    from PIL import Image, ImageChops
    im = im.convert("RGBA")
    flat = Image.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, 255)), im).convert("RGB")
    diff = ImageChops.difference(flat, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda x: 255 if x > 18 else 0)
    box = diff.getbbox()
    if not box: return im
    w, h = im.size; px, py = int(w * pad), int(h * pad)
    return im.crop((max(0, box[0] - px), max(0, box[1] - py), min(w, box[2] + px), min(h, box[3] + py)))


def prep_mx_logos(it, get=_img_get, say=print):
    """🏷️ WP-1005: لكلِّ خانة أوّلُ شعارٍ يتحمّل هنا ⇒ مقصوصُ الحواف (PNG مضمَّن) · و«favicon» يُتخطّى (أيقونةُ متصفّح لا شعار —
    أوناس دائرةٌ بلا اسم) · وsvg يمرّ لكروم كما هو. ما تحمّل منها شيء ⇒ قائمةٌ فاضية ⇒ الحرفُ بلونه."""
    import base64, re
    from PIL import Image
    for pg in it.get("pages") or []:
        for t in pg.get("items") or []:
            out = []
            for u in t.get("logos") or []:
                if re.search(r"favicon", u, re.I): say("   ↷", t.get("name"), "أيقونة متصفّح لا شعار"); continue
                if re.search(r"\.svg(\?|$)", u, re.I): out.append(u); continue
                try:
                    im = Image.open(io.BytesIO(get(u))); im.load()
                except Exception as e:
                    say("   ↷", t.get("name"), "ما تحمّل الشعار:", str(e)[:60]); continue
                if max(im.size) < MX_LOGO_MIN: say("   ↷", t.get("name"), "شعارٌ صغير", im.size); continue
                im = mx_trim(im); im.thumbnail((640, 640))
                buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
                out.append("data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()); break
            t["logos"] = out


# الشعار: أوّلُ مصدرٍ يتحمّل بعرضٍ يُقرأ (≥ 96 — أيقونةُ 32 تتغبّش) يُرسم مكان الحرف · مستطيلٌ عريض ⇒ wide · مربّعٌ ⇒ حوافّ مدوّرة.
# ما تحمّل منها شيء (موقعٌ يحجب · رابطٌ مات) ⇒ يبقى الحرفُ بلونه. يعيد عددَ الشعارات المرسومة من الكلّ.
MX_LOGO_MIN = 96
MX_LOGO_JS = """async (minw) => {
  const load = (u) => new Promise((res) => { const im = new Image(); const t = setTimeout(() => res(null), 9000);
    im.onload = () => { clearTimeout(t); res(im); }; im.onerror = () => { clearTimeout(t); res(null); }; im.src = u; });
  let drawn = 0, all = 0;
  for (const box of document.querySelectorAll('.lg')) {
    all++;
    let list = []; try { list = JSON.parse(box.dataset.logos || '[]'); } catch (e) {}
    for (const u of list) {
      const im = await load(u);
      if (!im) continue;
      const svg = /\\.svg(\\?|$)/i.test(u);
      if (!svg && im.naturalWidth < minw && im.naturalHeight < minw) continue;
      const r = (im.naturalWidth || 3) / (im.naturalHeight || 1);
      im.className = r >= 2.2 ? 'wide' : (r > 0.8 && r < 1.25 ? 'sq' : '');
      box.innerHTML = ''; box.appendChild(im); drawn++; break;
    }
  }
  return {drawn, all};
}"""


# 🖼️ ═══ WP-973 — العنوانُ يدخل في الصفحة دائمًا، والحارسُ يرى ما يراه القارئ ═══
#   قوله 2026-11-06 «١ بشكل جذري» بعد تجميعة 18:41: «ماركات الإلكترونيات بخصم يوصل 66%» عرضُه 1199 على 996 ⇒ انقصّ الرقم،
#   والحارسُ القديم كان يقيس الطولَ وحده فمرّت. ٩ من ١٠ مجالات كانت تطلع برّا بخطّ 76.
#   ① FIT_JS: يصغّر العنوانَ خطوةً خطوة حتى يدخل (حتى 72% من حجمه) · وإن ما كفى ينزل سطرين متوازنين («يوصل X%» لا تنفصل)
#   ①ب CARDS_FIT_JS: بطاقةٌ محتواها أطولُ منها (اسمٌ بسطرين + مقاسات) أو سطرُ السعر أعرضُ من مكانه (583.94 بدل 2910 -80% — دخل على الصورة) ⇒ الصفحةُ كلُّها تضيق درجةً (t1) ثمّ درجتين (t2) بدل ما تنقصّ
#   ② INSPECT_JS: كلُّ عنصرٍ داخل الصفحة وداخل بطاقته · لا بطاقةَ أطولَ من مكانها · لا حرفَ مقصوصٌ من تحت (نقاط الياء)
#   ③ أيُّ عيبٍ ⇒ azrun.py لا يرفع الصفحة ⇒ التجميعةُ تنزل بصور المنتجات (احتياطُ WP-962) بدل صورةٍ مقصوصة
FIT_MIN = 0.72      # أصغرُ حجمٍ للعنوان نسبةً لحجمه في القالب (76 ⇐ 54 · 70 ⇐ 50)
FIT_JS = """(minr) => {
  const h = document.querySelector('h1'); if (!h) return null;
  const base = parseFloat(getComputedStyle(h).fontSize), min = Math.round(base * minr);
  const fits = () => h.scrollWidth <= h.clientWidth + 1;
  const set = (s) => { h.style.fontSize = s + 'px'; return s; };
  let s = base;
  while (!fits() && s > min) s = set(Math.max(min, s - 2));
  if (fits()) return {size: s, lines: 1, base};
  h.style.whiteSpace = 'normal'; h.style.textWrap = 'balance';
  const lines = () => { const l = parseFloat(getComputedStyle(h).lineHeight) || s * 1.12; return Math.round(h.getBoundingClientRect().height / l); };
  s = set(Math.round(base * 0.86));
  while ((lines() > 2 || !fits()) && s > min) s = set(Math.max(min, s - 2));
  return {size: s, lines: lines(), base};
}"""
CARDS_FIT_JS = """() => {
  const tall = () => [...document.querySelectorAll('.card')].some(c => c.scrollHeight > c.clientHeight + 2)
    || [...document.querySelectorAll('.pr')].some(e => e.scrollWidth > e.clientWidth + 1)
    || [...document.querySelectorAll('.nm,.sz')].some(e => { const l = parseFloat(getComputedStyle(e).lineHeight); return Math.round(e.scrollHeight / l) <= 2 && e.scrollHeight > e.clientHeight + 0.5; });
  let lv = 0;
  for (const c of ['t1', 't2']) { if (!tall()) break; document.body.classList.remove('t1'); document.body.classList.add(c); lv++; }
  return lv;
}"""
# 🖼️ WP-1004: الصورةُ فوق أو جنب؟ — تُقاس مساحةُ المنتج المرسومة فعلًا (بنسبة صورته بعد القصّ) في الوضعين، ويُختار الأكبرُ للصفحة كلّها
#   (الجزمةُ والشنطة عريضة ⇒ فوق · العطرُ والجوال طويل ⇒ جنب). بطاقاتُ الصفّ العريض (rows · span2) جنبٌ دائمًا.
PIC_MIN = 0.10      # أصغرُ نسبةٍ لمساحة المنتج من بطاقته
PIC_AREA_JS = """() => [...document.querySelectorAll('.card')].map(c => {
  const im = c.querySelector('.pic img'), b = c.querySelector('.pic');
  if (!im || !b || !im.naturalWidth) return null;
  const r = b.getBoundingClientRect(), k = Math.min(r.width / im.naturalWidth, r.height / im.naturalHeight);
  return (im.naturalWidth * k) * (im.naturalHeight * k) / (c.clientWidth * c.clientHeight);
})"""
LAYOUT_PICK_JS = """() => {
  const f = """ + PIC_AREA_JS + """;
  const area = () => f().reduce((s, x) => s + (x || 0), 0);
  const bad = () => [...document.querySelectorAll('.card')].some(c => c.scrollHeight > c.clientHeight + 2)
    || [...document.querySelectorAll('.pr')].some(e => e.scrollWidth > e.clientWidth + 1)
    || [...document.querySelectorAll('.info')].some(i => { const ir = i.getBoundingClientRect();
         return [...i.querySelectorAll('*')].some(e => { const r = e.getBoundingClientRect(); return r.width && (r.left < ir.left - 1 || r.right > ir.right + 1); }); })
    || [...document.querySelectorAll('.nm,.sz')].some(e => { const l = parseFloat(getComputedStyle(e).lineHeight); return Math.round(e.scrollHeight / l) <= 2 && e.scrollHeight > e.clientHeight + 0.5; });
  const B = document.body.classList, set = (m, t) => { B.remove('ph', 't1', 't2'); if (m === 'ph') B.add('ph'); if (t) B.add(t); };
  const tries = [];
  // كلُّ تضييقٍ للنصّ له ثمن (الخطُّ يصغر) ⇒ لا يُختار إلّا إذا كبّر المنتجَ فعلًا: ×0.9 لـt1 و×0.78 لـt2
  const W = {'': 1, t1: 0.9, t2: 0.78};
  for (const m of ['pv', 'ph']) for (const t of ['', 't1', 't2']) { set(m, t); const ok = !bad(); tries.push({m, t, ok, a: area(), s: area() * W[t]}); }
  const ok = tries.filter(x => x.ok);
  const best = ok.length ? ok.reduce((x, y) => (y.s > x.s * 1.05 ? y : x)) : tries.find(x => x.m === 'pv' && x.t === 't2');
  set(best.m, best.t);
  const g = (m) => { const o = tries.filter(x => x.m === m && x.ok); return o.length ? Math.max(...o.map(x => x.a)) : null; };
  const mins = f().filter(x => x != null);
  return {min: mins.length ? +Math.min(...mins).toFixed(3) : null, mode: best.m, t: best.t, pv: g('pv') == null ? null : +g('pv').toFixed(3), ph: g('ph') == null ? null : +g('ph').toFixed(3)};
}"""
INSPECT_JS = """(H) => {
  const W = document.documentElement.clientWidth, out = [];
  const nm = (e) => '«' + (e.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 34) + '»';
  if (document.body.scrollHeight > H + 1) out.push('الصفحة أطول من المقاس بـ' + (document.body.scrollHeight - H) + 'px');
  const h = document.querySelector('h1');
  if (h && h.scrollWidth > h.clientWidth + 1) out.push('العنوان أعرض من الصفحة بـ' + (h.scrollWidth - h.clientWidth) + 'px ' + nm(h));
  for (const e of document.querySelectorAll('body *')) {
    if (e.tagName === 'STYLE' || e.closest('h1')) continue;
    const r = e.getBoundingClientRect(); if (!r.width && !r.height) continue;
    if (r.left < -1 || r.right > W + 1) { out.push('عنصر طالع برا الصفحة ' + nm(e)); continue; }
    const c = e.closest('.card');
    if (c && c !== e) { const cr = c.getBoundingClientRect(); if (r.left < cr.left - 1 || r.right > cr.right + 1) out.push('عنصر طالع برا بطاقته ' + nm(e)); }
    const f = e.closest('.info');
    if (f && f !== e) { const fr = f.getBoundingClientRect(); if (r.left < fr.left - 1 || r.right > fr.right + 1) out.push('عنصر داخل على صورة المنتج ' + nm(e)); }
  }
  for (const c of document.querySelectorAll('.card')) if (c.scrollHeight > c.clientHeight + 2) out.push('بطاقة محتواها أطول منها ' + nm(c.querySelector('.nm') || c));
  for (const e of document.querySelectorAll('.nm,.sz')) {
    const l = parseFloat(getComputedStyle(e).lineHeight);
    if (Math.round(e.scrollHeight / l) <= 2 && e.scrollHeight > e.clientHeight + 0.5) out.push('حروف مقصوصة من تحت (نقاط الياء) ' + nm(e));
  }
  for (const e of document.querySelectorAll('.sub,.subt')) if (getComputedStyle(e).overflow !== 'visible' && e.scrollHeight > e.clientHeight + 0.5) out.push('حروف مقصوصة من تحت ' + nm(e));
  return [...new Set(out)];
}"""


def render_az(it, scale=2):
    """كلُّ صفحة ⇒ JPEG 2160×2700 بالضبط. يعيد [(page, jpg, broken_imgs, issues)] — issues قائمةُ عيوبٍ بالعربي (WP-973)، فاضيةٌ = سليمة."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pgw = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=scale)
        guide = it.get("layout") == "gd1"
        mx = it.get("layout") == "mx1"   # 🖼️ WP-1005: بطاقةُ المخلوطة — شعاراتٌ لا صورُ منتجات
        if guide: prep_guide_imgs(it)   # 🖼️ WP-991: أنظفُ صورةٍ من معرض كلِّ موديل
        elif mx: prep_mx_logos(it)      # 🏷️ WP-1005: الشعاراتُ مقصوصةُ الحواف · الأيقوناتُ الصغيرة تُتخطّى
        elif it.get("layout") not in ("cp1", "mx1"): prep_card_imgs(it)   # 🖼️ WP-1004: حوافُّ صور التجميعات مقصوصة
        for pg in it.get("pages") or []:
            path = os.path.join(HERE, "_azcard_%d.html" % pg["page"])
            # ➕ WP-995: بطاقةُ المرافق بقالبها (cp1)
            html_ = mix_html(it, pg) if mx else (comp_html(it, pg) if it.get("layout") == "cp1" else (guide_html(it, pg) if guide else page_html(it, pg)))
            open(path, "w", encoding="utf-8").write(html_)
            pgw.goto("file://" + path, wait_until="networkidle", timeout=60000)
            pgw.wait_for_timeout(700)
            if mx:
                lg = pgw.evaluate(MX_LOGO_JS, MX_LOGO_MIN)
                print("   🏷️ صفحة", pg["page"], "⇐ الشعارات", lg["drawn"], "من", lg["all"], "· الباقي بالحرف")
            broken = pgw.evaluate("[...document.images].filter(i=>!i.complete||!i.naturalWidth).length")
            pgw.evaluate(FIT_JS, FIT_MIN)
            lp = None
            if not guide and it.get("layout") not in ("cp1", "mx1"):
                lp = pgw.evaluate(LAYOUT_PICK_JS)
                print("   📐 صفحة", pg["page"], "⇐ الصورة", "جنب" if lp["mode"] == "ph" else "فوق", ("· تضييق " + lp["t"]) if lp["t"] else "", "· مساحة المنتج: فوق", lp["pv"], "· جنب", lp["ph"], "· أصغر بطاقة", lp["min"])
            pgw.evaluate(CARDS_FIT_JS)
            over = pgw.evaluate(INSPECT_JS, H)
            # 🖼️ WP-1004: حارسُ «صورة صغيرة» — منتجٌ يأخذ أقلَّ من عُشر بطاقته (القديم كان 0.09–0.12 · الجديد ≥0.13 مقيس 9/11) ⇒ عيبٌ يوقف الصفحة
            if lp and lp.get("min") is not None and lp["min"] < PIC_MIN:
                over = list(over) + ["صورة المنتج صغيرة في بطاقتها (%d%% من البطاقة — الحد %d%%)" % (round(lp["min"] * 100), round(PIC_MIN * 100))]
            png = pgw.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})
            im = Image.open(io.BytesIO(png)).convert("RGB")
            assert im.size == (W * scale, H * scale), im.size
            for q in (86, 80, 72, 64):
                buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
                if buf.tell() <= 1150000: break
            out.append((pg["page"], buf.getvalue(), broken, over))
        b.close()
    return out
