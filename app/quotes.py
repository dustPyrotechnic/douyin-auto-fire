from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date, datetime
from typing import Any
from urllib.request import urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.config import ConfigError


QUOTE_DATA_URL = "https://raw.githubusercontent.com/mudroljub/programming-quotes-api/master/data/quotes.json"
_REQUEST_TIMEOUT_SECONDS = 15


class QuoteError(ConfigError):
    """编程名言数据不可用。"""


def fetch_daily_quote(
    timezone_name: str,
    *,
    today: date | None = None,
    opener: Callable[..., Any] = urlopen,
) -> str:
    """获取当前任务日期对应的编程名言。"""
    if today is None:
        try:
            today = datetime.now(ZoneInfo(timezone_name)).date()
        except ZoneInfoNotFoundError as exc:
            raise QuoteError(f"任务时区无效: {timezone_name}") from exc

    try:
        with opener(QUOTE_DATA_URL, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except (OSError, TimeoutError, ValueError) as exc:
        raise QuoteError(f"获取编程名言失败: {QUOTE_DATA_URL}") from exc

    return select_daily_quote(payload, today)


def select_daily_quote(payload: object, day: date) -> str:
    """从名言数据中按日期稳定选择一条发送文本。"""
    if not isinstance(payload, list):
        raise QuoteError("编程名言数据必须是数组")

    quotes: list[tuple[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        author = item.get("author")
        if not isinstance(text, str) or not text.strip():
            continue
        if not isinstance(author, str) or not author.strip():
            continue
        quotes.append((text.strip(), author.strip()))

    if not quotes:
        raise QuoteError("没有可用的编程名言")

    text, author = quotes[day.toordinal() % len(quotes)]
    return f"{text}\n—— {author}"
