#!/bin/bash

set -e

echo "🔧 Fixing Hyperliquid Trading Bot Setup"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "1️⃣  Removing old lock file..."
rm -f uv.lock
echo "✅ Lock file removed"

echo ""
echo "2️⃣  Syncing dependencies with UV..."
uv sync --force
echo "✅ Dependencies synced"

echo ""
echo "3️⃣  Verifying pytest installation..."
uv run pytest --version
echo "✅ pytest is installed"

echo ""
echo "4️⃣  Running tests..."
uv run pytest tests/test_enhanced_config.py -v --tb=short
echo "✅ Tests passed"

echo ""
echo "========================================"
echo "✅ Setup fixed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Run all tests: uv run pytest tests/ -v"
echo "2. Validate config: uv run src/run_bot.py --validate"
echo "3. Run bot: uv run src/run_bot.py bots/btc_conservative.yaml"
echo ""
