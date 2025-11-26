"""
Model persistence utilities.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)


def save_model(model: Any, metadata: Dict[str, Any], explicit_path: Optional[str] = None) -> str:
    """
    Persist a trained model artifact on disk and write metadata alongside it.
    """

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    model_path = Path(explicit_path) if explicit_path else MODELS_DIR / f"model_{timestamp}.pkl"
    meta_path = model_path.with_suffix(".json")

    joblib.dump(model, model_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return str(model_path)


def load_model(model_id: str) -> Optional[Any]:
    """
    Load a model given its identifier (absolute path or basename under models/).
    """

    path = Path(model_id)
    if not path.is_absolute():
        path = MODELS_DIR / path

    if not path.exists():
        return None

    return joblib.load(path)
