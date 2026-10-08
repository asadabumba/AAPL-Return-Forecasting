# Research notes: original coursework vs. new open-source experiment

## Origin

The first-year coursework was written for the course *Fundamentals of Machine Learning* at RTU MIREA (2026). It studied the prediction of the following day's AAPL percentage return from lagged returns and technical indicators. The course report discussed ID3/CART and compared Linear Regression, Decision Tree, Random Forest, and Gradient Boosting using MAE/RMSE.

## Historical report numbers are not verified reproduction

The original report presents an AAPL dataset for approximately 2015–2024. Its model-comparison table lists MAE about **1.010 percentage points** for Random Forest, slightly below the other candidate models. R² values shown in the report are negative. That means reported out-of-sample performance cannot justify a claim of strong prediction and motivates explicit naive baselines in the rewritten implementation.

We do not ship the original report here because it contains identifying academic information, signatures, and scanned pages. The original source code excerpt was formatted for print and contains line wraps unsuitable for direct execution. The rewritten code is reproducible *once the underlying input CSV is provided* but must not be represented as the exact unchanged original pipeline.

## Improvements introduced by this repository

1. Canonical time-series input validation and explicit handling of extra CSV metadata rows.
2. Feature engineering from data available by time *t*, with an explicit next-day return label.
3. Strict chronological holdout and an embargo row to avoid cross-boundary label overlap.
4. Two naive comparison baselines rather than comparing complex models against each other only.
5. R² reported alongside MAE and RMSE; clear percentage-point units.
6. Scaled linear regression using a train-fitted pipeline; trees require no scaling.
7. Deterministic seeds and saved JSON predictions/metrics.
8. Synthetic smoke-test dataset that is never passed off as market evidence.
9. Automated unit tests and GitHub Actions workflow.

## Interpretation checklist before a portfolio screenshot

- Does the actual source CSV match the reported time period and adjustment conventions?
- Is the forecasting target percentage return, not next-day absolute price?
- Is there accidental target leakage from future features or preprocessing?
- Does the model beat both the zero-return and training-mean baselines on unseen dates?
- Are the R² values positive? If not, discuss negative results rather than hiding them.
- Were hyperparameters chosen without access to the final held-out test period?

**Do not claim trading profitability from predictive error metrics.**
