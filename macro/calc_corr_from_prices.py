#!/usr/bin/env python3
# macro/calc_corr_from_prices.py
import os, json, sys
from pathlib import Path
import pandas as pd

OUT_DIR = Path("data/macro"); OUT_DIR.mkdir(parents=True, exist_ok=True)
JSON_OUT = OUT_DIR / "corr.json"

WIN = int(os.getenv("CORR_WINDOW", "90"))  # 90日相关性窗口

def load_local_csv(path: Path):
    if not path.exists(): return None
    try:
        df = pd.read_csv(path, parse_dates=["date"])
        if "close" not in df.columns:
            # 最后一列当 close 兜底
            df.rename(columns={df.columns[-1]:"close"}, inplace=True)
        return df.sort_values("date")
    except Exception:
        return None

def fetch_yf(ticker):
    try:
        import yfinance as yf
    except ImportError:
        return None
    df = yf.Ticker(ticker).history(period="2y")[["Close"]]
    if df.empty: return None
    df = df.reset_index().rename(columns={"Date":"date","Close":"close"})
    return df

def get_series(name, primary, fallback=None, local=None):
    # 1) local csv 优先（如果你提供了）
    if local and local.exists():
        df = load_local_csv(local)
        if df is not None: 
            print(f"[corr] using local {name} -> {local}")
            return df
    # 2) yfinance
    df = fetch_yf(primary)
    if df is None and fallback:
        df = fetch_yf(fallback)
    if df is not None:
        print(f"[corr] using yfinance {name} -> {primary if df is not None else fallback}")
    return df

def latest_corr(a: pd.Series, b: pd.Series, win: int):
    df = pd.concat([a, b], axis=1).dropna()
    if df.shape[0] < win: return None
    ret = df.pct_change().dropna()
    return round(ret.iloc[-win:].corr().iloc[0,1], 4)

def main():
    base = Path("data/prices")
    spx  = get_series("SPX", "^GSPC", None, base/"spx.csv")
    dxy  = get_series("DXY", "DX-Y.NYB", "DX=F", base/"dxy.csv")
    tnx  = get_series("TNX", "^TNX", None, base/"tnx.csv")

    corr_dxy = corr_10y = None
    if spx is not None and dxy is not None:
        corr_dxy = latest_corr(spx["close"], dxy["close"], WIN)
    if spx is not None and tnx is not None:
        corr_10y = latest_corr(spx["close"], tnx["close"], WIN)

    # 兜底：环境或固定数
    if corr_dxy is None:
        try: corr_dxy = float(os.getenv("CORR_SPX_DXY", "-0.4"))
        except: corr_dxy = -0.4
    if corr_10y is None:
        try: corr_10y = float(os.getenv("CORR_SPX_10Y", "-0.3"))
        except: corr_10y = -0.3

    out = {"spx_dxy": float(corr_dxy), "spx_10y": float(corr_10y)}
    JSON_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[corr] wrote {JSON_OUT} -> {out}")

if __name__ == "__main__":
    main()