#!/usr/bin/env bash
set -euo pipefail
uv run src/services/grid_15m/main.py "$@"
