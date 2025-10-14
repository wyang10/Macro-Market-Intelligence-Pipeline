#!/usr/bin/env python3
# macro/fetch_vix_pctile.py
import os
from pathlib import Path
import io, sys
import pandas as pd

OUT_DIR = Path("data/macro"); OUT_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUT = OUT_DIR / "vix.csv"

WINDOW = int(os.getenv("VIX_WINDOW", "252"))  # 1年交易日
FALLBACK_ENV = os.getenv("VIX_PCTILE")        # 可手动兜底

def pctile(series, value):
    if series.dropna().empty: return None
    return (series <= value).mean()

def fetch_stooq():
    import requests, io, pandas as pd
    url = "https://stooq.com/q/d/l/?s=%5Evix&i=d"
    r = requests.get(url, timeout=12); r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    # 统一列名大小写并兜底
    df.columns = [c.strip().lower() for c in df.columns]
    # 可能的日期/收盘列名集合
    date_col = next((c for c in ["date","data","czas"] if c in df.columns), None)
    close_col = next((c for c in ["close","zamkniecie","last"] if c in df.columns), None)
    if not date_col or not close_col:
        raise ValueError(f"unexpected stooq columns: {df.columns.tolist()}")
    df = df.rename(columns={date_col:"date", close_col:"close"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date","close"]).sort_values("date").tail(WINDOW)
    return df

def fetch_yahoo():
    try:
        import yfinance as yf
    except ImportError:
        return None
    ticker = yf.Ticker("^VIX")
    df = ticker.history(period=f"{max(WINDOW, 300)}d")[["Close"]].rename(columns={"Close":"close"})
    if df.empty: return None
    df = df.reset_index().rename(columns={"Date":"date"}).tail(WINDOW)
    return df

def main():
    df = None
    # 主源
    try:
        df = fetch_stooq()
    except Exception as e:
        print(f"[vix] stooq failed: {e}", file=sys.stderr)
    # 备源
    if df is None:
        df = fetch_yahoo()

    if df is None or df.empty:
        # 环境或固定兜底
        try:
            v = float(FALLBACK_ENV) if FALLBACK_ENV not in (None,"") else 0.3
        except Exception:
            v = 0.3
        CSV_OUT.write_text("pctile\n" + str(v) + "\n", encoding="utf-8")
        print(f"[vix] wrote {CSV_OUT} with pctile={v} (fallback)")
        return

    close = df["close"].astype(float)
    latest = close.iloc[-1]
    pct = round(pctile(close, latest), 4)
    CSV_OUT.write_text("pctile\n" + str(pct) + "\n", encoding="utf-8")
    print(f"[vix] wrote {CSV_OUT} with pctile={pct}")

if __name__ == "__main__":
    main()