#!/usr/bin/env python3
# 🏭🏷️ ═══ WP-962 (D-259) — مصنعُ تصميم تجميعة ماركات أمازون (GitHub Actions · az-cards.yml) ═══
#   ① GET  /api/azbrands/card/todo   ⇐ القائمةُ المحسومة اليوم (قبل 18:30 بنصف ساعة) بصفحاتها + بصمتُها
#      🛒 WP-966: ثمّ /api/azgrocery/card/todo — تجميعةُ بقالة أمازون (قبل 15:00 بنصف ساعة) بقالب ag1
#      🏷️ WP-967: ثمّ /api/aebrands/card/todo — ماركاتُ علي إكسبريس (قبل 10:30 بنصف ساعة) بقالب ae1
#   ② ليست ببصمة اليوم ⇐ تُرسم كلُّ صفحة (azcard.py · كروم) ⇐ JPEG 2160×2700
#   ③ POST /api/azbrands/card/upload ⇐ صفحةً صفحة (تُقبل ببصمة القائمة وحدها)
# ⚖️ لا ينشر شيئًا. التجميعةُ تأخذ التصميمَ إن اكتمل، وإلّا صورَ المنتجات كما كانت. السرّ TT_BOT_KEY نفسُه.
import base64, os, sys, time
from run import api, api_post, say

DRY = "--dry" in sys.argv


# 🛒 WP-966: المصنعُ نفسُه يرسم تجميعتين — ماركات أمازون (18:00) وبقالة أمازون (14:30) — كلٌّ ببابها وقالبها
# (الأبوابُ مكتوبةً بحرفها — test_wp360 يقرأ كلَّ api(...) ويقارنه بأبواب المفتاح المسمّاة)
KINDS = [("azbrands", lambda: api("/api/azbrands/card/todo"), lambda b: api_post("/api/azbrands/card/upload", b), "🏷️", "az"),
         ("azgrocery", lambda: api("/api/azgrocery/card/todo"), lambda b: api_post("/api/azgrocery/card/upload", b), "🛒", "ag"),
         # 🏷️ WP-967: ماركاتُ علي إكسبريس (10:00 الحسم · 10:30 النشر) بقالب ae1
         ("aebrands", lambda: api("/api/aebrands/card/todo"), lambda b: api_post("/api/aebrands/card/upload", b), "🏷️", "ae")]


def one(route, todo, upload, icon, pre):
    st, t = todo()
    if st != 200 or not t.get("ok"):
        say(f"⛔ {route}/card/todo ردّ", st, t); return None
    items = t.get("items") or []
    if not items:
        say(f"{icon} لا تصميمَ مطلوب الآن:", t.get("why") or "—"); return (0, 0)
    it = items[0]
    if it.get("fresh"):
        say(f"{icon} تصميمُ اليوم مرسومٌ ببصمته", it.get("sig")); return (0, 0)
    from azcard import render_az
    say(f"{icon} {it.get('hl')} · {sum(len(p['items']) for p in it['pages'])} منتجات · {len(it['pages'])} صفحة · التصميم {t.get('layout')}")
    up = fail = 0
    for page, jpg, broken, over in render_az(it):
        tag = f"صفحة {page}/{len(it['pages'])} · {len(jpg)//1024}KB" + (f" · ⚠️ {broken} صورة ما نزلت" if broken else "") + (f" · ⚠️ فائض {over}" if over else "")
        if DRY:
            os.makedirs("out", exist_ok=True)
            open(os.path.join("out", f"{pre}_{page}.jpg"), "wb").write(jpg)
            say("   🖌️", tag, "(جافّ)"); continue
        st2, r = upload({"sig": it["sig"], "page": page, "jpg": base64.b64encode(jpg).decode()})
        if st2 == 200 and r.get("ok"): up += 1; say("   ✅", tag)
        else: fail += 1; say("   ❌", tag, st2, r.get("why") or r)
    say(f"🧾 {route}: رُفعت {up} · فشلت {fail}")
    return (up, fail)


def main():
    say(f"⏱️ {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())} · {os.environ.get('GITHUB_EVENT_NAME', 'local')}")
    res = [one(*k) for k in KINDS]
    if all(r is None for r in res): sys.exit(1)
    if any(r and r[1] and not r[0] for r in res): sys.exit(1)


if __name__ == "__main__":
    main()
