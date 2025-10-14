import os, re, json, pandas as pd
from datetime import datetime, timedelta

OUT_JSON = './data/macro/trade_conflict.json'

def load_keywords(cfg_path='./config/macro.yaml'):
    import yaml
    with open(cfg_path,'r',encoding='utf-8') as f:
        cfg = yaml.safe_load(f) or {}
    kws = cfg.get('trade_keywords',[]) or []
    return [k.lower() for k in kws]

def score_from_events(events_csv='./data/warehouse/events.csv', cfg_path='./config/macro.yaml'):
    if not os.path.exists(events_csv):
        res = {"last7":0, "prev7":0, "delta_pct": None, "note":"events.csv not found"}
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        json.dump(res, open(OUT_JSON,'w'), ensure_ascii=False, indent=2)
        print("Trade heat ->", OUT_JSON); return OUT_JSON

    df = pd.read_csv(events_csv)
    if df.empty:
        res = {"last7":0, "prev7":0, "delta_pct": None, "note":"empty events.csv"}
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        json.dump(res, open(OUT_JSON,'w'), ensure_ascii=False, indent=2)
        print("Trade heat ->", OUT_JSON); return OUT_JSON

    df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
    df = df.dropna(subset=['publish_time'])
    df['title'] = df.get('title','').astype(str).fillna('') + " " + df.get('summary','').astype(str).fillna('')
    kws = load_keywords(cfg_path)
    def hit(s):
        sl = str(s).lower()
        return any(k in sl for k in kws)
    df['hit'] = df['title'].apply(hit)

    end = df['publish_time'].max().normalize()
    start_last = end - pd.Timedelta(days=6)
    start_prev = start_last - pd.Timedelta(days=7)
    last7 = df[(df['publish_time']>=start_last) & (df['publish_time']<=end) & (df['hit'])].shape[0]
    prev7 = df[(df['publish_time']>=start_prev) & (df['publish_time']<start_last) & (df['hit'])].shape[0]

    delta_pct = None
    if prev7 == 0 and last7>0:
        delta_pct = 100.0
    elif prev7>0:
        delta_pct = (last7 - prev7) / prev7 * 100.0

    res = {"last7": int(last7), "prev7": int(prev7), "delta_pct": (None if delta_pct is None else round(delta_pct,1))}
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(res, open(OUT_JSON,'w'), ensure_ascii=False, indent=2)
    print("Trade heat ->", OUT_JSON, res)
    return OUT_JSON

if __name__=='__main__':
    score_from_events()
