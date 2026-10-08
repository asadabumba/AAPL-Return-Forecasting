# Reproduced real-data experiment — curated artifacts

Results for the provided 2015–2024 AAPL CSV: see [methodology, data hash and metrics](../docs/reproduced-results.md).

- `metrics.json`: numeric metrics, dataset split and evaluation protocol.
- `model_metrics.csv`: aggregate MAE/RMSE/R² (not observations or prices).
- `forecast.png`: test-series actual return versus the best-MAE *ML* model.
- `residuals.png`: residuals of that selected model.
- `feature_importance.png`: impurity-based Random Forest feature importance.

Individual `predictions.csv` and the input CSV are intentionally not published. **These results are not evidence of profitable or reliable price forecasting.**
