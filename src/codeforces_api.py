from __future__ import annotations

from typing import Any

import pandas as pd
import requests

API_URL = "https://codeforces.com/api/user.rating"
DEFAULT_TIMEOUT_SECONDS = 15
MIN_HANDLE_LENGTH = 3
MAX_HANDLE_LENGTH = 24


class CodeforcesAPIError(RuntimeError):
    """Raised when rating history cannot be retrieved from Codeforces."""


def _error_message(payload: dict[str, Any], handle: str) -> str:
    comment = str(payload.get("comment", "Unknown Codeforces API error."))
    lowered = comment.lower()

    if "not found" in lowered or "user with handle" in lowered:
        return f"Codeforces handle '{handle}' was not found."
    if "limit" in lowered and ("call" in lowered or "request" in lowered):
        return "Codeforces API rate limit reached. Please wait a moment and try again."

    return f"Codeforces API error: {comment}"


def _validate_handle(handle: str) -> str:
    clean_handle = handle.strip()
    if not clean_handle:
        raise CodeforcesAPIError("A Codeforces handle is required.")
    if not MIN_HANDLE_LENGTH <= len(clean_handle) <= MAX_HANDLE_LENGTH:
        raise CodeforcesAPIError(
            f"Codeforces handles must contain between {MIN_HANDLE_LENGTH} and "
            f"{MAX_HANDLE_LENGTH} characters."
        )
    return clean_handle


def fetch_rating_history(handle: str) -> pd.DataFrame:
    """Fetch a user's rated-contest history and return a normalized DataFrame."""
    clean_handle = _validate_handle(handle)

    try:
        response = requests.get(
            API_URL,
            params={"handle": clean_handle},
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.Timeout as exc:
        raise CodeforcesAPIError("The Codeforces request timed out. Try again.") from exc
    except requests.ConnectionError as exc:
        raise CodeforcesAPIError(
            "Could not reach the Codeforces API. Check your connection and try again."
        ) from exc
    except requests.RequestException as exc:
        raise CodeforcesAPIError("The Codeforces request failed. Please try again.") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        try:
            response.raise_for_status()
        except requests.RequestException as http_exc:
            raise CodeforcesAPIError(
                f"Codeforces returned HTTP {response.status_code}. Please try again."
            ) from http_exc
        raise CodeforcesAPIError("Codeforces returned an invalid response.") from exc

    if payload.get("status") != "OK":
        raise CodeforcesAPIError(_error_message(payload, clean_handle))

    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CodeforcesAPIError(
            f"Codeforces returned HTTP {response.status_code}. Please try again."
        ) from exc

    rows = payload.get("result", [])
    normalized = []
    for contest_number, item in enumerate(rows, start=1):
        normalized.append(
            {
                "contest_number": contest_number,
                "contest_id": item.get("contestId"),
                "contest_name": item.get("contestName", "Unknown contest"),
                "rank": item.get("rank"),
                "old_rating": item.get("oldRating"),
                "rating": item.get("newRating"),
                "rating_change": (
                    item.get("newRating", 0) - item.get("oldRating", 0)
                    if item.get("newRating") is not None
                    and item.get("oldRating") is not None
                    else None
                ),
                "rating_update_time": pd.to_datetime(
                    item.get("ratingUpdateTimeSeconds"), unit="s", utc=True
                ),
            }
        )

    return pd.DataFrame(normalized)
