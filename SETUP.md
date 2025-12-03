# Setup Guide - Hyperliquid Trading Bot

This guide helps you set up the development environment and fix common issues.

## Quick Start (Recommended)

### Option 1: Using UV (Fastest)

```bash
# 1. Install UV (macOS with Homebrew)
brew install uv

# 2. Verify installation
uv --version

# 3. Sync dependencies
uv sync

# 4. Run tests
uv run pytest tests/ -v

# 5. Validate configuration
uv run src/run_bot.py --validate
```

### Option 2: Using Python Virtual Environment (No UV Required)

```bash
# 1. Run setup script
python3 setup_env.py all

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Run tests
pytest tests/ -v

# 4. Validate configuration
python3 src/run_bot.py --validate
```

## Detailed Installation Steps

### Step 1: Install UV (macOS)

#### Option A: Using Homebrew (Recommended)

```bash
brew install uv
uv --version  # Verify installation
```

#### Option B: Using Curl

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then add UV to your PATH by adding this to `~/.zshrc` or `~/.bash_profile`:

```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

Then reload your shell:

```bash
source ~/.zshrc  # or source ~/.bash_profile
```

#### Option C: Using the Install Script

```bash
chmod +x install_uv.sh
./install_uv.sh
```

### Step 2: Verify Python Installation

```bash
python3 --version  # Should be 3.9 or higher
```

If Python is not installed, install it:

```bash
# macOS with Homebrew
brew install python@3.11

# Or download from https://www.python.org/downloads/
```

### Step 3: Sync Dependencies

```bash
# Using UV (recommended)
uv sync

# Or using Python venv
python3 setup_env.py install
```

This installs:
- Main dependencies (hyperliquid-python-sdk, eth-account, etc.)
- Test dependencies (pytest, pytest-asyncio, pytest-mock)
- Development dependencies (black, isort, mypy)

### Step 4: Verify Setup

```bash
# Using UV
uv run pytest tests/test_enhanced_config.py -v

# Or using venv
source .venv/bin/activate
pytest tests/test_enhanced_config.py -v
```

## Running Tests

### Using UV

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_enhanced_config.py -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config -v
```

### Using Python Virtual Environment

```bash
# Activate venv
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_enhanced_config.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Deactivate venv
deactivate
```

## Troubleshooting

### Issue: "error: Failed to spawn: `pytest`"

**Solution:**

```bash
# Remove old lock file and reinstall
rm -f uv.lock
uv sync --force

# Verify pytest is installed
uv run pytest --version

# Run tests
uv run pytest tests/ -v
```

Or use the fix script:

```bash
chmod +x fix_setup.sh
./fix_setup.sh
```

See [FIX_PYTEST.md](FIX_PYTEST.md) for detailed troubleshooting.

### Issue: "zsh: command not found: uv"

**Solution 1: Add UV to PATH**

```bash
# Add to ~/.zshrc
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell
source ~/.zshrc

# Verify
uv --version
```

**Solution 2: Reinstall UV**

```bash
# Remove old installation
rm -rf ~/.cargo/bin/uv

# Reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (see Solution 1)
```

**Solution 3: Use Python Setup Script**

```bash
python3 setup_env.py all
source .venv/bin/activate
```

### Issue: "ModuleNotFoundError: No module named 'pytest'"

**Solution:**

```bash
# Using UV
uv sync

# Or using Python
python3 setup_env.py install
source .venv/bin/activate
```

### Issue: "Python 3.9+ required"

**Solution: Install Python 3.11**

```bash
# macOS with Homebrew
brew install python@3.11

# Verify
python3 --version

# If needed, set as default
brew link python@3.11 --force
```

### Issue: "Permission denied" when running scripts

**Solution:**

```bash
chmod +x install_uv.sh
chmod +x setup_env.py

# Then run
./install_uv.sh
# or
python3 setup_env.py all
```

### Issue: Virtual environment not activating

**Solution:**

```bash
# Check if .venv exists
ls -la .venv

# If not, create it
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Verify (should show (.venv) prefix)
echo $VIRTUAL_ENV
```

### Issue: "No module named 'hyperliquid'"

**Solution:**

```bash
# Reinstall dependencies
uv sync --force

# Or using Python
python3 setup_env.py install
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: Tests timeout or hang

**Solution:**

```bash
# Run with timeout
uv run pytest tests/ --timeout=300 -v

# Or run specific test
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config -v
```

### Issue: "HYPERLIQUID_TESTNET_PRIVATE_KEY not found"

**Solution:**

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your testnet private key
nano .env

# Or set environment variable
export HYPERLIQUID_TESTNET_PRIVATE_KEY=0x...
export HYPERLIQUID_TESTNET=true
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# Required for trading
HYPERLIQUID_TESTNET_PRIVATE_KEY=0x...
HYPERLIQUID_TESTNET=true

# Optional for ML features
ML_MODEL_PATH=/path/to/model
ML_LOOKBACK=48
ML_ENTER_THRESHOLD=0.6
ML_EXIT_THRESHOLD=0.4

# Optional for paper trading
PAPER_TRADING=false
PAPER_INITIAL_BALANCE=100.0
```

## Development Workflow

### 1. Setup Environment

```bash
# Option A: Using UV
uv sync

# Option B: Using Python
python3 setup_env.py all
source .venv/bin/activate
```

### 2. Run Tests

```bash
# Using UV
uv run pytest tests/ -v

# Using venv
pytest tests/ -v
```

### 3. Validate Configuration

```bash
# Using UV
uv run src/run_bot.py --validate

# Using venv
python3 src/run_bot.py --validate
```

### 4. Run Bot

```bash
# Using UV
uv run src/run_bot.py bots/btc_conservative.yaml

# Using venv
python3 src/run_bot.py bots/btc_conservative.yaml
```

### 5. Run Learning Examples

```bash
# Using UV
uv run learning_examples/02_market_data/get_all_prices.py

# Using venv
python3 learning_examples/02_market_data/get_all_prices.py
```

## Checking Installation

```bash
# Check Python version
python3 --version

# Check UV installation
uv --version

# Check virtual environment
ls -la .venv

# Check installed packages
uv pip list
# or
pip list

# Check pytest
pytest --version

# Check project structure
ls -la src/
ls -la tests/
ls -la bots/
```

## Next Steps

1. ✅ Install UV or create virtual environment
2. ✅ Sync dependencies
3. ✅ Run tests: `uv run pytest tests/ -v`
4. ✅ Validate configuration: `uv run src/run_bot.py --validate`
5. 📖 Read TESTING.md for test development
6. 🚀 Run bot: `uv run src/run_bot.py bots/btc_conservative.yaml`

## Getting Help

If you encounter issues:

1. Check this SETUP.md file
2. Check TESTING.md for test-specific issues
3. Check AGENTS.md for development guidelines
4. Review error messages carefully
5. Try the alternative setup method (UV vs Python venv)

## References

- [UV Documentation](https://docs.astral.sh/uv/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Homebrew](https://brew.sh/)
