import json

from aapl_forecasting.experiment import run_experiment, score


def test_score_exact():
    values = score([0, 1, 2], [0, 1, 2])
    assert values["MAE_percentage_points"] == 0
    assert values["RMSE_percentage_points"] == 0
    assert values["R2"] == 1


def test_experiment_writes_artifacts(synthetic_prices, tmp_path):
    out = tmp_path / "results"
    result = run_experiment(synthetic_prices, out, "2018-01-01", "2018-12-31")
    assert result["train_rows"] > result["test_rows"]
    assert "ZeroReturnBaseline" in result["metrics"]
    assert "TrainMeanBaseline" in result["metrics"]
    assert "RandomForest" in result["metrics"]
    assert set(result["metrics"]["RandomForest"]) == {
        "MAE_percentage_points", "RMSE_percentage_points", "R2"
    }
    for filename in ("metrics.json", "predictions.csv", "forecast.png", "residuals.png", "feature_importance.png"):
        assert (out / filename).exists()
    saved = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert saved["embargo_rows"] == 1
    assert saved["best_model_by_MAE"] in (
        "LinearRegression", "DecisionTree", "RandomForest", "GradientBoosting"
    )
