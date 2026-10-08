import numpy as np
import pandas as pd
import pytest

from aapl_forecasting.data import (
    FEATURE_COLUMNS,
    chronological_split,
    create_features,
    load_prices,
)


def test_loader_and_features(synthetic_prices):
    prices = load_prices(synthetic_prices)
    frame = create_features(prices)
    assert len(frame) == 160 - 20  # first 19 rolling rows + final label row
    assert not frame.isna().any().any()
    assert set(FEATURE_COLUMNS).issubset(frame.columns)
    first = frame.iloc[0]
    prices_index = prices.set_index("Date")
    idx = prices_index.index.get_loc(first["Date"])
    expected = (
        prices_index.iloc[idx + 1]["Close"] / prices_index.iloc[idx]["Close"] - 1
    ) * 100
    assert first["Target"] == pytest.approx(expected)


def test_chronological_boundary(synthetic_prices):
    frame = create_features(load_prices(synthetic_prices))
    train, test = chronological_split(frame)
    assert train["Date"].max() < test["Date"].min()
    assert train.index.max() + 2 == test.index.min()
    assert len(test) > 10


def test_extra_ticker_row_ignored(synthetic_prices, tmp_path):
    csv = tmp_path / "prices_with_header.csv"
    original = synthetic_prices.read_text(encoding="utf-8")
    header, data = original.split("\n", 1)
    csv.write_text(header + "\nTicker,AAPL,AAPL,AAPL,AAPL\n" + data, encoding="utf-8")
    prices = load_prices(csv)
    assert len(prices) == 160
    assert prices.attrs["ignored_non_data_rows"] == 1


def test_reject_invalid_dated_row(synthetic_prices, tmp_path):
    bad = pd.read_csv(synthetic_prices)
    bad.loc[0, "Close"] = np.nan
    dest = tmp_path / "bad.csv"
    bad.to_csv(dest, index=False)
    with pytest.raises(ValueError, match="invalid values"):
        load_prices(dest)
