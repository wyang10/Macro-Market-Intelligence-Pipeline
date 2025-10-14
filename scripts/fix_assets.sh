#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${1:-$(pwd)}"
OUT_DIR="${ROOT_DIR}/report_out"
ASSET_DIR="${OUT_DIR}/report_assets"
mkdir -p "${ASSET_DIR}"

CANDIDATES=(
  "${ROOT_DIR}/report_assets/architecture.png"
  "${ROOT_DIR}/report_assets/architecture.jpeg"
  "${ROOT_DIR}/architecture.png"
  "${ROOT_DIR}/architecture.jpeg"
)
FOUND=""
for f in "${CANDIDATES[@]}"; do [[ -f "$f" ]] && { FOUND="$f"; break; }; done
[[ -z "$FOUND" ]] && { echo "[fix_assets] warn: no architecture image"; exit 0; }

ext="${FOUND##*.}"
base="architecture.${ext}"
cp -f "$FOUND" "${ASSET_DIR}/${base}"

latest_html="$(ls -t "${OUT_DIR}"/ai_chips_weekly_*.html 2>/dev/null | head -n1 || true)"
[[ -n "$latest_html" ]] && sed -i.bak "s#report_assets/architecture\.png#report_assets/${base}#g" "$latest_html" || true
echo "[fix_assets] ok -> ${ASSET_DIR}/${base}"