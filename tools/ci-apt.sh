#!/usr/bin/env bash
# ⏱️ WP-881 (2026-10-29) — apt على مشغّلات GitHub بمهلةٍ وإعادة، لا بلا سقف.
#
# قِيس (أكتوبر · az-video.yml): خطوةُ «تجهيز» أكلت 229 من 305 دقائق المصنع — ٨ تشغيلات علّقت
# ١٣–٢١ دقيقة داخل `apt-get update` (سجلّ الوظيفة 122437530175: بدأ 20:03:32 ولم يقرأ قاعدةَ الحزم إلّا 20:14:50)
# والعاديُّ ٢٣–٢٩ ثانية. والدقائقُ المجّانيّة 2,000 في الشهر.
# العلاج: كلُّ نداءٍ بمهلة (Acquire Timeout + timeout) ويُعاد؛ فالمرآةُ البطيئة تكلّف دقيقتين لا عشرين.
#
#   الاستعمال في سير العمل (بعد checkout):   bash tools/ci-apt.sh ffmpeg xvfb
set -u
[ "$#" -gt 0 ] || { echo "ci-apt: لا حزم"; exit 2; }
O=(-o Acquire::Retries=3 -o Acquire::http::Timeout=20 -o Acquire::https::Timeout=20 -o DPkg::Lock::Timeout=60)
upd() {
  for i in 1 2 3; do
    timeout 120 sudo apt-get "${O[@]}" update -qq && return 0
    echo "⏳ apt-get update تعثّر أو تجاوز دقيقتين — إعادة ($i/3)"; sleep 3
  done
  return 1
}
upd || echo "⚠️ apt-get update لم يكتمل — أحاول التثبيتَ بما عندي"
for i in 1 2; do
  timeout 240 sudo DEBIAN_FRONTEND=noninteractive apt-get "${O[@]}" install -y -qq "$@" && { echo "✅ ثُبّت: $*"; exit 0; }
  echo "⏳ apt-get install تعثّر — إعادة ($i/2)"; upd || true
done
echo "⛔ تعذّر تثبيت: $*"; exit 1
