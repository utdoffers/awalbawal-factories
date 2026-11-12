#!/usr/bin/env bash
# 🏭 WP-1037 (2026-11-12) — كروم Playwright للمصانع بلا اعتمادٍ على مرايا أوبونتو.
#
# قِيس 11/11 (سجلّ الوظيفة 130575739802): «تجهيز» علّق ~10 دقائق ثمّ طاح في 4 مصانع بين 17:12 و19:44 رياضًا —
# `playwright install --with-deps` يجيب الخطوط والمكتبات من apt، وapt ما قدر يوصل
# («Temporary failure resolving 'security.ubuntu.com'»). والعاديُّ 18–37 ثانية.
# وصورةُ مشغّل GitHub (Ubuntu 26.04) فيها أصلًا Google Chrome وChromium وخطّ الإيموجي (قِيس من runner-images)،
# وخطوطُ البطاقات نفسُها في المستودع (tools/codecard/fonts) ⇒ apt تحسينٌ لا شرط.
#
# الترتيب: ① كروم Playwright من خادم مايكروسوفت (لا أوبونتو) بمهلةٍ وإعادة
#          ② مكتباتُه وخطوطُه من apt بمهلة — تعثّرُها يُكتب ولا يوقف
#          ③ فحصٌ حيّ: كروم يفتح ويرسم صفحة عربية — هذا وحدَه يقرّر النجاح.
#   الاستعمال في سير العمل (بعد pip install playwright):   bash tools/ci-chromium.sh
set -u
PY="${PYTHON:-python3}"
got=0
for i in 1 2 3; do
  timeout -k 10 120 "$PY" -m playwright install chromium && { got=1; break; }
  echo "⏳ تنزيل كروم تعثّر — إعادة ($i/3)"; sleep 5
done
[ "$got" = 1 ] || echo "⚠️ تنزيل كروم Playwright ما اكتمل — أجرّب الفحص بما عندي"

LOG="${TMPDIR:-/tmp}/ci-chromium-deps.log"
if timeout -k 10 120 "$PY" -m playwright install-deps chromium >"$LOG" 2>&1; then
  echo "✅ مكتبات كروم وخطوطه من apt"
else
  echo "⚠️ مكتبات كروم من apt تعثّرت أو تجاوزت دقيقتين — أكمل بما في صورة المشغّل"
  grep -m3 -E "^(E|W): " "$LOG" || tail -3 "$LOG"
fi

timeout -k 5 60 "$PY" - <<'PYEOF' || { echo "⛔ كروم ما اشتغل — المصنع ما يقدر يرسم"; exit 1; }
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.set_content("<p dir='rtl' style='font-size:40px'>تجربة الرسم ✅</p>")
    pg.screenshot(path="/tmp/ci-chromium-smoke.png")
    b.close()
print("✅ كروم يفتح ويرسم")
PYEOF
