# Internship portfolio summary

## English — short

**AAPL Return Forecasting | Python, pandas, scikit-learn, classical ML**

Rebuilt my first-year ML coursework into a reproducible regression benchmark on historical AAPL prices. Engineered trailing technical indicators and return lags, compared linear regression, decision trees, random forests, and gradient boosting against simple baselines, and added chronological evaluation, tests, CI, and diagnostic plots. The project emphasizes leakage prevention and honest interpretation of noisy financial forecasts rather than claiming trading profitability.

## Русский — коротко

**Прогнозирование доходности AAPL | Python, pandas, scikit-learn, классическое ML**

Переработал курсовую первого курса в воспроизводимый ML-проект: подготовка финансового датасета, генерация признаков, обучение и сравнение линейной регрессии, дерева решений, Random Forest и Gradient Boosting. Добавил хронологическое разделение данных, сравнение с простыми базовыми прогнозами, MAE/RMSE/R², автоматические тесты и CI. В исследовании отдельно разбираю ограничения прогнозирования финансовых временных рядов.

## 15-second interview explanation

> I used classical ML to study next-day stock returns. The hard part was not running a Random Forest but making the evaluation honest: split data in time order, avoid using future information, compare to trivial baselines, and interpret negative R² correctly.

## Questions I should be ready to answer

- Why is the target tomorrow's return rather than tomorrow's absolute stock price?
- Why does shuffling cause problems in time-series evaluation?
- Why are two naive baselines necessary?
- Why does feature importance not imply causality?
- What do negative R² and MAE close to the daily volatility mean?
- Why was the StandardScaler fit on training data only?
- What would a walk-forward evaluation change?
