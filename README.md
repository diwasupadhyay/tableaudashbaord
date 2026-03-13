# Sales and Market Analytics Dashboard

This project builds a full analytics pipeline from raw data to dashboard-ready outputs:
- Data cleaning and transformation with Pandas
- KPI and monthly metric generation
- Time-series sales forecasting
- Tableau Public dashboard publishing

## 1. What you need to install

### Core software
1. Python 3.10+
2. VS Code
3. Tableau Public Desktop (free)
4. Git (optional)

### Python dependencies
Install from this project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Which dataset to use

Recommended dataset: Global Super Store Orders (TSV).

Reason:
- Includes sales, profit, discount, dates, categories, and geography
- Works perfectly for KPIs, trends, segmentation, and forecasting
- Commonly accepted in analytics interviews

## 3. How to get the dataset

Use this direct public source:

```text
https://raw.githubusercontent.com/plotly/datasets/master/global_super_store_orders.tsv
```

Download from terminal:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/plotly/datasets/master/global_super_store_orders.tsv" -OutFile "data_raw/global_super_store_orders.tsv"
```

## 4. Run the full pipeline

From project root:

```powershell
python scripts/run_pipeline.py --input data_raw/global_super_store_orders.tsv --outdir data_processed --horizon 6
```

This generates:
- data_processed/sales_cleaned.csv
- data_processed/monthly_metrics.csv
- data_processed/sales_forecast.csv
- data_processed/data_quality_log.txt

## 5. Build Tableau dashboard

Connect Tableau to these files:
1. data_processed/sales_cleaned.csv
2. data_processed/monthly_metrics.csv
3. data_processed/sales_forecast.csv

Create these sheets:
1. KPI cards: total sales, profit, margin, orders, customers
2. Monthly trend: sales and profit over time
3. Category and sub-category bars
4. Region map
5. Forecast chart: actual sales vs forecast with lower and upper bounds

Add filters:
- Region
- Category
- Segment
- Date range

## 6. Publish to Tableau Public

1. Sign in to Tableau Public in Tableau Desktop
2. Publish workbook
3. Copy live link
4. Add link to resume and LinkedIn

## 7. Suggested dashboard story insights

1. Top-performing regions by sales and margin
2. Loss-making sub-categories despite high sales
3. Seasonal peak months
4. Forward-looking expected sales range for the next 6 months
