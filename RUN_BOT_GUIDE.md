╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              🤖 COMO RODAR O BOT HYPERLIQUID TRADING                     ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝


🚀 REQUISITOS
═══════════════════════════════════════════════════════════════════════════

✅ Python 3.13+ (instalado em .venv)
✅ Dependências instaladas (requirements.txt)
✅ Chave de API Hyperliquid configurada (.env)
✅ Estratégia YAML em bots/ (btc_conservative.yaml ou btc_scalper_5m.yaml)


📝 CONFIGURAÇÃO (.env)
═══════════════════════════════════════════════════════════════════════════

1. Copiar template:
   cp .env.example .env

2. Editar .env com suas credenciais:
   HYPERLIQUID_API_KEY=sua_chave_aqui
   HYPERLIQUID_API_SECRET=seu_secret_aqui
   HYPERLIQUID_TESTNET=false  (true para testnet)

3. Salvar arquivo


🎯 ESTRATÉGIAS DISPONÍVEIS
═══════════════════════════════════════════════════════════════════════════

1. CONSERVATIVE (recomendado para começar):
   📁 bots/btc_conservative.yaml
   └─ Risco BAIXO
   └─ Range: ±5% do preço
   └─ 1 nível de grid
   └─ Alocação: 3% da conta

2. SCALPER 5MIN:
   📁 bots/btc_scalper_5m.yaml
   └─ Risco MÉDIO
   └─ Range: ±2% do preço
   └─ Múltiplos níveis
   └─ Timeframe: 5 minutos


💻 COMO RODAR
═══════════════════════════════════════════════════════════════════════════

OPÇÃO 1: RODAR COM CONFIGURAÇÃO PADRÃO
────────────────────────────────────────

O bot auto-descobre a primeira estratégia ativa em bots/:

    cd /Users/nicolaudev/hyperliquid-trading-bot
    python3 src/run_bot.py

Esperado:
    📁 Loading configuration: bots/btc_conservative.yaml
    🚀 Starting GridTradingBot...
    📡 Connected to Hyperliquid
    💰 Account balance: ...
    ✅ Bot running... (Press Ctrl+C to stop)


OPÇÃO 2: RODAR COM CONFIGURAÇÃO ESPECÍFICA
──────────────────────────────────────────

    python3 src/run_bot.py --config bots/btc_scalper_5m.yaml

OU

    python3 src/run_bot.py -c bots/btc_conservative.yaml


OPÇÃO 3: MODO TESTE (PAPER TRADING - SEM RISCO!)
─────────────────────────────────────────────

Testar a estratégia sem executar trades reais:

    python3 src/run_bot.py --paper

Esperado:
    📄 Paper Trading Mode ATIVO
    💾 Usando exchange simulada
    ✅ Nenhuma ordem real será executada
    📊 Simulando orders e price updates
    ⏱️  Reporte de trades simulados


OPÇÃO 4: VALIDAR CONFIGURAÇÃO
─────────────────────────────

Verificar se config está OK antes de rodar:

    python3 src/run_bot.py --validate

Esperado:
    ✅ Configuration valid
    📋 Config summary:
       Symbol: BTC
       Range: ±5%
       Levels: 1
       Risk: Conservative


OPÇÃO 5: VER AJUDA
──────────────────

    python3 src/run_bot.py --help

Mostrar todas as opções disponíveis


═══════════════════════════════════════════════════════════════════════════

🧪 WORKFLOW RECOMENDADO (primeira vez)
═══════════════════════════════════════════════════════════════════════════

PASSO 1: Validar Configuração
    python3 src/run_bot.py --validate
    
    Confirme:
    ✅ Configuration valid
    ✅ Todos os parâmetros OK

PASSO 2: Testar em Paper Trading (SEM RISCO)
    python3 src/run_bot.py --paper
    
    Observe:
    ✅ Ordens simuladas sendo criadas
    ✅ Preços atualizando
    ✅ Lógica funcionando
    
    Execute por 5-10 minutos, depois Ctrl+C

PASSO 3: Rodar em TESTNET (com API de teste)
    1. Altere em .env: HYPERLIQUID_TESTNET=true
    2. Use chaves de API de testnet
    3. python3 src/run_bot.py
    
    Observe:
    ✅ Conectando ao testnet
    ✅ Ordens criadas em testnet
    ✅ Sem gasto de capital real

PASSO 4: Rodar em MAINNET (CUIDADO!)
    1. Certifique-se que testnet funcionou
    2. Altere em .env: HYPERLIQUID_TESTNET=false
    3. Use chaves de API de mainnet
    4. python3 src/run_bot.py
    
    ⚠️  ISSO EXECUTARÁ TRADES REAIS COM DINHEIRO REAL!
    ⚠️  Comece com estratégia CONSERVATIVE
    ⚠️  Monitore de perto os primeiros trades


═══════════════════════════════════════════════════════════════════════════

🛑 PARAR O BOT
═══════════════════════════════════════════════════════════════════════════

No terminal onde o bot está rodando:
    Pressione: Ctrl + C

Esperado:
    📡 Received signal 2, shutting down...
    🔌 Cancelling open orders...
    ✅ Bot stopped
    💾 Session data saved


═══════════════════════════════════════════════════════════════════════════

📊 MONITORANDO O BOT
═══════════════════════════════════════════════════════════════════════════

Enquanto o bot está rodando, você verá:

    ✅ Connected to Hyperliquid
    💰 Account Balance: $1,000
    📍 BTC Price: $42,500
    🏪 Open Orders: 5
    ✅ Last Trade: SELL 0.01 BTC @ $42,400 (2m ago)
    📊 Grid Levels: ████████░░ (8/10 filled)
    ⏱️  Uptime: 1h 23m
    💾 Trades This Session: 12 (Profit: +$45)


═══════════════════════════════════════════════════════════════════════════

🔧 CUSTOMIZAR ESTRATÉGIA
═══════════════════════════════════════════════════════════════════════════

Edite o arquivo YAML para ajustar:

bots/btc_conservative.yaml:

    grid:
      symbol: "BTC"          ← Qual ativo (BTC, ETH, SOL, etc)
      levels: 1              ← Quantas ordens na grid (1, 5, 10, etc)
    
    price_range:
      auto:
        range_pct: 5.0       ← Amplitude (±% do preço)
    
    account:
      max_allocation_pct: 3.0  ← % da conta para usar

Exemplo - Aumentar agressividade:

    # CONSERVATIVE (Atual)
    range_pct: 5.0
    levels: 1
    max_allocation_pct: 3.0
    
    # MODERATE
    range_pct: 10.0
    levels: 5
    max_allocation_pct: 10.0
    
    # AGGRESSIVE (⚠️  Alto risco!)
    range_pct: 15.0
    levels: 20
    max_allocation_pct: 50.0


═══════════════════════════════════════════════════════════════════════════

🆘 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

ERRO: "Invalid API key"
└─ Solução:
   1. Verifique .env (HYPERLIQUID_API_KEY correto?)
   2. Regenere chaves em Hyperliquid dashboard
   3. Confirme formato sem espaços

ERRO: "Cannot connect to Hyperliquid"
└─ Solução:
   1. Verifique internet
   2. Confirme TESTNET flag em .env
   3. Tente: curl https://api.hyperliquid.xyz/info (conexão OK?)

ERRO: "Configuration error"
└─ Solução:
   1. Valide YAML: python3 src/run_bot.py --validate
   2. Confirme campos obrigatórios em bots/*.yaml
   3. Verifique indentação YAML (espaços, não tabs)

BOT TRAVA/NÃO RESPONDE
└─ Solução:
   1. Pressione Ctrl+C para parar
   2. Verifique logs
   3. Recomece: python3 src/run_bot.py

TRADES NÃO ESTÃO ACONTECENDO
└─ Solução:
   1. Confirme que exchange está ativo (não em manutenção)
   2. Verifique saldo da conta
   3. Confirme que config está "active: true"
   4. Use --paper mode para debug


═══════════════════════════════════════════════════════════════════════════

📚 EXEMPLOS DE USO
═══════════════════════════════════════════════════════════════════════════

1. Rodar estratégia conservadora em testnet:
   
   python3 src/run_bot.py \
     --config bots/btc_conservative.yaml \
     --testnet

2. Testar strategy em paper trading por 1 hora:
   
   python3 src/run_bot.py --paper
   # Deixar rodando por 1 hora, depois Ctrl+C

3. Rodar scalper 5min em mainnet (⚠️  real money):
   
   python3 src/run_bot.py \
     --config bots/btc_scalper_5m.yaml \
     --mainnet

4. Validar múltiplas configs:
   
   for config in bots/*.yaml; do
     python3 src/run_bot.py --config "$config" --validate
   done


═══════════════════════════════════════════════════════════════════════════

✅ CHECKLIST ANTES DE RODAR EM MAINNET
═══════════════════════════════════════════════════════════════════════════

[ ] .env configurado com chaves reais
[ ] Testei em paper trading mode
[ ] Testei em testnet com sucesso
[ ] Estratégia YAML validada (--validate)
[ ] Saldo confirmado na conta
[ ] Entendo o risco envolvido
[ ] Monitorei trades por 30 min
[ ] Tenho backup do .env
[ ] Sei como parar (Ctrl+C)


═══════════════════════════════════════════════════════════════════════════

📖 DOCUMENTAÇÃO ADICIONAL
═══════════════════════════════════════════════════════════════════════════

Mais detalhes em:
  • docs/DEVELOPMENT.md (como desenvolver)
  • docs/TROUBLESHOOTING.md (problema resolvidos)
  • docs/ARCHITECTURE.md (arquitetura do sistema)
  • src/core/enhanced_config.py (opções de config)


═══════════════════════════════════════════════════════════════════════════

🚀 COMEÇAR AGORA!
═══════════════════════════════════════════════════════════════════════════

1. Abra terminal:
   cd /Users/nicolaudev/hyperliquid-trading-bot

2. Valide config:
   python3 src/run_bot.py --validate

3. Teste em paper:
   python3 src/run_bot.py --paper

4. Se tudo OK, rode para real:
   python3 src/run_bot.py

Boa sorte! 🤖🚀

═══════════════════════════════════════════════════════════════════════════
