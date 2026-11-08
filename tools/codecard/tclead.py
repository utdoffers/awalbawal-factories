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
.cat .t{padding:8px 18px 0;font-size:28px;font-weight:700}
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
"""
CSS = _BASE + EXTRA
PCT = lambda s: re.sub(r"(\d+(?:\.\d+)?%)", r'<span class="n">\1</span>', s)
TOP = '<div class="top"><div class="logo"><b>✓</b>العروض أول بأول</div><div class="pill">ترينديول · <b>%s</b></div></div>'


def dm(d):
    try:
        y, m, dd = [int(v) for v in str(d).split("-")]
        return "%d/%d" % (dd, m)
    except Exception:
        return str(d)


def lead_html(it, pics):
    when = "اليوم بس" if it.get("today") else "لين " + dm(it.get("ends_on"))
    chips = []
    if it.get("upto"): chips.append('<div class="chip">%s</div>' % PCT("خصم يوصل %d%%" % int(it["upto"])))
    if it.get("code") and it.get("extra"): chips.append('<div class="chip o">%s</div>' % PCT("كود %s · %d%% زيادة" % (E(it["code"]), int(it["extra"]))))
    elif it.get("code"): chips.append('<div class="chip o">كود %s</div>' % E(it["code"]))
    cells = []
    for i, p in enumerate(it.get("items") or []):
        off = ('<div class="o">-%d%%</div>' % int(p["off"])) if p.get("off") else ""
        cells.append('<div class="cat">%s<div class="ph"><img src="%s"></div><div class="t">%s</div><div class="p">من<b>%s</b>ريال</div></div>'
                     % (off, pics[i] if i < len(pics) else "", E(p.get("type")), E(num(p.get("now")))))
    bar = ('<span>وبكود <b>%s</b> تنزل أكثر</span><span>الروابط في التغريدة</span>' % E(it["code"])) if it.get("code") else '<span>الروابط في التغريدة</span><span></span>'
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>' + TOP +
            '<h1>%s <em>من %s ريال</em></h1><div class="chips">%s</div><div class="g3">%s</div><div class="bar">%s</div>'
            '<div class="foot"><span>الأسعار من ترينديول %s قبل الكود · تتغير بأي لحظة</span><span dir="ltr">@awalbawal_sa</span></div>'
            '</body></html>') % (CSS, E(when), E(it.get("brand")), E(num(it.get("from"))),
                                 '<div class="plus">+</div>'.join(chips), "".join(cells), bar, E(day_ar(it.get("date"))))


def rest_html(it):
    rows = []
    for r in it.get("rows") or []:
        if r.get("upto") and r.get("extra"): b = "خصم يوصل <em>%d%%</em> + %d%% بالكود" % (int(r["upto"]), int(r["extra"]))
        elif r.get("extra"): b = "%d%% زيادة بالكود" % int(r["extra"])
        elif r.get("upto"): b = "خصم يوصل <em>%d%%</em>" % int(r["upto"])
        else: b = "عروض اليوم"
        if r.get("until"): b += " · لين " + dm(r["until"])
        cd = ('<div class="cd%s">%s</div>' % (" hot" if r.get("hot") else "", E(r["code"]))) if r.get("code") else '<div class="cd no">الخصم في السلة</div>'
        name = str(r.get("name") or "")
        first = (re.sub(r"[^\w؀-ۿ]", "", name)[:1] or "•").upper()
        rows.append('<div class="row"><div class="ic">%s</div><div class="nm"><div class="a">%s</div><div class="b">%s</div></div>%s</div>'
                    % (E(first), E(name), PCT(b), cd))
    more = int(it.get("more") or 0)
    sub = "كل ماركة بكودها · والروابط في نص الرد" + (" · و%d غيرها في النص" % more if more else "")
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>%s</style></head><body>' + TOP +
            '<h1>وعروض ثانية <em>اليوم بس</em></h1><div class="sub">%s</div><div class="list">%s</div>'
            '<div class="foot"><span>من ترينديول %s · العروض تتغير بأي لحظة</span><span dir="ltr">@awalbawal_sa</span></div>'
            '</body></html>') % (CSS, "اليوم بس", E(sub), "".join(rows), E(day_ar(it.get("date"))))


def _shoot(html_txt, name, scale=2):
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
          while (h.scrollWidth > h.clientWidth + 2 && f > 52) { f -= 2; h.style.fontSize = f + 'px'; } }""")
        chk = pg.evaluate("""() => ({
          foot: document.querySelector('.foot').getBoundingClientRect().bottom,
          wide: (() => { const h = document.querySelector('h1'); return h.scrollWidth > h.clientWidth + 2; })(),
          broken: [...document.images].filter(i => !i.complete || !i.naturalWidth).length })""")
        png = pg.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()
    why = None
    if chk["foot"] > H: why = "الصفحةُ أطول من 1350 (%d)" % chk["foot"]
    elif chk["wide"]: why = "العنوانُ أعرض من الصفحة"
    elif chk["broken"]: why = "%d صورة ما انرسمت" % chk["broken"]
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
    return _shoot(lead_html(it, pics), "_tclead.html", scale)


def render_rest(it, scale=2):
    return _shoot(rest_html(it), "_tcrest.html", scale)
