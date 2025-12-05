#!/usr/bin/env python3
"""
Executa operações finais de refatoração sem dependência de terminal
"""

import os
import sys
import shutil
from pathlib import Path

BASE_DIR = Path("/Users/nicolaudev/hyperliquid-trading-bot")
os.chdir(BASE_DIR)

print("\n" + "="*60)
print("  🚀 EXECUTANDO AÇÕES FINAIS DE REFATORAÇÃO")
print("="*60 + "\n")

# 1. Remove venv/ (Python 3.9)
print("1️⃣  REMOVENDO venv/ (93MB - Python 3.9)...")
venv_path = BASE_DIR / "venv"
if venv_path.exists():
    try:
        shutil.rmtree(venv_path, ignore_errors=True)
        print("   ✅ venv removido com sucesso!\n")
    except Exception as e:
        print("   ⚠️  Não foi possível remover venv:", str(e), "\n")
else:
    print("   ℹ️  venv não encontrado\n")

# 2. Archive old docs
print("2️⃣  ARQUIVANDO DOCUMENTOS HISTÓRICOS...")
archive_dir = BASE_DIR / "docs" / "archive"
archive_dir.mkdir(parents=True, exist_ok=True)

docs_to_archive = [
    "PHASE1_SUMMARY.md",
    "SETUP_SUMMARY.md",
    "MACOS_SETUP.md",
    "RUN_TESTS_SIMPLE.md",
]

for doc in docs_to_archive:
    src = BASE_DIR / doc
    dst = archive_dir / doc
    if src.exists() and not dst.exists():
        try:
            shutil.move(str(src), str(dst))
            print("   ✅ " + doc + " → docs/archive/")
        except Exception as e:
            print("   ⚠️  Erro ao mover " + doc + ":", str(e))

print()

# 3. Clean cache
print("3️⃣  LIMPANDO CACHE PYTHON...")
cache_dirs = [
    BASE_DIR / "__pycache__",
    BASE_DIR / ".pytest_cache",
]

for cache_dir in cache_dirs:
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir, ignore_errors=True)
            print("   ✅ Removido: " + cache_dir.name)
        except Exception as e:
            print("   ⚠️  Erro:", str(e))

print()

# 4. Verify structure
print("4️⃣  VERIFICANDO ESTRUTURA FINAL...")
critical_dirs = ["src", "tests", "bots", "docs", "scripts", "models"]
all_good = True
for dir_name in critical_dirs:
    dir_path = BASE_DIR / dir_name
    exists = dir_path.exists()
    status = "✅" if exists else "❌"
    print("   " + status + " " + dir_name + "/")
    if not exists:
        all_good = False

print()

# 5. Show stats
print("5️⃣  ESTATÍSTICAS FINAIS...")

md_files = list(BASE_DIR.glob("*.md"))
print("   📄 Arquivos .md na raiz: " + str(len(md_files)))

docs_dir = BASE_DIR / "docs"
if docs_dir.exists():
    doc_files = list(docs_dir.glob("*.md"))
    print("   📚 Arquivos em docs/: " + str(len(doc_files)))
    for f in doc_files:
        print("      - " + f.name)

scripts_dir = BASE_DIR / "scripts"
if scripts_dir.exists():
    script_files = [f for f in scripts_dir.glob("*") if f.is_file()]
    print("   🔧 Scripts em scripts/: " + str(len(script_files)))

venv_path = BASE_DIR / ".venv"
print("   🐍 .venv (Python 3.13): " + ("✅ Presente" if venv_path.exists() else "❌ Ausente"))

old_venv_path = BASE_DIR / "venv"
print("   🗑️  venv (Python 3.9): " + ("❌ Ainda presente" if old_venv_path.exists() else "✅ Removido"))

print()
print("="*60)
print("  ✨ REFATORAÇÃO COMPLETA!")
print("="*60)
print()
print("Próximas ações (execute no terminal):")
print("  1. git add .")
print("  2. git commit -m \"refactor: clean up project structure\"")
print("  3. pytest tests/ -v")
print("  4. git push origin main")
print()

sys.exit(0)
