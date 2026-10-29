#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 مشغّلُ مقاطع تيك توك — WP-084
يدور كلَّ فجرٍ على GitHub Actions، ولا يلمس كودَ التطبيق.

  ① يقرأ  GET /api/tt/today          ← الصفوفَ التي اختارها جدولُك فعلًا
  ② يقرأ  GET /api/site/offers?public=1 ← اسمَ المتجر والقيمةَ من المصدر
  ③ يسأل  GET /api/tt/videolist      ← قائمةَ المقاطع من مكتبتك الحيّة
  ④ يرسم مقطعًا بالتوليفة التالية في الدور (٣ أشكال × ٣ أصوات)
  ⑤ يودعه POST /api/tt/vid/upload بمفتاح الصفِّ نفسِه

ولماذا بمفتاح الصفِّ نفسِه؟ لأنّ العطبَ الذي أخفى المقاطعَ سنةً كان أنّ
`ttVideoFor` تطابق `offer_key` **تساويًا تامًّا**، ومفاتيحُ المخزون القديم من
عائلةٍ غير مفاتيح الصفوف. فالمولّدُ يرسم بمفتاح الصفِّ ⇒ المطابقةُ تنجح دائمًا.

**وكلُّ تخطٍّ يقول سببَه** — لا صمتَ ولا صفرٌ يبدو حقيقة (قاعدة المشروع ⑥).

  python3 run.py --dry     ← يفحص ويرسم ولا يودع
  python3 run.py           ← يودع فعلًا
"""
import os, re, sys, json, base64, zlib, argparse, subprocess, datetime, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("OS_BASE", "https://os.awalbawal.com").rstrip("/")
USER = os.environ.get("OS_USER", "")
PASS = os.environ.get("OS_PASS", "")
# 🔑 WP-360: مفتاحُ المقاطع وحدَها — يُفضَّل على كلمة مرور المدير متى وُجد
TT_KEY = os.environ.get("TT_BOT_KEY", "")

# سقفُ الإيداع في القاعدة (lib/ttvideo.js: TT_VIDEO_MAX_B64)
MAX_B64 = 1_400_000
# بدايةُ الدورة — منها تُحسب أيُّ توليفةٍ يأخذها الكود
EPOCH = datetime.date(2026, 8, 12)
# طولُ دورةٍ كاملة: ٧٩ زوجًا ÷ ٣ خاناتٍ يوميًّا ≈ ٢٦ يومًا (قِيس 2026-08-13)
CYCLE_DAYS = 26
FORMS = ["a", "b", "c", "d", "e", "f"]   # الهادئ · السريع · هوية المتجر · كشفُ الكود · سؤالٌ وجواب · التذكرة
FORMS_DEFAULT_ON = ["a", "b", "c"]       # الجديدةُ تدخل بعد اعتماده عيّناتِها (WP-628) — من النظام: `forms_on`
SOUNDS = ["1", "2", "3"]         # هادئ · إيقاع · تصعيدٌ وانفجار

# ═══ 🗣️ العباراتُ والفئات (WP-087 · اعتمدها المؤسس 2026-08-13) ═══
# فئةُ المتجر تُقرأ من `stores.json` — صُنّفت **بفتح المواقع لا بتخمين الأسماء**:
# «سويتر» غسيلُ سيّاراتٍ لا ملابس · «اطلبها» تمويلُ سيّارات · «بينه» محاماة.
# ومن لا فئةَ له يأخذ `none` (عباراتٌ محايدة) — ولا يُخمَّن له نوع.
def _load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)

_ST = _load("stores.json")["map"]
_PH = _load("phrases.json")
PHRASES = _PH["sets"]
N_PHRASE = len(PHRASES["none"])          # ٥ — والحارسُ أدناه يمنع اختلافَها بين الفئات
assert all(len(v) == N_PHRASE for v in PHRASES.values()), \
    "كلُّ فئةٍ يجب أن تحمل العددَ نفسَه من العبارات — وإلّا اختلّ الدوران"


# ═══ 📝 كاتبُ النصّ — واحدٌ لا اثنان (قرارُ صالح 2026-08-13) ═══
# العبارةُ تُختار هنا، فلو بناها التطبيقُ أيضًا لصار **كاتبان لحقيقةٍ واحدة**
# — وهو عطبُنا المتكرّر: المقطعُ يقول جملةً والنصُّ يقول غيرَها. فالمصنعُ
# يكتب النصَّ كاملًا ويودعه، والتطبيقُ يستعمله كما هو ولا يعيد تأليفَه.
#
# ويُكتب نصٌّ **لكلِّ صفوف اليوم** — حتّى ما لا يُرسم له مقطعٌ لأنّ كودَه غيرُ
# معتمد. فالتنويعُ يصل ١٠٠٪ من المنشورات لا ٦٧٪ (قرارُه بعد أن عرضتُ الحدَّين).
# 🏷️ ═══ بنكُ الوسوم — بنيّة البحث وتدور (WP-628 · قرارُه 2026-10-07) ═══
# قال: «ما صرنا نحط هاشتاقات مناسبة». والمقيس: وسمان للفئة + أربعةٌ ثابتةٌ في كلِّ
# منشور. فصار لكلِّ فئةٍ بنكٌ يُؤخذ منه ثلاثةٌ بالدور، ومن العامّ اثنان بالدور، و#إعلان.
# ⛔ ولا وسمَ باسم المتجر (قرارُه 2026-08-13 — شروطُ الشبكات) — اسمُه في سطر البحث نصًّا.
HASHTAGS = {
    "fashion": ["أزياء", "موضة", "تسوق_اونلاين", "ملابس", "ستايل", "عروض_ازياء", "شوبينق"],
    "home": ["ديكور", "أثاث", "ديكور_منزلي", "مطبخ", "تنظيم_المنزل", "منزل"],
    "food": ["مطاعم", "توصيل", "طلبات", "اكل", "عروض_مطاعم", "توصيل_طلبات"],
    "beauty": ["عناية_بالبشرة", "عطور", "مكياج", "جمال", "سكين_كير", "عناية"],
    "health": ["مكملات", "صحة", "صيدلية", "فيتامينات", "تغذية", "رياضة"],
    "travel": ["سفر", "حجوزات", "فنادق", "طيران", "سياحة", "رحلات"],
    "tech": ["إلكترونيات", "أجهزة", "جوالات", "تقنية", "اكسسوارات_جوال", "قيمنق"],
    "auto": ["سيارات", "خدمات_السيارات", "عناية_بالسيارة", "سيارتي"],
    "ride": ["مشاوير", "توصيل", "تطبيقات_توصيل", "تنقل"],
    "service": ["تطبيقات", "خدمات", "اشتراكات", "تطبيقات_سعودية"],
    "none": ["تسوق", "تسوق_اونلاين", "عروض_اليوم"],
}
GENERIC_TAGS = ["كوبونات", "عروض", "السعودية", "أول_بأول", "كود_خصم", "خصومات", "توفير", "اكواد_خصم"]


def tags_for(cat, seed):
    """٣ من بنك الفئة + ٢ من العامّ بالدور — فلا يتكرّر الطقمُ نفسُه منشورًا بعد منشور."""
    bank = HASHTAGS.get(cat, []) or HASHTAGS["none"]
    k = min(3, len(bank))
    cat_t = [bank[(seed + i) % len(bank)] for i in range(k)]
    gen_t = [GENERIC_TAGS[(seed * 3 + i) % len(GENERIC_TAGS)] for i in range(2)]
    seen, out = set(), []
    for t in cat_t + gen_t:
        if t not in seen:
            seen.add(t); out.append("#" + t)
    return out + [AD_TAG]
# 👥 دعوةُ المتابعة تدور — كانت سطرًا واحدًا يتكرّر ٩٠ مرّةً شهريًّا بحرفه
FOLLOW = ["👥 تابعنا يوصلك كل كود جديد", "👥 حطّ متابعة ولا يفوتك كود",
          "👥 تابعنا — أكوادٌ كلَّ يوم", "👥 متابعةٌ وحدة وتوفّر كلَّ يوم",
          "👥 تابعنا وخلّ الأكواد توصلك"]
TG_LINE = "👈 أكوادٌ جديدةٌ كلَّ يوم: تيليجرام @Awalbawal_offers"
AD_TAG = "#إعلان"        # إلزاميٌّ بسياسة تيك توك — لا يُحذف ولا يُنسى


# 🚫 ═══ ولا وسمَ باسم المتجر (قرارُ صالح 2026-08-13) ═══
# كنتُ أضفتُ `#<اسم المتجر>` لكلِّ منشور، ثمّ وجدتُ في `lib/arabclicks.js`
# قارئَ شرطٍ اسمُه `noHashtag` يترقّب في شروط الشبكات:
#     «no using of … hashtag» · «hashtag … not allowed/prohibited»
# ومعناه أنّ **بعض برامج الشبكات تمنع استعمالَ اسم المتجر وسمًا**.
#
# ولم أُثبت أنّ القيدَ يسري على متاجره بعينها — تعذّر القياسُ يومَها.
# فاختار **الحذفَ بلا انتظار**: وسمٌ واحدٌ لا يساوي حسابًا في شبكةٍ يُغلق.
# وتبقى ٦–٧ وسومٍ: الفئةُ والعلامةُ والإفصاح — وكلُّها ملكُنا لا ملكُ أحد.
#
# ⛔ ومن أراد إرجاعَه غدًا: يقرأ شروطَ كلِّ شبكةٍ أوّلًا، ويبني بوّابةً
#    تحذفه لمن يمنعه. والحارس ٥٧ يرفض النشرَ إن عاد بلا ذلك.


def caption_for(store, code, value, day, chosen=None):
    """نصُّ المنشور كاملًا — العبارةُ نفسُها التي في المقطع، فيتناغم الاثنان.

    ولا يُخترع رقمٌ ولا وعد: القيمةُ تُلحق **إن وُجدت فقط**، وما عداها كلامٌ
    لا يَعِد بشيءٍ لا نملكه (قاعدة ⑥).
    `chosen` = (cat, pi, ph) من خطّة الصفّ (`plan_row`) — فالنصُّ والمقطعُ عبارةٌ واحدة.
    """
    cat, pi, ph = chosen or phrase_for(store, code, day)
    seed = zlib.crc32(code.encode("utf-8")) + (day - EPOCH).days
    emoji = _PH["emoji"].get(cat, "🎟️")

    head = f"{emoji} {ph['h1']} {ph['h2']}"
    if str(value or "").strip():
        head += " — " + str(value).strip()

    # 🔎 سطرُ البحث أوّلًا (WP-628): ٨٥٪ من وصول الحساب بحث، والناسُ تكتب
    #    «كود خصم <متجر> <سنة>». نصًّا لا وسمًا — وسمُ المتجر ممنوعٌ بقراره.
    search = f"🔎 كود خصم {store} {day.year}"
    lines = [search, head, f"🎟️ الكود: {code}", ph["cta"], ""]
    lines.append(FOLLOW[seed % len(FOLLOW)])
    # 📣 وتيليجرام مرّةً كلَّ ثلاثةِ منشوراتٍ لا في كلِّ واحد — جمهورُ تيك توك
    #    لا يغادر التطبيق، والسطرُ الثابتُ يأكل مساحةً بلا مردودٍ مقيس.
    if seed % 3 == 0:
        lines.append(TG_LINE)
    lines.append("")

    lines.append(" ".join(tags_for(cat, seed)))
    return cat, pi, "\n".join(lines)


def cat_of(store):
    """فئةُ المتجر — أو `none` إن لم تكن مصنَّفةً. ولا تخمين."""
    return _ST.get(norm_store(store), "none")


def say(*a):
    print(*a, flush=True)


# 🛡️ ═══ درعُ Cloudflare — قياسُ 2026-08-12 ═══
# أوّلُ تشغيلٍ ردّ **403** لا 401. والفرقُ يشخّص: كودُ التطبيق يردّ 401 عند خطأ
# كلمة المرور (`needAuth()`)، فالـ403 من الحافّة لا من التطبيق — الطلبُ حُجب
# قبل أن يصل. وأرجحُ سببٍ: بصمةُ طلبٍ آليّ (`Python-urllib/3.x` بلا مُعرِّف).
# فنُعرّف أنفسنا تعريفًا صادقًا — لا انتحالَ متصفّحٍ ولا تحايلَ على حماية:
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0 Safari/537.36 AwalbawalTTVideo/1.0")


def _head(req):
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/json, text/plain, */*")
    req.add_header("Accept-Language", "ar,en;q=0.8")
    if TT_KEY:
        req.add_header("x-tt-key", TT_KEY)
    elif USER:
        tok = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
        req.add_header("Authorization", "Basic " + tok)
    return req


class DbBusy(RuntimeError):
    """القاعدةُ مشغولةٌ بتصدير «نسخة القاعدة» — ينتظر ولا يسقط (WP-363)."""


# ⏳ ═══ القاعدةُ تُقفل أثناء التصدير (قِيس 2026-09-17) ═══
# D1 ترفض الاستعلامات ما دام `wrangler d1 export` يعمل: «Currently processing a long-running export».
# شُغّل «مقاطع تيك توك» و«نسخة القاعدة» معًا فسقط الأوّل بـ500. والتصديرُ ~٢٠ ثانية،
# وجدولةُ GitHub تتأخّر ساعاتٍ فقد يتلاقيان يومَ الجمعة ⇒ ينتظر ويعيد بدل أن يسقط.
BUSY_MARK = "long-running export"
BUSY_TRIES = int(os.environ.get("TT_BUSY_TRIES", "6"))
BUSY_WAIT = float(os.environ.get("TT_BUSY_WAIT", "30"))


def _open_once(req, timeout):
    """وكلُّ فشلٍ يقول جسدَه — لا رمزٌ عارٍ بلا معنى (قاعدة المشروع ⑥)."""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode("utf-8", "replace")[:400]
        except Exception: pass
        if e.code in (500, 503) and BUSY_MARK in body:
            raise DbBusy(f"HTTP {e.code} على {req.full_url} · القاعدةُ مشغولةٌ بتصدير النسخة") from None
        hint = {401: ("مفتاحُ المقاطع مرفوض — طابِق TT_BOT_KEY في GitHub وفي Pages" if TT_KEY
                      else "بياناتُ الدخول مرفوضة — راجع OS_USER و OS_PASS"),
                503: "السرُّ غائبٌ عن اللوحة — أضف TT_BOT_KEY إلى Pages ثمّ انشر",
                403: "حجبٌ من درع Cloudflare قبل التطبيق — راجع Bot Fight Mode / WAF"}.get(e.code, "")
        raise RuntimeError(f"HTTP {e.code} على {req.full_url}"
                           + (f" · {hint}" if hint else "")
                           + (f"\n   الردّ: {body}" if body.strip() else "")) from None


def _open(req, timeout):
    import time
    for i in range(BUSY_TRIES + 1):
        try:
            return _open_once(req, timeout)
        except DbBusy as e:
            if i >= BUSY_TRIES:
                raise RuntimeError(str(e) + f" — بقيت مشغولةً بعد {BUSY_TRIES} محاولات") from None
            say(f"   ⏳ القاعدةُ مشغولةٌ بتصدير النسخة — أنتظر {BUSY_WAIT:g} ثانية ({i + 1}/{BUSY_TRIES})")
            time.sleep(BUSY_WAIT)


def api(path):
    """قراءةٌ من اللوحة بصلاحيتها (قرارُ صالح 2026-08-12)."""
    return _open(_head(urllib.request.Request(BASE + path)), 60)


def api_post(path, body):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    return _open(_head(req), 180)


# ═══ استخراجُ الكود من نصِّ المنشور ═══
# ⚠️ قِيس على صفوفٍ حيّة 2026-08-12: النظامُ يكتب السطرَ بثلاث صيغٍ مختلفة
#      «🔖 الكود: WALEED10»
#      «🎟️ كودك: K24UQ7J»
#      «🏷️ اكتب الكود عند الدفع: LA01»   ← بينهما كلامٌ فتنكسر المطابقةُ اللاصقة
#    فالقاعدةُ: نجد **السطرَ** الذي يذكر الكود، ثمّ نأخذ ما بعد آخر نقطتين فيه.
#    وهذا يحتمل صيغةً رابعةً لم نرَها بعد، بدل أن يصمت عنها.
CODE_LINE = re.compile(r"(?:الكود|كودك|الكوبون|كوبون)")


def code_of(text):
    for ln in str(text or "").splitlines():
        if not CODE_LINE.search(ln):
            continue
        if ":" in ln or "：" in ln:
            tail = re.split(r"[:：]", ln)[-1].strip()
        else:
            tail = ln.split()[-1].strip()
        tail = tail.split()[0] if tail.split() else ""
        # الكودُ لا يكون كلمةً عربيةً خالصة — وإلا فقد التقطنا وصفًا لا كودًا
        if tail and re.search(r"[A-Za-z0-9]", tail):
            return tail
    return ""


def norm_code(c):
    return re.sub(r"\s+", "", str(c or "")).strip().lower()


# ═══ اسمُ المتجر من نصِّ المنشور ═══
# ⚠️ عطبٌ أُمسك 2026-08-12: الكودُ وحدَه لا يكفي مفتاحًا — `LA01` مشترَكٌ بين
#    «ناتفِيتا» و«سمكو إضاءة»، و`LA1` بين أربعة متاجر. فمطابقةٌ بالكود وحده
#    كانت ستُخرج مقطعًا باسم متجرٍ غير الذي في المنشور. المفتاحُ: كودٌ + متجر.
def store_of(text):
    """أوّلُ سطرٍ شكلُه «<رمز> اسمُ المتجر — عرض»."""
    for ln in str(text or "").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        m = re.match(r"^\S*\s*(.+?)\s+[—–-]\s+", ln)
        return (m.group(1).strip() if m else "")
    return ""


def norm_store(s):
    s = re.sub(r"[\u0640\u064B-\u0652]", "", str(s or ""))   # تطويلٌ وتشكيل
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه")
    return re.sub(r"\s+", "", s).strip().lower()


# 🏷️ ═══ الأسماءُ البديلة — نُزعت في WP-318 ولا تُعاد ═══
# كانت لازمةً لأنّ المطابقةَ كانت **باسم المتجر + الكود** نصًّا، فاحتاجت
# بدائلَ يكتبها المؤسسُ بيده («سمارت هب1» ≈ «سمارت هب»). وصارت المطابقةُ
# بمعرّف العرض نفسِه، فزال السببُ وزالت معه. **والاسمُ لم يعد مفتاحًا.**


def combo_for(code, day):
    """التوليفةُ تُشتقُّ اشتقاقًا — لا حالةَ محفوظةٌ تضيع أو تتعارض.

    ثلاثةُ أشكالٍ × ثلاثةُ أصواتٍ × خمسُ عباراتٍ = **٤٥ توليفة**. والكودُ يظهر
    مرّةً كلَّ ٢٦ يومًا، فلا تعود توليفتُه إلا بعد ٤٥ ظهورًا ≈ **ثلاثةُ أعوام**.
    (كانت ٩ توليفاتٍ فقط قبل بنك العبارات — وهو سببُ شعوره بالروتين.)
    """
    span = 3 * 3 * N_PHRASE
    cycle = (day - EPOCH).days // CYCLE_DAYS
    idx = (zlib.crc32(code.encode("utf-8")) + cycle) % span
    return FORMS[idx % 3], SOUNDS[(idx // 3) % 3], (idx // 9) % N_PHRASE


# 🚫 ═══ ولا عبارتان متطابقتان في يومٍ واحد (عطبُ 2026-08-14) ═══
# خرج منشورا اليوم بالجملة نفسِها: «قبل ما تدفع في بلندز» و«قبل ما تدفع في
# سمكو إضاءة» — كلاهما فئةُ «بيت» ووقعا على العبارة نفسِها بالحساب.
# وهو الروتينُ بعينه الذي بُنيت الحزمةُ لكسره. فالتوليفةُ تُشتقُّ كما هي، ثمّ
# **إن تصادمت مع أختٍ في اليوم نفسِه تتقدّم خطوةً** — والدورانُ يبقى محفوظًا.
_USED_TODAY = set()


# 🔁 ═══ لا توليفةَ تتكرّر للكود نفسِه (WP-628) ═══
# كانت `combo_for` تشتقُّ التوليفةَ من دورةٍ ثابتةٍ ٢٦ يومًا، والكودُ صار يعود كلَّ
# ~١٧ يومًا ⇒ ظهوران في الدورة نفسِها = **المقطعُ نفسُه حرفًا**. فصار المصنعُ يسأل
# النظامَ عمّا خرج لكلِّ كودٍ (`tt/combos`) ويأخذ أوّلَ توليفةٍ لم تخرج له،
# وشكلًا لم يُستعمل اليومَ إن أمكن. والترتيبُ يبدأ من بذرة الكود فلا يتشابه كودان.
_FORMS_TODAY = set()


def plan_row(store, code, day, history, forms_on):
    """(form, snd, cat, pi, ph, combo) — توليفةٌ لم تخرج لهذا الكود قبل."""
    cat = cat_of(store)
    used = set(history.get(norm_code(code), []))
    fo = [x for x in FORMS if x in forms_on] or FORMS_DEFAULT_ON
    span = len(fo) * len(SOUNDS) * N_PHRASE
    start = zlib.crc32(code.encode("utf-8")) % span
    best = None
    for strict in (2, 1, 0):          # ٢: جديدٌ + شكلٌ وعبارةٌ لم تُستعمل اليوم · ١: جديد · ٠: أيُّ شيء
        for j in range(span):
            idx = (start + j) % span
            form, snd, pi = fo[idx % len(fo)], SOUNDS[(idx // len(fo)) % 3], (idx // (len(fo) * 3)) % N_PHRASE
            combo = f"{form}-{snd}-{pi + 1}"
            if strict >= 1 and combo in used:
                continue
            if strict == 2 and (form in _FORMS_TODAY or (cat, pi) in _USED_TODAY):
                continue
            best = (form, snd, pi, combo); break
        if best: break
    form, snd, pi, combo = best
    _FORMS_TODAY.add(form); _USED_TODAY.add((cat, pi))
    p = PHRASES.get(cat, PHRASES["none"])[pi]
    fill = lambda s: str(s or "").replace("{S}", store)
    return form, snd, cat, pi, {"h1": fill(p["h1"]), "h2": fill(p["h2"]), "cta": fill(p["cta"])}, combo


def phrase_for(store, code, day):
    """عبارةُ هذا المنشور — نصًّا جاهزًا باسم المتجر لا برمزٍ فيه {S}."""
    cat = cat_of(store)
    _, _, pi = combo_for(code, day)
    for _ in range(N_PHRASE):
        if (cat, pi) not in _USED_TODAY:
            break
        pi = (pi + 1) % N_PHRASE
    _USED_TODAY.add((cat, pi))
    p = PHRASES.get(cat, PHRASES["none"])[pi]
    fill = lambda s: str(s or "").replace("{S}", store)
    return cat, pi, {"h1": fill(p["h1"]), "h2": fill(p["h2"]), "cta": fill(p["cta"])}


# 🎚️ ═══ سلّمُ الجودة — والمصنعُ يضمن مقطعًا صالحًا لا يعتذر (عطبُ 2026-08-14) ═══
# صار السيناريو ١٣ ثانيةً بدل ٨، فخرج مقطعُ بلندز **١٫٥٧MB فوق سقف ١٫٤٠**
# فرُفض عند الإيداع: «0 جاهزًا · 1 فاشلًا». والسقفُ مقاسٌ لمقاطع أربع ثوانٍ،
# **ولا يُرفع** — صفُّ D1 لا يحتمل الميجابايتات، وهذا قرارٌ معماريٌّ لا رقمٌ عابر.
#
# فالمصنعُ ينزل درجةً في الجودة ويعيد، حتّى يدخل السقفَ أو ينفد السلّم.
# وكلُّ نزولٍ **يُقال في السجلّ** — فلا جودةٌ تنحدر بصمت.
CRF_LADDER = [26, 30, 34, 38]


def render(store, code, value, form, snd, out, phrase=None, crf=26):
    env = dict(os.environ)
    body = {"store": store, "code": code, "value": value, "cat": cat_of(store)}
    if phrase:
        body.update(phrase)
    env["OFFER_JSON"] = json.dumps(body, ensure_ascii=False)
    env["CRF"] = str(crf)
    r = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), form, snd, out],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-600:])
    return r.stdout.strip()


def render_fit(store, code, value, form, snd, out, phrase=None, say_=None):
    """يرسم ويعيد حتّى يدخل السقف — ويُعيد (البايتات، الجودة المستعملة)."""
    last = None
    for crf in CRF_LADDER:
        render(store, code, value, form, snd, out, phrase, crf=crf)
        raw = open(out, "rb").read()
        b64len = len(base64.b64encode(raw))
        if b64len <= MAX_B64:
            return raw, crf, b64len
        last = (raw, crf, b64len)
        if say_:
            say_(f"   🎚️ {b64len/1e6:.2f}MB فوق السقف عند جودة {crf} — أنزل درجة")
    return last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="ارسم وافحص ولا تودع")
    a = ap.parse_args()

    if not TT_KEY and (not USER or not PASS):
        say("⛔ لا بيانات دخول — اضبط TT_BOT_KEY (أو OS_USER و OS_PASS)"); return 1
    say("🔑 الدخول بمفتاح المقاطع" if TT_KEY else "🔑 الدخول بكلمة مرور اللوحة (انقل إلى TT_BOT_KEY)")

    # ═══ 🎬 قائمةُ المقاطع — من النظام لا من ملفٍّ في المستودع (WP-318) ═══
    # كانت تُقرأ من `approved.json` **على فرع master**، والعملُ على فرعٍ آخر،
    # فتأخّر تصحيحُ ٣١ أغسطس ثلاثةَ أسابيعَ وخرجت سبعةُ أكوادٍ معتمدةٍ صورةً.
    # والآن تُسأل المكتبةُ الحيّة: فما أوقفتَ شبكتَه أو خرج من مكتبتك يسقط
    # وحدَه، والكودُ الجديدُ يدخل بلا انتظار (قرارُه «أ»: الغيابُ يعني نعم).
    #
    # ⛔ وإن تعذّر السؤالُ **نقف ولا نرسم**: رسمٌ بقائمةٍ مجهولةٍ قد يُخرج مقطعًا
    #    لكودٍ أطفأه بيده — و«لا أعرف» ليست «نعم».
    try:
        vl = api("/api/tt/videolist")
        vids = {str(o["key"]): o for o in (vl.get("items") or []) if o.get("key")}
    except Exception as e:
        say(f"⛔ تعذّرت قراءةُ قائمة المقاطع من النظام: {e} — لا أرسم بقائمةٍ مجهولة")
        return 1
    if not vids:
        say("⛔ قائمةُ المقاطع فارغة — لا أرسم شيئًا حتى يُعرف السبب")
        return 1
    say(f"🎬 قائمةُ المقاطع: {len(vids)} كودًا · مطفأٌ بيدك {vl.get('off', 0)}")
    # 🎨 الأشكالُ المعتمدة من النظام (WP-628) — والقديمُ إن لم يُرسل بعد.
    forms_on = [x for x in (vl.get("forms_on") or FORMS_DEFAULT_ON) if x in FORMS] or FORMS_DEFAULT_ON
    say(f"🎨 الأشكال: {' · '.join(forms_on)}")
    # 🔁 ما خرج لكلِّ كودٍ قبلُ — وإن تعذّر لا نقف: نرسم بلا ذاكرةٍ ونقول ذلك.
    try:
        history = (api("/api/tt/combos") or {}).get("items") or {}
    except Exception as e:
        history = {}
        say(f"⚠️ تعذّرت قراءةُ ما خرج لكلِّ كود: {e} — قد تتكرّر توليفة")

    today = api("/api/tt/today")
    rows = list(today.get("tracks", {}).get("scheduled", []))
    # 🎬 WP-684: صفوفُ مقاطع المنتجات (PR-…) لها مصنعُها ومقطعُها — لا يُرسم لها هنا
    #    مقطعُ كود: الإيداعُ يستبدل المقطعَ المودَع بنفس المفتاح فيمحو مقطعَ المنتج.
    rows = [r for r in rows if not str(r.get("key") or "").startswith("PR-")]
    day = datetime.date.fromisoformat(today.get("day"))
    say(f"📅 يوم {day} · صفوفٌ مجدولة: {len(rows)}")
    if not rows:
        say("لا صفوفَ مجدولةً بعد — لا شيءَ يُرسم."); return 0

    # 💰 قيمةُ الخصم من مكتبته الحيّة — لا من قائمة الاعتماد وحدَها، فالمكتبةُ
    #    هي المصدر. وما لا قيمةَ له يبقى فارغًا: لا رقمَ مزروع.
    values = {}
    try:
        for o in (api("/api/site/offers?public=1") or []):
            if not isinstance(o, dict) or not o.get("code"):
                continue
            st = ((o.get("store") or {}).get("name") if isinstance(o.get("store"), dict)
                  else o.get("store_name")) or ""
            v = str(o.get("deal_value") or "").strip()
            # ⚠️ وقيمةٌ هي اسمُ المتجر مكرَّرًا ليست رقمًا («كود خصم فكرة») —
            #    قِيس أنّها ٦١٪ من أكواده. فتُطرح هنا ولا تُلحق بالنصّ.
            if v and norm_store(st) in norm_store(v):
                v = ""
            values[(norm_store(st), norm_code(o["code"]))] = v
    except Exception as e:
        say(f"⚠️ تعذّرت قراءةُ قيم الخصم: {e} — تخرج النصوصُ بلا أرقام")

    stock = api("/api/tt/vid/stock")
    # 📅 مقاطعُ **اليوم** وحدَها تُتخطّى — ومقطعُ أمسٍ يُعاد رسمُه بالقالب
    #    الحاليّ. (عطبُ 2026-08-14: صفُّ بلندز تدحرج من أمسِ فخرج بثمانِ
    #    ثوانٍ ساكنةٍ بينما أخوه ثلاثَ عشرةَ بسيناريو.)
    #    ويسقط على `keys` إن كانت اللوحةُ لم تُنشر بعد — فلا ينكسر شيء.
    have = set(stock.get("keys_today", stock.get("keys", [])))
    say(f"🎞️ في المخزون: queued={stock.get('queued')} · used={stock.get('used')}")

    # ═══ 📝 أوّلًا: نصُّ كلِّ صفٍّ — قبل الرسم وبمعزلٍ عنه ═══
    # يُكتب لكلِّ صفوف اليوم حتّى ما لا يُرسم له مقطع (كودُه غيرُ معتمد)،
    # فيصل التنويعُ ١٠٠٪ من المنشورات. والفشلُ هنا **لا يوقف الرسم**:
    # منشورٌ بنصٍّ قديمٍ خيرٌ من منشورٍ لا يخرج.
    caps = capfail = 0
    plans = {}
    for r in rows:
        key = r.get("key") or ""
        # 🏷️ الهويّةُ من حقولها إن أرسلتها اللوحةُ — ونثرُها آخرُ ملاذ.
        code = r.get("code") or code_of(r.get("text"))
        store = r.get("store") or store_of(r.get("text"))
        if not key or not code or not store:
            continue
        val = values.get((norm_store(store), norm_code(code)), "")
        off = vids.get(str(key))
        # 🧭 خطّةُ الصفّ مرّةً واحدة — يقرؤها النصُّ هنا والرسمُ أدناه (عبارةٌ واحدة)
        pr = plan_row((off or {}).get("store") or store, (off or {}).get("code") or code, day, history, forms_on)
        plans[key] = pr
        cat, pi, cap = caption_for(store, code, val, day, chosen=(pr[2], pr[3], pr[4]))
        if a.dry:
            caps += 1
            continue
        try:
            res = api_post("/api/tt/cap", {"key": key, "text": cap, "phrase": f"{cat}-{pi+1}"})
            if res.get("ok"): caps += 1
            else: capfail += 1; say(f"⚠️ نصُّ {key}: {res.get('error')}")
        except Exception as e:
            capfail += 1; say(f"⚠️ تعذّر إيداعُ نصِّ {key}: {e}")
    say(f"📝 النصوص: {caps} كُتبت" + (f" · {capfail} تعثّرت" if capfail else "")
        + (" (جافّ — لم تُودع)" if a.dry else ""))

    made = skipped = failed = 0
    blocked = 0          # ⛔ تخطٍّ يعني «لا مقطعَ لهذا الصفّ» — لا «موجودٌ سلفًا»
    for r in rows:
        key = r.get("key") or ""
        at = r.get("at") or "—"
        code = r.get("code") or code_of(r.get("text"))
        tag = f"{at} · {key}"

        if not code:
            say(f"⏭️ {tag} — لم أتعرّف على الكود في نصِّ المنشور"); skipped += 1; blocked += 1; continue
        if key in have:
            say(f"⏭️ {tag} · {code} — رُسم اليومَ سلفًا"); skipped += 1; continue

        # 🔑 المفتاحُ هو معرّفُ العرض نفسُه — وهو المفتاحُ الذي يُرفع به المقطع.
        #    فلا مطابقةَ أسماءٍ ولا أسماءَ بديلةً ولا لبسَ بين متجرين بنفس الكود.
        off = vids.get(str(key))
        if off is None:
            say(f"⏭️ {tag} · {code} — ليس في قائمة المقاطع (أطفأتَه أو خرج من مكتبتك) ⇒ يخرج صورةً")
            skipped += 1; blocked += 1; continue

        form, snd, cat, pi, ph, combo = plans.get(key) or plan_row(off["store"], off["code"], day, history, forms_on)
        out = os.path.join("/tmp", f"tt_{key}.mp4")
        try:
            raw, used_crf, b64len = render_fit(
                off["store"], off["code"], off.get("value") or "", form, snd, out, ph, say)
        except Exception as e:
            say(f"❌ {tag} · {code} — تعذّر الرسم: {e}"); failed += 1; continue

        b64 = base64.b64encode(raw).decode()
        if len(b64) > MAX_B64:
            say(f"❌ {tag} · {code} — {len(b64)/1e6:.2f}MB فوق السقف {MAX_B64/1e6:.2f} "
                f"حتّى عند أدنى جودة ({CRF_LADDER[-1]}) — قصّر المدّة أو خفّف الشكل")
            failed += 1; continue

        q = "" if used_crf == CRF_LADDER[0] else f" · جودة {used_crf}"
        line = (f"شكل {form} · صوت {snd} · {cat}-{pi+1} «{ph['h1']} / {ph['h2']}» · توليفة {combo} "
                f"· {len(raw)/1e6:.2f}MB{q}")
        if a.dry:
            say(f"🧪 {tag} · {off['store']} · {code} — جاهزٌ ولم يُودع ({line})")
            made += 1; continue

        try:
            res = api_post("/api/tt/vid/upload",
                           {"key": key, "mp4": "data:video/mp4;base64," + b64,
                            "code": off["code"], "combo": combo})
        except Exception as e:
            say(f"❌ {tag} · {code} — تعذّر الإيداع: {e}"); failed += 1; continue

        if res.get("ok") or res.get("id"):
            say(f"✅ {tag} · {off['store']} · {code} — أُودع ({line})"); made += 1
        else:
            say(f"❌ {tag} · {code} — رفضه النظام: {res}"); failed += 1

    say(f"\n📊 الحصيلة: {made} جاهزًا · {skipped} متخطًّى ({blocked} بلا مقطع) · {failed} فاشلًا")

    # ═══ 🟥 رفٌّ فارغٌ وضوءٌ أخضر — العطبُ الذي قِيس حيًّا 2026-08-22 ═══
    # كان الشرطُ `failed` وحدَه، والتخطّي لا يُسقط الدورة. فجاء يومٌ كانت
    # أكوادُه الثلاثةُ كلُّها خارج قائمة اعتماده، فتخطّى الثلاثة، وخرج
    # **«✅ نجحت»** ولم يُودع مقطعًا واحدًا. ومضت سبعةُ أيامٍ قبل أن يُسأل.
    #
    # والقاعدة: **نجاحٌ بلا وديعةٍ ليس نجاحًا**. فإن مُنع كلُّ صفٍّ ولم يخرج
    # مقطعٌ واحد ⇒ تسقط الدورة ويصله خبرُ GitHub في يومه.
    # ⚠️ ولا تسقط حين يكون التخطّي «رُسم اليومَ سلفًا» — ذاك رفٌّ ممتلئٌ لا فارغ.
    if made == 0 and blocked > 0:
        say(f"🟥 لم يخرج مقطعٌ واحدٌ و{blocked} صفًّا مُنع — رفٌّ فارغٌ لا يُقال له نجاح")
        return 1
    # الفشلُ يُسقط الدورة فيصلك خبرٌ من GitHub — والتخطّي وحدَه لا يُسقطها
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
