# Tableau Build Checklist

## Data source setup
1. Connect sales_cleaned.csv
2. Connect monthly_metrics.csv
3. Connect sales_forecast.csv
4. Ensure order_date is date type in all tables

## Calculated fields
1. Profit Margin = SUM([profit]) / SUM([sales])
2. Avg Order Value = SUM([sales]) / COUNTD([order_id])
3. Sales MoM % = (SUM([sales]) - LOOKUP(SUM([sales]), -1)) / ABS(LOOKUP(SUM([sales]), -1))

## Sheets
1. Executive KPIs
2. Sales Trend (monthly)
3. Profit Trend (monthly)
4. Category Performance
5. Sub-category Profitability
6. Region Map
7. Forecast vs Actual

## Dashboard interactions
1. Add global filters: Date, Region, Category, Segment
2. Enable Use as Filter on key charts
3. Add dynamic title by region and date
4. Configure tooltips with Sales, Profit, Margin

## QA
1. KPI totals match Python outputs
2. Date filters affect all sheets
3. Forecast starts after last actual month
4. Number formats are currency/percentage where needed
5. No null labels on map or bars
