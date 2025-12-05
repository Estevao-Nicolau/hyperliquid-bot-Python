from __future__ import annotations

from pathlib import Path

from src.services.shared.runner import main


if __name__ == "__main__":
    default_dir = Path("bots/5m")
    raise SystemExit(main(default_dir, service_timeframe="5m"))
