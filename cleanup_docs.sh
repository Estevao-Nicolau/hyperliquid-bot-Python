#!/bin/bash

# Script para centralizar e limpar documentação

echo "🧹 Limpando documentação duplicada..."

# Criar pasta de arquivo
mkdir -p .docs_archive

# Lista de arquivos que podem ser movidos (duplicados/obsoletos)
ARQUIVOS_PARA_MOVER=(
    "REFACTOR_QUICK_GUIDE.md"
    "REFACTOR_EXECUTIVE_SUMMARY.md"
    "REFACTOR_STATUS.md"
    "FINAL_ACTIONS.md"
    "REFACTOR_COMPLETE.md"
    "PHASE1_SUMMARY.md"
    "REFACTOR_FAQ.md"
    "QUICK_START_FINAL.md"
    "REFACTOR_MASTER_GUIDE.md"
    "DETAILED_REFACTOR_ANALYSIS.md"
    "AGENTS.md"
    "CLAUDE.md"
    "QUICK_FIX.md"
    "ML_SIGNAL_FIXED.md"
    "FIX_ML_ERROR.md"
    "TERMINAL_ERROR_FIX.md"
    "RUN_TESTS_SIMPLE.md"
    "REFACTOR_PROGRESS.txt"
    "REFACTOR_INDEX.md"
    "REFACTOR_START_HERE.txt"
    "REFACTOR_SUMMARY.txt"
    "NEXT_STEPS.md"
    "NEXT_STEPS.txt"
    "NEXT_STEPS_FINAL.md"
    "REFACTOR_ANALYSIS.md"
    "START_HERE_NOW.txt"
    "START_HERE.md"
    "SETUP_SUMMARY.md"
    "COMMIT_INSTRUCTIONS.md"
    "GITHUB_PUSH_GUIDE.md"
)

for arquivo in "${ARQUIVOS_PARA_MOVER[@]}"; do
    if [ -f "$arquivo" ]; then
        mv "$arquivo" ".docs_archive/$arquivo"
        echo "  ✅ Movido: $arquivo"
    fi
done

echo ""
echo "✨ Arquivos importantes mantidos na raiz:"
echo "  📄 README.md - Documentação principal"
echo "  📄 DOCUMENTACAO_CENTRALIZADA.md - Nova documentação consolidada ⭐"
echo "  🔧 SETUP.md - Setup do projeto"
echo "  📖 TESTING.md - Testes"
echo "  🍎 MACOS_SETUP.md - Setup macOS"
echo "  🚀 RUN_BOT_GUIDE.md - Guia de execução"
echo ""
echo "📦 Arquivos movidos para .docs_archive/ para referência futura"
echo ""
echo "✅ Limpeza completa!"
