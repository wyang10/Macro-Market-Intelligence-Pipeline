#!/usr/bin/env python3
# macro/fetch_polymarket_to_csv.py  (resilient)
import os, csv, time, json
from pathlib import Path
import requests

OUT = Path("data/macro"); OUT.mkdir(parents=True, exist_ok=True)
CSV = OUT / "polymarket_live.csv"

PRIMARY  = "https://delta.polymarket.com/markets?limit=50"
FALLBACK = "https://polymarket.com/api/markets?limit=50"  # 备用入口，若失效可再换

def extract_prob(items):
    def one(m):
        prob = 0.0; found = False
        for o in (m.get("outcomes") or []):
            try:
                p = float(o.get("price", 0))
                if p > 0: prob += p; found = True
            except: pass
        return min(prob, 1.0) if found else None

    probs=[]
    for m in items:
        title = (m.get("question") or m.get("title") or "").lower()
        if any(k in title for k in ["cut","decrease","lower","rate"]):
            p = one(m)
            if p is not None: probs.append(p)
    if probs:
        return round(sum(probs)/len(probs), 4)
    return None

def read_last_csv():
    if CSV.exists():
        try:
            rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
            if rows:
                v = rows[-1].get("prob")
                return float(v) if v not in (None,"") else None
        except: pass
    return None

def try_fetch(url, timeout=12):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    items = data.get("markets") or data  # 兼容不同结构
    return extract_prob(items)

def main():
    prob = None
    errs = []
    for url in (PRIMARY, FALLBACK):
        try:
            prob = try_fetch(url)
            if prob is not None:
                src = url
                break
        except Exception as e:
            errs.append(f"{url}: {e}")

    if prob is None:
        # 优先用上次值，再用环境变量
        prob = read_last_csv()
        if prob is None:
            envv = os.getenv("POLYMARKET_PROB")
            try: prob = float(envv) if envv not in (None,"") else None
            except: prob = None

    # 仍然没有，就给一个温和兜底，避免空值
    if prob is None:
        prob = 0.33

    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["prob"])
        w.writeheader()
        w.writerow({"prob": prob})
    print(f"[polymarket] wrote {CSV} with prob={prob}")
    if errs:
        print("[polymarket] fallback notes:", *errs, sep="\n  - ")

if __name__ == "__main__":
    main()