"""Data ingestion and time-safe feature creation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

FEATURE_COLUMNS = (
    "MA5_ratio",
    "MA20_ratio",
    "Pct_change",
    "Range",
    "Lag1",
    "Lag2",
    "Lag3",
    "Volume",
)


def load_prices(path: str | Path) -> pd.DataFrame:
    """Load a CSV with Date, Close, High, Low, and Volume.

    Some exported price files have one or two extra ticker/header rows.
    Rows with an unparseable date are removed, but malformed numeric rows
    with a valid date cause a hard error instead of being silently excluded.
    """
    raw = pd.read_csv(path, dtype=str)
    if "Date" not in raw.columns and "Price" in raw.columns:
        raw = raw.rename(columns={"Price": "Date"})

    required = ("Date", "Close", "High", "Low", "Volume")
    missing = sorted(set(required) - set(raw.columns))
    if missing:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")

    raw["Date"] = pd.to_datetime(raw["Date"], format="mixed", errors="coerce", utc=True)
    ignored = int(raw["Date"].isna().sum())
    prices = raw.loc[raw["Date"].notna(), list(required)].copy()
    if prices.empty:
        raise ValueError("No valid dated price observations were found")

    for column in ("Close", "High", "Low", "Volume"):
        prices[column] = pd.to_numeric(prices[column], errors="coerce")
    if prices[["Close", "High", "Low", "Volume"]].isna().any().any():
        raise ValueError("Numeric OHLCV data contains missing or invalid values")
    if (prices["Close"] <= 0).any() or (prices["High"] < prices["Low"]).any():
        raise ValueError("Prices must be positive and High must be >= Low")
    if (prices["Volume"] < 0).any():
        raise ValueError("Volume must not be negative")
    if prices["Date"].duplicated().any():
        raise ValueError("Duplicate dates found; review the input data")

    prices = prices.sort_values("Date").reset_index(drop=True)
    prices.attrs["ignored_non_data_rows"] = ignored
    return prices


def create_features(prices: pd.DataFrame) -> pd.DataFrame:
    """Features use data available by the current day's closing time.

    The label is *next* trading day's percentage return, in percentage points.
    No centered rolling windows or future-valued inputs are used.
    """
    frame = prices.copy()
    close = frame["Close"]
    returns = close.pct_change() * 100
    frame["MA5_ratio"] = close / close.rolling(window=5).mean()
    frame["MA20_ratio"] = close / close.rolling(window=20).mean()
    frame["Pct_change"] = returns
    frame["Range"] = (frame["High"] - frame["Low"]) / close * 100
    for lag in range(1, 4):
        frame[f"Lag{lag}"] = returns.shift(lag)
    frame["Target"] = returns.shift(-1)
    selected = ["Date", *FEATURE_COLUMNS, "Target"]
    frame = frame[selected].replace([np.inf, -np.inf], np.nan).dropna()
    if len(frame) < 50:
        raise ValueError("Not enough rows after feature creation (at least 50 required)")
    return frame.reset_index(drop=True)


def chronological_split(
    frame: pd.DataFrame, test_fraction: float = 0.2, embargo_rows: int = 1
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Chronological holdout with a one-row gap at the train/test boundary.

    The dropped boundary observation prevents its next-day training label
    from referencing the first test observation's day.
    """
    if not 0.05 <= test_fraction <= 0.5:
        raise ValueError("test_fraction must be between 0.05 and 0.5")
    if embargo_rows < 1:
        raise ValueError("At least one embargo row is required")
    cutoff = int(len(frame) * (1 - test_fraction))
    train = frame.iloc[: cutoff - embargo_rows].copy()
    test = frame.iloc[cutoff:].copy()
    if len(train) < 30 or len(test) < 10:
        raise ValueError("Not enough observations for chronological evaluation")
    assert train["Date"].max() < test["Date"].min()
    return train, test
