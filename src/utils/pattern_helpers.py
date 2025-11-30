from typing import Iterable, Optional

BULLISH_PATTERNS = {
    "hammer",
    "bullish_engulfing",
    "morning_star",
    "double_bottom",
    "inverse_head_and_shoulders",
    "ascending_triangle",
    "pennant",
    "triangle",
    "doji",
    "pin_bar",
}

BEARISH_PATTERNS = {
    "bearish_engulfing",
    "evening_star",
    "double_top",
    "head_and_shoulders",
    "descending_triangle",
    "hanging_man",
    "pennant_bearish",
}


def classify_pattern(pattern: Optional[str]) -> Optional[str]:
    if not pattern:
        return None
    name = pattern.lower()
    if name in BULLISH_PATTERNS:
        return "bullish"
    if name in BEARISH_PATTERNS:
        return "bearish"
    return None


def infer_bias(patterns: Iterable[str]) -> Optional[str]:
    for pattern in patterns:
        bias = classify_pattern(pattern)
        if bias:
            return bias
    return None
