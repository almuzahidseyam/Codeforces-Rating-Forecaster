from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.model import ForecastResult


def make_rating_chart(
    history: pd.DataFrame,
    forecast: ForecastResult,
    handle: str,
) -> go.Figure:
    """Build an interactive chart for historical ratings and projected trend."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=history["contest_number"],
            y=history["rating"],
            mode="lines+markers",
            name="Actual rating",
            customdata=history[["contest_name", "rank", "rating_change"]],
            hovertemplate=(
                "Contest #%{x}<br>"
                "%{customdata[0]}<br>"
                "Rating: %{y}<br>"
                "Rank: %{customdata[1]}<br>"
                "Change: %{customdata[2]}<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast.fitted["contest_number"],
            y=forecast.fitted["fitted_rating"],
            mode="lines",
            name="Historical trend",
            hovertemplate="Contest #%{x}<br>Trend: %{y:.0f}<extra></extra>",
        )
    )

    last_real_contest = int(history["contest_number"].iloc[-1])
    future_x = [last_real_contest] + forecast.future["contest_number"].astype(int).tolist()
    future_y = [
        float(forecast.fitted["fitted_rating"].iloc[-1])
    ] + forecast.future["projected_rating"].astype(float).tolist()

    fig.add_trace(
        go.Scatter(
            x=future_x,
            y=future_y,
            mode="lines",
            name="Projected trend",
            line={"dash": "dash"},
            hovertemplate="Contest #%{x}<br>Projection: %{y:.0f}<extra></extra>",
        )
    )

    fig.add_vline(
        x=last_real_contest,
        line_dash="dot",
        opacity=0.45,
        annotation_text="Projection starts",
        annotation_position="top left",
    )

    fig.update_layout(
        title=f"Rating history and projected trend — {handle}",
        xaxis_title="Rated contest number",
        yaxis_title="Codeforces rating",
        hovermode="x unified",
        legend_title_text="Series",
        margin={"l": 20, "r": 20, "t": 70, "b": 20},
    )

    return fig
