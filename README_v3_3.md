
#🌸 GitHub Repository Info

macro-market-intelligence-pipeline


# 🌐 Macro & Market Intelligence Pipeline (v3.3)

> **Built from signals to insights — a macro intelligence pipeline by Audrey Yang🦊.**

![Architecture Cover](report_assets/Cover.png)

---

## 🚀 Overview
This project automates the process of collecting, analyzing, and summarizing macroeconomic signals from multiple data sources — including **Polymarket**, **EDGAR filings**, and public **macro indicators** (VIX, DXY, UST10Y).  
It produces a **weekly Markdown + HTML report** featuring an AI-generated “Executive Summary 2.0,” which compresses market data into one-line macro insights.

---

## 🧠 Key Features
| Layer | Description |
|-------|--------------|
| **Ingest** | Fetch data from RSS feeds, EDGAR, Yahoo Finance & Polymarket (Gamma API). |
| **Process** | Normalize / clean / NER / aggregate event features (CAPEX, themes). |
| **Macro** | Calculate rolling correlations (SPX–DXY–UST10Y) and VIX percentiles. |
| **Summary Engine** | Generate **Executive Summary 2.0** — natural-language macro outlook. |
| **Report** | Produce Markdown → HTML reports with charts and architecture cover. |
| **Automation** | Single bash script (`run_weekly_with_macro.sh`) for end-to-end execution. |

---

## 🧩 Architecture
```bash
wind_demo_v3_3
├── config/                  # YAML configs
├── data/                    # raw → staging → macro → warehouse
├── ingest/                  # RSS, EDGAR, Polymarket modules
├── process/                 # normalization & feature extraction
├── macro/                   # macro signal fetch & analysis
├── report/                  # summary generation & HTML render
├── scripts/                 # automation & scheduler scripts
└── report_assets/           # figures & cover images




Description (short):

Automated macroeconomic intelligence pipeline integrating Polymarket, EDGAR, and financial indicators — from signals to insights.

data-engineering, cloud, ai, macroeconomics, edgar, polymarket, vix, 
pipeline, airflow, duckdb, report-automation, python, data-visualization


Run:
```bash
cd  macro-marcket-intelligence-pipeline

# 1️⃣ Install dependencies
pip install -r requirements.txt

# 2️⃣ Run the full weekly pipeline

cd wind_demo_v3_2
chmod +x scripts/*.sh

python3 scripts/render_summary_v3.py
bash scripts/run_weekly_min.sh

# 3️⃣ View generated report
open report_out/ai_chips_weekly_YYYY-MM-DD.html
```

Artifacts:
- `data/macro/polymarket_live.csv`
- `report_out/ai_chips_weekly_YYYY-MM-DD.md` (+ auto-injected Executive Summary 2.0) and `.html`
- `report_assets/polymarket_trend.png`


## Executive Summary 2.0 (Example)
High VIX percentile + diverging SPX–DXY correlation + 68 % rate-cut probability → Macro Caution Ahead.



## Report View
Description
Data Source Distribution — RSS & EDGAR breakdown by relevance.
Event Themes — clustering of economic topics & sentiment density.
Cumulative CAPEX — capital expenditure trends by sector.
Weekly Report HTML Snapshot — final rendered output.




![Macro Pipeline Architecture](report_assets/architecture.png)
![Macro Pipeline Macro](report_assets/Macro.png)
![Macro Pipeline Orchestration](report_assets/Orchestration.png)
![Macro Pipeline Micro](report_assets/Micro.png)




## 🧭 Tech Stack

Python 3.12, pandas, yfinance, requests, matplotlib, yaml, duckdb (ready)
Orchestration: bash + cron / future Airflow support
Storage: CSV → Parquet (DuckDB compatible)

🪄 Future Enhancements
	•	Integration with DuckDB Lakehouse & Airflow scheduler
	•	Sector-level analysis (AI chips / energy / RWA trends)
	•	Trade Conflict Heat Score visual dashboard
	•	Macro forecasting using time-series models
	
	
	
## 💬 About the Author

Audrey Yang — Data Engineer / Cloud Engineer with a focus on AI-driven financial intelligence systems.
From signals to insights. 💙



Topic:
data-engineering, cloud, ai, macroeconomics, edgar, polymarket, vix, 
pipeline, airflow, duckdb, report-automation, python, data-visualization




![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Build-Passing-brightgreen)