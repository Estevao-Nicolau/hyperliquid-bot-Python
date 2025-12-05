#!/usr/bin/env bash
set -euo pipefail
uv run src/services/grid_5m/main.py "$@"
