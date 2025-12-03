#!/bin/bash

set -e

echo "🔧 Installing UV Package Manager..."

if command -v uv &> /dev/null; then
    echo "✅ UV is already installed"
    uv --version
else
    echo "📥 Downloading and installing UV..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 Detected macOS"
        
        if command -v brew &> /dev/null; then
            echo "📦 Installing via Homebrew..."
            brew install uv
        else
            echo "📥 Installing via curl..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
            
            echo ""
            echo "⚠️  UV installed but not in PATH yet"
            echo "Add this to your shell profile (~/.zshrc or ~/.bash_profile):"
            echo ""
            echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\""
            echo ""
            echo "Then run: source ~/.zshrc"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "🐧 Detected Linux"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        echo ""
        echo "⚠️  UV installed but not in PATH yet"
        echo "Add this to your shell profile (~/.bashrc or ~/.zshrc):"
        echo ""
        echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\""
        echo ""
        echo "Then run: source ~/.bashrc"
    else
        echo "❌ Unsupported OS: $OSTYPE"
        exit 1
    fi
fi

echo ""
echo "✅ UV installation complete!"
echo ""
echo "Next steps:"
echo "1. Verify installation: uv --version"
echo "2. Sync dependencies: uv sync"
echo "3. Run tests: uv run pytest tests/ -v"
