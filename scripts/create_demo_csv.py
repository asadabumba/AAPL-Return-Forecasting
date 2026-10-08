"""Make entirely synthetic OHLCV data for smoke tests, never benchmark claims."""

from pathlib import Path

import numpy as np
import pandas as pd


def write_demo(path: str | Path, rows: int = 320) -> None:
    rng = np.random.default_rng(2026)
    dates = pd.bdate_range("2018-01-01", periods=rows)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.018, rows)))
    spread = rng.uniform(0.002, 0.03, rows)
    high = close * (1 + spread)
    low = close * (1 - spread)
    frame = pd.DataFrame({
        "Date": dates,
        "Close": close,
        "High": high,
        "Low": low,
        "Volume": rng.integers(100_000, 2_000_000, rows),
    })
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(dest, index=False)
    print(f"Created SYNTHETIC sample: {dest} ({rows} rows)")


if __name__ == "__main__":
    write_demo("data/demo_synthetic.csv")
