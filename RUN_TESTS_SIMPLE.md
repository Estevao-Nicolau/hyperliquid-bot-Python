# Run Tests - Simple Guide

Se UV não está funcionando, use estas instruções simples.

## Opção 1: Usar Python Diretamente (Recomendado)

### Passo 1: Instalar dependências de teste

```bash
python3 -m pip install pytest pytest-asyncio pytest-mock
```

### Passo 2: Rodar os testes

```bash
# Todos os testes
python3 -m pytest tests/ -v

# Apenas testes de configuração
python3 -m pytest tests/test_enhanced_config.py -v

# Apenas testes de precisão
python3 -m pytest tests/test_hl_adapter_precision.py -v

# Um teste específico
python3 -m pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config -v
```

## Opção 2: Usar Script Shell

```bash
chmod +x run_tests.sh
./run_tests.sh
```

## Opção 3: Usar Script Python

```bash
python3 run_tests.py
```

## Opção 4: Instalar Tudo com requirements.txt

```bash
# Instalar todas as dependências
python3 -m pip install -r requirements.txt

# Rodar testes
python3 -m pytest tests/ -v
```

## Verificar Instalação

```bash
# Verificar pytest
python3 -m pytest --version

# Listar pacotes instalados
python3 -m pip list | grep pytest

# Verificar que os testes podem ser descobertos
python3 -m pytest tests/ --collect-only
```

## Rodar Testes com Cobertura

```bash
# Instalar coverage
python3 -m pip install coverage pytest-cov

# Rodar com cobertura
python3 -m pytest tests/ --cov=src --cov-report=html

# Abrir relatório
open htmlcov/index.html
```

## Próximas Ações

Após rodar os testes com sucesso:

```bash
# Validar configuração
python3 src/run_bot.py --validate

# Rodar bot
python3 src/run_bot.py bots/btc_conservative.yaml

# Rodar exemplo
python3 learning_examples/02_market_data/get_all_prices.py
```

## Se Ainda Não Funcionar

### Problema: "No module named pytest"

```bash
# Reinstalar
python3 -m pip install --upgrade pytest pytest-asyncio pytest-mock
```

### Problema: "Permission denied"

```bash
# Dar permissão
chmod +x run_tests.sh
chmod +x run_tests.py

# Rodar
./run_tests.sh
# ou
python3 run_tests.py
```

### Problema: Testes não encontrados

```bash
# Verificar estrutura
ls -la tests/
ls -la tests/test_*.py

# Coletar testes
python3 -m pytest tests/ --collect-only
```

## Referências

- [Pytest Documentation](https://docs.pytest.org/)
- [Python pip](https://pip.pypa.io/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
