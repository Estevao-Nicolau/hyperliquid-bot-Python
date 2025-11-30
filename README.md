## Extensible grid trading bot for [Hyperliquid DEX](https://hyperliquid.xyz)

> ⚠️ This software is for educational and research purposes. Trading cryptocurrencies involves substantial risk of loss. Never trade with funds you cannot afford to lose. Always thoroughly test strategies on testnet before live deployment.

This project is under active development. Feel free to submit questions, suggestions, and issues through GitHub.

You're welcome to use the best docs on Hyperliquid API via [Chainstack Developer Portal MCP server](https://docs.chainstack.com/docs/developer-portal-mcp-server).

## 🚀 Quick start

### **Prerequisites**
- [uv package manager](https://github.com/astral-sh/uv)
- Hyperliquid testnet account with testnet funds (see [Chainstack Hyperliquid faucet](https://faucet.chainstack.com/hyperliquid-testnet-faucet))

### **Installation**

```bash
# Clone the repository
git clone https://github.com/chainstacklabs/hyperliquid-trading-bot
cd hyperliquid-trading-bot

# Install dependencies using uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your Hyperliquid testnet private key
```

### **Local infrastructure (MongoDB + Redis)**

```bash
# Start Mongo + Redis with Docker
docker compose up -d mongo redis

# Shut them down when finished
docker compose down
```

Environment variables (defaults already handled in code):

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=hyperliquid_bot
REDIS_URL=redis://localhost:6379/0
```

### **Configuration**

Create your environment file:
```bash
# .env
HYPERLIQUID_TESTNET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
HYPERLIQUID_TESTNET=true
```

The bot comes with a pre-configured conservative BTC grid strategy in `bots/btc_conservative.yaml`. Review and adjust parameters as needed.

### **Running the bot**

```bash
# Auto-discover and run the first active configuration
uv run src/run_bot.py

# Validate configuration before running
uv run src/run_bot.py --validate

# Run specific configuration
uv run src/run_bot.py bots/btc_conservative.yaml

# Collect Binance historical candles once (example: from 2018 to 2024)
uv run python -m src.data_pipeline.binance_collector --start-date 2018-01-01 --end-date 2024-12-31

# Snapshot pattern outcomes (5% gain / 5% stop example)
PYTHONPATH=src uv run python -m src.data_pipeline.pattern_snapshot --lookback 48 --horizon 4 --gain 0.05 --stop 0.05 --replace

# Train dedicated models per pattern
PYTHONPATH=src uv run python -m src.ml.pattern_trainer --min-samples 200

### **ML signal helpers (opcional)**

```bash
# Treinar modelo baseline (ajuste os hiperparâmetros conforme necessário)
PYTHONPATH=src uv run python -m src.ml.train --lookback 48 --horizon 4 --target-return 0.003

# Rodar inferência rápida na última janela de candles
PYTHONPATH=src uv run python -m src.ml.inference --model-path model_YYYYMMDD-HHMMSS.pkl --lookback 48

# Lançar bot com checagem de ML + thresholds automáticos
PYTHONPATH=src uv run python -m src.tools.ml_launcher --model-path model_YYYYMMDD-HHMMSS.pkl [bots/btc_conservative.yaml]

# Assistente em tempo real (apenas recomendações, sem ordens)
PYTHONPATH=src uv run python -m src.tools.trade_assistant --pattern-models "hammer:model_hammer.pkl;engulfing:model_engulfing.pkl"
```

Para ativar o gate de ML no bot defina em `.env`:

```
ML_MODEL_PATH=models/model_YYYYMMDD-HHMMSS.pkl
ML_LOOKBACK=48
ML_ENTER_THRESHOLD=0.6
ML_EXIT_THRESHOLD=0.4
ML_EVAL_INTERVAL=60
# Se quiser mapear modelos específicos por padrão:
# ML_PATTERN_MODELS=hammer:model_hammer.pkl;engulfing:model_engulfing.pkl
# ML_PATTERN_GAIN_PCT=0.05
# ML_PATTERN_STOP_PCT=0.05
# ML_PATTERN_HORIZON=4
```

### **Paper trading / simulações sem risco**

Ative o modo paper no bot principal exportando:

```
PAPER_TRADING=true
PAPER_INITIAL_BALANCE=100  # saldo fictício em USD
```

Depois execute `uv run src/run_bot.py` normalmente. Nenhuma ordem real é enviada e o resultado fica salvo em `paper_reports/session_*.json`.

Para sessões cronometradas (ex.: 6h com US$100 e modelo de ML ativo):

```bash
PYTHONPATH=src uv run python -m src.tools.paper_session \
  --hours 6 \
  --initial-balance 100 \
  --model-path models/model_YYYYMMDD-HHMMSS.pkl
```

O comando mantém o bot rodando em paper trading pelo tempo definido e imprime um resumo final (PnL, posição aberta e caminho do relatório gerado).
```

## ⚙️ Configuration

Bot configurations use YAML format with comprehensive parameter documentation:

```yaml
# Conservative BTC Grid Strategy
name: "btc_conservative_clean"
active: true  # Enable/disable this strategy

account:
  max_allocation_pct: 10.0  # Use only 10% of account balance

grid:
  symbol: "BTC"
  levels: 10               # Number of grid levels
  price_range:
    mode: "auto"           # Auto-calculate from current price
    auto:
      range_pct: 5.0      # ±5% price range (conservative)

risk_management:
  # Exit Strategies
  stop_loss_enabled: false      # Auto-close positions on loss threshold
  stop_loss_pct: 8.0           # Loss % before closing (1-20%)
  take_profit_enabled: false   # Auto-close positions on profit threshold
  take_profit_pct: 25.0        # Profit % before closing (5-100%)
  
  # Account Protection
  max_drawdown_pct: 15.0       # Stop trading on account drawdown % (5-50%)
  max_position_size_pct: 40.0  # Max position as % of account (10-100%)
  
  # Grid Rebalancing
  rebalance:
    price_move_threshold_pct: 12.0  # Rebalance trigger

monitoring:
  log_level: "INFO"       # DEBUG/INFO/WARNING/ERROR
```

## 📚 Learning examples

Master the Hyperliquid API with standalone educational scripts:

```bash
# Authentication and connection
uv run learning_examples/01_authentication/basic_connection.py

# Market data and pricing
uv run learning_examples/02_market_data/get_all_prices.py
uv run learning_examples/02_market_data/get_market_metadata.py

# Account information
uv run learning_examples/03_account_info/get_user_state.py
uv run learning_examples/03_account_info/get_open_orders.py

# Trading operations
uv run learning_examples/04_trading/place_limit_order.py
uv run learning_examples/04_trading/cancel_orders.py

# Real-time data
uv run learning_examples/05_websockets/realtime_prices.py
```

## 🛡️ Exit strategies

The bot includes automated risk management and position exit features:

**Position-level exits:**
- **Stop loss**: Automatically close positions when loss exceeds configured percentage (1-20%)
- **Take profit**: Automatically close positions when profit exceeds configured percentage (5-100%)

**Account-level protection:**
- **Max drawdown**: Stop all trading when account-level losses exceed threshold (5-50%)
- **Position size limits**: Prevent individual positions from exceeding percentage of account (10-100%)

**Operational exits:**
- **Grid rebalancing**: Cancel orders and recreate grid when price moves outside range
- **Graceful shutdown**: Cancel pending orders on bot termination (positions preserved by default)

All exit strategies are configurable per bot and disabled by default for safety.

## 🔧 Development

### **Package management**
This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management:

```bash
uv sync              # Install/sync dependencies
uv add <package>     # Add new dependencies
uv run <command>     # Run commands in virtual environment
```

### **Testing**
All components are tested against Hyperliquid testnet:

```bash
# Test learning examples
uv run learning_examples/04_trading/place_limit_order.py

# Validate bot configuration
uv run src/run_bot.py --validate

# Run bot in testnet mode (default)
uv run src/run_bot.py
```
### **Ambiente 5m (scalper)**

Para trabalhar com o timeframe de 5 minutos:

1. **Coletar candles 5m**
   ```bash
   PYTHONPATH=src ./venv/bin/uv run python -m src.data_pipeline.binance_collector \
     --start-date 2020-01-01 --end-date 2020-04-01 \
     --timeframe 5m --interval 5m
   ```
   (repita por intervalos menores para não estourar timeout)

2. **Gerar snapshot + treinar padrões**
   ```bash
   PYTHONPATH=src ./venv/bin/uv run python -m src.data_pipeline.pattern_snapshot \
     --timeframe 5m --lookback 48 --horizon 4 --gain 0.02 --stop 0.02 --replace

   PYTHONPATH=src ./venv/bin/uv run python -m src.ml.pattern_trainer \
     --timeframe 5m --min-samples 100
   ```

3. **Treinar modelo principal 5m**
   ```bash
   PYTHONPATH=src ./venv/bin/uv run python -m src.ml.train \
     --timeframe 5m --lookback 48 --horizon 4 --target-return 0.02
   ```

4. **Configurar ambiente**
   - Use `bots/btc_scalper_5m.yaml` (ordem única, range pequeno).
   - Carregue `.env.5m` ou exporte manualmente:
     ```
     export ML_MODEL_PATH=models/model_20251127-192550.pkl
     export ML_PATTERN_MODELS=hammer=...;bearish_engulfing=... (ver `.env.5m`)
     export GRID_TAKE_PROFIT_PCT=0.02
     export GRID_STOP_LOSS_PCT=0.02
     ```

5. **Rodar o bot em 5m**
   ```bash
   PYTHONPATH=src ./venv/bin/uv run python -m src.run_bot bots/btc_scalper_5m.yaml
   ```

Para voltar ao ambiente de 15 m, basta usar `bots/btc_conservative.yaml` e o `.env` padrão.
