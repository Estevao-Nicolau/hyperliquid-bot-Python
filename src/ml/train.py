"""
Training orchestration entry points.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from . import dataset
from . import model_store


def train_model(config: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
    """
    Train a simple classifier using logistic regression.
    """

    candles = dataset.load_candles_from_mongo(
        limit=config.get("max_candles", 80000),
        symbol=config.get("symbol", "BTC"),
        timeframe=config.get("timeframe", "15m"),
    )
    X, y = dataset.build_supervised_dataset(
        candles,
        lookback=config["lookback"],
        prediction_horizon=config["prediction_horizon"],
        target_return_pct=config.get("target_return_pct", 0.003),
    )

    X_arr = np.array(X, dtype=float)
    y_arr = np.array(y, dtype=float)

    X_train, X_test, y_train, y_test = train_test_split(
        X_arr, y_arr, test_size=0.2, shuffle=False
    )

    clf = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=config.get("max_iter", 200),
                    class_weight="balanced",
                ),
            ),
        ]
    )

    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)

    accuracy = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds, output_dict=True, zero_division=0)

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lookback": config["lookback"],
        "prediction_horizon": config["prediction_horizon"],
        "target_return_pct": config.get("target_return_pct", 0.003),
        "max_candles": config.get("max_candles", 80000),
        "accuracy": accuracy,
        "report": report,
    }

    return clf, metadata


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Train ML model on 15m BTC candles")
    parser.add_argument("--lookback", type=int, default=48)
    parser.add_argument("--horizon", type=int, default=4)
    parser.add_argument("--target-return", type=float, default=0.003)
    parser.add_argument("--max-candles", type=int, default=80000)
    parser.add_argument("--symbol", type=str, default="BTC")
    parser.add_argument("--timeframe", type=str, default="15m")
    parser.add_argument("--output", type=str, help="Optional explicit model path")
    args = parser.parse_args()

    model, metadata = train_model(
        {
            "lookback": args.lookback,
            "prediction_horizon": args.horizon,
            "target_return_pct": args.target_return,
            "max_candles": args.max_candles,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
        }
    )

    model_id = model_store.save_model(model, metadata, explicit_path=args.output)

    print(f"Model saved to: {model_id}")
    print(f"Accuracy: {metadata['accuracy']:.4f}")
    print("Classification report:")
    for label, stats in metadata["report"].items():
        if label in {"accuracy", "macro avg", "weighted avg"}:
            continue
        print(
            f"  Class {label}: precision={stats['precision']:.3f} "
            f"recall={stats['recall']:.3f} f1={stats['f1-score']:.3f}"
        )


if __name__ == "__main__":
    run_cli()
