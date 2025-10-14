#!/usr/bin/env python3
# scripts/emit_metrics_adapter.py
import os, json, argparse, math
from pathlib import Path
import csv

def safe_num(v, default=None):
    try:
        if v is None: return default
        if isinstance(v, str):
            v = v.strip().replace('%','')
            if v == "": return default
            v = float(v)
        if isinstance(v, float) and (v != v):  # NaN
            return default
        return float(v)
    except Exception:
        return default

def load_from_json(path: Path, key: str):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        # 支持嵌套 key（如 a.b.c）
        cur = data
        for k in key.split('.'):
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return None
        return cur
    except Exception:
        return None

def load_from_csv(path: Path, column: str, agg:str="last"):
    try:
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        if not rows: return None
        if agg == "last":
            v = rows[-1].get(column)
        elif agg == "mean":
            vals = [safe_num(r.get(column)) for r in rows if safe_num(r.get(column)) is not None]
            v = sum(vals)/len(vals) if vals else None
        else:
            v = rows[-1].get(column)
        return v
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser(description="Emit metrics.json for LumiereX")
    ap.add_argument("--out", default="out/metrics.json")
    # 文件来源
    ap.add_argument("--rate-cut", help="path to JSON/CSV with rate-cut odds")
    ap.add_argument("--rate-cut-key", default="rate_cut_odds", help="JSON key or CSV column")
    ap.add_argument("--vix", help="path to JSON/CSV with vix percentile")
    ap.add_argument("--vix-key", default="vix_pctile", help="JSON key or CSV column")
    ap.add_argument("--corr", help="path to JSON/CSV with correlations (expects spx_dxy / spx_10y)")
    ap.add_argument("--corr-dxy-key", default="corr_spx_dxy")
    ap.add_argument("--corr-10y-key", default="corr_spx_10y")
    # 环境变量覆盖
    ap.add_argument("--from-env", action="store_true", help="prefer environment variables if present")
    # CSV 聚合策略（可选）
    ap.add_argument("--csv-agg", default="last", choices=["last","mean"])
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def pick_num(env_key, file_path, key):
        # 1) env 优先（若指定 --from-env）
        if args.from_env:
            v_env = os.getenv(env_key)
            num = safe_num(v_env) if v_env is not None else None
            if num is not None: return num
        # 2) 文件
        if file_path:
            p = Path(file_path)
            if p.suffix.lower() in [".json"]:
                num = safe_num(load_from_json(p, key))
            elif p.suffix.lower() in [".csv"]:
                num = safe_num(load_from_csv(p, key, agg=args.csv_agg))
            else:
                num = None
            if num is not None: return num
        # 3) env 兜底
        v_env = os.getenv(env_key)
        num = safe_num(v_env) if v_env is not None else None
        return num

    def pick_str(env_key, default=None):
        v = os.getenv(env_key)
        return v if v not in (None, "") else default

    metrics = {
      "rate_cut_odds": pick_num("RATE_CUT_ODDS", args.rate_cut, args.rate_cut_key),
      "vix_pctile":    pick_num("VIX_PCTILE", args.vix, args.vix_key),
      "corr_spx_dxy":  pick_num("CORR_SPX_DXY", args.corr, args.corr_dxy_key),
      "corr_spx_10y":  pick_num("CORR_SPX_10Y", args.corr, args.corr_10y_key),
      "stance":        pick_str("STANCE", "Neutral")
    }

    # 将 None 正常写出，渲染端会显示 N/A
    out_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[emit_metrics_adapter] wrote ->", out_path)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()