#!/usr/bin/env python3
# 👻🏭 ═══ WP-814 — مصنعُ ستوري سناب (GitHub Actions) ═══
#   ① GET  /api/snap/cards/todo   ⇐ صفوفُ سناب القادمة: القالبُ والحقولُ والبصمة (الخادمُ يقرّر ماذا يُرسم)
#   ② ما بطاقتُه ليست ببصمة اليوم ⇐ يُنزّل شعارَ المتجر/صورتَه ⇐ يرسم (snap.py) ⇐ JPEG 1080×1920
#   ③ POST /api/snap/cards/upload ⇐ تُقبل ببصمة اليوم وحدها
# ⚖️ لا ينشر شيئًا: النحلةُ تأخذ البطاقةَ وقتَ الخانة. وكلُّ تخطٍّ يقول سببَه.
import base64, os, sys, time
from run import api, api_post, fetch_img, say
from snap import render_snap

DRY = "--dry" in sys.argv

def main():
    st, t = api("/api/snap/cards/todo")
    if st != 200 or not t.get("ok"):
        say("⛔ snap/cards/todo ردّ", st, t); sys.exit(1)
    items = t.get("items") or []
    need = [i for i in items if not i.get("fresh")]
    say(f"👻 بطاقاتُ سناب المطلوبة: {len(items)} · تحتاج رسمًا: {len(need)} · التصميم {t.get('layout')}")
    for s in (t.get("skipped") or [])[:10]: say("   ⏭️", s.get("at"), s.get("why"))
    up = fail = 0
    for it in need:
        f = it.get("fields") or {}
        logo = fetch_img(f.get("logo")) if f.get("logo") else None
        poster = fetch_img(f.get("poster")) if f.get("poster") else None
        try:
            jpg = render_snap(f, logo=logo, poster=poster)
        except Exception as e:
            fail += 1; say("   ❌ رسم", it["ckey"], repr(e)[:120]); continue
        tag = f"{it['tpl']} · {it['ckey'][:60]}"
        if DRY:
            os.makedirs("out", exist_ok=True)
            open(os.path.join("out", it["ckey"].replace("|", "_").replace("/", "_")[:80] + ".jpg"), "wb").write(jpg)
            say("   🖌️", tag, f"{len(jpg)//1024}KB (جافّ)"); continue
        st2, r = api_post("/api/snap/cards/upload", {"ckey": it["ckey"], "sig": it["sig"], "jpg": base64.b64encode(jpg).decode()})
        if st2 == 200 and r.get("ok"): up += 1; say("   ✅", tag, f"{len(jpg)//1024}KB")
        else: fail += 1; say("   ❌", tag, st2, r.get("why") or r)
        time.sleep(0.3)
    say(f"🧾 رُفعت {up} · فشلت {fail}")
    if fail and not up: sys.exit(1)

if __name__ == "__main__":
    main()
