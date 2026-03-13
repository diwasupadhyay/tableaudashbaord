import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def parse_dates(df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def parse_numeric_column(series: pd.Series) -> pd.Series:
    # Supports values like "1,234.56" and "45,06" by normalizing separators.
    s = series.astype("string").str.strip()
    has_dot = s.str.contains("\\.", regex=True, na=False)
    has_comma = s.str.contains(",", regex=False, na=False)

    both = has_dot & has_comma
    comma_only = (~has_dot) & has_comma

    s = s.where(~both, s.str.replace(",", "", regex=False))
    s = s.where(~comma_only, s.str.replace(",", ".", regex=False))

    return pd.to_numeric(s, errors="coerce")


def clean_superstore(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    # Rename known variants to expected names.
    rename_map = {
        "order_date": "order_date",
        "ship_date": "ship_date",
        "sales": "sales",
        "profit": "profit",
        "quantity": "quantity",
        "discount": "discount",
        "order_id": "order_id",
        "customer_id": "customer_id",
        "customer_name": "customer_name",
        "segment": "segment",
        "category": "category",
        "sub_category": "sub_category",
        "region": "region",
        "state": "state",
        "city": "city",
    }

    for col in list(rename_map.keys()):
        if col not in df.columns:
            continue

    df = parse_dates(df, ["order_date", "ship_date"])

    # Remove full duplicates.
    before = len(df)
    df = df.drop_duplicates().copy()
    dropped_duplicates = before - len(df)

    # Standard numeric coercion.
    for col in ["sales", "profit", "quantity", "discount", "shipping_cost"]:
        if col in df.columns:
            df[col] = parse_numeric_column(df[col])

    # Fill numeric nulls with robust defaults.
    for col in ["sales", "profit", "quantity", "discount"]:
        if col in df.columns:
            if col in ["sales", "profit"]:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(0)

    # Fill categorical nulls.
    for col in ["segment", "category", "sub_category", "region", "state", "city", "customer_id", "order_id"]:
        if col in df.columns:
            df[col] = df[col].astype("string").fillna("Unknown")

    # Drop rows without order date because time analysis requires it.
    if "order_date" in df.columns:
        df = df[df["order_date"].notna()].copy()

    # Feature engineering.
    if "ship_date" in df.columns and "order_date" in df.columns:
        df["shipping_delay_days"] = (df["ship_date"] - df["order_date"]).dt.days
    else:
        df["shipping_delay_days"] = np.nan

    if "sales" in df.columns and "profit" in df.columns:
        df["profit_margin"] = np.where(df["sales"].abs() > 1e-9, df["profit"] / df["sales"], np.nan)
    else:
        df["profit_margin"] = np.nan

    if "order_date" in df.columns:
        df["order_year"] = df["order_date"].dt.year
        df["order_month"] = df["order_date"].dt.month
        df["order_quarter"] = df["order_date"].dt.to_period("Q").astype(str)
        df["year_month"] = df["order_date"].dt.to_period("M").astype(str)

    if "customer_id" in df.columns and "sales" in df.columns:
        clv = df.groupby("customer_id", dropna=False)["sales"].sum()
        df["customer_lifetime_sales"] = df["customer_id"].map(clv)

    if "customer_id" in df.columns and "order_date" in df.columns:
        order_counts = df.groupby("customer_id", dropna=False)["order_date"].transform("count")
        df["returning_customer"] = (order_counts > 1).astype(int)

    df.attrs["dropped_duplicates"] = dropped_duplicates
    return df


def create_monthly_metrics(df: pd.DataFrame) -> pd.DataFrame:
    required = ["order_date", "sales", "profit"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for monthly metrics: {missing}")

    monthly = (
        df.groupby(pd.Grouper(key="order_date", freq="MS"))
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique") if "order_id" in df.columns else ("sales", "size"),
            customers=("customer_id", "nunique") if "customer_id" in df.columns else ("sales", "size"),
        )
        .reset_index()
        .sort_values("order_date")
    )

    monthly["avg_order_value"] = np.where(monthly["orders"] > 0, monthly["sales"] / monthly["orders"], np.nan)
    monthly["profit_margin"] = np.where(monthly["sales"].abs() > 1e-9, monthly["profit"] / monthly["sales"], np.nan)
    monthly["sales_mom_growth_pct"] = monthly["sales"].pct_change() * 100.0

    return monthly


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean Superstore-like data and generate analytics tables.")
    parser.add_argument("--input", required=True, help="Path to raw CSV, TSV, or XLSX file")
    parser.add_argument("--outdir", default="data_processed", help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    suffix = input_path.suffix.lower()

    if suffix in [".xlsx", ".xls"]:
        df_raw = pd.read_excel(input_path)
    elif suffix in [".tsv", ".txt"]:
        df_raw = pd.read_csv(input_path, sep="\t", encoding="utf-8")
    else:
        try:
            df_raw = pd.read_csv(input_path, encoding="utf-8")
        except UnicodeDecodeError:
            df_raw = pd.read_csv(input_path, encoding="latin1")

    cleaned = clean_superstore(df_raw)
    monthly = create_monthly_metrics(cleaned)

    cleaned_path = outdir / "sales_cleaned.csv"
    monthly_path = outdir / "monthly_metrics.csv"
    quality_log_path = outdir / "data_quality_log.txt"

    cleaned.to_csv(cleaned_path, index=False)
    monthly.to_csv(monthly_path, index=False)

    dropped_duplicates = cleaned.attrs.get("dropped_duplicates", 0)
    with open(quality_log_path, "w", encoding="utf-8") as f:
        f.write("Data Quality Log\n")
        f.write(f"Input rows: {len(df_raw)}\\n")
        f.write(f"Output rows: {len(cleaned)}\\n")
        f.write(f"Dropped full duplicates: {dropped_duplicates}\\n")
        f.write(f"Columns: {', '.join(cleaned.columns)}\\n")

    print(f"Saved cleaned data to: {cleaned_path}")
    print(f"Saved monthly metrics to: {monthly_path}")
    print(f"Saved quality log to: {quality_log_path}")


if __name__ == "__main__":
    main()
