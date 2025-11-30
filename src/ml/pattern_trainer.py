"""
Train separate models for each candlestick pattern using aggregated signals.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from infrastructure.db import get_mongo_db
from ml.features import INDICATOR_KEYS
from ml.model_store import save_model


def load_pattern_dataset(
    pattern: str, timeframe: Optional[str], min_samples: int
) -> Tuple[np.ndarray, np.ndarray]:
    db = get_mongo_db()
    query: Dict[str, Any] = {"pattern": pattern}
    if timeframe:
        query["timeframe"] = timeframe
    cursor = db["pattern_signals"].find(query)
    X: List[List[float]] = []
    y: List[float] = []

    for doc in cursor:
        indicators: Dict[str, float] = doc.get("indicators", {})
        if not indicators:
            continue

        features = [indicators.get(key, 0.0) for key in INDICATOR_KEYS]
        features.append(doc.get("gain_pct", 0.0))
        features.append(doc.get("stop_pct", 0.0))
        features.append(float(doc.get("lookback", 0)))
        features.append(float(doc.get("horizon", 0)))

        outcome = doc.get("outcome")
        label = 1.0 if outcome == "target" else 0.0

        X.append(features)
        y.append(label)

    if len(X) < min_samples:
        raise ValueError(f"Pattern {pattern} has insufficient samples ({len(X)})")

    return np.array(X, dtype=float), np.array(y, dtype=float)


def train_pattern_model(
    pattern: str, timeframe: Optional[str], min_samples: int
) -> Tuple[str, Dict[str, any]]:
    X, y = load_pattern_dataset(pattern, timeframe, min_samples)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, shuffle=True, stratify=y
    )

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=400,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds, output_dict=True, zero_division=0)

    metadata = {
        "pattern": pattern,
        "timeframe": timeframe or "unknown",
        "samples": int(len(X)),
        "accuracy": accuracy,
        "report": report,
    }

    model_id = save_model(pipeline, metadata)
    return model_id, metadata


def main():
    parser = argparse.ArgumentParser(description="Train per-pattern classifiers")
    parser.add_argument("--pattern", help="Specific pattern name (default: all in DB)")
    parser.add_argument("--min-samples", type=int, default=200)
    parser.add_argument("--timeframe", help="Filter pattern signals by timeframe (e.g., 5m)")
    args = parser.parse_args()

    db = get_mongo_db()
    if args.pattern:
        patterns = [args.pattern]
    else:
        patterns = sorted(db["pattern_signals"].distinct("pattern"))

    results = {}
    for pattern in patterns:
        try:
            model_id, metadata = train_pattern_model(pattern, args.timeframe, args.min_samples)
            results[pattern] = {"model_id": model_id, "accuracy": metadata["accuracy"]}
            print(f"{pattern}: model saved at {model_id} (accuracy {metadata['accuracy']:.3f})")
        except ValueError as exc:
            print(f"{pattern}: skipped ({exc})")

    print("Summary:", results)


if __name__ == "__main__":
    main()
