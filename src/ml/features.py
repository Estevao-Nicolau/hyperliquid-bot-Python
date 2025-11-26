"""
Feature engineering helpers.
"""

from __future__ import annotations

from typing import Dict, List, Any

import numpy as np

INDICATOR_KEYS = [
    "ema_12",
    "ema_26",
    "ema_ratio",
    "rsi_14",
    "macd",
    "atr_14",
    "bb_upper",
    "bb_lower",
    "bb_width",
]


def _ema(values: List[float], period: int) -> float:
    if len(values) < period:
        return values[-1]
    weights = np.exp(np.linspace(-1.0, 0.0, period))
    weights /= weights.sum()
    return float(np.dot(values[-period:], weights))


def _rsi(values: List[float], period: int = 14) -> float:
    if len(values) < period + 1:
        return 50.0
    deltas = np.diff(values[-(period + 1) :])
    gains = np.maximum(deltas, 0)
    losses = np.abs(np.minimum(deltas, 0))
    avg_gain = gains.mean()
    avg_loss = losses.mean()
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _macd(values: List[float]) -> float:
    if len(values) < 26:
        return 0.0
    ema12 = _ema(values, 12)
    ema26 = _ema(values, 26)
    return ema12 - ema26


def _atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    trs = []
    for i in range(-period, 0):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i - 1] if i - 1 >= -len(closes) else closes[i]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    return float(np.mean(trs)) if trs else 0.0


def _bollinger(values: List[float], period: int = 20) -> Dict[str, float]:
    if len(values) < period:
        return {"bb_upper": values[-1], "bb_lower": values[-1], "bb_width": 0.0}
    window = values[-period:]
    mean_val = np.mean(window)
    std_val = np.std(window)
    upper = mean_val + 2 * std_val
    lower = mean_val - 2 * std_val
    width = (upper - lower) / max(1e-9, mean_val)
    return {"bb_upper": float(upper), "bb_lower": float(lower), "bb_width": float(width)}


def compute_indicator_set(candles: List[Dict[str, Any]]) -> Dict[str, float]:
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]

    indicators: Dict[str, float] = {}
    indicators["ema_12"] = _ema(closes, 12)
    indicators["ema_26"] = _ema(closes, 26)
    indicators["ema_ratio"] = indicators["ema_12"] / max(1e-9, indicators["ema_26"])
    indicators["rsi_14"] = _rsi(closes, 14)
    indicators["macd"] = _macd(closes)
    indicators["atr_14"] = _atr(highs, lows, closes, 14)
    bollinger = _bollinger(closes, 20)
    indicators.update(bollinger)
    # Ensure ordering for downstream consumers
    return {key: indicators[key] for key in INDICATOR_KEYS}
