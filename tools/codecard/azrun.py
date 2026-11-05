#!/usr/bin/env python3
# 🏭🏷️ ═══ WP-962 (D-259) — مصنعُ تصميم تجميعة ماركات أمازون (GitHub Actions · az-cards.yml) ═══
#   ① GET  /api/azbrands/card/todo   ⇐ القائمةُ المحسومة اليوم (قبل 18:30 بنصف ساعة) بصفحاتها + بصمتُها
#   ② ليست ببصمة اليوم ⇐ تُرسم كلُّ صفحة (azcard.py · كروم) ⇐ JPEG 2160×2700
#   ③ POST /api/azbrands/card/upload ⇐ صفحةً صفحة (تُقبل ببصمة القائمة وحدها)
# ⚖️ لا ينشر شيئًا. التجميعةُ تأخذ التصميمَ إن اكتمل، وإلّا صورَ المنتجات كما كانت. السرّ TT_BOT_KEY نفسُه.
import base64, os, sys, time
from run import api, api_post, say

DRY = "--dry" in sys.argv


def main():
    say(f"⏱️ {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())} · {os.environ.get('GITHUB_EVENT_NAME', 'local')}")
    st, t = api("/api/azbrands/card/todo")
    if st != 200 or not t.get("ok"):
        say("⛔ azbrands/card/todo ردّ", st, t); sys.exit(1)
    items = t.get("items") or []
    if not items:
        say("🏷️ لا تصميمَ مطلوب الآن:", t.get("why") or "—"); return
    it = items[0]
    if it.get("fresh"):
        say("🏷️ تصميمُ اليوم مرسومٌ ببصمته", it.get("sig")); return
    from azcard import render_az
    say(f"🏷️ {it.get('hl')} · {sum(len(p['items']) for p in it['pages'])} منتجات · {len(it['pages'])} صفحة · التصميم {t.get('layout')}")
    up = fail = 0
    for page, jpg, broken, over in render_az(it):
        tag = f"صفحة {page}/{len(it['pages'])} · {len(jpg)//1024}KB" + (f" · ⚠️ {broken} صورة ما نزلت" if broken else "") + (f" · ⚠️ فائض {over}" if over else "")
        if DRY:
            os.makedirs("out", exist_ok=True)
            open(os.path.join("out", f"az_{page}.jpg"), "wb").write(jpg)
            say("   🖌️", tag, "(جافّ)"); continue
        st2, r = api_post("/api/azbrands/card/upload", {"sig": it["sig"], "page": page, "jpg": base64.b64encode(jpg).decode()})
        if st2 == 200 and r.get("ok"): up += 1; say("   ✅", tag)
        else: fail += 1; say("   ❌", tag, st2, r.get("why") or r)
    say(f"🧾 رُفعت {up} · فشلت {fail}")
    if fail and not up: sys.exit(1)


if __name__ == "__main__":
    main()
