#!/usr/bin/env python3
"""
Completar refatoração via Python
"""

import os
import shutil
import subprocess
from pathlib import Path

def main():
    os.chdir("/Users/nicolaudev/hyperliquid-trading-bot")
    
    print("\n🧹 Completando Refatoração...\n")
    
    # 1. Remover venv
    print("1️⃣  Removendo venv/ antigo...")
    venv_path = Path("venv")
    if venv_path.exists():
        shutil.rmtree(venv_path)
        print("   ✅ venv removido (93MB liberados!)")
    else:
        print("   ℹ️  venv já não existe")
    
    # 2. Limpar cache
    print("2️⃣  Limpando cache Python...")
    cache_dir = Path(".pytest_cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)
    print("   ✅ Cache limpo")
    
    # 3. Arquivar docs
    print("3️⃣  Arquivando documentação velha...")
    os.makedirs("docs/archive", exist_ok=True)
    
    for doc in ["PHASE1_SUMMARY.md", "SETUP_SUMMARY.md"]:
        src = Path(doc)
        if src.exists():
            dst = Path(f"docs/archive/{doc}")
            shutil.move(str(src), str(dst))
            print(f"   ✅ {doc} arquivado")
    
    # 4. Atualizar .gitignore
    print("4️⃣  Atualizando .gitignore...")
    gitignore_path = Path(".gitignore")
    content = gitignore_path.read_text()
    if "venv/" not in content:
        gitignore_path.write_text(content + "\nvenv/\n")
        print("   ✅ venv/ adicionado ao .gitignore")
    else:
        print("   ℹ️  venv/ já em .gitignore")
    
    # 5. Verificar estrutura
    print("5️⃣  Estrutura Final:")
    print(f"   📁 .md files: {len(list(Path('.').glob('*.md')))} arquivos")
    print(f"   📁 docs/: {len(list(Path('docs').glob('*.md')))} arquivos")
    print(f"   📁 scripts/: {len(list(Path('scripts').glob('*')))} arquivos")
    
    print("\n✨ Refatoração Completada!\n")
    
    # 6. Git status
    print("📋 Mudanças no Git:")
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    print(result.stdout[:500])
    
    print("\n🚀 Próximos Passos:")
    print("   1. git add .")
    print("   2. git commit -m 'refactor: clean up project structure'")
    print("   3. git push origin main")
    print("   4. pytest tests/ -v")

if __name__ == "__main__":
    main()

