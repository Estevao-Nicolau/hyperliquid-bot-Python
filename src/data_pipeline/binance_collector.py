"""
Binance historical collector for BTC 15m candles.

Fetches klines from Binance once and stores them in MongoDB so we do not need
to hit the exchange repeatedly.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from .collector import save_candles_to_mongo  # Reuse existing Mongo helper

BINANCE_BASE_URL = "https://api.binance.com"
SYMBOL_PAIR = "BTCUSDT"
SYMBOL = "BTC"
TIMEFRAME = "15m"
INTERVAL = "15m"
MAX_LIMIT = 1000
CHUNK_MS = MAX_LIMIT * 15 * 60 * 1000  # ~10.4 days per request


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


async def fetch_binance_klines(
    client: httpx.AsyncClient, start_ts: int, end_ts: int
) -> List[List[Any]]:
    params = {
        "symbol": SYMBOL_PAIR,
        "interval": INTERVAL,
        "limit": MAX_LIMIT,
        "startTime": start_ts,
        "endTime": end_ts,
    }
    resp = await client.get(f"{BINANCE_BASE_URL}/api/v3/klines", params=params, timeout=30.0)
    resp.raise_for_status()
    return resp.json()


def _normalize_candles(raw: List[List[Any]]) -> List[Dict[str, Any]]:
    candles = []
    for entry in raw:
        open_time = int(entry[0])
        candles.append(
            {
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME,
                "open_time": open_time,
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5]),
                "close_time": int(entry[6]),
                "source": "binance",
                "exchange_symbol": SYMBOL_PAIR,
            }
        )
    return candles


async def collect_binance_history(
    start_date: str, end_date: Optional[str] = None, throttle: float = 0.2
) -> int:
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date) if end_date else datetime.now(tz=timezone.utc)

    start_ts = int(start_dt.timestamp() * 1000)
    end_ts = int(end_dt.timestamp() * 1000)

    total_candles = 0
    total_upserts = 0
    current = start_ts

    async with httpx.AsyncClient() as client:
        while current < end_ts:
            chunk_end = min(current + CHUNK_MS, end_ts)
            raw = await fetch_binance_klines(client, current, chunk_end)
            if not raw:
                current = chunk_end + 1
                await asyncio.sleep(throttle)
                continue

            candles = _normalize_candles(raw)
            total_candles += len(candles)
            total_upserts += save_candles_to_mongo(candles)

            current = int(raw[-1][6]) + 1  # move past last close time
            await asyncio.sleep(throttle)

    print(
        f"Collected {total_candles} Binance candles, {total_upserts} upserts "
        f"(range: {start_dt.isoformat()} — {end_dt.isoformat()})"
    )
    return total_upserts


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Binance BTC 15m collector")
    parser.add_argument("--start-date", required=True, help="ISO date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="ISO date (optional, defaults to now UTC)")
    parser.add_argument("--throttle", type=float, default=0.2, help="Sleep (s) between calls")
    args = parser.parse_args()

    asyncio.run(
        collect_binance_history(
            start_date=args.start_date, end_date=args.end_date, throttle=args.throttle
        )
    )


if __name__ == "__main__":
    main()
