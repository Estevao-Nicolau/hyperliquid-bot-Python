#!/bin/bash
set -e
cd /Users/nicolaudev/hyperliquid-trading-bot
export $(grep -v '^#' .env.5m | xargs)
PYTHONPATH=src ./venv/bin/uv run python -m src.run_bot bots/btc_scalper_5m.yaml
