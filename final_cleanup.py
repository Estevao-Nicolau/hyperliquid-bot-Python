#!/usr/bin/env python3
"""
Script final para completar refatoração
Executa: remove venv, archive docs, valida estrutura
"""

import os
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path("/Users/nicolaudev/hyperliquid-trading-bot")

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def remove_venv():
    """Remove ambiente obsoleto Python 3.9"""
    print_header("1️⃣  REMOVENDO VENV (93MB)")
    
    venv_path = BASE_DIR / "venv"
    if venv_path.exists():
        print("🗑️  Removendo " + str(venv_path) + "...")
        shutil.rmtree(venv_path, ignore_errors=True)
        print("✅ venv removido com sucesso!")
    else:
        print("⚠️  venv não encontrado")

def archive_old_docs():
    """Move documentos históricos para archive"""
    print_header("2️⃣  ARQUIVANDO DOCUMENTOS HISTÓRICOS")
    
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
        if src.exists():
            shutil.move(str(src), str(dst))
            print("✅ " + doc + " → docs/archive/")
        else:
            print("⚠️  " + doc + " não encontrado")

def clean_cache():
    """Remove cache Python"""
    print_header("3️⃣  LIMPANDO CACHE PYTHON")
    
    cache_dirs = [
        BASE_DIR / "__pycache__",
        BASE_DIR / ".pytest_cache",
        BASE_DIR / "src" / "__pycache__",
        BASE_DIR / "tests" / "__pycache__",
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            shutil.rmtree(cache_dir, ignore_errors=True)
            print("✅ Removido: " + cache_dir.name)

def verify_structure():
    """Valida estrutura final"""
    print_header("4️⃣  VERIFICANDO ESTRUTURA FINAL")
    
    critical_dirs = ["src", "tests", "bots", "docs", "scripts", "models"]
    for dir_name in critical_dirs:
        dir_path = BASE_DIR / dir_name
        status = "✅" if dir_path.exists() else "❌"
        print(status + " " + dir_name + "/")
    
    # Verificar arquivos importantes
    print("\n📄 Arquivos Principais:")
    key_files = [
        "README.md",
        "pyproject.toml",
        "requirements.txt",
        "src/run_bot.py",
        ".gitignore",
        ".env.example",
    ]
    
    for file_name in key_files:
        file_path = BASE_DIR / file_name
        status = "✅" if file_path.exists() else "❌"
        print(status + " " + file_name)

def show_final_stats():
    """Mostra estatísticas finais"""
    print_header("5️⃣  ESTATÍSTICAS FINAIS")
    
    # Contar arquivos .md
    md_files = list(BASE_DIR.glob("*.md"))
    print("📄 Arquivos .md na raiz: " + str(len(md_files)))
    
    # Estrutura de docs
    docs_dir = BASE_DIR / "docs"
    if docs_dir.exists():
        doc_files = list(docs_dir.glob("*.md"))
        print("📚 Arquivos em docs/: " + str(len(doc_files)))
        for f in doc_files:
            print("   - " + f.name)
    
    # Estrutura de scripts
    scripts_dir = BASE_DIR / "scripts"
    if scripts_dir.exists():
        script_files = [f for f in scripts_dir.glob("*") if f.is_file()]
        print("🔧 Scripts em scripts/: " + str(len(script_files)))
        for f in script_files:
            print("   - " + f.name)
    
    # Verificar .venv
    venv_path = BASE_DIR / ".venv"
    venv_size = "✅ Presente" if venv_path.exists() else "❌ Ausente"
    print("\n🐍 .venv (Python 3.13): " + venv_size)
    
    old_venv_path = BASE_DIR / "venv"
    old_venv_size = "❌ Ainda presente" if old_venv_path.exists() else "✅ Removido"
    print("🗑️  venv (Python 3.9): " + old_venv_size)

def main():
    """Executa todas as ações"""
    print("\n" + "="*60)
    print("  🚀 FINALIZANDO REFATORAÇÃO DO PROJETO")
    print("="*60)
    
    try:
        remove_venv()
        archive_old_docs()
        clean_cache()
        verify_structure()
        show_final_stats()
        
        print_header("✨ REFATORAÇÃO COMPLETA!")
        print("""
Próximas ações:
1. git add .
2. git commit -m "refactor: clean up project structure"
3. pytest tests/ -v
4. git push origin main
        """)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
