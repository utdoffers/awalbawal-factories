#!/usr/bin/env bash
# ⏱️ WP-881 (2026-10-29) — apt على مشغّلات GitHub بمهلةٍ وإعادة، لا بلا سقف.
#
# قِيس (أكتوبر · az-video.yml): خطوةُ «تجهيز» أكلت 229 من 305 دقائق المصنع — ٨ تشغيلات علّقت
# ١٣–٢١ دقيقة داخل `apt-get update` (سجلّ الوظيفة 122437530175: بدأ 20:03:32 ولم يقرأ قاعدةَ الحزم إلّا 20:14:50)
# والعاديُّ ٢٣–٢٩ ثانية. والدقائقُ المجّانيّة 2,000 في الشهر.
# العلاج: كلُّ نداءٍ بمهلة (Acquire Timeout + timeout) ويُعاد؛ فالمرآةُ البطيئة تكلّف دقيقتين لا عشرين.
#
#   الاستعمال في سير العمل (بعد checkout):   bash tools/ci-apt.sh ffmpeg xvfb
#   🏭 WP-1037: الموجودُ مسبقًا يُتخطّى · وffmpeg له بديلٌ جاهز إذا apt ما وصل.
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
# 🏭 WP-1037 (2026-11-12): الموجودُ في صورة المشغّل ما يُطلب من apt (xvfb وخطّ الإيموجي فيها أصلًا — قِيس من runner-images)
#   (على مشغّل GitHub فقط — GITHUB_ACTIONS=true — فتجربةُ الماك بـapt مزيّف ما تتأثّر بما في جهازه)
have() { [ "${GITHUB_ACTIONS:-}" = true ] && dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"; }
NEED=()
for p in "$@"; do have "$p" && echo "✅ موجودة مسبقًا: $p" || NEED+=("$p"); done
[ "${#NEED[@]}" -gt 0 ] || exit 0
set -- "${NEED[@]}"

upd || echo "⚠️ apt-get update لم يكتمل — أحاول التثبيتَ بما عندي"
for i in 1 2; do
  timeout 240 sudo DEBIAN_FRONTEND=noninteractive apt-get "${O[@]}" install -y -qq "$@" && { echo "✅ ثُبّت: $*"; exit 0; }
  echo "⏳ apt-get install تعثّر — إعادة ($i/2)"; upd || true
done

# 🏭 WP-1037: apt ما وصل (11/11: «Temporary failure resolving 'security.ubuntu.com'» ساعتين ونصف) ⇒ ffmpeg من بديله الجاهز على GitHub نفسه
ffmpeg_static() {
  [ -z "${CI_FFMPEG_FORCE:-}" ] && command -v ffmpeg >/dev/null 2>&1 && return 0   # CI_FFMPEG_FORCE للاختبار فقط
  local dest="${CI_FFMPEG_DEST:-/usr/local/bin}"
  local u="${CI_FFMPEG_URL:-https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz}"
  local d; d="$(mktemp -d)"
  for i in 1 2; do
    if timeout 180 curl -fsSL --retry 2 --connect-timeout 20 -o "$d/f.tar.xz" "$u" && tar -xJf "$d/f.tar.xz" -C "$d"; then
      local b; b="$(find "$d" -type f -name ffmpeg -perm -u+x | head -1)"
      [ -n "$b" ] && sudo install -m 755 "$b" "$dest/ffmpeg" \
        && { local q; q="$(dirname "$b")/ffprobe"; [ -x "$q" ] && sudo install -m 755 "$q" "$dest/ffprobe"; true; } \
        && "$dest/ffmpeg" -version >/dev/null 2>&1 && { echo "✅ ffmpeg من البديل الجاهز (apt ما وصل)"; return 0; }
    fi
    echo "⏳ بديل ffmpeg تعثّر — إعادة ($i/2)"; sleep 3
  done
  return 1
}
LEFT=()
for p in "$@"; do
  if have "$p"; then continue
  elif [ "$p" = ffmpeg ] && ffmpeg_static; then continue
  else LEFT+=("$p"); fi
done
[ "${#LEFT[@]}" -eq 0 ] && { echo "✅ اكتمل التجهيز بالبديل"; exit 0; }
echo "⛔ تعذّر تثبيت: ${LEFT[*]}"; exit 1
