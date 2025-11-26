"""
Generate pattern signal documents with outcomes for later training.
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List

from infrastructure.db import get_mongo_db
from ml.dataset import load_candles_from_mongo
from ml.features import compute_indicator_set
from ml.patterns import analyze_patterns


def evaluate_outcome(
    candles: List[Dict[str, Any]],
    entry_index: int,
    horizon: int,
    gain_pct: float,
    stop_pct: float,
) -> Dict[str, Any]:
    entry_price = candles[entry_index]["close"]
    target_up = entry_price * (1 + gain_pct)
    target_down = entry_price * (1 - stop_pct)

    future = candles[entry_index + 1 : entry_index + 1 + horizon]
    for idx, candle in enumerate(future, start=1):
        if candle["high"] >= target_up:
            return {
                "outcome": "target",
                "return": gain_pct,
                "candles_to_outcome": idx,
            }
        if candle["low"] <= target_down:
            return {
                "outcome": "stop",
                "return": -stop_pct,
                "candles_to_outcome": idx,
            }

    if not future:
        return {"outcome": "insufficient", "return": 0.0, "candles_to_outcome": 0}

    final_return = future[-1]["close"] / entry_price - 1
    return {
        "outcome": "open",
        "return": final_return,
        "candles_to_outcome": len(future),
    }


def main():
    parser = argparse.ArgumentParser(description="Snapshot pattern outcomes for ML")
    parser.add_argument("--symbol", default="BTC")
    parser.add_argument("--timeframe", default="15m")
    parser.add_argument("--lookback", type=int, default=48)
    parser.add_argument("--horizon", type=int, default=4)
    parser.add_argument("--gain", type=float, default=0.05, help="Target gain pct (0.05=5%)")
    parser.add_argument("--stop", type=float, default=0.05, help="Stop loss pct")
    parser.add_argument("--max-candles", type=int, default=120000)
    parser.add_argument("--batch", type=int, default=500)
    parser.add_argument("--replace", action="store_true", help="Drop previous pattern signals")
    args = parser.parse_args()

    db = get_mongo_db()
    collection = db["pattern_signals"]
    if args.replace:
        collection.drop()

    candles = load_candles_from_mongo(
        limit=args.max_candles,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )
    total = len(candles)
    inserted = 0
    docs: List[Dict[str, Any]] = []

    for idx in range(args.lookback, total - args.horizon):
        window = candles[idx - args.lookback : idx]
        patterns = analyze_patterns(window)
        active = {name: flag for name, flag in patterns.items() if flag}
        if not active:
            continue

        entry_index = idx - 1
        outcome = evaluate_outcome(candles, entry_index, args.horizon, args.gain, args.stop)
        indicators = compute_indicator_set(window)
        entry_candle = candles[entry_index]

        for pattern_name in active.keys():
            doc = {
                "symbol": args.symbol,
                "timeframe": args.timeframe,
                "pattern": pattern_name,
                "entry_time": entry_candle["open_time"],
                "entry_price": entry_candle["close"],
                "lookback": args.lookback,
                "horizon": args.horizon,
                "gain_pct": args.gain,
                "stop_pct": args.stop,
                "outcome": outcome["outcome"],
                "return": outcome["return"],
                "candles_to_outcome": outcome["candles_to_outcome"],
                "indicators": indicators,
            }
            docs.append(doc)

        if len(docs) >= args.batch:
            collection.insert_many(docs)
            inserted += len(docs)
            docs.clear()

    if docs:
        collection.insert_many(docs)
        inserted += len(docs)

    print(f"Inserted {inserted} pattern signal documents")


if __name__ == "__main__":
    main()
