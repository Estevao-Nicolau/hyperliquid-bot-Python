"""
Binance historical collector for BTC candles (configurable timeframe).

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
MAX_LIMIT = 1000


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def interval_to_ms(interval: str) -> int:
    """
    Convert Binance interval strings (e.g., 5m, 15m, 1h) to milliseconds.
    """

    unit = interval[-1]
    value = int(interval[:-1])
    if unit == "m":
        return value * 60 * 1000
    if unit == "h":
        return value * 60 * 60 * 1000
    if unit == "d":
        return value * 24 * 60 * 60 * 1000
    raise ValueError(f"Unsupported interval: {interval}")


async def fetch_binance_klines(
    client: httpx.AsyncClient,
    start_ts: int,
    end_ts: int,
    symbol_pair: str,
    interval: str,
) -> List[List[Any]]:
    params = {
        "symbol": symbol_pair,
        "interval": interval,
        "limit": MAX_LIMIT,
        "startTime": start_ts,
        "endTime": end_ts,
    }
    resp = await client.get(f"{BINANCE_BASE_URL}/api/v3/klines", params=params, timeout=30.0)
    resp.raise_for_status()
    return resp.json()


def _normalize_candles(
    raw: List[List[Any]],
    symbol: str,
    timeframe: str,
    symbol_pair: str,
) -> List[Dict[str, Any]]:
    candles = []
    for entry in raw:
        open_time = int(entry[0])
        candles.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "open_time": open_time,
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5]),
                "close_time": int(entry[6]),
                "source": "binance",
                "exchange_symbol": symbol_pair,
            }
        )
    return candles


async def collect_binance_history(
    start_date: str,
    end_date: Optional[str] = None,
    throttle: float = 0.2,
    symbol: str = "BTC",
    symbol_pair: str = "BTCUSDT",
    timeframe: str = "15m",
    interval: str = "15m",
) -> int:
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date) if end_date else datetime.now(tz=timezone.utc)

    start_ts = int(start_dt.timestamp() * 1000)
    end_ts = int(end_dt.timestamp() * 1000)

    interval_ms = interval_to_ms(interval)
    chunk_ms = MAX_LIMIT * interval_ms
    total_candles = 0
    total_upserts = 0
    current = start_ts

    async with httpx.AsyncClient() as client:
        while current < end_ts:
            chunk_end = min(current + chunk_ms, end_ts)
            raw = await fetch_binance_klines(client, current, chunk_end, symbol_pair, interval)
            if not raw:
                current = chunk_end + 1
                await asyncio.sleep(throttle)
                continue

            candles = _normalize_candles(raw, symbol, timeframe, symbol_pair)
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
    parser.add_argument("--symbol", default="BTC", help="Asset symbol (default: BTC)")
    parser.add_argument(
        "--symbol-pair", default="BTCUSDT", help="Binance symbol pair (default: BTCUSDT)"
    )
    parser.add_argument(
        "--timeframe",
        default="15m",
        help="Timeframe label to store in Mongo (default: 15m)",
    )
    parser.add_argument(
        "--interval",
        default="15m",
        help="Binance klines interval (default: 15m). Use values like 5m, 15m, 1h.",
    )
    args = parser.parse_args()

    asyncio.run(
        collect_binance_history(
            start_date=args.start_date,
            end_date=args.end_date,
            throttle=args.throttle,
            symbol=args.symbol,
            symbol_pair=args.symbol_pair,
            timeframe=args.timeframe,
            interval=args.interval,
        )
    )


if __name__ == "__main__":
    main()
