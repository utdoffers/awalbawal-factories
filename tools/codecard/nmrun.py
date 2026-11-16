#!/usr/bin/env python3
# 🏭🏷️ ═══ WP-1110 — مصنعُ صور نمشي بشريط الكود (خطوةٌ في code-cards.yml) ═══
#   ① GET  /api/nmstamp/todo    ⇐ صورُ صيد نمشي آخر ٤٨ ساعة بلا طابعٍ ببصمتها (المفتاح · البصمة · الكود · رابطُ الصورة)
#   ② يُنزّل الصورة ⇐ يرسم (nmstamp.py) ⇐ JPEG 2160×2700
#   ③ POST /api/nmstamp/upload  ⇐ تُقبل ببصمة الدفتر والكود الآن وحدها
# ⚖️ لا ينشر شيئًا: النشرُ يأخذ الطابعَ إن وُجد، وإلّا صورةَ المنتج كما كانت. صورةٌ ما نزلت ⇐ لا طابع (لا شريطَ على فراغ).
import base64, os, sys, time
from run import api, api_post, say, fetch_img
from nmstamp import render_nm, W, H

DRY = "--dry" in sys.argv

def main():
    st, t = api("/api/nmstamp/todo")
    if st != 200 or not t.get("ok"):
        say("⛔ nmstamp/todo ردّ", st, t); sys.exit(1)
    items = t.get("items") or []
    say(f"🏷️ صور نمشي تنتظر شريطَ الكود: {len(items)}" + (f" — {t.get('why')}" if not items and t.get("why") else ""))
    up = fail = skip = 0
    for it in items:
        p = fetch_img(it.get("src"))
        if p is None:
            skip += 1; say("   ⏭️", it["okey"], "صورتُه ما نزلت — تبقى الأصليّة"); continue
        jpg = render_nm(it, product=p)
        if DRY:
            os.makedirs("out", exist_ok=True)
            open(os.path.join("out", it["okey"] + ".jpg"), "wb").write(jpg)
            say("   🖌️", it["okey"], f"{len(jpg)//1024}KB {W}×{H} (جافّ)"); continue
        st2, r = api_post("/api/nmstamp/upload", {"okey": it["okey"], "sig": it["sig"], "jpg": base64.b64encode(jpg).decode()})
        if st2 == 200 and r.get("ok"): up += 1; say("   ✅", it["okey"], f"{len(jpg)//1024}KB")
        else: fail += 1; say("   ❌", it["okey"], st2, r.get("why") or r)
        time.sleep(0.3)
    say(f"🧾 نمشي: رُفعت {up} · تُخطّيت {skip} · فشلت {fail}")
    if fail and not up: sys.exit(1)

if __name__ == "__main__":
    main()
