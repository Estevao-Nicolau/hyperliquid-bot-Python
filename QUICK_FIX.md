# Quick Fix - Run Tests Now

UV não está funcionando? Sem problema! Use Python diretamente.

## ⚡ Solução Rápida (30 segundos)

```bash
# 1. Instalar pytest
python3 -m pip install pytest pytest-asyncio pytest-mock

# 2. Rodar testes
python3 -m pytest tests/ -v
```

Pronto! Os testes devem rodar agora.

## 🎯 Opções de Execução

### Opção A: Linha de Comando Direta

```bash
# Instalar dependências de teste
python3 -m pip install pytest pytest-asyncio pytest-mock

# Rodar todos os testes
python3 -m pytest tests/ -v

# Rodar testes de configuração
python3 -m pytest tests/test_enhanced_config.py -v

# Rodar testes de precisão
python3 -m pytest tests/test_hl_adapter_precision.py -v
```

### Opção B: Script Shell

```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Opção C: Script Python

```bash
python3 run_tests.py
```

### Opção D: Instalar Tudo com requirements.txt

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest tests/ -v
```

## 📊 Esperado Ver

Quando os testes rodarem com sucesso, você verá:

```
tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config PASSED
tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_account_max_allocation_pct_too_low PASSED
tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_account_max_allocation_pct_too_high PASSED
...
tests/test_hl_adapter_precision.py::TestHyperliquidAdapterPrecision::test_round_price_btc_to_whole_dollar PASSED
tests/test_hl_adapter_precision.py::TestHyperliquidAdapterPrecision::test_round_price_other_asset_two_decimals PASSED
...

======================== 50+ passed in X.XXs ========================
```

## 🔍 Verificar Instalação

```bash
# Verificar Python
python3 --version

# Verificar pytest
python3 -m pytest --version

# Listar testes
python3 -m pytest tests/ --collect-only

# Rodar um teste específico
python3 -m pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config -v
```

## 📝 Próximas Ações

Após os testes passarem:

```bash
# 1. Validar configuração
python3 src/run_bot.py --validate

# 2. Rodar bot
python3 src/run_bot.py bots/btc_conservative.yaml

# 3. Rodar exemplo
python3 learning_examples/02_market_data/get_all_prices.py
```

## ❌ Se Ainda Não Funcionar

### Problema: "No module named pytest"

```bash
python3 -m pip install --upgrade pytest pytest-asyncio pytest-mock
```

### Problema: "Permission denied" no script

```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Problema: Testes não encontrados

```bash
# Verificar que os arquivos existem
ls -la tests/test_*.py

# Coletar testes
python3 -m pytest tests/ --collect-only
```

### Problema: Erro de import

```bash
# Instalar todas as dependências
python3 -m pip install -r requirements.txt
```

## 🎓 Entender os Testes

### test_enhanced_config.py (30+ testes)
Valida a configuração do bot:
- Carregamento de config válida
- Validação de ranges (account, grid, risk)
- Validação cruzada de campos
- Validação de chaves privadas

### test_hl_adapter_precision.py (20+ testes)
Valida precisão de preço e tamanho:
- Arredondamento de preço BTC (inteiro)
- Arredondamento de preço outros ativos (2 casas)
- Arredondamento de tamanho (5 casas)
- Tamanho mínimo (0.0001)
- Edge cases

## 📚 Documentação

- [RUN_TESTS_SIMPLE.md](RUN_TESTS_SIMPLE.md) - Guia detalhado
- [TESTING.md](TESTING.md) - Desenvolvimento de testes
- [SETUP.md](SETUP.md) - Setup completo
- [FIX_PYTEST.md](FIX_PYTEST.md) - Troubleshooting

## ✅ Checklist

- [ ] Python 3.9+ instalado (`python3 --version`)
- [ ] pytest instalado (`python3 -m pip install pytest`)
- [ ] Testes rodando (`python3 -m pytest tests/ -v`)
- [ ] Todos os testes passando (50+ passed)
- [ ] Configuração validada (`python3 src/run_bot.py --validate`)
- [ ] Bot pronto para rodar

## 🚀 Você Está Pronto!

Após os testes passarem, o bot está pronto para:
- ✅ Validar configurações
- ✅ Rodar em testnet
- ✅ Executar estratégias de grid
- ✅ Gerenciar risco
- ✅ Coletar dados de mercado

Divirta-se! 🎉
