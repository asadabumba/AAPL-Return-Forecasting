"""Training, baseline comparison, saved metrics, and diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from aapl_forecasting.data import (
    FEATURE_COLUMNS,
    chronological_split,
    create_features,
    load_prices,
)

matplotlib.use("Agg")

def build_models(seed: int = 42) -> dict:
    """Match the four model families used in the original coursework.

    Tree-based models do not require scaling. LinearRegression receives
    train-fitted scaling through an sklearn Pipeline (no test leakage).
    """
    return {
        "LinearRegression": make_pipeline(StandardScaler(), LinearRegression()),
        "DecisionTree": DecisionTreeRegressor(
            max_depth=4, min_samples_leaf=20, random_state=seed
        ),
        "RandomForest": RandomForestRegressor(
            n_estimators=300, max_depth=4, min_samples_leaf=20,
            random_state=seed, n_jobs=1,
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            random_state=seed,
        ),
    }


def score(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """MAE and RMSE are in percentage points, not prices or relative errors."""
    return {
        "MAE_percentage_points": round(float(mean_absolute_error(y_true, y_pred)), 6),
        "RMSE_percentage_points": round(
            float(np.sqrt(mean_squared_error(y_true, y_pred))), 6
        ),
        "R2": round(float(r2_score(y_true, y_pred)), 6),
    }


def run_experiment(
    csv_path: str | Path,
    output_dir: str | Path,
    start_date: str | None = "2015-01-01",
    end_date: str | None = "2024-12-31",
) -> dict:
    """Train four models and compare them to two simple baselines."""
    prices = load_prices(csv_path)
    ignored = prices.attrs["ignored_non_data_rows"]
    if start_date:
        prices = prices.loc[prices["Date"] >= pd.Timestamp(start_date, tz="UTC")]
    if end_date:
        prices = prices.loc[prices["Date"] <= pd.Timestamp(end_date, tz="UTC")]
    features = create_features(prices.reset_index(drop=True))
    train, test = chronological_split(features)

    x_train = train[list(FEATURE_COLUMNS)]
    y_train = train["Target"].to_numpy()
    x_test = test[list(FEATURE_COLUMNS)]
    y_test = test["Target"].to_numpy()

    predictions: dict[str, np.ndarray] = {
        "ZeroReturnBaseline": np.zeros_like(y_test),
        "TrainMeanBaseline": np.full_like(y_test, y_train.mean()),
    }
    fitted = build_models()
    for name, model in fitted.items():
        model.fit(x_train, y_train)
        predictions[name] = model.predict(x_test)

    metrics = {name: score(y_test, p) for name, p in predictions.items()}
    best_name = min(fitted, key=lambda name: metrics[name]["MAE_percentage_points"])
    baseline_best_mae = min(
        metrics[name]["MAE_percentage_points"]
        for name in ("ZeroReturnBaseline", "TrainMeanBaseline")
    )

    result = {
        "source": str(csv_path),
        "ignored_non_date_header_rows": ignored,
        "input_rows_after_date_filter": len(prices),
        "feature_rows": len(features),
        "train_rows": len(train),
        "test_rows": len(test),
        "train_last_date": train["Date"].max().date().isoformat(),
        "test_first_date": test["Date"].min().date().isoformat(),
        "test_last_date": test["Date"].max().date().isoformat(),
        "embargo_rows": 1,
        "target": "next-day close-to-close percentage return",
        "features": list(FEATURE_COLUMNS),
        "metrics": metrics,
        "best_model_by_MAE": best_name,
        "beats_best_simple_baseline_by_MAE": (
            metrics[best_name]["MAE_percentage_points"] < baseline_best_mae
        ),
        "notes": (
            "One chronological holdout, not walk-forward CV. "
            "These results do not establish trading profitability. "
            "Check R2 and simple baselines before claiming predictive signal."
        ),
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    pred = pd.DataFrame({
        "Date": test["Date"].dt.strftime("%Y-%m-%d"),
        "actual_return_pct": y_test,
        **{f"pred_{key}": val for key, val in predictions.items()},
    })
    pred.to_csv(output / "predictions.csv", index=False)

    plt.figure(figsize=(12, 4))
    plt.plot(y_test, label="Actual daily return", linewidth=1)
    plt.plot(predictions[best_name], label=best_name, linewidth=1)
    plt.axhline(0, linewidth=0.6)
    plt.title("Next-day AAPL return: chronological test set")
    plt.xlabel("Test trading-day index")
    plt.ylabel("Return (percentage points)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "forecast.png", dpi=140)
    plt.close()

    residuals = y_test - predictions[best_name]
    plt.figure(figsize=(12, 3))
    plt.plot(residuals, linewidth=0.8)
    plt.axhline(0, linewidth=0.6)
    plt.title(f"Residuals: {best_name}")
    plt.xlabel("Test trading-day index")
    plt.ylabel("Actual - predicted (pp)")
    plt.tight_layout()
    plt.savefig(output / "residuals.png", dpi=140)
    plt.close()

    forest = fitted["RandomForest"]
    importances = pd.Series(forest.feature_importances_, index=FEATURE_COLUMNS)
    plt.figure(figsize=(8, 4))
    importances.sort_values().plot.barh()
    plt.title("Random Forest feature importance (impurity-based)")
    plt.xlabel("Importance (not causality)")
    plt.tight_layout()
    plt.savefig(output / "feature_importance.png", dpi=140)
    plt.close()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="CSV with daily AAPL prices")
    parser.add_argument("--out", default="outputs", help="Output directory")
    parser.add_argument("--start", default="2015-01-01")
    parser.add_argument("--end", default="2024-12-31")
    args = parser.parse_args()
    result = run_experiment(args.csv, args.out, args.start, args.end)
    print("Results written to", args.out)
    for name, metrics in result["metrics"].items():
        print(f"{name:24} MAE={metrics['MAE_percentage_points']:.3f} pp "
              f"RMSE={metrics['RMSE_percentage_points']:.3f} pp "
              f"R2={metrics['R2']:.3f}")
    print("Beats simple baseline:", result["beats_best_simple_baseline_by_MAE"])


if __name__ == "__main__":
    main()
