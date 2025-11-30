"""
Runtime ML signal service for the trading engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from .dataset import load_candles_from_mongo, _window_features  # type: ignore
from .model_store import load_model, MODELS_DIR
from .patterns import analyze_patterns
from .features import compute_indicator_set, INDICATOR_KEYS
from utils.pattern_helpers import classify_pattern, infer_bias


class MLSignalService:
    def __init__(
        self,
        model_path: str,
        lookback: int,
        symbol: str = "BTC",
        timeframe: str = "15m",
        pattern_models: Dict[str, str] | None = None,
        pattern_gain_pct: float = 0.05,
        pattern_stop_pct: float = 0.05,
        pattern_horizon: int = 4,
        context_days: int = 7,
    ):
        self.lookback = lookback
        self.symbol = symbol
        self.timeframe = timeframe
        self.pattern_gain_pct = pattern_gain_pct
        self.pattern_stop_pct = pattern_stop_pct
        self.pattern_horizon = pattern_horizon
        self.context_days = context_days

        path = Path(model_path)
        if not path.is_absolute():
            path = MODELS_DIR / path

        self.model = load_model(str(path))
        if self.model is None:
            raise FileNotFoundError(f"Model not found at {path}")

        self.pattern_models: Dict[str, Any] = {}
        if pattern_models:
            for pattern, model_path in pattern_models.items():
                model = load_model(model_path if Path(model_path).is_absolute() else str((MODELS_DIR / model_path).resolve()))
                if model:
                    self.pattern_models[pattern] = model

    def evaluate_signal(self) -> Dict[str, Any]:
        candles = load_candles_from_mongo(
            limit=max(
                self.lookback + 20,
                int(self.context_days * 96) + 20,
            ),
            symbol=self.symbol,
            timeframe=self.timeframe,
        )
        if len(candles) < self.lookback:
            raise ValueError("Not enough candles to evaluate ML signal")

        window = candles[-self.lookback :]
        features = _window_features(window)
        probability = self.model.predict_proba(np.array([features]))[0][1]
        patterns = analyze_patterns(window)
        indicators = compute_indicator_set(window)
        pattern_predictions: Dict[str, float] = {}

        for pattern, model in self.pattern_models.items():
            if not patterns.get(pattern):
                continue

            vector = [indicators[key] for key in INDICATOR_KEYS]
            vector.extend(
                [
                    self.pattern_gain_pct,
                    self.pattern_stop_pct,
                    float(self.lookback),
                    float(self.pattern_horizon),
                ]
            )
            prob = model.predict_proba(np.array([vector]))[0][1]
            pattern_predictions[pattern] = float(prob)

        context_summary = self._build_context_summary(candles)
        best_pattern = (
            max(pattern_predictions, key=pattern_predictions.get)
            if pattern_predictions
            else None
        )
        pattern_bias = classify_pattern(best_pattern) or infer_bias(
            [name for name, active in patterns.items() if active]
        )

        return {
            "probability": float(probability),
            "patterns": patterns,
            "pattern_predictions": pattern_predictions,
            "timestamp": candles[-1]["open_time"],
            "context_days": self.context_days,
            "context_summary": context_summary,
            "indicator_snapshot": indicators,
            "pattern_bias": pattern_bias,
            "best_pattern": best_pattern,
        }

    def _build_context_summary(self, candles: List[Dict[str, Any]]) -> Dict[str, float]:
        ctx_len = min(len(candles), int(self.context_days * 96))
        context = candles[-ctx_len:]
        closes = [c["close"] for c in context]
        highs = [c["high"] for c in context]
        lows = [c["low"] for c in context]
        volumes = [c.get("volume", 0.0) for c in context]
        start = closes[0]
        end = closes[-1]
        total_return = (end - start) / max(1e-9, start)
        volatility = float(np.std(closes)) if len(closes) > 1 else 0.0
        avg_volume = float(np.mean(volumes)) if volumes else 0.0
        trend = "ALTA" if total_return > 0.02 else "BAIXA" if total_return < -0.02 else "LATERAL"
        return {
            "candles": ctx_len,
            "return": total_return,
            "volatility": volatility,
            "avg_volume": avg_volume,
            "high": max(highs) if highs else 0.0,
            "low": min(lows) if lows else 0.0,
            "trend": trend,
        }
