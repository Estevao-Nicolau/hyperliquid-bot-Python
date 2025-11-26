"""
Convenience CLI to preview ML signal and launch the trading bot with ML gating enabled.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from ml.inference import evaluate_signal, print_report
from run_bot import main as bot_main


def _launch_bot(config_path: Optional[str], extra_args: Optional[list[str]] = None) -> int:
    argv_backup = sys.argv[:]
    sys.argv = ["run_bot"]
    if config_path:
        sys.argv.append(config_path)
    if extra_args:
        sys.argv.extend(extra_args)

    try:
        return asyncio.run(bot_main())
    finally:
        sys.argv = argv_backup


def main():
    parser = argparse.ArgumentParser(description="Preview ML signal and launch bot")
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to trained model .pkl (relative to models/ or absolute)",
    )
    parser.add_argument("--lookback", type=int, default=48, help="Lookback window used for model")
    parser.add_argument("--enter-threshold", type=float, default=0.6, help="Entry probability")
    parser.add_argument("--exit-threshold", type=float, default=0.4, help="Pause probability")
    parser.add_argument("--eval-interval", type=int, default=60, help="Seconds between ML evaluations")
    parser.add_argument("--only-signal", action="store_true", help="Only print signal and exit")
    parser.add_argument("--assist-mode", action="store_true", help="Run trade assistant instead of executing orders")
    parser.add_argument("--pattern-models", help="Pattern models mapping (pattern=model.pkl;...) for assist mode")
    parser.add_argument("--assist-gain", type=float, default=0.05, help="Gain target for assist mode")
    parser.add_argument("--assist-stop", type=float, default=0.05, help="Stop loss for assist mode")
    parser.add_argument("--assist-context-days", type=int, default=7, help="Context days for assist mode")
    parser.add_argument("config", nargs="?", help="Optional config path (default: auto-discover)")
    args, extra = parser.parse_known_args()

    result = evaluate_signal(args.model_path, args.lookback)
    print_report(result)

    if args.only_signal:
        return

    if args.assist_mode:
        if not args.pattern_models:
            raise ValueError("--pattern-models is required for assist mode")
        cmd = (
            f"PYTHONPATH=src ./venv/bin/uv run python -m src.tools.trade_assistant "
            f'--pattern-models "{args.pattern_models}" '
            f"--gain {args.assist_gain} --stop {args.assist_stop} "
            f"--context-days {args.assist_context_days}"
        )
        os.system(cmd)
        return

    os.environ.setdefault("ML_MODEL_PATH", args.model_path)
    os.environ.setdefault("ML_LOOKBACK", str(args.lookback))
    os.environ.setdefault("ML_ENTER_THRESHOLD", str(args.enter_threshold))
    os.environ.setdefault("ML_EXIT_THRESHOLD", str(args.exit_threshold))
    os.environ.setdefault("ML_EVAL_INTERVAL", str(args.eval_interval))

    code = _launch_bot(args.config, extra)
    sys.exit(code)


if __name__ == "__main__":
    main()
