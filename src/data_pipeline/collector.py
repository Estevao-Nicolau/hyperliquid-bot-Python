"""
Historical data collector for BTC 15m candles.

Usage:
    uv run python -m src.data_pipeline.collector
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

from hyperliquid.info import Info
from hyperliquid.utils.error import ClientError

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from core.endpoint_router import get_endpoint_router  # noqa: E402
from infrastructure.db import get_mongo_db  # noqa: E402

SYMBOL = "BTC"
TIMEFRAME = "15m"
INTERVAL = "15m"
DEFAULT_HISTORY_DAYS = 30
MAX_CHUNK_DAYS = 30  # Avoid massive payloads per request


def _use_testnet() -> bool:
    return os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"


def _default_info_url(testnet: bool) -> str:
    return (
        "https://api.hyperliquid-testnet.xyz/info"
        if testnet
        else "https://api.hyperliquid.xyz/info"
    )


def _build_info_client() -> Info:
    testnet = _use_testnet()
    router = get_endpoint_router(testnet)
    info_url = router.get_endpoint_for_method("candles") or router.get_endpoint_for_method(
        "meta"
    )
    if not info_url:
        info_url = _default_info_url(testnet)

    base_url = info_url[:-5] if info_url.endswith("/info") else info_url
    return Info(base_url, skip_ws=True)


async def fetch_btc_15m_candles(
    start_ts: int, end_ts: int, client: Optional[Info] = None, max_retries: int = 5
) -> List[Dict[str, Any]]:
    """
    Fetch BTC 15m candles between start_ts and end_ts (timestamps in ms).
    """

    local_client = client or _build_info_client()
    loop = asyncio.get_running_loop()

    attempt = 0
    while True:
        try:
            raw_candles = await loop.run_in_executor(
                None,
                lambda: local_client.candles_snapshot(SYMBOL, INTERVAL, start_ts, end_ts),
            )
            break
        except ClientError as exc:
            attempt += 1
            if exc.status_code == 429 and attempt < max_retries:
                await asyncio.sleep(min(2**attempt, 30))
                continue
            raise
    candles: List[Dict[str, Any]] = []

    for entry in raw_candles or []:
        open_time = int(entry.get("T") or entry.get("t"))
        candles.append(
            {
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME,
                "open_time": open_time,
                "open": float(entry["o"]),
                "high": float(entry["h"]),
                "low": float(entry["l"]),
                "close": float(entry["c"]),
                "volume": float(entry["v"]),
                "close_time": int(entry.get("t", open_time)),
                "interval": entry.get("i", INTERVAL),
            }
        )

    return candles


def save_candles_to_mongo(candles: List[Dict[str, Any]]) -> int:
    """
    Upsert candles into MongoDB using (symbol,timeframe,open_time) as key.
    """

    if not candles:
        return 0

    db = get_mongo_db()
    collection = db["candles"]
    upserts = 0

    for candle in candles:
        filter_doc = {
            "symbol": candle["symbol"],
            "timeframe": candle["timeframe"],
            "open_time": candle["open_time"],
        }
        result = collection.update_one(filter_doc, {"$set": candle}, upsert=True)
        upserts += bool(result.upserted_id) or result.modified_count > 0

    return upserts


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def _chunk_ranges(start_ts: int, end_ts: int, chunk_ms: int) -> List[Tuple[int, int]]:
    ranges = []
    current = start_ts
    while current < end_ts:
        chunk_end = min(current + chunk_ms, end_ts)
        ranges.append((current, chunk_end))
        current = chunk_end + 1
    return ranges


async def collect_btc_15m_history(
    days: Optional[int] = None,
    years: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> int:
    """
    Fetch and persist BTC 15m candles for a configurable window.
    """

    end_dt = _parse_date(end_date) or datetime.now(tz=timezone.utc)
    total_days = days or 0
    if years:
        total_days += years * 365
    if total_days <= 0 and not start_date:
        total_days = DEFAULT_HISTORY_DAYS

    if start_date:
        start_dt = _parse_date(start_date)
    else:
        start_dt = end_dt - timedelta(days=total_days)

    start_ts = int(start_dt.timestamp() * 1000)
    end_ts = int(end_dt.timestamp() * 1000)

    chunk_ms = MAX_CHUNK_DAYS * 24 * 60 * 60 * 1000
    total_candles = 0
    total_upserts = 0
    client = _build_info_client()

    for chunk_start, chunk_end in _chunk_ranges(start_ts, end_ts, chunk_ms):
        candles = await fetch_btc_15m_candles(chunk_start, chunk_end, client=client)
        total_candles += len(candles)
        total_upserts += save_candles_to_mongo(candles)

    print(
        f"Collected {total_candles} candles, {total_upserts} documents upserted "
        f"(range: {start_dt.isoformat()} — {end_dt.isoformat()})"
    )
    return total_upserts


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BTC 15m candle collector")
    parser.add_argument("--days", type=int, help="Number of days to fetch")
    parser.add_argument("--years", type=int, help="Number of years to fetch")
    parser.add_argument(
        "--start-date",
        type=str,
        help="ISO date (YYYY-MM-DD) to start from (UTC). Overrides days/years.",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="ISO date (YYYY-MM-DD) to end at (UTC). Defaults to now.",
    )

    args = parser.parse_args()
    asyncio.run(
        collect_btc_15m_history(
            days=args.days,
            years=args.years,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    )
