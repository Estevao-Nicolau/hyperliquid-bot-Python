#!/bin/bash

set -e

echo "🚀 Quick Setup - Hyperliquid Trading Bot"
echo "=========================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

install_uv_macos() {
    echo "📦 Installing UV via Homebrew..."
    
    if check_command brew; then
        brew install uv
        echo "✅ UV installed via Homebrew"
        return 0
    else
        echo "⚠️  Homebrew not found, installing UV via curl..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        echo ""
        echo "⚠️  UV installed but may not be in PATH"
        echo "Add this to ~/.zshrc or ~/.bash_profile:"
        echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\""
        echo ""
        echo "Then run: source ~/.zshrc"
        return 1
    fi
}

install_uv_linux() {
    echo "📦 Installing UV via curl..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    echo ""
    echo "⚠️  UV installed but may not be in PATH"
    echo "Add this to ~/.bashrc or ~/.zshrc:"
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\""
    echo ""
    echo "Then run: source ~/.bashrc"
    return 1
}

echo "1️⃣  Checking prerequisites..."
echo ""

if ! check_command python3; then
    echo "❌ Python 3 not found"
    echo "Install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"

echo ""
echo "2️⃣  Checking UV installation..."
echo ""

if check_command uv; then
    UV_VERSION=$(uv --version)
    echo "✅ UV already installed: $UV_VERSION"
else
    echo "❌ UV not found, installing..."
    echo ""
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if install_uv_macos; then
            echo ""
        else
            echo ""
            echo "⚠️  Please add UV to PATH and try again"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if install_uv_linux; then
            echo ""
        else
            echo ""
            echo "⚠️  Please add UV to PATH and try again"
            exit 1
        fi
    else
        echo "❌ Unsupported OS: $OSTYPE"
        echo "Please install UV manually from https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
fi

echo "3️⃣  Syncing dependencies..."
echo ""

if check_command uv; then
    uv sync
    echo "✅ Dependencies synced"
else
    echo "❌ UV still not available"
    echo "Please add UV to PATH manually:"
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\""
    exit 1
fi

echo ""
echo "4️⃣  Running tests..."
echo ""

uv run pytest tests/test_enhanced_config.py -v --tb=short

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run all tests: uv run pytest tests/ -v"
echo "2. Validate config: uv run src/run_bot.py --validate"
echo "3. Run bot: uv run src/run_bot.py bots/btc_conservative.yaml"
echo ""
