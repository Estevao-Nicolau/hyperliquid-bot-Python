#!/bin/bash

#######################################################################
#  🚀 SCRIPT FINAL DE REFATORAÇÃO
#  Execute em um NOVO terminal para evitar corrupção anterior
#######################################################################

set -e  # Exit on error

BASE_DIR="/Users/nicolaudev/hyperliquid-trading-bot"
cd "$BASE_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      🚀 FINALIZANDO REFATORAÇÃO DO PROJETO               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Remove venv/ (Python 3.9 obsoleto)
echo "1️⃣  Removendo venv/ (93MB - Python 3.9 obsoleto)..."
if [ -d venv ]; then
    rm -rf venv
    echo "   ✅ venv removido com sucesso!"
else
    echo "   ℹ️  venv não encontrado"
fi
echo ""

# 2. Archive old docs
echo "2️⃣  Arquivando documentos históricos..."
mkdir -p docs/archive

for doc in PHASE1_SUMMARY.md SETUP_SUMMARY.md MACOS_SETUP.md RUN_TESTS_SIMPLE.md; do
    if [ -f "$doc" ]; then
        mv "$doc" "docs/archive/$doc" 2>/dev/null && echo "   ✅ $doc → docs/archive/"
    fi
done
echo ""

# 3. Clean cache
echo "3️⃣  Limpando cache Python..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true
rm -rf src/__pycache__ tests/__pycache__ 2>/dev/null || true
echo "   ✅ Cache limpo"
echo ""

# 4. Verify structure
echo "4️⃣  Verificando estrutura final..."
for dir in src tests bots docs scripts models; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir/"
    else
        echo "   ❌ $dir/ - FALTANDO!"
    fi
done
echo ""

# 5. Show stats
echo "5️⃣  Estatísticas finais..."
MD_COUNT=$(ls -1 *.md 2>/dev/null | wc -l)
echo "   📄 Arquivos .md na raiz: $MD_COUNT"

DOCS_COUNT=$(ls -1 docs/*.md 2>/dev/null | wc -l || echo "0")
echo "   📚 Arquivos em docs/: $DOCS_COUNT"

SCRIPTS_COUNT=$(ls -1 scripts/ 2>/dev/null | wc -l || echo "0")
echo "   🔧 Scripts em scripts/: $SCRIPTS_COUNT"

if [ -d ".venv" ]; then
    echo "   🐍 .venv (Python 3.13): ✅ Presente"
else
    echo "   🐍 .venv (Python 3.13): ❌ Ausente"
fi

if [ ! -d "venv" ]; then
    echo "   🗑️  venv (Python 3.9): ✅ Removido"
else
    echo "   🗑️  venv (Python 3.9): ❌ Ainda presente"
fi
echo ""

# 6. Git operations
echo "6️⃣  Preparando git commit..."
git add . 2>/dev/null || true
echo "   ✅ Mudanças staged"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          ✨ REFATORAÇÃO FINALIZADA COM SUCESSO!          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Status das mudanças:"
git status --short | head -20 || echo "Nenhuma mudança pendente"
echo ""

echo "📋 Próximos passos manuais:"
echo "   1. git commit -m \"refactor: clean up project structure\""
echo "   2. pytest tests/ -v"
echo "   3. git push origin main"
echo ""
