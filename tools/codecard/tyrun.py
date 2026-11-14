#!/usr/bin/env python3
# 🏭🖼️ ═══ WP-732(٨) — مصنعُ بطاقات حملات ترينديول «قبل وبعد» (GitHub Actions) ═══
#   ① GET  /api/tycamp/cards/todo   ⇐ حملاتُ اليوم بمنتجها (قرأه التابلت من بحث trendyol.sa) + بصمتُه
#   ② ما ليس ببصمة اليوم ⇐ ينزّل صورة المنتج (cdn.dsmcdn.com) ⇐ يرسم (render_ty) ⇐ JPEG
#   ③ POST /api/tycamp/cards/upload  ⇐ تُقبل ببصمة اليوم وحدها
# ⚖️ لا ينشر شيئًا. منشورُ العصر يأخذ البطاقات إن وُجدت، وإلّا نصًّا كما كان. السرّ TT_BOT_KEY نفسُه.
# 🧡 WP-980: وصورةُ التجميعة الواحدة (أقوى ٤ منتجات) — `pack` في ردّ todo ⇐ tcpack.py ⇐ upload cid=pack
# 🏷️ WP-960: ومعها تصميمُ تجميعة ماركات ترينديول — /api/tybrands/card/todo ⇐ tbcard.py (كروم) ⇐ /api/tybrands/card/upload
import base64, os, sys, time
from render import render_ty
from run import api, api_post, fetch_img, say

DRY = "--dry" in sys.argv

def main():
    # WP-732(٩): متى ولماذا شُغّل (والعنوانُ يصل مبسَّطًا: بلا حروفٍ تركيّة لا يرسمها الخطّ) — قِيس 2026-10-16 أنّ البطاقة رُسمت 18:33 رياضًا والمنشورُ 16:00 (جدولةُ GitHub تتأخّر)
    say(f"⏱️ {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())} · {os.environ.get('GITHUB_EVENT_NAME', 'local')} · {os.environ.get('GITHUB_EVENT_SCHEDULE', '')}")
    tb_ok = brands()
    st, t = api("/api/tycamp/cards/todo")
    if st != 200 or not t.get("ok"):
        say("⛔ tycamp/cards/todo ردّ", st, t); sys.exit(0 if tb_ok else 1)
    th_ok = thread_cards(t.get("lead"), t.get("rest"))   # 🧵 WP-986: صورتا الثريد أوّلًا — هما اللي تنزلان يوم فيه ماركةُ اليوم
    td_ok = td_cards(t.get("td") or [])   # 🖼️ WP-1063: خاناتُ يوم ترينديول (7:30 · 8:30 · 1:30 · 5:00)
    pk_ok = pack(t.get("pack"))   # 🧡 WP-980: صورةُ التجميعة — تنزل يوم بلا ماركة اليوم
    items = t.get("items") or []
    need = [i for i in items if not i.get("fresh")]
    say(f"🟠 حملات اليوم بمنتج: {len(items)} · تحتاج رسمًا: {len(need)} · التصميم {t.get('layout')}")
    up = fail = 0
    for it in need:
        p = fetch_img(it.get("img"))
        if p is None:
            fail += 1; say("   ❌", it.get("store"), "صورةُ المنتج لم تُنزَّل — لا بطاقة"); continue
        jpg = render_ty(it, product=p)
        tag = f"{it.get('store')} · {it.get('now')}/{it.get('was')}"
        if DRY:
            os.makedirs("out", exist_ok=True)
            open(os.path.join("out", "ty_" + str(abs(hash(it["cid"]))) + ".jpg"), "wb").write(jpg)
            say("   🖌️", tag, f"{len(jpg)//1024}KB (جافّ)"); continue
        st2, r = api_post("/api/tycamp/cards/upload", {"cid": it["cid"], "sig": it["sig"], "jpg": base64.b64encode(jpg).decode()})
        if st2 == 200 and r.get("ok"): up += 1; say("   ✅", tag, f"{len(jpg)//1024}KB")
        else: fail += 1; say("   ❌", tag, st2, r.get("why") or r)
        time.sleep(0.3)
    say(f"🧾 رُسمت ورُفعت {up} · فشلت {fail}")
    if (fail and not up) or not pk_ok or not th_ok or not td_ok: sys.exit(1)

def td_cards(items):
    """🖼️ WP-1063 — تصاميمُ خانات يوم ترينديول ببصمة نصّها (cid=td_am1 · td_am2 · td_rest · td_gen):
    «lead» ⇒ قالبُ ماركة اليوم · «rest» ⇒ قائمةُ العروض. أيُّ عيبٍ مقيس ⇒ لا رفع (تنزل بصور منتجاتها لا بصورةٍ غلط)."""
    if not items: return True
    try:
        from tclead import render_lead, render_rest
    except Exception as e:
        say("   ❌ 🖼️ tclead تعذّر:", repr(e)[:200]); return False
    ok = True
    for it in items:
        cid = it.get("cid")
        if it.get("fresh"): say(f"🖼️ {cid}: مرسومةٌ ببصمة نصّها"); continue
        try:
            jpg, why = render_lead(it, fetch_img) if it.get("kind") == "lead" else render_rest(it, fetch=fetch_img)   # 🖼️ WP-1064: صورُ القائمة
        except Exception as e:
            say(f"   ❌ 🖼️ {cid}:", repr(e)[:200]); ok = False; continue
        tag = (it.get("brand") or "") + f" · {len(it.get('items') or it.get('rows') or [])}"
        if why: say(f"   🚫 🖼️ {cid}", tag, "·", why); ok = False; continue
        if DRY:
            os.makedirs("out", exist_ok=True); open(os.path.join("out", f"{cid}.jpg"), "wb").write(jpg)
            say(f"   🖌️ 🖼️ {cid}", tag, f"{len(jpg)//1024}KB (جافّ)"); continue
        st2, r = api_post("/api/tycamp/cards/upload", {"cid": cid, "sig": it["sig"], "jpg": base64.b64encode(jpg).decode()})
        if st2 == 200 and r.get("ok"): say(f"   ✅ 🖼️ {cid}", tag, f"{len(jpg)//1024}KB")
        else: say(f"   ❌ 🖼️ {cid}", tag, st2, r.get("why") or r); ok = False
    return ok

def thread_cards(lead, rest):
    """🧵 WP-986 — صورتا ثريد حملات ترينديول ببصمة اليوم (cid=lead · rest). أيُّ عيبٍ مقيس ⇒ لا رفع (التغريدةُ بلا صورة لا بصورةٍ غلط)."""
    if not lead: say("🧵 ماركةُ اليوم: ما فيه ماركة معروفة بثلاثة أقسام مقروءة — تنزل التجميعة"); return True
    ok = True
    try:
        from tclead import render_lead, render_rest
    except Exception as e:
        say("   ❌ 🧵 tclead تعذّر:", repr(e)[:200]); return False
    for cid, it, fn in (("lead", lead, lambda x: render_lead(x, fetch_img)), ("rest", rest, render_rest)):
        if not it: continue
        if it.get("fresh"): say(f"🧵 {cid}: مرسومةٌ ببصمة اليوم"); continue
        try:
            jpg, why = fn(it)
        except Exception as e:
            say(f"   ❌ 🧵 {cid}:", repr(e)[:200]); ok = False; continue
        tag = (it.get("brand") or "") + f" · {len(it.get('items') or it.get('rows') or [])}"
        if why: say(f"   🚫 🧵 {cid}", tag, "·", why); ok = False; continue
        if DRY:
            os.makedirs("out", exist_ok=True); open(os.path.join("out", f"tc{cid}.jpg"), "wb").write(jpg)
            say(f"   🖌️ 🧵 {cid}", tag, f"{len(jpg)//1024}KB (جافّ)"); continue
        st2, r = api_post("/api/tycamp/cards/upload", {"cid": cid, "sig": it["sig"], "jpg": base64.b64encode(jpg).decode()})
        if st2 == 200 and r.get("ok"): say(f"   ✅ 🧵 {cid}", tag, f"{len(jpg)//1024}KB")
        else: say(f"   ❌ 🧵 {cid}", tag, st2, r.get("why") or r); ok = False
    return ok

def pack(it):
    """🧡 WP-980 — صورةُ تجميعة الحملات (أقوى ٤) ببصمة اليوم. أيُّ عيبٍ مقيس ⇒ لا رفع والمنشورُ بالبطاقات كما كان. True إن لم يفشل شيء."""
    if not it: say("🧡 التجميعة: ما فيه منتجين من ماركتين مقروءين بعد"); return True
    if it.get("fresh"): say("🧡 التجميعة: مرسومةٌ ببصمة اليوم"); return True
    try:
        from tcpack import render_pack
        jpg, why = render_pack(it, fetch_img)
    except Exception as e:
        say("   ❌ 🧡 رسمُ التجميعة تعذّر:", repr(e)[:200]); return False
    tag = " · ".join(f"{p.get('brand')} {p.get('now')}/{p.get('was')}" for p in (it.get("items") or []))
    if why:
        say("   🚫 🧡", tag, "·", why); return False
    if DRY:
        os.makedirs("out", exist_ok=True); open(os.path.join("out", "tcpack.jpg"), "wb").write(jpg)
        say("   🖌️ 🧡", tag, f"{len(jpg)//1024}KB (جافّ)"); return True
    st2, r = api_post("/api/tycamp/cards/upload", {"cid": "pack", "sig": it["sig"], "jpg": base64.b64encode(jpg).decode()})
    if st2 == 200 and r.get("ok"): say("   ✅ 🧡", tag, f"{len(jpg)//1024}KB"); return True
    say("   ❌ 🧡", tag, st2, r.get("why") or r); return False

def brands():
    """🏷️ تصميمُ تجميعة ماركات ترينديول — مرّةً لليوم ببصمته. يعيد True إن لم يكن فيه فشل."""
    st, t = api("/api/tybrands/card/todo")
    if st != 200 or not t.get("ok"):
        say("⛔ tybrands/card/todo ردّ", st, t); return False
    it = t.get("item")
    if not it: say("🏷️ تجميعة الماركات:", t.get("why") or "لا شيء اليوم"); return True
    if t.get("fresh"): say("🏷️ تجميعة الماركات: مرسومةٌ ببصمة اليوم"); return True
    try:
        from tbcard import render_tb
        jpg, broken = render_tb(it)
    except Exception as e:
        say("   ❌ رسمُ تصميم الماركات تعذّر:", repr(e)[:200]); return False
    tag = f"{it.get('hl')} · {len(it.get('items') or [])} منتجات · صورٌ ما حمّلت {broken}"
    if DRY:
        os.makedirs("out", exist_ok=True); open(os.path.join("out", "tybrands.jpg"), "wb").write(jpg)
        say("   🖌️", tag, f"{len(jpg)//1024}KB (جافّ)"); return True
    st2, r = api_post("/api/tybrands/card/upload", {"sig": it["sig"], "jpg": base64.b64encode(jpg).decode()})
    if st2 == 200 and r.get("ok"): say("   ✅ 🏷️", tag, f"{len(jpg)//1024}KB"); return True
    say("   ❌ 🏷️", tag, st2, r.get("why") or r); return False

if __name__ == "__main__":
    main()
