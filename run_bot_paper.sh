#!/bin/bash

# Reset terminal e rodar bot
set -e

BASE_DIR="/Users/nicolaudev/hyperliquid-trading-bot"
cd "$BASE_DIR"

echo ""
echo "🔧 Limpando terminal..."
reset 2>/dev/null || true

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🤖 INICIANDO BOT EM PAPER TRADING                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "✅ Diretório: $BASE_DIR"
echo "✅ Python: $(python3 --version)"
echo ""

echo "📊 Rodando em PAPER TRADING MODE (sem risco)..."
echo "⏱️  Deixe rodando por 5-10 minutos"
echo "🛑 Pressione Ctrl+C para parar"
echo ""

python3 src/run_bot.py --paper

echo ""
echo "✅ Bot finalizado"
echo ""
