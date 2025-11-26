"""
Dataset construction helpers for ML experiments.
"""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Any, Dict, List, Tuple

from infrastructure.db import get_mongo_db
from ml.patterns import analyze_patterns
from ml.features import compute_indicator_set, INDICATOR_KEYS

PATTERN_KEYS = [
    "hammer",
    "hanging_man",
    "doji",
    "bullish_engulfing",
    "bearish_engulfing",
    "pin_bar",
    "morning_star",
    "evening_star",
    "double_bottom",
    "double_top",
    "head_and_shoulders",
    "inverse_head_and_shoulders",
    "triangle",
    "ascending_triangle",
    "descending_triangle",
    "flag",
    "pennant",
    "channel",
]


def load_candles_from_mongo(
    limit: int = 50000, symbol: str = "BTC", timeframe: str = "15m"
) -> List[Dict[str, Any]]:
    """
    Load candles (ascending by time) from MongoDB for training.
    """

    db = get_mongo_db()
    cursor = (
        db["candles"]
        .find(
            {"symbol": symbol, "timeframe": timeframe},
            projection={
                "_id": 0,
                "open_time": 1,
                "open": 1,
                "high": 1,
                "low": 1,
                "close": 1,
                "volume": 1,
            },
            sort=[("open_time", 1)],
            limit=limit,
        )
    )
    return list(cursor)


def _window_features(window: List[Dict[str, Any]]) -> List[float]:
    closes = [c["close"] for c in window]
    highs = [c["high"] for c in window]
    lows = [c["low"] for c in window]
    volumes = [c.get("volume", 0.0) for c in window]

    last_close = closes[-1]
    prev_close = closes[-2] if len(closes) >= 2 else closes[-1]
    first_close = closes[0]

    body_ratios = []
    range_ratios = []
    for c in window:
        rng = max(1e-9, c["high"] - c["low"])
        body = abs(c["close"] - c["open"])
        body_ratios.append(body / max(1e-9, c["close"]))
        range_ratios.append(rng / max(1e-9, c["close"]))

    features = [
        (last_close - prev_close) / max(1e-9, prev_close),  # momentum
        (last_close - first_close) / max(1e-9, first_close),  # total return
        pstdev(closes) if len(closes) > 1 else 0.0,  # volatility
        mean(body_ratios),
        mean(range_ratios),
        volumes[-1] / max(1e-6, mean(volumes[:-1]) if len(volumes) > 1 else volumes[-1]),
    ]

    indicators = compute_indicator_set(window)
    features.extend(indicators[key] for key in INDICATOR_KEYS)

    patterns = analyze_patterns(window)
    features.extend(1.0 if patterns.get(key) else 0.0 for key in PATTERN_KEYS)
    return features


def build_supervised_dataset(
    candles: List[Dict[str, Any]],
    lookback: int,
    prediction_horizon: int,
    target_return_pct: float = 0.003,
) -> Tuple[List[List[float]], List[float]]:
    """
    Transform raw candles into supervised learning inputs/targets.
    """

    if lookback <= 1 or prediction_horizon < 1:
        raise ValueError("lookback must be >1 and prediction_horizon >=1")

    X: List[List[float]] = []
    y: List[float] = []

    total = len(candles)
    for idx in range(lookback, total - prediction_horizon):
        window = candles[idx - lookback : idx]
        if len(window) < lookback:
            continue

        feature_vector = _window_features(window)
        future_close = candles[idx + prediction_horizon - 1]["close"]
        current_close = window[-1]["close"]
        future_return = (future_close - current_close) / max(1e-9, current_close)
        label = 1.0 if future_return >= target_return_pct else 0.0

        X.append(feature_vector)
        y.append(label)

    if not X:
        raise ValueError("Not enough candles to build dataset")

    return X, y
