import argparse
import subprocess
import sys


def run(cmd: list[str]) -> None:
    print("Running:", " ".join(cmd))
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full cleaning + forecasting pipeline")
    parser.add_argument("--input", required=True, help="Path to raw dataset")
    parser.add_argument("--outdir", default="data_processed", help="Output directory")
    parser.add_argument("--horizon", type=int, default=6, help="Forecast horizon in months")
    args = parser.parse_args()

    run(
        [
            sys.executable,
            "scripts/clean_data.py",
            "--input",
            args.input,
            "--outdir",
            args.outdir,
        ]
    )

    run(
        [
            sys.executable,
            "scripts/forecast.py",
            "--input",
            f"{args.outdir}/monthly_metrics.csv",
            "--out",
            f"{args.outdir}/sales_forecast.csv",
            "--horizon",
            str(args.horizon),
        ]
    )

    print("Pipeline complete.")


if __name__ == "__main__":
    main()
