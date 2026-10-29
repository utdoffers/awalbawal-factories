#!/usr/bin/env python3
# 🏭🎟️ ═══ WP-699 — مصنعُ بطاقات الأكواد (GitHub Actions) ═══
#   ① GET  /api/cc/todo    ⇐ كلُّ كودٍ منشور + صورُ متجره (جلبها التابلت من صفحة المتجر) + بصمتُه
#   ② ما بطاقتُه ليست ببصمة اليوم ⇐ يُنزّل صورَ متجره ⇐ يرسم (render.py) ⇐ JPEG
#   ③ POST /api/cc/upload  ⇐ تُقبل ببصمة اليوم وحدها
# ⚖️ لا ينشر شيئًا: النشرُ في النظام يأخذ البطاقةَ إن وُجدت، وإلّا نصًّا كما كان.
#    كلُّ تخطٍّ يقول سببَه في التقرير. السرّ TT_BOT_KEY نفسُه (يرى أبوابَه المسمّاة فقط).
import base64, json, os, sys, time, urllib.request, urllib.error
from render import render, load_image

BASE = os.environ.get("OS_BASE", "https://os.awalbawal.com").rstrip("/")
KEY = os.environ.get("TT_BOT_KEY", "")
DRY = "--dry" in sys.argv
UA_SELF = "Mozilla/5.0 AwalbawalCodeCards/1.0"
UA_WEB = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
MAX_PER_RUN = int(os.environ.get("CC_MAX", "120"))

def say(*a): print(" ".join(str(x) for x in a), flush=True)

def _req(path, body=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method="POST" if data is not None else "GET")
    req.add_header("User-Agent", UA_SELF); req.add_header("Accept", "application/json")
    if data is not None: req.add_header("Content-Type", "application/json")
    if KEY: req.add_header("x-tt-key", KEY)
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode("utf-8", "replace"))
        except Exception: return e.code, {}

def api(path): return _req(path)
def api_post(path, body): return _req(path, body)

_cache = {}
def fetch_img(url):
    if not url: return None
    if url in _cache: return _cache[url]
    im = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA_WEB, "Accept": "image/*,*/*"})
        with urllib.request.urlopen(req, timeout=40) as r: im = load_image(r.read(6_000_000), url)
    except Exception as e:
        say("   ⚠️ تعذّر تنزيل الصورة:", url[:90], repr(e)[:60])
    _cache[url] = im
    return im

def pick(it):
    """poster عريضٌ بما يكفي ⇐ إعلان · وإلّا أكبرُ شعارٍ صالح (ومنه og الصغير) · وإلّا الاسم."""
    p = fetch_img(it.get("poster")) if it.get("poster") else None
    if p is not None and p.width >= 400: return p, None, "poster"
    cands = [x for x in (fetch_img(it.get("logo")) if it.get("logo") else None, p) if x is not None and x.width >= 64]
    if cands: return None, max(cands, key=lambda x: x.width), "logo"
    return None, None, "name"

def main():
    st, t = api("/api/cc/todo")
    if st != 200 or not t.get("ok"):
        say("⛔ cc/todo ردّ", st, t); sys.exit(1)
    items = t.get("items") or []
    need = [i for i in items if not i.get("fresh")]
    say(f"🎟️ أكواد منشورة: {len(items)} · تحتاج رسمًا: {len(need)} · التصميم {t.get('layout')}")
    done = {"poster": 0, "logo": 0, "name": 0}; up = fail = 0
    for it in need[:MAX_PER_RUN]:
        p, l, kind = pick(it)
        jpg = render(it, poster=p, logo=l)
        done[kind] += 1
        tag = f"{it['store']} · {it['code']} · {kind}" + (" · (صورتُه محجوبة بقراره)" if it.get("poster_blocked") else "")
        if DRY:
            os.makedirs("out", exist_ok=True)
            open(os.path.join("out", it["ckey"].replace("|", "_").replace("/", "_") + ".jpg"), "wb").write(jpg)
            say("   🖌️", tag, f"{len(jpg)//1024}KB (جافّ)"); continue
        st2, r = api_post("/api/cc/upload", {"ckey": it["ckey"], "sig": it["sig"], "jpg": base64.b64encode(jpg).decode()})
        if st2 == 200 and r.get("ok"): up += 1; say("   ✅", tag, f"{len(jpg)//1024}KB")
        else: fail += 1; say("   ❌", tag, st2, r.get("why") or r)
        time.sleep(0.3)
    say(f"🧾 رُسمت: إعلان {done['poster']} · شعار {done['logo']} · اسم {done['name']} · رُفعت {up} · فشلت {fail}")
    if fail and not up: sys.exit(1)

if __name__ == "__main__":
    main()
