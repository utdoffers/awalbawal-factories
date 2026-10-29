# -*- coding: utf-8 -*-
"""🎬 مصنعُ مقاطع المنتجات — WP-684 (2026-10-12)

قراره: «لازم كل شي يصير بدون تدخل مني» — بعد فحص الحسابات الناجحة: المنتجُ لا الخصم،
مقطعٌ حقيقيٌّ ٧–١٠ ثوانٍ، جملةٌ تقول وش يسوي، والكودُ آخرًا.

  ① GET  /api/tt/product/state   ← الخاناتُ الفاضية + ما نزل + كودُه (من سجلّه لا من هنا)
  ② يختار نوعًا من kinds.json لم ينزل خلال «أيام الراحة»
  ③ يصطاد من علي إكسبريس منتجًا من النوع **له فيديو** وينزّله
  ④ يرسم: الفيديو + جملةُ الافتتاح فوق + شريطُ نون (اكتب في البحث · الكود) + موسيقى مولَّدة
  ⑤ POST /api/tt/vid/upload  ثمّ  POST /api/tt/product/add   ← ونحلةُ تيك توك تنشره في موعده

قواعدُه: لا يخترع سعرًا ولا خصمًا · كلُّ تخطٍّ يقول سببَه · ما لم يُفهم لا يُرسم · لا يكتب كودًا بيده.
"""
import os, re, sys, json, base64, random, argparse, subprocess, datetime, urllib.request, urllib.error, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("OS_BASE", "https://os.awalbawal.com").rstrip("/")
TT_KEY = os.environ.get("TT_BOT_KEY", "")
UA_SELF = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/127.0 Safari/537.36 AwalbawalTTProduct/1.0")
UA_WEB = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
W, H = 720, 1280
MAX_B64 = 1_350_000          # سقفُ الخادم 1.4 مليون حرف (lib/ttvideo.js) — وهامشٌ صغير
REPORT = []

def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); REPORT.append(s)

def _req(path, body=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method="POST" if data is not None else "GET")
    req.add_header("User-Agent", UA_SELF); req.add_header("Accept", "application/json")
    if data is not None: req.add_header("Content-Type", "application/json")
    if TT_KEY: req.add_header("x-tt-key", TT_KEY)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        b = ""
        try: b = e.read().decode("utf-8", "replace")[:300]
        except Exception: pass
        raise RuntimeError(f"HTTP {e.code} على {path} — {b}") from None

def api(path): return _req(path)
def api_post(path, body): return _req(path, body)

# ═══ 🛒 علي إكسبريس: بحثٌ ⇐ صفحةُ منتج ⇐ رابطُ الفيديو ⇐ تنزيل ═══
def search_ids(q):
    """قِيس 2026-10-12: صفحةُ البحث تُقرأ من GitHub بـcurl (٧٢ منتجًا) — وصفحةُ المنتج لا."""
    # WP-693 (قراره 2026-10-13 «نفذ»): «الأكثر طلبًا» — منتجاتٌ مجرّبة لها فيديو (قِيس ٥ من ٦ مقابل ٠ من ٣)
    url = "https://www.aliexpress.com/w/wholesale-" + re.sub(r"\s+", "-", q.strip()) + ".html?SortType=total_tranpro_desc"
    try:
        r = subprocess.run(["curl", "-sSL", "-m", "40", "-A", UA_WEB, "-H", "Accept-Language: en-US,en;q=0.9", url], capture_output=True, timeout=60)
        h = r.stdout.decode("utf-8", "ignore")
    except Exception: h = ""
    ids = list(dict.fromkeys(re.findall(r"item/(\d{13,})\.html", h)))
    say(f"   🔎 «{q}»: {len(ids)} منتجًا ({len(h)//1000}k)")
    return ids

def tab_search(k):
    """📱 WP-691 (قراره 2026-10-13 «نفذ»): علي إكسبريس حجب بحثَ GitHub (صفحةٌ فاضية) ⇐ كرومُ التابلت يبحث
    ويصفّ المنتجاتِ بنفسه، ونحن ننتظره من ميزانية الدورة كما ننتظر الفيديو."""
    try:
        r = api_post("/api/tt/product/aeq", {"kind": k["kind"], "q": k["q"]})
        say(f"   📱 «{k['kind']}»: البحثُ انحجب هنا ⇐ طُلب من التابلت ({r.get('search') or r.get('why')})")
    except Exception as e:
        say("   ⚠️ ما وصل طلبُ البحث للتابلت:", e)
WAIT_BUDGET = [900]   # ⏱️ ١٥ دقيقةً انتظارٌ للتابلت في الدورة كلِّها — لا لكلِّ نوع (قِيس: ٣٠ دقيقة انقضت في نوعين)

def prequeue(kinds):
    """📱 نصفّ أرقامَ عدّة أنواعٍ دفعةً واحدة — فيقرأها التابلتُ معًا بينما ننتظر."""
    for k in kinds:
        have = api("/api/tt/product/ae?kind=" + k["kind"])
        if (have.get("videos") and len(have["videos"]) >= 2) or have.get("waiting"): continue
        ids = search_ids(k["q"])
        if ids:
            r = api_post("/api/tt/product/aeq", {"kind": k["kind"], "ids": ids[:10]})
            say(f"   📱 «{k['kind']}»: صُفّ للتابلت {r.get('queued')} من {r.get('of')}")
        else:
            tab_search(k)

def find_videos(kind, q, want=3):
    """روابطُ الفيديو يقرؤها كرومُ التابلت (tyapp/ae). ما قرأه سابقًا يُستعمل فورًا؛ وإلّا ننتظر من ميزانية الدورة."""
    import time
    got = api("/api/tt/product/ae?kind=" + kind)
    if not got.get("videos") and not got.get("waiting"):
        ids = search_ids(q)
        if ids: api_post("/api/tt/product/aeq", {"kind": kind, "ids": ids[:10]})
        else: tab_search({"kind": kind, "q": q})
        got = api("/api/tt/product/ae?kind=" + kind)
    while got.get("waiting") and len(got.get("videos") or []) < want and WAIT_BUDGET[0] > 0:
        if (got.get("block") or {}).get("paused"):   # 🧩 WP-697: التابلتُ واقفٌ عند صفحة التحقق ⇒ لا ننتظر عبثًا
            say(f"   🧩 التابلتُ محجوبٌ في علي إكسبريس لين {got['block'].get('until')} — ما بقي ينتظر للدورة القادمة")
            WAIT_BUDGET[0] = 0; break
        time.sleep(30); WAIT_BUDGET[0] -= 30
        got = api("/api/tt/product/ae?kind=" + kind)
    v = got.get("videos") or []
    say(f"   🎞️ «{kind}» له فيديو: {len(v)} · ينتظر التابلت: {got.get('waiting')} · بلا فيديو: {got.get('none')} · بقي للانتظار {WAIT_BUDGET[0]}ث")
    return v

def download(url, dst):
    r = subprocess.run(["curl", "-sSL", "-m", "120", "-o", dst, "-w", "%{http_code}", url], capture_output=True, timeout=150)
    code = r.stdout.decode().strip()
    return code == "200" and os.path.exists(dst) and os.path.getsize(dst) > 200_000

def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", path], capture_output=True)
    try:
        j = json.loads(r.stdout); s = j["streams"][0]
        return int(s["width"]), int(s["height"]), float(j["format"]["duration"])
    except Exception: return None

# ═══ 🖼️ الطبقةُ فوق الفيديو ═══
def overlay(png, l1, l2, search, code, y0=1440):
    from PIL import Image, ImageDraw, ImageFont
    # نرسم على 1080×1920 ثمّ نصغّر إلى مقاس المقطع — حروفٌ أنعم
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); Y = (254, 238, 0); INK = (16, 16, 16)
    f = ImageFont.truetype(os.path.join(HERE, "fonts", "plexfull-700.ttf"), 66)
    w = max(d.textlength(l1, font=f), d.textlength(l2, font=f)) + 90
    d.rounded_rectangle((540 - w / 2, 150, 540 + w / 2, 365), 36, fill=(255, 255, 255, 245))
    d.text((540, 205), l1, font=f, fill=INK, anchor="mm"); d.text((540, 305), l2, font=f, fill=INK, anchor="mm")
    d.rounded_rectangle((60, y0, 1020, y0 + 330), 40, fill=Y + (250,))
    d.text((540, y0 + 62), "في نون اكتب", font=ImageFont.truetype(os.path.join(HERE, "fonts", "plexfull-400.ttf"), 44), fill=INK, anchor="mm")
    fs = 64
    while fs > 40 and d.textlength(search, font=ImageFont.truetype(os.path.join(HERE, "fonts", "plexfull-700.ttf"), fs)) > 900: fs -= 4
    d.text((540, y0 + 135), search, font=ImageFont.truetype(os.path.join(HERE, "fonts", "plexfull-700.ttf"), fs), fill=INK, anchor="mm")
    d.rounded_rectangle((290, y0 + 200, 790, y0 + 300), 28, fill=INK)
    d.text((540, y0 + 250), "كود " + code, font=ImageFont.truetype(os.path.join(HERE, "fonts", "plexfull-700.ttf"), 60), fill=Y, anchor="mm")
    im.resize((W, H), Image.LANCZOS).save(png)

def render(src, png, wav, out, wid, hei, dur):
    """٨٫٧٥ ثانية: نتخطّى بداية الفيديو (غالبًا كرتون التغليف) ونسرّع ×٢٫٤ إن اتّسع."""
    span = 21.0
    start = max(0.0, min(dur * 0.2, dur - span))
    speed = max(1.0, min(2.4, (dur - start) / 8.75))
    vert = hei >= wid
    if vert:
        vf = f"setpts=PTS/{speed},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=contrast=1.06:saturation=1.12"
        fc = f"[0:v]{vf}[v];[v][1:v]overlay=0:0,format=yuv420p[o]"
    else:
        ch = int(hei * 0.86)   # نقصّ أسفلَ الفيديو العرضيّ — هناك تسكن ترجماتُهم غالبًا
        fc = (f"[0:v]setpts=PTS/{speed},crop={wid}:{ch}:0:0,split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=20:2,eq=brightness=-0.15[bg];"
              f"[b]scale={int(W*1.28)}:-2,crop={W}:ih,eq=contrast=1.06:saturation=1.1[fg];[bg][fg]overlay=0:(H-h)/2-40[v];"
              f"[v][1:v]overlay=0:0,format=yuv420p[o]")
    for br in ("850k", "700k", "560k"):
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.2f}", "-i", src, "-i", png, "-i", wav,
               "-filter_complex", fc, "-map", "[o]", "-map", "2:a", "-t", "8.75", "-r", "30",
               "-c:v", "libx264", "-preset", "slow", "-b:v", br, "-maxrate", br, "-bufsize", "1200k",
               "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0: return None, r.stderr.decode()[-300:]
        b64 = base64.b64encode(open(out, "rb").read()).decode()
        if len(b64) <= MAX_B64: return b64, None
    return None, "المقطعُ أكبرُ من سقف الخادم حتى بأقلّ جودة"

# ═══ ▶️ يوتيوب شورتس — WP-878 (قوله «مقطعين - يوتيوب مباشر - ما نحط علامه») ═══
# المصنعُ نفسُه: الصيدُ والرسمُ كما هما · المقاسُ 1080×1920 بجودةٍ أعلى (لا يمرّ المقطعُ بالقاعدة فلا سقفَ ١ ميغا)
# · الشريطُ الأصفر أعلى (يوتيوب يغطّي أسفلَ الشاشة باسم القناة والعنوان) · النصُّ يُحجز من الخادم (`yt/claim`)
# بكوده وبوّابته · الرفعُ مباشرةً بـYouTube Data API بـ`publishAt` (يوتيوب ينشره في دقيقته — موعدُ GitHub يتأخّر ساعات).
YT_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
YT_BAND_Y = 1180

def yt_token():
    """🔑 مفتاحُ رفعٍ قصير (ساعة) من خادمنا — سرُّ القناة الطويل لا يغادر الخادم ولا يسكن GitHub."""
    try: t = api("/api/yt/token")
    except Exception as e: raise RuntimeError(f"ما وصل مفتاحُ يوتيوب من الخادم: {e}") from None
    if not t.get("ok") or not t.get("access_token"): raise RuntimeError(t.get("why") or "الخادم ما أعطى مفتاحَ يوتيوب")
    return t["access_token"]

def yt_upload(path, claim):
    """رفعٌ على دفعتين (resumable): الوصفُ أوّلًا ثمّ الملفّ. يُرجع رقمَ الفيديو."""
    tok = yt_token()
    status = {"selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}
    if claim.get("publish_at"): status.update(privacyStatus="private", publishAt=claim["publish_at"])
    else: status["privacyStatus"] = "public"
    meta = {"snippet": {"title": claim["title"], "description": claim["description"], "tags": claim.get("tags") or [],
                        "categoryId": claim.get("category") or "26", "defaultLanguage": "ar", "defaultAudioLanguage": "ar"},
            "status": status}
    size = os.path.getsize(path)
    req = urllib.request.Request(YT_UPLOAD_URL, data=json.dumps(meta, ensure_ascii=False).encode("utf-8"), method="POST")
    req.add_header("Authorization", "Bearer " + tok); req.add_header("Content-Type", "application/json; charset=UTF-8")
    req.add_header("X-Upload-Content-Type", "video/mp4"); req.add_header("X-Upload-Content-Length", str(size))
    try:
        with urllib.request.urlopen(req, timeout=60) as r: loc = r.headers.get("Location")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"يوتيوب رفض بدء الرفع ({e.code}): {e.read().decode('utf-8','replace')[:300]}") from None
    if not loc: raise RuntimeError("يوتيوب ما أعطى رابطَ الرفع")
    up = urllib.request.Request(loc, data=open(path, "rb").read(), method="PUT")
    up.add_header("Authorization", "Bearer " + tok); up.add_header("Content-Type", "video/mp4")
    try:
        with urllib.request.urlopen(up, timeout=600) as r: j = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"يوتيوب رفض الملف ({e.code}): {e.read().decode('utf-8','replace')[:300]}") from None
    if not j.get("id"): raise RuntimeError("يوتيوب ما أعطى رقمَ الفيديو")
    return j["id"], (j.get("status") or {}).get("uploadStatus")

def render_yt(src, png, wav, out, wid, hei, dur):
    """مثل render لكن 1080×1920 بمعدّلٍ أعلى ويُرجع الملفّ لا base64."""
    span = 21.0
    start = max(0.0, min(dur * 0.2, dur - span))
    speed = max(1.0, min(2.4, (dur - start) / 8.75))
    if hei >= wid:
        fc = f"[0:v]setpts=PTS/{speed},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=contrast=1.06:saturation=1.12[v];[v][1:v]overlay=0:0,format=yuv420p[o]"
    else:
        ch = int(hei * 0.86)
        fc = (f"[0:v]setpts=PTS/{speed},crop={wid}:{ch}:0:0,split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=20:2,eq=brightness=-0.15[bg];"
              f"[b]scale={int(W*1.28)}:-2,crop={W}:ih,eq=contrast=1.06:saturation=1.1[fg];[bg][fg]overlay=0:(H-h)/2-140[v];"
              f"[v][1:v]overlay=0:0,format=yuv420p[o]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.2f}", "-i", src, "-i", png, "-i", wav,
           "-filter_complex", fc, "-map", "[o]", "-map", "2:a", "-t", "8.75", "-r", "30",
           "-c:v", "libx264", "-preset", "slow", "-b:v", "3500k", "-maxrate", "4500k", "-bufsize", "7000k",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(out): return None, r.stderr.decode()[-300:]
    return out, None

def main_youtube(a):
    global W, H
    W, H = 1080, 1920
    if not a.dry:   # 🔑 لا نحجز خانةً بلا مفتاح رفع — نتأكّد قبل الصيد والرسم
        try: yt_token()
        except Exception as e: say("⛔", e, "— ما أحجز خانةً بلا رفع"); sys.exit(1)
    st = api("/api/yt/state")
    if not st.get("ok"): say("⛔ ما وصل حالُ الخادم:", st); sys.exit(1)
    if st.get("why"): say("⏸️", st["why"]); return
    free, code = st.get("free") or [], st.get("code") or ""
    if not free: say("✅ لا خانةَ فاضيةَ ليوتيوب في اليومين القادمين — ما في شغل"); return
    cfg = st.get("cfg") or {}; rest = int(cfg.get("rest_days") or 21)
    kinds = json.load(open(os.path.join(HERE, "kinds.json"), encoding="utf-8"))["kinds"]
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=rest)).isoformat()
    recent = st.get("recent") or []
    used_recent = {r.get("kind") for r in recent if str(r.get("slot_at") or "") >= cutoff}
    used_src = {str(r.get("src_id")) for r in recent}
    pool = [k for k in kinds if k["kind"] not in used_recent]
    if not pool: say("⏸️ كلُّ الأنواع نزلت على يوتيوب خلال أيام الراحة — أضِف أنواعًا لـ kinds.json"); return
    day = datetime.datetime.utcnow().strftime("%Y%m%d")
    rnd = random.Random("yt" + day)
    rnd.shuffle(pool)
    prequeue(pool[: min(len(pool), 2 * a.max + 2)])
    made = 0
    for slot in free[: a.max]:
        done = False
        while pool and not done:
            k = pool.pop(0)
            say(f"▶️ خانة يوتيوب {slot['day']} {slot['hm']} ← النوع «{k['kind']}»")
            try:
                cands = [c for c in find_videos(k["kind"], k["q"]) if c["id"] not in used_src]
            except Exception as e:
                say("   ⚠️ تعثّر الصيد:", e); continue
            got = []
            for c in cands[:6]:
                tmp = tempfile.mkdtemp(prefix="yt")
                src = os.path.join(tmp, "src.mp4")
                if not download(c["video"], src): say("   ⚠️ ما نزل الفيديو"); continue
                p = probe(src)
                if not p or p[2] < 6: say("   ⚠️ فيديو قصيرٌ أو تالف"); continue
                got.append((c, tmp, src, p))
                if p[1] >= p[0] or len(got) >= 4: break
            got.sort(key=lambda g: (0 if g[3][1] >= g[3][0] else 1))
            for c, tmp, src, p in got:
                hook = rnd.choice(k["hooks"])
                png = os.path.join(tmp, "ov.png"); wav = os.path.join(tmp, "m.wav"); out = os.path.join(tmp, "out.mp4")
                overlay(png, hook[0], hook[1], k["search"], code, y0=YT_BAND_Y)
                subprocess.run([sys.executable, os.path.join(HERE, "music.py"), "8.75", str(rnd.randint(1, 10**6)), wav], check=True, capture_output=True)
                path, err = render_yt(src, png, wav, out, *p)
                if not path: say("   ⚠️ تعثّر الرسم:", err); continue
                key = f"YS-{day}-{k['kind']}-{c['id'][-6:]}"
                title = hook[0] + " " + hook[1]
                if a.dry:
                    say(f"   🧪 جافّ: {key} · {os.path.getsize(path)//1000}KB · {p[0]}x{p[1]} {p[2]:.0f}ث"); done = True; break
                cl = api_post("/api/yt/claim", {"key": key, "kind": k["kind"], "title": title, "search": k["search"],
                                                "tags": k.get("tags") or [], "src_id": c["id"], "at": slot["at"]})
                if not cl.get("ok"): say("   ⚠️ الخادم ما حجز:", cl.get("why") or cl); done = True; break
                try:
                    vid, ust = yt_upload(path, cl)
                except Exception as e:
                    api_post("/api/yt/done", {"key": key, "why": str(e)[:280]})
                    say("   ⛔ تعذّر الرفع ليوتيوب:", e); done = True; break
                api_post("/api/yt/done", {"key": key, "video_id": vid})
                say(f"   ✅ رُفع: https://www.youtube.com/shorts/{vid} ({ust}) ← {cl.get('publish_at') or 'الآن'}")
                made += 1; done = True; break
            if not done: say(f"   ↪️ «{k['kind']}» بلا فيديو صالح — النوعُ التالي")
    say(f"🏁 يوتيوب: رُفع {made} من {min(len(free), a.max)}")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); ap.add_argument("--max", type=int, default=2)
    ap.add_argument("--to", choices=["tiktok", "youtube"], default="tiktok")   # ▶️ WP-878
    a = ap.parse_args()
    if not TT_KEY: say("⛔ لا مفتاحَ مقاطع (TT_BOT_KEY)"); sys.exit(1)
    if a.to == "youtube": return main_youtube(a)
    st = api("/api/tt/product/state")
    if not st.get("ok"): say("⛔ ما وصل حالُ الخادم:", st); sys.exit(1)
    if st.get("why"): say("⏸️", st["why"]); return
    free, code = st.get("free") or [], st.get("code") or ""
    if not free: say("✅ لا خانةَ فاضيةَ في اليومين القادمين — ما في شغل"); return
    cfg = st.get("cfg") or {}; rest = int(cfg.get("rest_days") or 21)
    kinds = json.load(open(os.path.join(HERE, "kinds.json"), encoding="utf-8"))["kinds"]
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=rest)).isoformat()
    recent = st.get("recent") or []
    used_recent = {r.get("kind") for r in recent if str(r.get("slot_at") or "") >= cutoff}
    used_src = {str(r.get("src_id")) for r in recent}
    pool = [k for k in kinds if k["kind"] not in used_recent]
    if not pool: say("⏸️ كلُّ الأنواع نزلت خلال أيام الراحة — أضِف أنواعًا لـ kinds.json"); return
    day = datetime.datetime.utcnow().strftime("%Y%m%d")
    rnd = random.Random(day)
    rnd.shuffle(pool)
    prequeue(pool[: min(len(pool), 2 * a.max + 2)])
    made = 0
    for slot in free[: a.max]:
        done = False
        while pool and not done:
            k = pool.pop(0)
            say(f"🎯 خانة {slot['day']} {slot['hm']} ← النوع «{k['kind']}»")
            try:
                cands = [c for c in find_videos(k["kind"], k["q"]) if c["id"] not in used_src]
            except Exception as e:
                say("   ⚠️ تعثّر الصيد:", e); continue
            # 📐 نُنزّل حتى أربعة ونفضّل الطوليّ: العرضيُّ يصغر في الشاشة وقد تتسرّب ترجمتُه
            got = []
            for c in cands[:6]:
                tmp = tempfile.mkdtemp(prefix="tp")
                src = os.path.join(tmp, "src.mp4")
                if not download(c["video"], src): say("   ⚠️ ما نزل الفيديو"); continue
                p = probe(src)
                if not p or p[2] < 6: say("   ⚠️ فيديو قصيرٌ أو تالف"); continue
                got.append((c, tmp, src, p))
                if p[1] >= p[0] or len(got) >= 4: break
            got.sort(key=lambda g: (0 if g[3][1] >= g[3][0] else 1))
            for c, tmp, src, p in got:
                hook = rnd.choice(k["hooks"])
                png = os.path.join(tmp, "ov.png"); wav = os.path.join(tmp, "m.wav"); out = os.path.join(tmp, "out.mp4")
                overlay(png, hook[0], hook[1], k["search"], code)
                subprocess.run([sys.executable, os.path.join(HERE, "music.py"), "8.75", str(rnd.randint(1, 10**6)), wav], check=True, capture_output=True)
                b64, err = render(src, png, wav, out, *p)
                if not b64: say("   ⚠️ تعثّر الرسم:", err); continue
                key = f"PR-{day}-{k['kind']}-{c['id'][-6:]}"
                title = hook[0] + " " + hook[1]
                if a.dry:
                    say(f"   🧪 جافّ: {key} · {len(b64)//1000}k حرف · {p[0]}x{p[1]} {p[2]:.0f}ث"); done = True; break
                up = api_post("/api/tt/vid/upload", {"key": key, "mp4": "data:video/mp4;base64," + b64})
                if not (up.get("ok") or up.get("id")): say("   ⚠️ رفض الإيداع:", up.get("error") or up); continue
                add = api_post("/api/tt/product/add", {"key": key, "kind": k["kind"], "title": title, "search": k["search"],
                                                       "tags": k.get("tags") or [], "src_id": c["id"], "at": slot["at"]})
                if not add.get("ok"): say("   ⚠️ ما دخل الطابور:", add.get("why") or add); continue
                say(f"   ✅ دخل الطابور: {title} ← {add.get('day')} {add.get('hm')}")
                made += 1; done = True; break
            if not done: say(f"   ↪️ «{k['kind']}» بلا فيديو صالح — النوعُ التالي")
    say(f"🏁 رُسم وأُدخل {made} من {min(len(free), a.max)}")

if __name__ == "__main__":
    main()
