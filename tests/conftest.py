from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def synthetic_prices(tmp_path):
    """A synthetic sample constructed only for tests, not result reporting."""
    rng = np.random.default_rng(17)
    days = pd.bdate_range("2018-01-01", periods=160)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(days))))
    df = pd.DataFrame({
        "Date": days,
        "Close": close,
        "High": close * 1.012,
        "Low": close * 0.988,
        "Volume": rng.integers(100_000, 2_000_000, len(days)),
    })
    path = tmp_path / "prices.csv"
    df.to_csv(path, index=False)
    return path
