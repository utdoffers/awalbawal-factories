#!/usr/bin/env python3
# 🧵🖼️ ═══ WP-986 — صورتا ثريد حملات ترينديول 4:5 (قالبا tl1 · tr1) ═══
#   قوله 2026-11-08 «اعتمد» على النموذج المرسوم: ① «<الماركة> من X ريال» بأقسامها (صورةُ أرخص قطعة لكلّ قسم)
#   ② «وعروض ثانية اليوم بس» قائمةُ الباقي بأكوادها. المصنعُ نفسُه (ty-cards.yml): tyrun.py يأخذ `lead` و`rest`
#   من /api/tycamp/cards/todo ⇐ هنا HTML بكروم ⇐ JPEG 2160×2700 ⇐ /api/tycamp/cards/upload (cid=lead|rest).
#   كلُّ ما يُرسم من الخادم. أرقامٌ إنجليزيّة (قراره 16/10) و«55%» لا «%55» (عزلُ الاتجاه). بلا إيموجي (خطُّ المصنع لا يرسمها).
import io, os, re
from tcpack import CSS as _BASE, E, W, H, num, day_ar, img_uri

EXTRA = """
.chips{display:flex;gap:12px;margin-top:14px;align-items:center;flex-wrap:wrap}
.chip{background:#fff;border-radius:16px;padding:9px 18px;font-size:26px;font-weight:700}
.chip.o{background:#f27a1a;color:#fff}
.plus{font-size:28px;font-weight:700;color:#999}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:24px}
.cat{background:#fff;border-radius:26px;overflow:hidden;position:relative;height:410px;display:flex;flex-direction:column}
.cat .ph{height:292px;display:flex;align-items:center;justify-content:center;background:#fff}
.cat .ph img{max-height:292px;max-width:100%;object-fit:contain}
.cat .t{padding:8px 18px 0;font-size:28px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}   /* 🖼️ WP-1063: سطرٌ واحد — الاسمُ بسطرين كان يقصّ السعر (فحص كاراكا 12/11) */
.cat .p{padding:0 18px;font-size:22px;color:#666}
.cat .p b{font-size:40px;color:#1f9a3c;margin:0 4px}
.cat .o{position:absolute;top:14px;right:14px;background:#e0302e;color:#fff;font-weight:700;font-size:22px;border-radius:30px;padding:4px 14px;direction:ltr}
.list{margin-top:22px;display:flex;flex-direction:column;gap:14px}
.row{background:#fff;border-radius:24px;display:flex;align-items:center;padding:0 26px;height:118px;gap:22px}
.ic{width:72px;height:72px;border-radius:50%;background:#fde3cc;color:#c4560a;display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:700;flex:none}
.nm{flex:1;min-width:0}
.nm .a{font-size:33px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nm .b{font-size:24px;color:#555}
.nm .b em{font-style:normal;color:#e0302e;font-weight:700}
.cd{background:#1c1c1c;color:#fff;font-weight:700;font-size:28px;border-radius:14px;padding:6px 18px;letter-spacing:1px;direction:ltr;flex:none}
.cd.hot{background:#f27a1a}
.cd.no{background:#eaf6ed;color:#1f7a34;letter-spacing:0;direction:rtl;font-size:22px}
.n{direction:ltr;unicode-bidi:isolate;display:inline-block}
.cat .c{padding:0 18px 4px;font-size:21px;color:#8a8a8a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}   /* 🏷️ WP-1193: «في موقع أديداس 299 · في نمشي 249» — بس لما ترينديول أرخص */
"""
CSS = _BASE + EXTRA
PCT = lambda s: re.sub(r"(\d+(?:\.\d+)?%)", r'<span class="n">\1</span>', s)
TOP = '<div class="top"><div class="logo"><b>✓</b>العروض أول بأول</div><div class="pill">ترينديول · <b>%s</b></div></div>'
# ⏳ WP-1227: بلا نهايةٍ قالها الإيميل ⇒ الشارةُ «ترينديول» وحدها (الـ%s مكانُه مخفيّ فيبقى ترتيبُ المعاملات)
TOP_PLAIN = '<div class="top"><div class="logo"><b>✓</b>العروض أول بأول</div><div class="pill">ترينديول<b style="display:none">%s</b></div></div>'


# 🖼️ WP-1063: عنوانُ قائمة العروض — «عروض ترينديول <em>اليوم بس</em>» من الخادم (وسمُ <em> وحده مسموح) · وبلاه العنوانُ القديم لردّ الثريد
def HEAD(h):
    if not h: return "وعروض ثانية <em>اليوم بس</em>"
    # 🖼️ WP-1089: «70%» معزولة الاتجاه في العنوان أيضًا (العنوانُ صار فيه نسبة — كانت تنقلب «%70»)
    return PCT(E(str(h)).replace("&lt;em&gt;", "<em>").replace("&lt;/em&gt;", "</em>"))


# 🖼️ WP-1063: قائمةٌ قصيرة (≤٤) تملأ الصفحة بصفوفٍ أكبر بدل فراغ نصّ الصفحة (3 عروض 14/11 كانت تنتهي عند الثلث)
BIG = """
body{height:1350px;box-sizing:border-box;display:flex;flex-direction:column}
.list.big{flex:1;justify-content:center;gap:30px}
.list.big .row{height:210px;padding:0 36px;gap:30px}
.list.big .ic{width:104px;height:104px;font-size:48px}
.ic.pic{background:#fff;border-radius:20px;overflow:hidden;width:96px;height:96px}
.ic.pic img{width:100%;height:100%;object-fit:contain}
.list.big .ic.pic{width:170px;height:170px;border-radius:24px}
.list.big.haspic .ic{width:170px;height:170px;font-size:64px}   /* الحرفُ بمقاس الصورة ⇒ الأسماءُ على خطٍّ واحد */
.list.big .nm .a{font-size:48px}
.list.big .nm .b{font-size:32px;margin-top:6px}
.list.big .cd{font-size:36px;padding:10px 26px}
/* 🧩 WP-1080: الصفوفُ تملأ الصفحة بعددها (15/11: سطران بطول 210 وثلثا الصفحة فاضي) — كلُّ صفٍّ يكبر لين حدّه ولا يطلع برّا */
.list.big .row{height:auto;flex:1 1 0;min-height:150px;max-height:400px}
.list.big.n1 .row{max-height:640px}
.list.big.n1 .row,.list.big.n2 .row{display:grid;grid-template-columns:300px 1fr;grid-template-rows:auto auto;column-gap:40px;row-gap:18px;align-content:center}
.list.big.n1 .ic,.list.big.n2 .ic{grid-row:1 / span 2;width:300px;height:300px;font-size:110px}
.list.big.n1 .ic.pic,.list.big.n2 .ic.pic{width:300px;height:300px}
.list.big.n1 .nm,.list.big.n2 .nm{grid-column:2;align-self:end}
.list.big.n1 .cd,.list.big.n2 .cd{grid-column:2;justify-self:start;align-self:start}
.list.big.n1 .nm .a,.list.big.n2 .nm .a{font-size:56px}
.list.big.n1 .row{grid-template-columns:440px 1fr}
.list.big.n1 .ic,.list.big.n1 .ic.pic{width:440px;height:440px;font-size:150px}
.list.big.n1 .nm .a{font-size:64px}
.list.big.n1 .nm .b{font-size:38px}
/* 🧾 WP-1230 (قوله 2026-11-23 «١»): ٥–٧ صفوف تملأ الصفحة بعد (5:11 23/11: خمسةُ صفوفٍ بطول 118 وثلثُ الصفحة تحت فاضي) */
.list.fill{flex:1;gap:18px}
.list.fill .row{height:auto;flex:1 1 0;min-height:118px;max-height:240px}
.list.fill .ic{width:96px;height:96px;font-size:44px}
.list.fill .ic.pic{width:150px;height:150px}
.list.fill .nm .a{font-size:40px}
.list.fill .nm .b{font-size:29px;margin-top:4px}
.list.fill .cd{font-size:32px;padding:8px 22px}
.list.fill.n6 .ic.pic{width:124px;height:124px}
.list.fill.n7 .ic.pic{width:108px;height:108px}   /* ستّة وسبعة: الصورة بحجم الصفّ (≈131) ما تطلع برّاه */
.list .ic.pic{margin-top:0}   /* 🧾 WP-1230: ‎.pic‎ في القالب الأساسيّ (صورةُ البطاقة) يعطيها 34px من فوق ⇒ كانت تنزل تحت حافّة الصفّ */
"""


# 🖼️ WP-1071: «ماركة اليوم» تملأ الصفحة — الشبكةُ تاخذ كلَّ المساحة بين العنوان والشريط
#   (واحدة بعرض الصفحة · ثنتان صفّ · ثلاث: الأولى عريضة وثنتان تحتها · أربع 2×2 · خمس وست 3×2)
#   قِيس 14/11: ثلاثُ بطاقات بطول 410 ⇒ المحتوى ينتهي عند 60% ونصُّ الصفحة تحت فاضي. والبطاقةُ بطولها: الصورةُ تكبر، والاسمُ والسعرُ ثابتان.
FILL = """
body{height:1350px;display:flex;flex-direction:column}
.g3.fill{flex:1;min-height:0;grid-auto-rows:1fr}
.g3.fill .cat{height:auto;min-height:0}
.g3.fill .ph{flex:1;height:auto;min-height:0}
.g3.fill .ph img{max-height:100%;max-width:100%}
.g3.fill .t,.g3.fill .p,.g3.fill .c{flex:none}
.g3.fill .p{padding-bottom:16px}
.g3.fill.n1{grid-template-columns:1fr}
.g3.fill.n2,.g3.fill.n3,.g3.fill.n4{grid-template-columns:1fr 1fr}
.g3.fill.n3 .cat:first-child{grid-column:1 / span 2}
"""


def dm(d):
    try:
        y, m, dd = [int(v) for v in str(d).split("-")]
        return "%d/%d" % (dd, m)
    except Exception:
        return str(d)


def lead_html(it, pics):
    # ⏳ WP-1227: «اليوم بس» و«لين» بس لو الإيميل كتب نهايته (said) — وإلّا الشارةُ «ترينديول» وحدها
    when = "اليوم بس" if it.get("today") else ("لين " + dm(it.get("ends_on")) if it.get("said", True) and it.get("ends_on") else "")
    chips = []
    # 🎁 WP-1227: عرضُ العميل («3 بسعر 2») أوّلُ شريحة وحسبتُه في العنوان
    if it.get("upto"): chips.append('<div class="chip">%s</div>' % PCT("خصم يوصل %d%%" % int(it["upto"])))
    # 🔗 WP-1235: «20% زيادة» تنقرأ إنّ السعر يزيد ⇒ «خصم إضافي 20%»
    if it.get("code") and it.get("extra"): chips.append('<div class="chip o">%s</div>' % PCT("كود %s · خصم إضافي %d%%" % (E(it["code"]), int(it["extra"]))))
    elif it.get("code"): chips.append('<div class="chip o">كود %s</div>' % E(it["code"]))
    cells = []
    for i, p in enumerate(it.get("items") or []):
        off = ('<div class="o">-%d%%</div>' % int(p["off"])) if p.get("off") else ""
        cmp = ('<div class="c">%s</div>' % E(p["cmp"])) if p.get("cmp") else ""   # 🏷️ WP-1193 (D-446)
        cells.append('<div class="cat">%s<div class="ph"><img src="%s"></div><div class="t">%s</div><div class="p">من<b>%s</b>ريال</div>%s</div>'
                     % (off, pics[i] if i < len(pics) else "", E(p.get("type")), E(num(p.get("now"))), cmp))
    lk = "الرابط في التغريدة" if int(it.get("links") or 0) == 1 else "الروابط في التغريدة"   # 🔗 WP-1235: رابطٌ واحد ⇒ «الرابط»
    bar = ('<span>وبكود <b>%s</b> تنزل أكثر</span><span>%s</span>' % (E(it["code"]), lk)) if it.get("code") else '<span>%s</span><span></span>' % lk
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>' + (TOP if when else TOP_PLAIN) +
            '<h1>%s <em>%s</em></h1>%s<div class="chips">%s</div><div class="g3 fill n%d">%s</div><div class="bar">%s</div>'
            '<div class="foot"><span>الأسعار من ترينديول %s قبل الكود · تتغير بأي لحظة</span><span dir="ltr">@awalbawal_sa</span></div>'
            '</body></html>') % (CSS + FILL, E(when), E(it.get("brand")), (E(it["offer"]) if it.get("offer") else "من %s ريال" % E(num(it.get("from")))),
                                 # 🎁 WP-1227: حسبةُ العرض سطرٌ تحت العنوان («3 قطع بـ130 ريال بدل 300») — في العنوان نفسه كانت تطلع برّا الصورة
                                 ('<div style="font-size:46px;font-weight:700;color:#1f1f1f;margin:-4px 0 16px">%s</div>' % E(it["math"])) if it.get("offer") and it.get("math") else "",
                                 '<div class="plus">+</div>'.join(chips), min(len(cells), 6), "".join(cells), bar, E(day_ar(it.get("date"))))


def rest_html(it, pics=None):
    # 🖼️ WP-1089: الشارةُ فوق من الخادم (it["when"]: «اليوم بس» أو تاريخُ اليوم) — كانت «اليوم بس» ثابتة على كلِّ قائمة
    rows = []
    for i, r in enumerate(it.get("rows") or []):
        if r.get("upto") and r.get("extra"): b = "خصم يوصل <em>%d%%</em> + %d%% بالكود" % (int(r["upto"]), int(r["extra"]))
        elif r.get("extra"): b = "خصم إضافي %d%% بالكود" % int(r["extra"])   # 🔗 WP-1235: كان «20% زيادة بالكود»
        elif r.get("upto"): b = "خصم يوصل <em>%d%%</em>" % int(r["upto"])
        else: b = "عروض اليوم"
        if r.get("until"): b += " · لين " + dm(r["until"])
        cd = ('<div class="cd%s">%s</div>' % (" hot" if r.get("hot") else "", E(r["code"]))) if r.get("code") else '<div class="cd no">الخصم في السلة</div>'
        name = str(r.get("name") or "")
        first = (re.sub(r"[^\w؀-ۿ]", "", name)[:1] or "•").upper()
        pic = (pics or {}).get(i) if pics else None   # 🖼️ WP-1064: صورةُ أقوى منتجٍ في الحملة بدل الحرف (بلاها الحرف)
        ic = ('<div class="ic pic"><img src="%s"></div>' % pic) if pic else ('<div class="ic">%s</div>' % E(first))
        rows.append('<div class="row">%s<div class="nm"><div class="a">%s</div><div class="b">%s</div></div>%s</div>'
                    % (ic, E(name), PCT(b), cd))
    more = int(it.get("more") or 0)
    sub = (it.get("sub") or "كل ماركة بكودها · والروابط في نص الرد") + (" · و%d غيرها في النص" % more if more else "")   # 🖼️ WP-1063: منشورٌ لحاله ⇒ «الروابط في التغريدة»
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>' + TOP +
            '<h1>%s</h1><div class="sub">%s</div><div class="list%s">%s</div>'
            '<div class="foot"><span>من ترينديول %s · العروض تتغير بأي لحظة</span><span dir="ltr">@awalbawal_sa</span></div>'
            '</body></html>') % (CSS + BIG, E(it.get("when") or "اليوم بس"), HEAD(it.get("head")), E(sub), (" big n%d" % len(rows) if len(rows) <= 4 else " fill n%d" % len(rows)) + (" haspic" if pics else ""), "".join(rows), E(day_ar(it.get("date"))))


def _shoot(html_txt, name, scale=2, fill=False):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    open(path, "w", encoding="utf-8").write(html_txt)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=scale)
        pg.goto("file://" + path, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(800)
        pg.evaluate("""() => { const h = document.querySelector('h1'); let f = 76;
          while (h.scrollWidth > h.clientWidth + 2 && f > 52) { f -= 2; h.style.fontSize = f + 'px'; }
          /* 🧩 WP-1080: اسمُ السطر يصغر لين يدخل كاملًا (15/11: «s Perfumes» و«trongville» — القصُّ بنقاطٍ في سطرٍ عربيٍّ فيه لاتيني يقصّ من أوّل الكلمة) */
          for (const a of document.querySelectorAll('.nm .a')) { let g = parseFloat(getComputedStyle(a).fontSize);
            while (a.scrollWidth > a.clientWidth + 2 && g > 26) { g -= 2; a.style.fontSize = g + 'px'; } }
          /* 🧱 WP-1087: واسمُ المنتج في «ماركة اليوم» كذلك — كان يُقصّ بنقاطٍ من أوّل الكلمة اللاتينيّة («...den Rose»)
             يصغر لين 22 ثمّ ينزل سطرين (الصورةُ تصغر لا السعر) */
          for (const t of document.querySelectorAll('.cat .t')) { let g = parseFloat(getComputedStyle(t).fontSize);
            while (t.scrollWidth > t.clientWidth + 2 && g > 22) { g -= 1; t.style.fontSize = g + 'px'; }
            if (t.scrollWidth > t.clientWidth + 2) { t.style.whiteSpace = 'normal'; t.style.lineHeight = '1.25'; } } }""")
        chk = pg.evaluate("""() => ({
          foot: document.querySelector('.foot').getBoundingClientRect().bottom,
          wide: (() => { const h = document.querySelector('h1'); return h.scrollWidth > h.clientWidth + 2; })(),
          broken: [...document.images].filter(i => !i.complete || !i.naturalWidth).length,
          name: [...document.querySelectorAll('.nm .a'), ...document.querySelectorAll('.cat .t')].filter(a => a.scrollWidth > a.clientWidth + 2 || a.scrollHeight > a.clientHeight + 4).length,   // 🧱 WP-1087: وأسماءُ «ماركة اليوم»
          cut: [...document.querySelectorAll('.cat')].filter(c => { const p = c.querySelector('.p'); return p && p.getBoundingClientRect().bottom > c.getBoundingClientRect().bottom + 1; }).length,
          gap: (() => { const els = [...document.body.children].filter(e => e.getBoundingClientRect().height > 0);
                        return Math.max(0, ...els.map((e, i) => (i + 1 < els.length ? els[i + 1].getBoundingClientRect().top : document.body.getBoundingClientRect().bottom) - e.getBoundingClientRect().bottom)); })() })""")
        png = pg.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()
    why = None
    if chk["foot"] > H: why = "الصفحةُ أطول من 1350 (%d)" % chk["foot"]
    elif chk["wide"]: why = "العنوانُ أعرض من الصفحة"
    elif chk["broken"]: why = "%d صورة ما انرسمت" % chk["broken"]
    elif chk.get("name"): why = "%d اسم مقصوص في سطره" % chk["name"]   # 🧩 WP-1080: لا رفع لاسمٍ مقصوص (الخادمُ يرسل ≤ 22 حرفًا والخطُّ يصغر قبلها)
    elif chk.get("cut"): why = "%d سعر مقصوص في خانته" % chk["cut"]   # 🖼️ WP-1063: لا رفع لصورةٍ سعرُها مقصوص
    elif fill and chk.get("gap", 0) > H * 0.25: why = "فراغٌ %d بكسل في الصفحة (أكثر من ربعها)" % chk["gap"]   # 🖼️ WP-1071: لا رفع لصورةٍ نصُّها فاضي
    im = Image.open(io.BytesIO(png)).convert("RGB")
    if im.size != (W * scale, H * scale): why = why or "المقاس %dx%d لا %dx%d" % (im.size[0], im.size[1], W * scale, H * scale)
    for q in (86, 80, 72, 64):
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
        if buf.tell() <= 1000000: break
    return buf.getvalue(), why


def render_lead(it, fetch, scale=2):
    """⇒ (jpg, مشكلة أو None) — صورةُ قسمٍ ما نزلت ⇒ مشكلة (لا رفع)."""
    items = it.get("items") or []
    pics = [img_uri(fetch(p.get("img"))) for p in items]
    if any(not u for u in pics):
        return None, "صورةُ قسمٍ ما نزلت (%d من %d)" % (sum(1 for u in pics if not u), len(pics))
    return _shoot(lead_html(it, pics), "_tclead.html", scale, fill=True)


def render_rest(it, scale=2, fetch=None):
    """🖼️ WP-1064: `fetch` ⇒ صورةُ كلِّ سطرٍ (img) — ما نزلت ⇒ حرفُه كما كان (لا تمنع الرفع)."""
    pics = {}
    if fetch:
        for i, r in enumerate(it.get("rows") or []):
            if r.get("img"):
                try:
                    u = img_uri(fetch(r["img"]))
                    if u: pics[i] = u
                except Exception:
                    pass
    return _shoot(rest_html(it, pics), "_tcrest.html", scale)
