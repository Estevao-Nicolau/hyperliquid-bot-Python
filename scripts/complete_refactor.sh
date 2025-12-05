#!/bin/bash
# Completar refatoração

cd /Users/nicolaudev/hyperliquid-trading-bot

echo "🧹 Completando refatoração..."

# 1. Remover venv antigo
echo "1. Removendo venv/ antigo..."
rm -rf venv/
echo "✅ venv removido"

# 2. Limpar cache Python
echo "2. Limpando cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache
echo "✅ Cache limpo"

# 3. Arquivar documentação velha
echo "3. Arquivando documentação velha..."
mv PHASE1_SUMMARY.md docs/archive/ 2>/dev/null || echo "  (PHASE1 já movido)"
mv SETUP_SUMMARY.md docs/archive/ 2>/dev/null || echo "  (SETUP_SUMMARY já movido)"
echo "✅ Documentação arquivada"

# 4. Atualizar .gitignore
echo "4. Atualizando .gitignore..."
if ! grep -q "^venv/" .gitignore; then
    echo "venv/" >> .gitignore
    echo "✅ Adicionado venv/ ao .gitignore"
else
    echo "✅ venv/ já em .gitignore"
fi

# 5. Verificar estrutura
echo "5. Verificando estrutura..."
echo "📁 Raiz (MD files):"
ls -1 *.md 2>/dev/null | wc -l | xargs echo "  Arquivos .md:"
echo "📁 docs/:"
ls -1 docs/ 2>/dev/null
echo "📁 scripts/:"
ls -1 scripts/ 2>/dev/null | head -10

echo ""
echo "✨ Refatoração completada!"
echo ""
echo "Próximos passos:"
echo "1. git status (verificar mudanças)"
echo "2. pytest tests/ -v (rodar testes)"
echo "3. git add . && git commit -m 'refactor: clean up project structure'"
echo ""

