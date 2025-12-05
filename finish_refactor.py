#!/usr/bin/env python3
"""Completar tarefas de refatoração"""
import os
import shutil
import subprocess
from pathlib import Path

os.chdir("/Users/nicolaudev/hyperliquid-trading-bot")

print("\n🧹 COMPLETANDO REFATORAÇÃO\n")

# Remover venv
print("1. Removendo venv/...")
if Path("venv").exists():
    shutil.rmtree("venv")
    print("   ✅ Removido!")
else:
    print("   ℹ️ Já removido")

# Arquivar docs
print("2. Arquivando documentação velha...")
os.makedirs("docs/archive", exist_ok=True)
for doc in ["PHASE1_SUMMARY.md", "SETUP_SUMMARY.md"]:
    src = Path(doc)
    if src.exists():
        dst = Path(f"docs/archive/{doc}")
        shutil.move(str(src), str(dst))
        print(f"   ✅ {doc}")

# Limpar cache
print("3. Limpando cache...")
for pycache in Path(".").rglob("__pycache__"):
    shutil.rmtree(pycache, ignore_errors=True)
if Path(".pytest_cache").exists():
    shutil.rmtree(".pytest_cache")
print("   ✅ Cache limpo")

# Adicionar ao .gitignore
print("4. Atualizando .gitignore...")
gitignore = Path(".gitignore")
content = gitignore.read_text()
if "venv/" not in content:
    gitignore.write_text(content + "\nvenv/\n")
    print("   ✅ Adicionado venv/")
else:
    print("   ℹ️ venv/ já existe")

print("\n✨ Refatoração Completada!\n")

# Status
print("📊 Estrutura Final:")
print(f"  .md files: {len(list(Path('.').glob('*.md')))}")
print(f"  docs/.md: {len(list(Path('docs').glob('*.md')))}")
print(f"  scripts/*: {len(list(Path('scripts').iterdir()))}")

print("\n🚀 Próximos Passos:")
print("  1. git add .")
print("  2. git commit -m 'refactor: clean up project structure'")
print("  3. git push origin main")
print("  4. pytest tests/ -v")
print("")

