#!/usr/bin/env python3
# 🏭🖼️ ═══ WP-732(٨) — مصنعُ بطاقات حملات ترينديول «قبل وبعد» (GitHub Actions) ═══
#   ① GET  /api/tycamp/cards/todo   ⇐ حملاتُ اليوم بمنتجها (قرأه التابلت من بحث trendyol.sa) + بصمتُه
#   ② ما ليس ببصمة اليوم ⇐ ينزّل صورة المنتج (cdn.dsmcdn.com) ⇐ يرسم (render_ty) ⇐ JPEG
#   ③ POST /api/tycamp/cards/upload  ⇐ تُقبل ببصمة اليوم وحدها
# ⚖️ لا ينشر شيئًا. منشورُ العصر يأخذ البطاقات إن وُجدت، وإلّا نصًّا كما كان. السرّ TT_BOT_KEY نفسُه.
import base64, os, sys, time
from render import render_ty
from run import api, api_post, fetch_img, say

DRY = "--dry" in sys.argv

def main():
    # WP-732(٩): متى ولماذا شُغّل (والعنوانُ يصل مبسَّطًا: بلا حروفٍ تركيّة لا يرسمها الخطّ) — قِيس 2026-10-16 أنّ البطاقة رُسمت 18:33 رياضًا والمنشورُ 16:00 (جدولةُ GitHub تتأخّر)
    say(f"⏱️ {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())} · {os.environ.get('GITHUB_EVENT_NAME', 'local')} · {os.environ.get('GITHUB_EVENT_SCHEDULE', '')}")
    st, t = api("/api/tycamp/cards/todo")
    if st != 200 or not t.get("ok"):
        say("⛔ tycamp/cards/todo ردّ", st, t); sys.exit(1)
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
    if fail and not up: sys.exit(1)

if __name__ == "__main__":
    main()
