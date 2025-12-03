# Testing Guide

This document describes how to run tests for the Hyperliquid Trading Bot.

## Setup

### Install UV Package Manager

UV is required to run tests. Install it using:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then add UV to your PATH:

```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

### Install Dependencies

Install all dependencies including test dependencies:

```bash
uv sync
```

This installs:
- Main dependencies (hyperliquid-python-sdk, eth-account, pyyaml, etc.)
- Test dependencies (pytest, pytest-asyncio, pytest-mock)

## Running Tests

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Specific Test File

```bash
uv run pytest tests/test_enhanced_config.py -v
uv run pytest tests/test_hl_adapter_precision.py -v
```

### Run Specific Test Class

```bash
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation -v
uv run pytest tests/test_hl_adapter_precision.py::TestHyperliquidAdapterPrecision -v
```

### Run Specific Test

```bash
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=src --cov-report=html
```

### Run with Verbose Output

```bash
uv run pytest tests/ -vv
```

### Run with Print Statements

```bash
uv run pytest tests/ -s
```

## Test Structure

### test_enhanced_config.py

Tests for configuration validation and constraints:

- **Valid configurations**: Minimal valid config loads and validates
- **Account constraints**: max_allocation_pct range validation
- **Grid constraints**: levels, price_range, position_sizing validation
- **Risk management**: stop_loss_pct, take_profit_pct, max_drawdown_pct validation
- **Cross-field validation**: Conflicts between max_allocation_pct and balance_reserve_pct
- **Private key validation**: Format checking and security warnings
- **Exchange and monitoring**: Type and log level validation

**Total tests**: 30+

### test_hl_adapter_precision.py

Tests for Hyperliquid adapter price and size precision:

- **BTC price rounding**: Whole dollar precision
- **Other asset prices**: 2 decimal place precision
- **Size rounding**: 5 decimal place precision (szDecimals)
- **Minimum size**: 0.0001 BTC enforcement
- **Type preservation**: Float types maintained after rounding
- **Edge cases**: Zero values, negative values, very large/small values
- **String conversion**: Proper handling of string inputs
- **Consistency**: Precision maintained across multiple orders

**Total tests**: 20+

## Test Development Workflow (TDD)

1. **Red**: Write test that fails (test the requirement)
2. **Green**: Implement minimal code to pass the test
3. **Refactor**: Improve code while keeping tests passing

### Example: Adding a New Validation

```python
# 1. Write the test (RED)
def test_new_constraint_fails(self):
    config_dict = {"name": "test", "new_field": "invalid"}
    config = EnhancedBotConfig._dict_to_dataclass(config_dict)
    with pytest.raises(ValueError, match="new_field must be"):
        config.validate()

# 2. Run test (should fail)
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_new_constraint_fails -v

# 3. Implement validation in enhanced_config.py (GREEN)
# Add validation logic to make test pass

# 4. Run test again (should pass)
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_new_constraint_fails -v

# 5. Run all tests to ensure no regressions
uv run pytest tests/ -v
```

## Continuous Integration

To run tests in CI/CD pipeline:

```bash
#!/bin/bash
set -e

# Install dependencies
uv sync

# Run all tests
uv run pytest tests/ -v --tb=short

# Generate coverage report
uv run pytest tests/ --cov=src --cov-report=term-missing

# Exit with error if coverage below threshold
uv run pytest tests/ --cov=src --cov-fail-under=70
```

## Debugging Tests

### Run with Debugging Output

```bash
uv run pytest tests/ -vv -s --tb=long
```

### Run with Python Debugger

```bash
uv run pytest tests/ --pdb
```

### Run with Breakpoint

Add `breakpoint()` in test code:

```python
def test_something(self):
    config = EnhancedBotConfig._dict_to_dataclass({...})
    breakpoint()  # Execution pauses here
    config.validate()
```

Then run:

```bash
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_something -s
```

## Common Issues

### "ModuleNotFoundError: No module named 'pytest'"

Solution: Run `uv sync` to install test dependencies

### "zsh: command not found: uv"

Solution: Install UV and add to PATH:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

### Tests timeout

Solution: Increase timeout:

```bash
uv run pytest tests/ --timeout=300
```

### Import errors in tests

Solution: Ensure src/ is in Python path (already handled in test files via sys.path.insert)

## Next Steps

After these tests pass:

1. **Integration tests**: Test engine + strategy + adapter together
2. **Market data tests**: Test WebSocket reconnection and data streaming
3. **Risk manager tests**: Test all risk rules and actions
4. **E2E testnet tests**: Run against real Hyperliquid testnet
5. **Learning examples smoke tests**: Verify all examples work

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Asyncio](https://pytest-asyncio.readthedocs.io/)
- [Pytest Mock](https://pytest-mock.readthedocs.io/)
- [UV Documentation](https://docs.astral.sh/uv/)
