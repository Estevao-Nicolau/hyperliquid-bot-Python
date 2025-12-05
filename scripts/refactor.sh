#!/bin/bash

###############################################################################
# Refactor Script - Clean up project structure
###############################################################################

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔧 Starting Project Refactorization..."
echo "📂 Root: $PROJECT_ROOT"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counter for changes
REMOVED=0
MOVED=0
CREATED=0

cleanup_and_confirm() {
    local item=$1
    local description=$2
    
    echo -e "${YELLOW}❓ $description${NC}"
    read -p "   Continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Create docs/ directory${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ ! -d "docs" ]; then
    mkdir -p docs/archive
    echo -e "${GREEN}✅ Created docs/ and docs/archive/${NC}"
    ((CREATED++))
else
    echo -e "${YELLOW}ℹ️  docs/ already exists${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: Move scripts to scripts/ directory${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

SCRIPTS_TO_MOVE=(
    "setup_env.py"
    "quick_setup.sh"
    "install_uv.sh"
    "run_tests.py"
    "run_tests.sh"
)

for script in "${SCRIPTS_TO_MOVE[@]}"; do
    if [ -f "$script" ]; then
        if cleanup_and_confirm "$script" "Move $script to scripts/"; then
            mv "$script" "scripts/$script"
            echo -e "${GREEN}✅ Moved $script${NC}"
            ((MOVED++))
        fi
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 3: Remove duplicate/obsolete scripts${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

SCRIPTS_TO_REMOVE=(
    "fix_setup.sh"
    "commit.sh"
    "do_commit.py"
    "run_bot_15m.sh"
    "run_bot_5m.sh"
)

for script in "${SCRIPTS_TO_REMOVE[@]}"; do
    if [ -f "$script" ]; then
        if cleanup_and_confirm "$script" "Remove $script (use configs in bots/ instead)"; then
            rm "$script"
            echo -e "${GREEN}✅ Removed $script${NC}"
            ((REMOVED++))
        fi
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 4: Remove duplicate environment file${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f ".env.5m" ]; then
    if cleanup_and_confirm ".env.5m" "Remove .env.5m (use YAML configs instead)"; then
        rm ".env.5m"
        echo -e "${GREEN}✅ Removed .env.5m${NC}"
        ((REMOVED++))
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 5: Remove obsolete venv directory${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ -d "venv" ]; then
    SIZE=$(du -sh venv | cut -f1)
    echo -e "${YELLOW}ℹ️  venv/ size: $SIZE (Python 3.9 - obsolete)${NC}"
    if cleanup_and_confirm "venv/" "Remove old venv/ (keep .venv with Python 3.13)"; then
        rm -rf venv
        echo -e "${GREEN}✅ Removed venv/ (freed $SIZE)${NC}"
        ((REMOVED++))
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 6: Archive old documentation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

DOCS_TO_ARCHIVE=(
    "PHASE1_SUMMARY.md"
    "SETUP_SUMMARY.md"
)

for doc in "${DOCS_TO_ARCHIVE[@]}"; do
    if [ -f "$doc" ]; then
        if cleanup_and_confirm "$doc" "Archive $doc to docs/archive/"; then
            mv "$doc" "docs/archive/$doc"
            echo -e "${GREEN}✅ Archived $doc${NC}"
            ((MOVED++))
        fi
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 7: Create consolidated documentation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if cleanup_and_confirm "docs" "Create new consolidated documentation files"; then
    
    # Create DEVELOPMENT.md
    cat > docs/DEVELOPMENT.md << 'EOF'
# Development Guidelines

## Code Style
- Follow existing patterns in the codebase
- Use type hints consistently
- Keep functions focused and single-purpose

## Architecture Patterns
- **Interface-based design** - Clear separation between business logic and implementation
- **Dependency injection** - Adapters injected into strategies and engines
- **Event-driven** - WebSocket events trigger strategy decisions
- **Async/await** - Non-blocking I/O for real-time operations

## Error Handling
- Use custom exceptions from `src/utils/exceptions.py`
- Graceful degradation for network issues
- Comprehensive logging at appropriate levels
- Clean shutdown on signals (SIGINT, SIGTERM)

## Testing Requirements
- Validate against Hyperliquid testnet
- Test all learning examples ensure they work with real API responses
- Configuration validation verify all parameters work
- Integration testing end-to-end trading workflows

## Environment Setup
**Required Environment Variables:**
```bash
# .env file
HYPERLIQUID_TESTNET_PRIVATE_KEY=0x...  # For testnet trading
HYPERLIQUID_TESTNET=true               # Enable testnet mode
```

**Development Workflow:**
1. Set up environment variables
2. Test with learning examples first
3. Configure bot with small allocation percentages
4. Validate configuration with `--validate` flag
5. Test on testnet before any mainnet deployment

## Private Key Security
- Never commit private keys to git
- Use `.env` file for local development
- Consider environment variables for CI/CD

## Running Tests
```bash
# Basic test run
python3 -m pytest tests/ -v

# With coverage
python3 -m pytest tests/ --cov=src

# Specific test file
python3 -m pytest tests/test_enhanced_config.py -v
```

EOF
    echo -e "${GREEN}✅ Created docs/DEVELOPMENT.md${NC}"
    ((CREATED++))
    
    # Create TROUBLESHOOTING.md
    cat > docs/TROUBLESHOOTING.md << 'EOF'
# Troubleshooting Guide

## Common Issues

### "No module named pytest"
```bash
python3 -m pip install pytest pytest-asyncio pytest-mock
```

### Tests not found
```bash
python3 -m pytest tests/ --collect-only
```

### Import errors
```bash
python3 -m pip install -r requirements.txt
```

### Module import issues in src/
Add to Python path:
```bash
export PYTHONPATH=src:$PYTHONPATH
```

### Precision issues with BTC orders
- BTC requires whole dollars for prices
- Size should be 5 decimal places (0.0001 minimum)
- Check `src/exchanges/hyperliquid/adapter.py` for tick size handling

### WebSocket connection issues
- Verify network connectivity
- Check Hyperliquid API status
- Ensure private key is valid
- Try testnet first

### Paper trading not working
- Set `PAPER_TRADING=true` in `.env`
- Verify `PAPER_INITIAL_BALANCE` is set
- Check logs for initialization errors

## Performance Tips

1. **Reduce grid levels** - Fewer levels = faster execution
2. **Increase polling intervals** - Reduces API calls
3. **Use paper trading first** - Test strategy before live
4. **Monitor memory** - Check for memory leaks in long runs

EOF
    echo -e "${GREEN}✅ Created docs/TROUBLESHOOTING.md${NC}"
    ((CREATED++))
    
    # Create ARCHITECTURE.md
    cat > docs/ARCHITECTURE.md << 'EOF'
# Architecture Overview

## System Components

### Core Engine (src/core/engine.py)
Main orchestrator that connects:
- Strategies to market data
- Trading signals to exchange
- Risk management enforcement
- Order lifecycle management

### Trading Strategies (src/strategies/)
Implements `TradingStrategy` interface:
- `BasicGridStrategy` - Multi-level buy/sell orders
- Extensible design for custom strategies

### Exchange Adapters (src/exchanges/)
Implements `ExchangeAdapter` interface:
- `HyperliquidAdapter` - Real DEX integration
- `PaperExchange` - Simulation for testing

### Risk Management (src/core/risk_manager.py)
Protects account with:
- Stop loss enforcement
- Take profit targeting
- Drawdown limits
- Position sizing

### Market Data (src/exchanges/hyperliquid/market_data.py)
Real-time price updates via:
- WebSocket subscriptions
- Fallback to HTTP polling
- Event-driven strategy updates

### ML Integration (src/ml/)
Optional signal gating:
- Model inference on market data
- Pattern classification
- Entry/exit probability estimation

### Configuration (src/core/enhanced_config.py)
YAML-based bot configuration:
- Account allocation
- Grid parameters
- Risk settings
- ML options

## Data Flow

```
Market Data (WebSocket)
    ↓
Strategy (generates signals)
    ↓
Risk Manager (validates)
    ↓
Exchange Adapter (executes)
    ↓
Position tracking + accounting
```

## Extension Points

### Add New Strategy
1. Implement `TradingStrategy` interface
2. Add to `STRATEGY_REGISTRY`
3. Update configuration schema

### Add New Exchange
1. Implement `ExchangeAdapter` interface
2. Add to `EXCHANGE_REGISTRY`
3. Handle authentication + order execution

### Add ML Model
1. Train model with `src/ml/pattern_trainer.py`
2. Reference in bot config
3. Service auto-loads at startup

EOF
    echo -e "${GREEN}✅ Created docs/ARCHITECTURE.md${NC}"
    ((CREATED++))
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 8: Clean Python cache${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo ""

if cleanup_and_confirm "cache" "Remove Python cache files (__pycache__, .pytest_cache)"; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    rm -rf .pytest_cache 2>/dev/null || true
    echo -e "${GREEN}✅ Cleaned Python cache${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 9: Update .gitignore${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if cleanup_and_confirm ".gitignore" "Update .gitignore to exclude venv/"; then
    if grep -q "^venv/" .gitignore; then
        echo -e "${YELLOW}ℹ️  venv/ already in .gitignore${NC}"
    else
        echo "venv/" >> .gitignore
        echo -e "${GREEN}✅ Added venv/ to .gitignore${NC}"
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Refactorization Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Summary:"
echo -e "  ${GREEN}✅ Created: $CREATED directories/files${NC}"
echo -e "  ${GREEN}→ Moved: $MOVED files${NC}"
echo -e "  ${RED}✗ Removed: $REMOVED files/directories${NC}"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Test: python3 -m pytest tests/ -v"
echo "  3. Commit: git add . && git commit -m 'refactor: clean up project structure'"
echo ""
