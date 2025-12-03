"""
Analyze historical candles to find the indicator/pattern context that precedes
large moves (+/-3%, +/-5%, +/-10%) within a given horizon.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from statistics import mean
from typing import Dict, List, Tuple

from ml.dataset import load_candles_from_mongo
from ml.features import compute_indicator_set
from ml.patterns import analyze_patterns

MOVE_THRESHOLDS = [0.03, 0.05, 0.10]
DEFAULT_LOOKBACK = 48
DEFAULT_HOURS = 240
DEFAULT_HORIZON = {
    "5m": 60,   # 5m * 60 = 300 min (~5h)
    "15m": 24,  # 15m * 24 = 360 min (~6h)
}


def load_recent_candles(symbol: str, timeframe: str, hours: int) -> List[Dict[str, float]]:
    candles = load_candles_from_mongo(limit=50000, symbol=symbol, timeframe=timeframe)
    if not candles:
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = [
        c
        for c in candles
        if datetime.fromtimestamp(c["open_time"] / 1000, tz=timezone.utc) >= cutoff
    ]
    if len(recent) < DEFAULT_LOOKBACK + DEFAULT_HORIZON.get(timeframe, 60):
        return candles[-(DEFAULT_LOOKBACK + DEFAULT_HORIZON.get(timeframe, 60) + 1) :]
    return recent


def analyze_momentum_context(
    symbol: str, timeframe: str, hours: int, lookback: int
) -> Dict[float, Dict[str, Dict[str, object]]]:
    candles = load_recent_candles(symbol, timeframe, hours)
    if len(candles) <= lookback:
        return {}
    horizon = DEFAULT_HORIZON.get(timeframe, 60)
    stats = {thr: {"up": [], "down": []} for thr in MOVE_THRESHOLDS}
    pattern_hits = {
        thr: {"up": defaultdict(int), "down": defaultdict(int)} for thr in MOVE_THRESHOLDS
    }

    for idx in range(lookback, len(candles) - horizon - 1):
        window = candles[idx - lookback : idx]
        indicators = compute_indicator_set(window)
        patterns = analyze_patterns(window)
        current = candles[idx]["close"]
        future = candles[idx + 1 : idx + 1 + horizon]
        high = max(c["high"] for c in future)
        low = min(c["low"] for c in future)
        up_change = (high - current) / current
        down_change = (low - current) / current
        for thr in MOVE_THRESHOLDS:
            if up_change >= thr:
                stats[thr]["up"].append(indicators)
                for name, flag in patterns.items():
                    if flag:
                        pattern_hits[thr]["up"][name] += 1
            if down_change <= -thr:
                stats[thr]["down"].append(indicators)
                for name, flag in patterns.items():
                    if flag:
                        pattern_hits[thr]["down"][name] += 1

    summary: Dict[float, Dict[str, Dict[str, object]]] = {}
    for thr in MOVE_THRESHOLDS:
        entry = {}
        for direction in ("up", "down"):
            samples = stats[thr][direction]
            if not samples:
                entry[direction] = {"count": 0}
                continue
            avg = {
                key: mean(s.get(key, 0.0) for s in samples)
                for key in samples[0].keys()
            }
            top_patterns = sorted(
                pattern_hits[thr][direction].items(), key=lambda kv: kv[1], reverse=True
            )[:5]
            entry[direction] = {
                "count": len(samples),
                "avg_rsi": avg.get("rsi_14"),
                "avg_macd": avg.get("macd"),
                "avg_volume_ratio": avg.get("volume_ratio"),
                "avg_bb_width": avg.get("bb_width"),
                "top_patterns": top_patterns,
            }
        summary[thr] = entry

    return summary


def print_summary(symbol: str, timeframe: str, summary: Dict[float, Dict[str, Dict[str, object]]]) -> None:
    print(f"\n=== {symbol} {timeframe} ===")
    if not summary:
        print("Sem dados suficientes.")
        return
    for thr, detail in summary.items():
        print(f"\nMovimentos >= {thr*100:.0f}%")
        for direction in ("up", "down"):
            info = detail.get(direction, {})
            count = info.get("count", 0)
            print(f" {direction.upper()}: {count} ocorrências")
            if not count:
                continue
            print(
                f"   RSI médio: {info.get('avg_rsi'):.2f} | MACD médio: {info.get('avg_macd'):.2f} | "
                f"Volume ratio: {info.get('avg_volume_ratio'):.3f} | BB width: {info.get('avg_bb_width'):.4f}"
            )
            top_patterns = ", ".join(
                f"{name}({hits})" for name, hits in info.get("top_patterns", [])
            )
            print(f"   Padrões recorrentes: {top_patterns if top_patterns else 'nenhum'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze momentum context for BTC.")
    parser.add_argument("--symbol", default="BTC")
    parser.add_argument("--timeframes", default="5m,15m")
    parser.add_argument("--hours", type=int, default=240, help="Número de horas recentes para analisar")
    parser.add_argument("--lookback", type=int, default=DEFAULT_LOOKBACK)
    args = parser.parse_args()

    for tf in [t.strip() for t in args.timeframes.split(",") if t.strip()]:
        summary = analyze_momentum_context(args.symbol, tf, args.hours, args.lookback)
        print_summary(args.symbol, tf, summary)


if __name__ == "__main__":
    main()

