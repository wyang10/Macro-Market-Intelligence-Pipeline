#!/usr/bin/env python3
import json, os, argparse, datetime
from pathlib import Path

def jload(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_num(x):
    if x is None: return None
    try: return float(x)
    except Exception: return None

def resolve_arch_asset(root: Path, outdir: Path) -> str | None:
    """
    返回报告里应该使用的架构图相对路径（优先 SVG，再 PNG/JPG）。
    搜索顺序：
      report_out/report_assets > report_assets > 项目根
    """
    candidates = [
        outdir/"report_assets/architecture.svg",
        outdir/"report_assets/architecture.png",
        outdir/"report_assets/architecture.jpg",
        outdir/"report_assets/architecture.jpeg",
        root/"report_assets/architecture.svg",
        root/"report_assets/architecture.png",
        root/"report_assets/architecture.jpg",
        root/"report_assets/architecture.jpeg",
        root/"architecture.svg",
        root/"architecture.png",
        root/"architecture.jpg",
        root/"architecture.jpeg",
    ]
    for p in candidates:
        if p.exists():
            # 确保最终都放到 report_out/report_assets 下，便于相对引用
            target = outdir/"report_assets"/p.name
            target.parent.mkdir(parents=True, exist_ok=True)
            if p != target:
                try: target.write_bytes(p.read_bytes())
                except Exception: pass
            return f"report_assets/{p.name}"
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", default="out/metrics.json")
    ap.add_argument("--events",  default="data/macro/trade_conflict.json")
    ap.add_argument("--outdir",  default="report_out")
    ap.add_argument("--title",   default="LumiereX Weekly — AI Chips / Macro Snapshot")
    ap.add_argument("--allow-na", action="store_true")
    args = ap.parse_args()

    ROOT   = Path(os.getcwd())
    OUTDIR = ROOT / args.outdir
    OUTDIR.mkdir(parents=True, exist_ok=True)

    m = jload(ROOT/args.metrics)
    req = ["rate_cut_odds","vix_pctile","corr_spx_dxy","corr_spx_10y","stance"]
    miss = [k for k in req if k not in m]
    if miss and not args.allow_na:
        raise SystemExit(f"[render] missing keys in metrics: {miss}")

    ratecut = safe_num(m.get("rate_cut_odds"))
    vixpct  = safe_num(m.get("vix_pctile"))
    corr_dx = safe_num(m.get("corr_spx_dxy"))
    corr_10 = safe_num(m.get("corr_spx_10y"))
    stance  = m.get("stance","N/A")

    ev = {}
    ev_path = ROOT/args.events
    if ev_path.exists():
        try: ev = jload(ev_path)
        except: ev = {}
    l7, p7, dp = ev.get("last7","N/A"), ev.get("prev7","N/A"), ev.get("delta_pct","N/A")

    def fmt_pct(x):   return "N/A" if x is None else f"{x*100:.1f}%"
    def fmt_num(x,n=3): return "N/A" if x is None else f"{x:.{n}f}"

    # ——— 新：解析架构图
    arch_src = resolve_arch_asset(ROOT, OUTDIR)

    as_of = datetime.date.today().isoformat()
    head = f"""<!doctype html><html><head>
<meta charset="utf-8"/>
<title>{args.title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
 body{{font-family:ui-sans-serif,system-ui;max-width:900px;margin:32px auto;line-height:1.6}}
 h1{{margin:0 0 6px}} .tag{{padding:6px 12px;border-radius:999px;background:#eee;margin-right:8px;display:inline-block}}
 .card{{border:1px solid #eee;border-radius:12px;padding:16px;margin-top:16px}}
 .arch{{background:#fafafa}}
 .arch img{{width:100%;height:auto;display:block;max-height:70vh;object-fit:contain;cursor:zoom-in;transition:transform .15s ease;image-rendering:-webkit-optimize-contrast;}}
 .arch img.zoom{{transform:scale(1.8);cursor:zoom-out;transform-origin:center center;}}
 .hint{{font-size:12px;opacity:.65;margin-top:6px}}
</style></head><body>
<h1>{args.title}</h1>
<div class="tag">{as_of}</div><div class="tag">Bias: {stance}</div>
"""

    executive = f"""
<div class="card">
  <h3>Executive Summary</h3>
  <ul>
    <li><b>Rate-cut odds:</b> {fmt_pct(ratecut)}</li>
    <li><b>VIX percentile:</b> {fmt_num(vixpct,2)}</li>
    <li><b>Corr(SPX, DXY):</b> {fmt_num(corr_dx)}</li>
    <li><b>Corr(SPX, 10Y):</b> {fmt_num(corr_10)}</li>
    <li><b>Trade events last7/prev7/Δ%:</b> {l7}/{p7}/{dp}</li>
    <li><b>Overall stance:</b> {stance}</li>
  </ul>
  <p style="color:#a52828"><i>* Educational demo — not investment advice.</i></p>
</div>
"""

    # ——— 新：Architecture 区块（有图才渲染）
    if arch_src:
        arch = f"""
<div class="card arch">
  <h3>Architecture</h3>
  <img id="archImg" src="{arch_src}" alt="architecture" loading="lazy">
  <div class="hint">点击图片放大/还原</div>
</div>
<script>
  (function(){{ const img=document.getElementById('archImg'); if(img) img.addEventListener('click',()=>img.classList.toggle('zoom')); }})();
</script>
"""
    else:
        arch = ""

    html = head + executive + arch + "\n</body></html>"
    fout = OUTDIR / f"ai_chips_weekly_{as_of}_final.html"
    fout.write_text(html, encoding="utf-8")
    print(f"[render_v3] OK -> {fout}")

if __name__ == "__main__":
    main()