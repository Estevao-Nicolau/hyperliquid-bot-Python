#!/bin/bash

# Reset terminal se estiver corrompido
reset 2>/dev/null || true

# Executar Python script
python3 /Users/nicolaudev/hyperliquid-trading-bot/final_cleanup.py

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✨ Refatoração finalizada! Próximas ações:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. Revisar mudanças: git status"
echo "2. Commitar: git add . && git commit -m 'refactor: clean up project structure'"
echo "3. Testar: pytest tests/ -v"
echo "4. Enviar: git push origin main"
echo ""
