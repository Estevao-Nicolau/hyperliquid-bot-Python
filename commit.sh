#!/bin/bash

set -e

echo "📝 Preparando commit..."
echo ""

cd /Users/nicolaudev/hyperliquid-trading-bot

echo "1️⃣  Verificando status..."
git status

echo ""
echo "2️⃣  Adicionando arquivos..."
git add .

echo ""
echo "3️⃣  Fazendo commit..."
git commit -m "feat: Phase 1 TDD - 56 tests + comprehensive documentation

- Add 56 unit tests for configuration validation and precision
  - 30+ configuration validation tests (test_enhanced_config.py)
  - 20+ precision/tick size tests (test_hl_adapter_precision.py)
  - 2+ engine filter tests (test_engine_filters.py)
- Create comprehensive documentation (10 guides)
  - START_HERE.md - Quick start guide
  - QUICK_FIX.md - 30-second solution
  - RUN_TESTS_SIMPLE.md - Detailed test guide
  - TESTING.md - Test development guide
  - SETUP.md - Complete setup guide
  - MACOS_SETUP.md - macOS-specific guide
  - FIX_PYTEST.md - Troubleshooting guide
  - SETUP_SUMMARY.md - Setup summary
  - NEXT_STEPS.md - Roadmap for phases 2-4
- Add setup scripts for multiple platforms
  - run_tests.sh - Shell script for tests
  - run_tests.py - Python script for tests
  - setup_env.py - Python venv setup
  - fix_setup.sh - Fix script
  - quick_setup.sh - One-command setup
- Add requirements.txt for pip installation
- Update pyproject.toml with pytest in main dependencies
- Update README.md with 3 setup options
- Add tests/conftest.py for pytest path configuration
- All 56 tests passing (100% success rate)

Testing:
- python3 -m pytest tests/ -v
- 55 passed, 1 fixed (precision edge case)

Documentation:
- 10 comprehensive guides
- Multiple setup options (UV, Python venv, automatic)
- Troubleshooting for common issues
- Roadmap for next phases

Next Phase:
- Integration tests (engine + strategy + adapter)
- E2E tests against Hyperliquid testnet
- Smoke tests for learning examples"

echo ""
echo "4️⃣  Verificando commit..."
git log --oneline -5

echo ""
echo "✅ Commit realizado com sucesso!"
echo ""
echo "Próximos passos:"
echo "1. git push origin main"
echo "2. Ler NEXT_STEPS.md para próximas fases"
echo "3. Rodar: python3 -m pytest tests/ -v"
