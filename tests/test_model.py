import pandas as pd
import pytest

from src.model import build_forecast


def sample_history() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "contest_number": [1, 2, 3, 4, 5],
            "rating": [800, 900, 980, 1040, 1090],
        }
    )


def test_build_forecast_returns_requested_horizon() -> None:
    result = build_forecast(sample_history(), future_contests=7)

    assert len(result.future) == 7
    assert result.future.iloc[0]["contest_number"] == 6
    assert result.future.iloc[-1]["contest_number"] == 12
    assert result.r_squared <= 1.0


def test_build_forecast_rejects_short_history() -> None:
    with pytest.raises(ValueError, match="At least two"):
        build_forecast(pd.DataFrame({"contest_number": [1], "rating": [800]}))


def test_build_forecast_rejects_zero_horizon() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        build_forecast(sample_history(), future_contests=0)
