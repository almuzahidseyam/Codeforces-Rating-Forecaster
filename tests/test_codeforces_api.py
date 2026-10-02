import requests
import pytest

from src.codeforces_api import (
    CodeforcesAPIError,
    RATING_HISTORY_COLUMNS,
    fetch_rating_history,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def test_fetch_rating_history_normalizes_rows(monkeypatch) -> None:
    payload = {
        "status": "OK",
        "result": [
            {
                "contestId": 1,
                "contestName": "Sample Round",
                "rank": 42,
                "oldRating": 1000,
                "newRating": 1050,
                "ratingUpdateTimeSeconds": 1_700_000_000,
            }
        ],
    }

    monkeypatch.setattr(
        "src.codeforces_api.requests.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    history = fetch_rating_history("abc")

    assert len(history) == 1
    assert history.iloc[0]["contest_name"] == "Sample Round"
    assert history.iloc[0]["rating_change"] == 50
    assert history.iloc[0]["contest_number"] == 1


def test_fetch_rating_history_preserves_schema_for_empty_result(monkeypatch) -> None:
    payload = {"status": "OK", "result": []}
    monkeypatch.setattr(
        "src.codeforces_api.requests.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    history = fetch_rating_history("abc")

    assert history.empty
    assert tuple(history.columns) == RATING_HISTORY_COLUMNS


def test_fetch_rating_history_sorts_rows_chronologically(monkeypatch) -> None:
    payload = {
        "status": "OK",
        "result": [
            {
                "contestId": 2,
                "newRating": 1100,
                "oldRating": 1050,
                "ratingUpdateTimeSeconds": 200,
            },
            {
                "contestId": 1,
                "newRating": 1050,
                "oldRating": 1000,
                "ratingUpdateTimeSeconds": 100,
            },
        ],
    }
    monkeypatch.setattr(
        "src.codeforces_api.requests.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    history = fetch_rating_history("abc")

    assert history["contest_id"].tolist() == [1, 2]
    assert history["contest_number"].tolist() == [1, 2]


def test_fetch_rating_history_reports_missing_handle(monkeypatch) -> None:
    payload = {
        "status": "FAILED",
        "comment": "handles: User with handle missing_user not found",
    }
    monkeypatch.setattr(
        "src.codeforces_api.requests.get",
        lambda *args, **kwargs: FakeResponse(payload, status_code=400),
    )

    with pytest.raises(CodeforcesAPIError, match="was not found"):
        fetch_rating_history("missing_user")


def test_fetch_rating_history_validates_handle_length() -> None:
    with pytest.raises(CodeforcesAPIError, match="between 3 and 24"):
        fetch_rating_history("ab")


@pytest.mark.parametrize("payload", [[], {"status": "OK", "result": None}, {"status": "OK", "result": [1]}])
def test_fetch_rating_history_rejects_malformed_payload(monkeypatch, payload) -> None:
    monkeypatch.setattr(
        "src.codeforces_api.requests.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    with pytest.raises(CodeforcesAPIError, match="invalid"):
        fetch_rating_history("abc")
