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

