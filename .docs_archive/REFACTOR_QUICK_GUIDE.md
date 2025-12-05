# 📋 Refactorization Quick Guide

## 🎯 Objetivo

Limpar e reorganizar o projeto removendo duplicação, consolidando documentação e criando uma estrutura profissional.

**Economias esperadas:**
- 📄 77% menos linhas de documentação (3,598 → 800)
- 💾 ~100MB de espaço (removendo venv/ antigo)
- 🧹 Scripts organizados e claros
- 🏗️ Arquitetura profissional

---

## 🚀 Como Executar a Refatoração

### Opção 1: Script Automático (Recomendado)

```bash
# Fazer backup primeiro
git add .
git commit -m "backup: before refactor"

# Executar refatoração
bash scripts/refactor.sh
```

O script vai:
- ✅ Perguntar para confirmar cada ação
- ✅ Criar pasta `docs/`
- ✅ Mover scripts para `scripts/`
- ✅ Remover duplicatas
- ✅ Limpar cache Python
- ✅ Criar documentação consolidada

### Opção 2: Manual (Passo a Passo)

```bash
# 1. Criar pastas
mkdir -p docs/archive

# 2. Mover scripts
mv setup_env.py scripts/
mv quick_setup.sh scripts/
mv run_tests.py scripts/

# 3. Remover obsoletos
rm fix_setup.sh commit.sh do_commit.py
rm run_bot_15m.sh run_bot_5m.sh
rm .env.5m
rm -rf venv/

# 4. Arquivar documentação antiga
mv PHASE1_SUMMARY.md docs/archive/
mv SETUP_SUMMARY.md docs/archive/

# 5. Limpar cache
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache
```

---

## 📁 Estrutura Antes vs Depois

### ANTES (Poluído)
```
├── AGENTS.md ❌ (duplicado)
├── CLAUDE.md ❌ (duplicado)
├── README.md
├── START_HERE.md
├── QUICK_FIX.md ❌ (duplicado)
├── FIX_PYTEST.md ❌ (duplicado)
├── SETUP.md
├── SETUP_SUMMARY.md ❌ (redundante)
├── MACOS_SETUP.md ❌ (parte de SETUP)
├── TESTING.md
├── RUN_TESTS_SIMPLE.md ❌ (duplicado)
├── COMMIT_INSTRUCTIONS.md
├── NEXT_STEPS.md
├── PHASE1_SUMMARY.md ❌ (archive)
│
├── setup_env.py ❌ (mover para scripts/)
├── quick_setup.sh ❌ (mover para scripts/)
├── install_uv.sh ❌ (mover para scripts/)
├── run_tests.py ❌ (mover para scripts/)
├── run_tests.sh ❌ (mover para scripts/)
├── fix_setup.sh ❌ (remover)
├── commit.sh ❌ (remover)
├── do_commit.py ❌ (remover)
├── run_bot_15m.sh ❌ (usar config YAML)
├── run_bot_5m.sh ❌ (usar config YAML)
│
├── .env
├── .env.5m ❌ (remover)
│
├── .venv/ (219MB)
├── venv/ ❌ (93MB obsoleto)
│
└── src/
    └── services/
        ├── grid_15m/ ❌ (desnecessário)
        ├── grid_5m/ ❌ (desnecessário)
        └── shared/ ❌ (vazio)
```

### DEPOIS (Profissional)
```
├── docs/
│   ├── README.md              (Overview)
│   ├── SETUP.md               (Instalação)
│   ├── DEVELOPMENT.md         (Guidelines)
│   ├── TROUBLESHOOTING.md     (FAQ)
│   ├── ARCHITECTURE.md        (Design)
│   └── archive/
│       ├── PHASE1_SUMMARY.md
│       └── SETUP_SUMMARY.md
│
├── scripts/
│   ├── setup.py               (Setup única)
│   ├── run_tests.sh           (Testes)
│   ├── dev.sh                 (Helper commands)
│   └── refactor.sh            (Refactor script)
│
├── src/
│   ├── run_bot.py
│   ├── core/
│   ├── strategies/
│   ├── exchanges/
│   ├── ml/
│   ├── interfaces/
│   ├── utils/
│   ├── data_pipeline/
│   ├── tools/
│   └── api/                   (OPCIONAL)
│
├── tests/
├── bots/
├── models/
├── learning_examples/
│
├── .github/
│   └── workflows/             (OPCIONAL: CI/CD)
│
├── README.md                  (Quick start na raiz)
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── .venv/                     (Único ambiente)
```

---

## ✅ Verificação Pós-Refatoração

```bash
# 1. Verificar estrutura
ls -la docs/
ls -la scripts/
find . -maxdepth 1 -name "*.md" | wc -l  # Deve ser < 5

# 2. Testar ambiente
source .venv/bin/activate
python --version  # Deve ser 3.13+

# 3. Rodar testes
python3 -m pytest tests/ -v

# 4. Validar config
python3 src/run_bot.py --validate

# 5. Testar bot
python3 src/run_bot.py bots/btc_conservative.yaml
```

---

## 📊 Resultado Final

```bash
# Tamanho do repositório
du -sh .

# Arquivos de documentação
find . -maxdepth 1 -name "*.md" | wc -l

# Cache Python
find . -name "__pycache__" | wc -l
```

---

## 🔄 Git Workflow

```bash
# 1. Fazer backup
git add .
git commit -m "backup: before refactor"

# 2. Executar refatoração
bash scripts/refactor.sh

# 3. Verificar changes
git status

# 4. Revisar mudanças (optional)
git diff HEAD

# 5. Adicionar tudo
git add .

# 6. Commit refator
git commit -m "refactor: clean up project structure

- Consolidate 14 markdown docs into 4 focused files
- Move scripts to scripts/ directory
- Remove duplicate/obsolete files
- Archive historical documentation
- Remove deprecated venv/
- Clean Python cache
- Update .gitignore

Savings:
- 77% less documentation (3598 → 800 lines)
- 100MB freed (removed old venv)
- Cleaner project structure
- Professional organization"

# 7. Push
git push origin main
```

---

## ⚠️ Rollback (Se Necessário)

```bash
# Desfazer refatoração
git reset --hard HEAD~1

# Ou volta para commit específico
git log --oneline | head -5
git reset --hard <commit-hash>
```

---

## 💡 Dicas

1. **Fazer backup antes**: Sempre comitar antes de mudanças grandes
2. **Testar após**: Certificar que tudo funciona
3. **Revisar git changes**: Verificar `git status` antes de commit
4. **Documentar mudanças**: Bom commit message explica o quê e por quê

---

## 📞 Suporte

Se algo der errado:

1. Consulte `docs/TROUBLESHOOTING.md`
2. Faça rollback com `git reset --hard`
3. Abra issue no GitHub

