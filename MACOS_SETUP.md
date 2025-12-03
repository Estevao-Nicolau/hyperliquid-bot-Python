# macOS Setup Guide

Complete step-by-step guide for setting up the Hyperliquid Trading Bot on macOS.

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python3 --version

# Check if Homebrew is installed
brew --version

# Check if UV is installed
uv --version
```

## Installation Methods

### Method 1: Homebrew (Recommended - Fastest)

**Step 1: Install Homebrew (if not already installed)**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Step 2: Install UV**

```bash
brew install uv
```

**Step 3: Verify Installation**

```bash
uv --version
```

**Step 4: Sync Dependencies**

```bash
cd /path/to/hyperliquid-trading-bot
uv sync
```

**Step 5: Run Tests**

```bash
uv run pytest tests/ -v
```

### Method 2: Curl Installation

**Step 1: Install UV via Curl**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2: Add UV to PATH**

Add this line to your shell profile (`~/.zshrc` for zsh or `~/.bash_profile` for bash):

```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

**Step 3: Reload Shell**

```bash
source ~/.zshrc  # or source ~/.bash_profile
```

**Step 4: Verify Installation**

```bash
uv --version
```

**Step 5: Sync Dependencies**

```bash
cd /path/to/hyperliquid-trading-bot
uv sync
```

**Step 6: Run Tests**

```bash
uv run pytest tests/ -v
```

### Method 3: Python Virtual Environment (No UV)

**Step 1: Create Virtual Environment**

```bash
cd /path/to/hyperliquid-trading-bot
python3 -m venv .venv
```

**Step 2: Activate Virtual Environment**

```bash
source .venv/bin/activate
```

**Step 3: Upgrade pip**

```bash
pip install --upgrade pip
```

**Step 4: Install Dependencies**

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install hyperliquid-python-sdk eth-account pyyaml python-dotenv websockets pytest pytest-asyncio pytest-mock
```

**Step 5: Run Tests**

```bash
pytest tests/ -v
```

**Step 6: Deactivate When Done**

```bash
deactivate
```

### Method 4: Automatic Setup Script

**Step 1: Make Script Executable**

```bash
chmod +x quick_setup.sh
```

**Step 2: Run Setup Script**

```bash
./quick_setup.sh
```

The script will:
- Check Python installation
- Install UV if needed
- Sync dependencies
- Run initial tests

## Fixing Common macOS Issues

### Issue: "zsh: command not found: uv"

**Solution 1: Add to PATH**

```bash
# Edit ~/.zshrc
nano ~/.zshrc

# Add this line at the end
export PATH="$HOME/.cargo/bin:$PATH"

# Save (Ctrl+O, Enter, Ctrl+X)
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

### Issue: "Python 3.9+ required"

**Solution: Install Python 3.11 via Homebrew**

```bash
# Install Python 3.11
brew install python@3.11

# Verify
python3 --version

# If needed, set as default
brew link python@3.11 --force
```

### Issue: "Permission denied" when running scripts

**Solution: Make Scripts Executable**

```bash
chmod +x install_uv.sh
chmod +x setup_env.py
chmod +x quick_setup.sh

# Then run
./quick_setup.sh
```

### Issue: "ModuleNotFoundError: No module named 'pytest'"

**Solution: Reinstall Dependencies**

```bash
# Using UV
uv sync --force

# Or using Python venv
source .venv/bin/activate
pip install --upgrade pytest pytest-asyncio pytest-mock
```

### Issue: Virtual Environment Not Activating

**Solution: Create and Activate Properly**

```bash
# Create venv
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Verify (should show (.venv) prefix in terminal)
echo $VIRTUAL_ENV

# Install dependencies
pip install -r requirements.txt
```

### Issue: "Homebrew not found"

**Solution: Install Homebrew**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH if needed
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# Verify
brew --version
```

## Verifying Installation

```bash
# Check Python
python3 --version

# Check UV
uv --version

# Check virtual environment
ls -la .venv

# Check installed packages
uv pip list
# or
pip list

# Check pytest
pytest --version

# Run a simple test
uv run pytest tests/test_enhanced_config.py::TestEnhancedConfigValidation::test_valid_minimal_config -v
```

## Setting Up Environment Variables

**Step 1: Create .env File**

```bash
cp .env.example .env
```

**Step 2: Edit .env File**

```bash
nano .env
```

**Step 3: Add Your Testnet Private Key**

```bash
HYPERLIQUID_TESTNET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
HYPERLIQUID_TESTNET=true
```

**Step 4: Save and Exit**

Press `Ctrl+O`, then `Enter`, then `Ctrl+X`

## Running Tests on macOS

### Using UV

```bash
# All tests
uv run pytest tests/ -v

# Specific test file
uv run pytest tests/test_enhanced_config.py -v

# With coverage
uv run pytest tests/ --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Using Python venv

```bash
# Activate venv
source .venv/bin/activate

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html

# Deactivate when done
deactivate
```

## Running the Bot on macOS

### Using UV

```bash
# Validate configuration
uv run src/run_bot.py --validate

# Run bot
uv run src/run_bot.py bots/btc_conservative.yaml
```

### Using Python venv

```bash
# Activate venv
source .venv/bin/activate

# Validate configuration
python3 src/run_bot.py --validate

# Run bot
python3 src/run_bot.py bots/btc_conservative.yaml

# Deactivate when done
deactivate
```

## Useful macOS Commands

```bash
# Check disk space
df -h

# Check memory usage
top -l 1 | head -20

# List processes
ps aux | grep python

# Kill a process
kill -9 <PID>

# Check open ports
lsof -i :8000

# View system logs
log stream --predicate 'process == "python"'

# Check shell configuration
cat ~/.zshrc

# Edit shell configuration
nano ~/.zshrc

# Reload shell
source ~/.zshrc
```

## Troubleshooting Shell Issues

### If commands don't work after installation:

**Step 1: Check Your Shell**

```bash
echo $SHELL
```

**Step 2: Edit Correct Profile**

- If shell is `/bin/zsh`: Edit `~/.zshrc`
- If shell is `/bin/bash`: Edit `~/.bash_profile`

**Step 3: Add PATH**

```bash
# For zsh
nano ~/.zshrc

# For bash
nano ~/.bash_profile

# Add this line
export PATH="$HOME/.cargo/bin:$PATH"

# Save and reload
source ~/.zshrc  # or source ~/.bash_profile
```

## Next Steps

1. ✅ Install UV or Python venv
2. ✅ Sync dependencies
3. ✅ Run tests: `uv run pytest tests/ -v`
4. ✅ Validate configuration: `uv run src/run_bot.py --validate`
5. 📖 Read TESTING.md for test development
6. 🚀 Run bot: `uv run src/run_bot.py bots/btc_conservative.yaml`

## Getting Help

- **Setup Issues**: See SETUP.md
- **Testing Issues**: See TESTING.md
- **General Help**: See README.md
- **Development**: See AGENTS.md

## References

- [UV Documentation](https://docs.astral.sh/uv/)
- [Homebrew Documentation](https://brew.sh/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [macOS Terminal Tips](https://support.apple.com/en-us/HT201236)
