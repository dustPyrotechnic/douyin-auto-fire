from __future__ import annotations

import io
import json
from datetime import date

import pytest

from app.quotes import QuoteError, fetch_daily_quote, select_daily_quote


class _Response:
    def __init__(self, payload: object) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> io.BytesIO:
        return io.BytesIO(self._body)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None


def test_select_daily_quote_formats_text_and_author() -> None:
    quote = select_daily_quote(
        [{"text": "Simplicity is prerequisite for reliability.", "author": "Edsger W. Dijkstra"}],
        date(2026, 10, 7),
    )

    assert quote == "Simplicity is prerequisite for reliability.\n—— Edsger W. Dijkstra"


def test_daily_quote_is_stable_for_a_date_and_changes_with_the_next_date() -> None:
    quotes = [
        {"text": "quote 0", "author": "author 0"},
        {"text": "quote 1", "author": "author 1"},
        {"text": "quote 2", "author": "author 2"},
    ]

    first = select_daily_quote(quotes, date(2026, 10, 7))
    repeated = select_daily_quote(quotes, date(2026, 10, 7))
    next_day = select_daily_quote(quotes, date(2026, 10, 8))

    assert repeated == first
    assert next_day != first


def test_fetch_daily_quote_skips_malformed_records() -> None:
    response = _Response(
        [
            {"text": "", "author": "missing text"},
            {"text": "Keep it simple.", "author": "Unknown"},
            {"text": "missing author"},
        ]
    )

    result = fetch_daily_quote(
        "Asia/Shanghai",
        today=date(2026, 10, 7),
        opener=lambda url, *, timeout: response,
    )

    assert result == "Keep it simple.\n—— Unknown"


def test_select_daily_quote_rejects_empty_or_invalid_data() -> None:
    with pytest.raises(QuoteError, match="没有可用的编程名言"):
        select_daily_quote([], date(2026, 10, 7))

    with pytest.raises(QuoteError, match="必须是数组"):
        select_daily_quote({"text": "not an array"}, date(2026, 10, 7))
