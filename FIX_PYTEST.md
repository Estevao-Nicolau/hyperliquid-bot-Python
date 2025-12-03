# Fix: pytest Not Found

Se você receber o erro `error: Failed to spawn: 'pytest'`, siga estas instruções.

## Problema

O UV removeu pytest ao sincronizar porque estava em `optional-dependencies` em vez de `dependencies` no `pyproject.toml`.

## Solução Rápida (Recomendado)

### Opção 1: Usar Script de Fix

```bash
chmod +x fix_setup.sh
./fix_setup.sh
```

Este script:
1. Remove o arquivo `uv.lock` antigo
2. Sincroniza dependências novamente
3. Verifica que pytest está instalado
4. Roda um teste rápido

### Opção 2: Manual Fix

```bash
# 1. Remove lock file
rm -f uv.lock

# 2. Sync dependencies
uv sync --force

# 3. Verify pytest
uv run pytest --version

# 4. Run tests
uv run pytest tests/ -v
```

### Opção 3: Reinstall Pytest Directly

```bash
# Install pytest directly
uv pip install pytest pytest-asyncio pytest-mock

# Verify
uv run pytest --version

# Run tests
uv run pytest tests/ -v
```

## O Que Foi Corrigido

Atualizei `pyproject.toml` para mover pytest de `optional-dependencies` para `dependencies`:

**Antes:**
```toml
dependencies = [
    # ... main deps ...
]

[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-mock>=3.0",
]
```

**Depois:**
```toml
dependencies = [
    # ... main deps ...
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-mock>=3.0",
]

[project.optional-dependencies]
dev = [
    "black",
    "isort",
    "mypy",
]
```

## Verificar Instalação

```bash
# Check pytest is installed
uv run pytest --version

# List installed packages
uv pip list | grep pytest

# Run a simple test
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config -v
```

## Próximas Ações

Após o fix:

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Validate configuration
uv run src/run_bot.py --validate

# Run bot
uv run src/run_bot.py bots/btc_conservative.yaml
```

## Se Ainda Não Funcionar

### Opção A: Clean Reinstall

```bash
# Remove everything
rm -rf .venv uv.lock

# Reinstall
uv sync

# Verify
uv run pytest --version
```

### Opção B: Use Python Virtual Environment

```bash
# Create venv
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Opção C: Check UV Installation

```bash
# Verify UV is working
uv --version

# Check UV can find Python
uv python list

# Reinstall UV
brew reinstall uv
```

## References

- [UV Documentation](https://docs.astral.sh/uv/)
- [Pytest Documentation](https://docs.pytest.org/)
- [pyproject.toml Format](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
