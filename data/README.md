# Local-only datasets

**Do not commit real datasets or personal files here.** The public repository
intentionally ships without stock-price data or the university PDF.

Download an appropriate AAPL daily OHLCV dataset from a licensed source and
save it as `data/AAPL_stock_2015_2025.csv`. The original university coursework
cites this source:

https://www.kaggle.com/datasets/saibhossain/apple-aapl-stock-prices-20152025

Expected columns: `Date,Close,High,Low,Volume` (other columns allowed).
Ticker/metadata rows containing an invalid date are ignored by the loader.
For valid dated rows, malformed values cause an explicit error.

To generate **synthetic smoke-test data** instead (never treat it as actual AAPL data):

```bash
python scripts/create_demo_csv.py
```
