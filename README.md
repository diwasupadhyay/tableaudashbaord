# Sales and Market Analytics Dashboard

Simple end-to-end analytics project using Python + Tableau.

## Live Dashboard

Tableau Public:
https://public.tableau.com/app/profile/diwas.upadhyay/viz/Sales-Market-Analytics-Dashboard/SalesMarketAnalyticsDashboard

## What This Project Does

1. Downloads and cleans sales data with Pandas
2. Creates monthly KPI tables
3. Builds a 6-month sales forecast
4. Uses output files in Tableau for dashboarding

## Dataset

Global Super Store Orders (public TSV):
https://raw.githubusercontent.com/plotly/datasets/master/global_super_store_orders.tsv

Download command:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/plotly/datasets/master/global_super_store_orders.tsv" -OutFile "data_raw/global_super_store_orders.tsv"
```

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/run_pipeline.py --input data_raw/global_super_store_orders.tsv --outdir data_processed --horizon 6
```

## Output Files

1. data_processed/sales_cleaned.csv
2. data_processed/monthly_metrics.csv
3. data_processed/sales_forecast.csv
4. data_processed/data_quality_log.txt

## Dashboard Pages

1. KPI Overview
2. Sales and Profit Trends
3. Category and Region Analysis
4. Forecast View

## Tech Stack

1. Python (Pandas, NumPy, Statsmodels)
2. Tableau Public
