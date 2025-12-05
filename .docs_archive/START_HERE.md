# 🚀 START HERE - Hyperliquid Trading Bot

Bem-vindo! Aqui está como começar em 3 passos.

## 3 Passos para Rodar os Testes

### Passo 1: Instalar pytest (30 segundos)

```bash
python3 -m pip install pytest pytest-asyncio pytest-mock
```

### Passo 2: Rodar os testes (1 minuto)

```bash
python3 -m pytest tests/ -v
```

### Passo 3: Ver os resultados ✅

Você deve ver algo como:

```
tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config PASSED
tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_account_max_allocation_pct_too_low PASSED
...
======================== 50+ passed in 2.34s ========================
```

## 📋 O Que Você Tem

### ✅ 50+ Testes Prontos
- **30+ testes de configuração** - Valida todas as opções do bot
- **20+ testes de precisão** - Valida arredondamento de preço/tamanho

### ✅ 3 Formas de Rodar
1. **Python direto** - `python3 -m pytest tests/ -v`
2. **Script shell** - `./run_tests.sh`
3. **Script Python** - `python3 run_tests.py`

### ✅ Documentação Completa
- [QUICK_FIX.md](QUICK_FIX.md) - Solução rápida
- [RUN_TESTS_SIMPLE.md](RUN_TESTS_SIMPLE.md) - Guia detalhado
- [TESTING.md](TESTING.md) - Desenvolvimento de testes
- [SETUP.md](SETUP.md) - Setup completo

## 🎯 Próximas Ações

Após os testes passarem:

```bash
# 1. Validar configuração
python3 src/run_bot.py --validate

# 2. Rodar bot em testnet
python3 src/run_bot.py bots/btc_conservative.yaml

# 3. Rodar exemplo
python3 learning_examples/02_market_data/get_all_prices.py
```

## 🔧 Se Algo Não Funcionar

### Problema: "No module named pytest"
```bash
python3 -m pip install pytest pytest-asyncio pytest-mock
```

### Problema: Testes não encontrados
```bash
python3 -m pytest tests/ --collect-only
```

### Problema: Erro de import
```bash
python3 -m pip install -r requirements.txt
```

## 📚 Estrutura do Projeto

```
hyperliquid-trading-bot/
├── tests/                          # 50+ testes
│   ├── test_enhanced_config.py     # Config validation
│   ├── test_hl_adapter_precision.py # Precision tests
│   └── test_engine_filters.py      # Existing tests
├── src/                            # Source code
│   ├── run_bot.py                 # Bot runner
│   ├── core/                      # Core components
│   ├── strategies/                # Trading strategies
│   ├── exchanges/                 # Exchange adapters
│   └── interfaces/                # Business logic
├── bots/                           # Bot configurations
│   ├── btc_conservative.yaml      # Conservative strategy
│   └── btc_scalper_5m.yaml        # Scalper strategy
├── learning_examples/              # Educational scripts
│   ├── 02_market_data/            # Price data
│   ├── 03_account_info/           # Account info
│   ├── 04_trading/                # Order placement
│   └── 05_websockets/             # Real-time data
└── requirements.txt                # All dependencies
```

## 🎓 Entender o Projeto

### O Bot Faz:
- ✅ Grid trading automático (compra/venda em múltiplos níveis)
- ✅ Gerenciamento de risco (stop loss, take profit, drawdown)
- ✅ Dados de mercado em tempo real (WebSocket)
- ✅ Suporte a spot e perpetuals
- ✅ Sinais de ML (opcional)

### Arquitetura:
- **Engine** - Orquestra tudo
- **Strategy** - Lógica de trading (grid)
- **Adapter** - Integração com Hyperliquid
- **Risk Manager** - Proteção de conta
- **Market Data** - Preços em tempo real

## 🚀 Começar Agora

```bash
# 1. Instalar pytest
python3 -m pip install pytest pytest-asyncio pytest-mock

# 2. Rodar testes
python3 -m pytest tests/ -v

# 3. Validar config
python3 src/run_bot.py --validate

# 4. Rodar bot
python3 src/run_bot.py bots/btc_conservative.yaml
```

## 📖 Documentação

| Arquivo | Propósito |
|---------|-----------|
| [QUICK_FIX.md](QUICK_FIX.md) | Solução rápida para pytest |
| [RUN_TESTS_SIMPLE.md](RUN_TESTS_SIMPLE.md) | Como rodar testes |
| [TESTING.md](TESTING.md) | Desenvolvimento de testes |
| [SETUP.md](SETUP.md) | Setup completo do ambiente |
| [MACOS_SETUP.md](MACOS_SETUP.md) | Setup específico macOS |
| [FIX_PYTEST.md](FIX_PYTEST.md) | Troubleshooting pytest |
| [README.md](README.md) | Documentação principal |
| [AGENTS.md](AGENTS.md) | Diretrizes de desenvolvimento |

## ✅ Checklist

- [ ] Python 3.9+ instalado
- [ ] pytest instalado
- [ ] Testes rodando
- [ ] Todos os testes passando
- [ ] Configuração validada
- [ ] Bot pronto para usar

## 🎉 Você Está Pronto!

Agora você tem:
- ✅ 50+ testes validando o bot
- ✅ Documentação completa
- ✅ Exemplos de aprendizado
- ✅ Configurações prontas
- ✅ Bot pronto para trading

Divirta-se! 🚀

---

**Precisa de ajuda?** Veja [QUICK_FIX.md](QUICK_FIX.md) ou [SETUP.md](SETUP.md)
