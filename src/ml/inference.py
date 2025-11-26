"""
Quick CLI to inspect latest candles and model prediction.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

from infrastructure.db import get_mongo_db
from ml.dataset import _window_features  # type: ignore
from ml.model_store import load_model, MODELS_DIR
from ml.patterns import analyze_patterns


def fetch_recent_candles(limit: int = 60) -> List[Dict[str, Any]]:
    db = get_mongo_db()
    cursor = (
        db["candles"]
        .find(
            {"symbol": "BTC", "timeframe": "15m"},
            projection={"_id": 0, "open_time": 1, "open": 1, "high": 1, "low": 1, "close": 1},
            sort=[("open_time", -1)],
            limit=limit,
        )
    )
    candles = list(cursor)
    candles.reverse()
    return candles


def load_features(candles: List[Dict[str, Any]], lookback: int) -> List[float]:
    window = candles[-lookback:]
    return _window_features(window)


def evaluate_signal(model_path: str, lookback: int) -> Dict[str, Any]:
    candles = fetch_recent_candles(limit=max(lookback + 5, 80))
    features = load_features(candles, lookback)
    patterns = analyze_patterns(candles[-lookback:])

    path = Path(model_path)
    if not path.is_absolute():
        path = (MODELS_DIR / path).resolve()

    model = load_model(str(path))
    if model is None:
        raise FileNotFoundError(f"Model not found: {path}")

    proba = model.predict_proba(np.array([features]))[0][1]
    sentiment = "ALTA" if proba >= 0.6 else "BAIXA" if proba <= 0.4 else "NEUTRA"
    recommendation = (
        "Considerar entrada (com confirmação e gestão de risco)."
        if proba >= 0.6
        else "Evitar novas posições / proteger ordens existentes."
        if proba <= 0.4
        else "Aguardar mais confirmações."
    )

    active_patterns = [name.replace("_", " ").title() for name, value in patterns.items() if value]

    return {
        "probability": float(proba),
        "sentiment": sentiment,
        "patterns": active_patterns,
        "recommendation": recommendation,
    }


def print_report(result: Dict[str, Any]) -> None:
    proba = result["probability"]
    sentiment = result["sentiment"]
    print(f"Probabilidade de retorno >= alvo: {proba:.1%} ({sentiment})")

    if result["patterns"]:
        print("Padrões detectados: " + ", ".join(result["patterns"]))
    else:
        print("Sem padrões fortes no momento.")

    print("Recomendação: " + result["recommendation"])


def main():
    parser = argparse.ArgumentParser(description="Inspect latest pattern/model signal")
    parser.add_argument("--model-path", required=True, help="Path to trained model .pkl")
    parser.add_argument("--lookback", type=int, default=48, help="Lookback used during training")
    args = parser.parse_args()

    result = evaluate_signal(args.model_path, args.lookback)
    print_report(result)


if __name__ == "__main__":
    main()
