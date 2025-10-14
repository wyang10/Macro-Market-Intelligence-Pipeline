#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p out report_out/report_assets

echo "[min] STEP 1/3: 拉数据 & 生成 metrics.json"
# 先拉 VIX 分位 & 相关性（自动回退）
python3 macro/fetch_vix_pctile.py
python3 macro/calc_corr_from_prices.py

# 环境兜底（防止任何一项缺失）
export STANCE=${STANCE:-Cautious}
export RATE_CUT_ODDS=${RATE_CUT_ODDS:-0.35}

# 把三项整合写入 out/metrics.json
python3 scripts/emit_metrics_adapter.py \
  --vix data/macro/vix.csv --vix-key pctile \
  --corr data/macro/corr.json --corr-dxy-key spx_dxy --corr-10y-key spx_10y \
  --from-env

# STEP 3: 覆盖渲染（指定 metrics 路径；渲染前可清理旧 final，避免误看）
# rm -f report_out/ai_chips_weekly_*_final.html || true
python3 scripts/render_summary_v3.py --metrics out/metrics.json  