"""
Pattern detection utilities for 15m BTC candles.

Each helper expects candles as dictionaries with keys:
open, high, low, close, volume (volume optional for most checks).
"""

from __future__ import annotations

from statistics import mean
from typing import Dict, List, Tuple

Candle = Dict[str, float]


def _body(candle: Candle) -> float:
    return abs(candle["close"] - candle["open"])


def _range(candle: Candle) -> float:
    return candle["high"] - candle["low"]


def _upper_shadow(candle: Candle) -> float:
    return candle["high"] - max(candle["open"], candle["close"])


def _lower_shadow(candle: Candle) -> float:
    return min(candle["open"], candle["close"]) - candle["low"]


def _trend_strength(closes: List[float]) -> float:
    if len(closes) < 2:
        return 0.0
    start, end = closes[0], closes[-1]
    return (end - start) / abs(start) if start else 0.0


def is_hammer(candle: Candle) -> bool:
    body = _body(candle)
    rng = _range(candle)
    if rng == 0:
        return False
    lower = _lower_shadow(candle)
    upper = _upper_shadow(candle)
    return lower >= body * 2 and upper <= body * 0.5 and body / rng <= 0.4


def is_hanging_man(prev_closes: List[float], candle: Candle) -> bool:
    return _trend_strength(prev_closes) > 0.03 and is_hammer(candle)


def is_doji(candle: Candle, threshold: float = 0.1) -> bool:
    rng = _range(candle)
    return rng > 0 and _body(candle) <= rng * threshold


def is_pin_bar(candle: Candle) -> bool:
    body = _body(candle)
    return (_upper_shadow(candle) >= body * 2) ^ (_lower_shadow(candle) >= body * 2)


def detect_bullish_engulfing(prev: Candle, cur: Candle) -> bool:
    return (
        prev["close"] < prev["open"]
        and cur["close"] > cur["open"]
        and cur["close"] >= prev["open"]
        and cur["open"] <= prev["close"]
        and _body(cur) > _body(prev)
    )


def detect_bearish_engulfing(prev: Candle, cur: Candle) -> bool:
    return (
        prev["close"] > prev["open"]
        and cur["close"] < cur["open"]
        and cur["open"] >= prev["close"]
        and cur["close"] <= prev["open"]
        and _body(cur) > _body(prev)
    )


def detect_morning_star(window: List[Candle]) -> bool:
    if len(window) != 3:
        return False
    first, second, third = window
    return (
        first["close"] < first["open"]
        and is_doji(second, 0.2)
        and third["close"] > third["open"]
        and third["close"] >= (first["open"] + first["close"]) / 2
    )


def detect_evening_star(window: List[Candle]) -> bool:
    if len(window) != 3:
        return False
    first, second, third = window
    return (
        first["close"] > first["open"]
        and is_doji(second, 0.2)
        and third["close"] < third["open"]
        and third["close"] <= (first["open"] + first["close"]) / 2
    )


def detect_double_bottom(closes: List[float], tolerance: float = 0.01) -> bool:
    if len(closes) < 5:
        return False
    lows = sorted(closes)[:2]
    if not lows:
        return False
    return abs(lows[0] - lows[1]) / max(1.0, abs(lows[0])) <= tolerance


def detect_double_top(closes: List[float], tolerance: float = 0.01) -> bool:
    if len(closes) < 5:
        return False
    highs = sorted(closes, reverse=True)[:2]
    if not highs:
        return False
    return abs(highs[0] - highs[1]) / max(1.0, abs(highs[0])) <= tolerance


def detect_head_and_shoulders(highs: List[float]) -> bool:
    if len(highs) < 7:
        return False
    left = max(highs[: len(highs) // 3])
    head = max(highs[len(highs) // 3 : 2 * len(highs) // 3])
    right = max(highs[2 * len(highs) // 3 :])
    return head > left and head > right and abs(left - right) / head <= 0.05


def detect_inverse_head_and_shoulders(lows: List[float]) -> bool:
    if len(lows) < 7:
        return False
    left = min(lows[: len(lows) // 3])
    head = min(lows[len(lows) // 3 : 2 * len(lows) // 3])
    right = min(lows[2 * len(lows) // 3 :])
    return head < left and head < right and abs(left - right) / abs(head) <= 0.05


def detect_triangle(highs: List[float], lows: List[float]) -> bool:
    if len(highs) < 5 or len(lows) < 5:
        return False
    upper_trend = highs[-1] - highs[0]
    lower_trend = lows[-1] - lows[0]
    return upper_trend < 0 and lower_trend > 0


def detect_ascending_triangle(highs: List[float], lows: List[float]) -> bool:
    if len(highs) < 5 or len(lows) < 5:
        return False
    return abs(max(highs) - min(highs)) <= max(highs) * 0.01 and lows[-1] > lows[0]


def detect_descending_triangle(highs: List[float], lows: List[float]) -> bool:
    if len(highs) < 5 or len(lows) < 5:
        return False
    return abs(max(lows) - min(lows)) <= max(1.0, max(lows)) * 0.01 and highs[-1] < highs[0]


def detect_flag(closes: List[float]) -> bool:
    if len(closes) < 10:
        return False
    up_move = _trend_strength(closes[:5])
    consolidation = abs(_trend_strength(closes[5:]))
    return abs(up_move) > 0.05 and consolidation < 0.01


def detect_pennant(highs: List[float], lows: List[float]) -> bool:
    if len(highs) < 6 or len(lows) < 6:
        return False
    return detect_triangle(highs[-6:], lows[-6:])


def detect_channel(highs: List[float], lows: List[float], tolerance: float = 0.02) -> bool:
    if len(highs) < 6 or len(lows) < 6:
        return False
    high_slope = (highs[-1] - highs[0]) / len(highs)
    low_slope = (lows[-1] - lows[0]) / len(lows)
    return abs(high_slope - low_slope) <= tolerance * max(1.0, abs(high_slope))


def analyze_patterns(candles: List[Candle]) -> Dict[str, bool]:
    results: Dict[str, bool] = {}
    if not candles:
        return results

    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    current = candles[-1]

    results["hammer"] = is_hammer(current)
    results["hanging_man"] = is_hanging_man(closes[:-1], current) if len(closes) > 1 else False
    results["doji"] = is_doji(current)
    if len(candles) >= 2:
        results["bullish_engulfing"] = detect_bullish_engulfing(candles[-2], current)
        results["bearish_engulfing"] = detect_bearish_engulfing(candles[-2], current)
    results["pin_bar"] = is_pin_bar(current)
    if len(candles) >= 3:
        results["morning_star"] = detect_morning_star(candles[-3:])
        results["evening_star"] = detect_evening_star(candles[-3:])
    results["double_bottom"] = detect_double_bottom(closes[-20:])
    results["double_top"] = detect_double_top(closes[-20:])
    results["head_and_shoulders"] = detect_head_and_shoulders(highs[-30:])
    results["inverse_head_and_shoulders"] = detect_inverse_head_and_shoulders(lows[-30:])
    results["triangle"] = detect_triangle(highs[-20:], lows[-20:])
    results["ascending_triangle"] = detect_ascending_triangle(highs[-20:], lows[-20:])
    results["descending_triangle"] = detect_descending_triangle(highs[-20:], lows[-20:])
    results["flag"] = detect_flag(closes[-20:])
    results["pennant"] = detect_pennant(highs[-12:], lows[-12:])
    results["channel"] = detect_channel(highs[-20:], lows[-20:])
    return results


__all__ = [
    "analyze_patterns",
    "detect_bearish_engulfing",
    "detect_bullish_engulfing",
    "detect_double_bottom",
    "detect_double_top",
    "detect_evening_star",
    "detect_morning_star",
    "detect_head_and_shoulders",
    "detect_inverse_head_and_shoulders",
    "detect_triangle",
    "detect_ascending_triangle",
    "detect_descending_triangle",
    "detect_flag",
    "detect_pennant",
    "detect_channel",
    "is_hammer",
    "is_hanging_man",
    "is_doji",
    "is_pin_bar",
]
