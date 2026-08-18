from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ForecastResult:
    fitted: pd.DataFrame
    future: pd.DataFrame
    slope: float
    intercept: float
    r_squared: float


def _predict(x: np.ndarray, slope: float, intercept: float) -> np.ndarray:
    return intercept + slope * np.log2(x)


def build_forecast(history: pd.DataFrame, future_contests: int = 20) -> ForecastResult:
    """Fit logarithmic regression to historical ratings and project the fitted trend."""
    if future_contests < 1:
        raise ValueError("future_contests must be at least 1")
    if len(history) < 2:
        raise ValueError("At least two historical ratings are required")

    x = history["contest_number"].to_numpy(dtype=float)
    y = history["rating"].to_numpy(dtype=float)

    slope, intercept = np.polyfit(np.log2(x), y, 1)
    historical_prediction = _predict(x, slope, intercept)

    residual_sum_squares = float(np.sum((y - historical_prediction) ** 2))
    total_sum_squares = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = (
        1.0 - residual_sum_squares / total_sum_squares
        if total_sum_squares > 0
        else 1.0
    )

    fitted = pd.DataFrame(
        {
            "contest_number": history["contest_number"].astype(int),
            "fitted_rating": historical_prediction,
        }
    )

    last_contest = int(history["contest_number"].iloc[-1])
    future_x = np.arange(last_contest + 1, last_contest + future_contests + 1)
    future = pd.DataFrame(
        {
            "contest_number": future_x,
            "projected_rating": _predict(future_x.astype(float), slope, intercept),
        }
    )

    return ForecastResult(
        fitted=fitted,
        future=future,
        slope=float(slope),
        intercept=float(intercept),
        r_squared=float(r_squared),
    )
