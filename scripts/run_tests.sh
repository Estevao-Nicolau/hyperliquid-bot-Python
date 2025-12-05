#!/bin/bash

set -e

cd /Users/nicolaudev/hyperliquid-trading-bot

echo "🧪 Running Tests Directly"
echo "=========================="
echo ""

echo "1️⃣  Installing test dependencies..."
python3 -m pip install -q pytest pytest-asyncio pytest-mock
echo "✅ Test dependencies installed"

echo ""
echo "2️⃣  Verifying pytest..."
python3 -m pytest --version
echo "✅ pytest verified"

echo ""
echo "3️⃣  Running configuration tests..."
python3 -m pytest tests/test_enhanced_config.py -v --tb=short

echo ""
echo "4️⃣  Running precision tests..."
python3 -m pytest tests/test_hl_adapter_precision.py -v --tb=short

echo ""
echo "5️⃣  Running all tests..."
python3 -m pytest tests/ -v --tb=short

echo ""
echo "=========================="
echo "✅ All tests completed!"
echo "=========================="
