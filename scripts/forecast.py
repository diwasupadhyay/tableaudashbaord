import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def fit_forecast(monthly: pd.DataFrame, horizon: int = 6) -> pd.DataFrame:
    ts = monthly.copy().sort_values("order_date")
    ts = ts[["order_date", "sales"]].dropna()
    ts = ts.set_index("order_date").asfreq("MS")
    ts["sales"] = ts["sales"].interpolate()

    if len(ts) < 24:
        raise ValueError("Need at least 24 monthly points for stable seasonal forecasting.")

    split_idx = int(len(ts) * 0.8)
    train = ts.iloc[:split_idx]
    test = ts.iloc[split_idx:]

    model = ExponentialSmoothing(
        train["sales"],
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    )
    fit = model.fit(optimized=True, use_brute=True)

    test_pred = fit.forecast(len(test))
    mae = mean_absolute_error(test["sales"], test_pred)
    mape = (np.abs((test["sales"] - test_pred) / test["sales"].replace(0, np.nan))).mean() * 100.0

    # Refit on full history for forward forecast.
    full_model = ExponentialSmoothing(
        ts["sales"],
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    )
    full_fit = full_model.fit(optimized=True, use_brute=True)
    future_pred = full_fit.forecast(horizon)

    # Naive confidence bounds from residual spread.
    resid_std = np.std(full_fit.resid)
    z = 1.96
    lower = future_pred - z * resid_std
    upper = future_pred + z * resid_std

    out = pd.DataFrame(
        {
            "order_date": future_pred.index,
            "forecast_sales": future_pred.values,
            "forecast_lower_95": lower.values,
            "forecast_upper_95": upper.values,
            "model": "Holt-Winters Additive",
            "mae": mae,
            "mape": mape,
        }
    )

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate monthly sales forecast from monthly_metrics.csv")
    parser.add_argument("--input", default="data_processed/monthly_metrics.csv", help="Path to monthly metrics CSV")
    parser.add_argument("--out", default="data_processed/sales_forecast.csv", help="Path to forecast output CSV")
    parser.add_argument("--horizon", type=int, default=6, help="Forecast horizon in months")
    args = parser.parse_args()

    monthly = pd.read_csv(args.input)
    monthly["order_date"] = pd.to_datetime(monthly["order_date"], errors="coerce")

    forecast = fit_forecast(monthly, horizon=args.horizon)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    forecast.to_csv(out_path, index=False)

    print(f"Saved forecast to: {out_path}")
    print(f"Model MAE: {forecast['mae'].iloc[0]:.2f}")
    print(f"Model MAPE: {forecast['mape'].iloc[0]:.2f}%")


if __name__ == "__main__":
    main()
