╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          📚 DOCUMENTAÇÃO CENTRALIZADA - HYPERLIQUID BOT                   ║
║                                                                            ║
║  Tudo que você precisa saber sobre estratégias, regras e banco de dados   ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


═════════════════════════════════════════════════════════════════════════════
📋 ÍNDICE RÁPIDO
═════════════════════════════════════════════════════════════════════════════

1. [Estratégias do Bot](#estratégias)
   - Estratégia 15 Minutos (Conservative)
   - Estratégia 5 Minutos (Scalper)
   - Diferenças entre elas

2. [Regras de Operação](#regras)
   - Filtros de entrada
   - Filtros de saída
   - Gerenciamento de risco
   - Rebalanceamento

3. [Banco de Dados](#banco-de-dados)
   - Estrutura MongoDB
   - Dados armazenados
   - Queries úteis

4. [Arquivos de Configuração](#configuração)
   - Localização das estratégias
   - Parâmetros ajustáveis
   - Variáveis de ambiente


═════════════════════════════════════════════════════════════════════════════
🎯 ESTRATÉGIAS
═════════════════════════════════════════════════════════════════════════════


## 1️⃣ ESTRATÉGIA 15 MINUTOS - CONSERVATIVE (Padrão)

📁 Arquivo: `bots/btc_conservative.yaml`
⏱️  Timeframe: 15 minutos
🎯 Alvo: BTC/USD
🔄 Ativa: SIM (padrão)

### Características:

   🛡️  RISCO BAIXO
   ├─ Alocação máxima: 3% da conta (~US$30 em base de $1k)
   ├─ Range de preço: ±5% do preço atual
   ├─ Levels de grid: 1 (apenas 1 ordem)
   └─ Rebalanceamento: Quando preço sai >12% do range

   💰 Parâmetros:
   ├─ Stop Loss: DESABILITADO (ou 8% se ativar)
   ├─ Take Profit: DESABILITADO (ou 25% se ativar)
   ├─ Max Drawdown: 15%
   ├─ Max Position: 40% da conta
   └─ Intervalo Rebalanceamento: A cada 5 min (verifica mudanças)

   📊 Como funciona:
   1. Bot monitora preço de BTC a cada 15 minutos
   2. Se preço sair do range ±5%, cria nova ordem
   3. Coloca ordem no meio do novo range
   4. Ajusta automaticamente se preço continua mudando
   5. Mantém apenas 1 ordem ativa por vez

   ✅ Quando usar:
   - Iniciantes que querem testar o bot
   - Conta pequena (até $1k)
   - Não tem muito tempo para monitorar
   - Quer trading automático e seguro


## 2️⃣ ESTRATÉGIA 5 MINUTOS - SCALPER

📁 Arquivo: `bots/btc_scalper_5m.yaml`
⏱️  Timeframe: 5 minutos
🎯 Alvo: BTC/USD
🔄 Ativa: NÃO (ative quando quiser usar)

### Características:

   ⚡ RISCO MÉDIO-ALTO
   ├─ Alocação máxima: 3% da conta (~US$30 em base de $1k)
   ├─ Range de preço: ±2% do preço atual
   ├─ Range mínimo: 1% (em mercados tranquilos)
   ├─ Range máximo: 10% (em mercados voláteis)
   └─ Rebalanceamento: Quando preço sai >12% do range

   💰 Parâmetros:
   ├─ Stop Loss: DESABILITADO (ou 8% se ativar)
   ├─ Take Profit: DESABILITADO (ou 25% se ativar)
   ├─ Max Drawdown: 15%
   ├─ Max Position: 40% da conta
   └─ Intervalo Rebalanceamento: A cada 1 min (mais frequente)

   📊 Como funciona:
   1. Bot monitora preço de BTC a cada 5 minutos
   2. Range mais apertado (±2%) para lucros rápidos
   3. Se preço sair do range, cria nova ordem
   4. Reajusta mais frequentemente que o conservative
   5. Melhor para mercados movimentados

   ✅ Quando usar:
   - Traders com experiência
   - Tem tempo para monitorar
   - Mercado está MUITO volátil
   - Quer maximizar lucros rápidos (scalping)
   - Aceita risco maior


## 📊 DIFERENÇAS RESUMIDAS

┌─────────────────────────┬──────────────┬────────────────┐
│ Aspecto                 │ Conservative │ Scalper 5m     │
├─────────────────────────┼──────────────┼────────────────┤
│ Timeframe               │ 15 min       │ 5 min          │
│ Risco                   │ BAIXO        │ MÉDIO-ALTO     │
│ Range de Preço          │ ±5%          │ ±2%            │
│ Grid Levels             │ 1            │ 1              │
│ Rebalanceamento         │ Lento        │ RÁPIDO         │
│ Ideal para              │ Iniciantes   │ Traders Exp.   │
│ Lucro esperado          │ Lento/Seguro │ Rápido/Arriscado│
├─────────────────────────┼──────────────┼────────────────┤
│ Status Padrão           │ ✅ ATIVO     │ ❌ INATIVO     │
└─────────────────────────┴──────────────┴────────────────┘


═════════════════════════════════════════════════════════════════════════════
⚙️  REGRAS DE OPERAÇÃO
═════════════════════════════════════════════════════════════════════════════


### 🎯 FILTROS DE ENTRADA (Quando criar ordem)

1. **Filtro de Sinal ML** (OPCIONAL - Desabilitado atualmente)
   └─ Se habilitado, só entra se modelo ML der sinal positivo
   └─ Atualmente DESABILITADO (ML_MODEL_PATH comentado em .env)

2. **Filtro de Volatilidade**
   ├─ Verifica volatilidade dos últimos 24h
   ├─ Se muito volátil: expande range
   ├─ Se calmo: reduz range
   └─ Parâmetro: volatility_multiplier = 2.0

3. **Filtro de Liquidez**
   ├─ Verifica se há liquidez em BTC/USD
   ├─ Consulta últimos preços e volume
   └─ Só executa se houver volume suficiente

4. **Filtro de Rebalanceamento**
   ├─ Se preço saiu >12% do range anterior
   ├─ Canckela ordem antiga
   └─ Cria ordem nova no novo range


### 📤 FILTROS DE SAÍDA (Quando fechar posição)

1. **Take Profit**
   ├─ Status: DESABILITADO
   ├─ Se ativar: fecha com +25% de lucro
   └─ Parâmetro em YAML: take_profit_pct

2. **Stop Loss**
   ├─ Status: DESABILITADO
   ├─ Se ativar: fecha com -8% de perda
   └─ Parâmetro em YAML: stop_loss_pct

3. **Max Drawdown**
   ├─ Status: ATIVO
   ├─ Limite: -15% de perda máxima
   ├─ Se atingir, para de tradear
   └─ Parâmetro em YAML: max_drawdown_pct

4. **Fechamento Manual**
   ├─ Usuário pressiona Ctrl+C
   ├─ Bot fecha posição aberta
   ├─ Envia ordem de venda ao mercado
   └─ Para graciosamente


### 🔄 GERENCIAMENTO DE RISCO

1. **Alocação de Capital**
   ├─ Max allocation: 3% por operação
   ├─ Em $1k: ~$30 por trade
   ├─ Pode ser ajustado em YAML
   └─ Parâmetro: max_allocation_pct

2. **Position Sizing**
   ├─ Balance reserve: 50% (mantém em caixa)
   ├─ Max single position: 10%
   ├─ Min position size: $10 USD
   └─ Parâmetro: position_sizing.auto

3. **Rebalanceamento Automático**
   ├─ Preço move >12% fora do range
   ├─ Bot fecha ordem atual
   ├─ Cria ordem nova no novo preço
   └─ Parâmetro: price_move_threshold_pct = 12.0


═════════════════════════════════════════════════════════════════════════════
🗄️  BANCO DE DADOS
═════════════════════════════════════════════════════════════════════════════

### Tecnologia: MongoDB

   📍 Configuração padrão:
   ├─ Host: localhost:27017
   ├─ Banco: hyperliquid_bot
   └─ URI padrão: mongodb://localhost:27017

   🔧 Para usar servidor remoto:
      Adicione em .env:
      MONGO_URI=mongodb://user:pass@server:27017
      MONGO_DB=seu_banco


### 📊 Coleções disponíveis:

   1. **trades** - Histórico de todas as trades
      └─ Estrutura:
         {
           _id: ObjectId,
           symbol: "BTC",
           entry_price: 45000.50,
           exit_price: 45450.75,
           quantity: 0.001,
           profit: 450.25,
           profit_pct: 1.0,
           entry_time: ISODate,
           exit_time: ISODate,
           strategy: "grid",
           status: "closed"
         }

   2. **orders** - Ordens abertas/fechadas
      └─ Estrutura:
         {
           _id: ObjectId,
           order_id: "12345",
           symbol: "BTC",
           side: "buy",
           price: 45000.00,
           quantity: 0.001,
           status: "closed",
           created_at: ISODate,
           filled_at: ISODate
         }

   3. **market_data** - Histórico de preços
      └─ Estrutura:
         {
           _id: ObjectId,
           symbol: "BTC",
           timestamp: ISODate,
           price: 45000.50,
           volume_24h: 25000000
         }

   4. **metrics** - Métricas do bot
      └─ Estrutura:
         {
           _id: ObjectId,
           timestamp: ISODate,
           total_trades: 50,
           win_rate: 0.65,
           total_profit: 1250.50,
           max_drawdown: -0.12,
           sharpe_ratio: 1.25
         }


### 📈 Queries úteis (MongoDB):

   # Ver todas as trades:
   db.trades.find()

   # Ver trades lucrativas:
   db.trades.find({ profit_pct: { $gt: 0 } })

   # Ver trades de hoje:
   db.trades.find({ entry_time: { $gte: ISODate("2025-12-05") } })

   # Lucro total:
   db.trades.aggregate([
     { $group: { _id: null, total: { $sum: "$profit" } } }
   ])

   # Win rate:
   db.trades.countDocuments({ profit_pct: { $gt: 0 } }) / 
   db.trades.countDocuments()


═════════════════════════════════════════════════════════════════════════════
⚙️  ARQUIVOS DE CONFIGURAÇÃO
═════════════════════════════════════════════════════════════════════════════

### 📁 Estrutura:

   /hyperliquid-trading-bot/
   ├── .env                          # Variáveis de ambiente (API keys, ML config)
   ├── .env.example                  # Template (sem senhas)
   ├── bots/
   │   ├── btc_conservative.yaml     # ← Estratégia 15min (PADRÃO)
   │   └── btc_scalper_5m.yaml       # ← Estratégia 5min (OPCIONAL)
   └── src/
       ├── core/
       │   ├── enhanced_config.py    # Carregador de YAML
       │   └── engine.py             # Motor principal
       └── strategies/grid/
           └── basic_grid.py         # Implementação da estratégia


### 🔧 Arquivo .env:

   # Credentials Hyperliquid
   HYPERLIQUID_TESTNET=false
   HYPERLIQUID_MAINNET=true
   HYPERLIQUID_MAINNET_PRIVATE_KEY=0x...

   # ML Configuration (Desabilitado)
   # ML_MODEL_PATH=model_main_15m_h6_r4_v2.pkl  # Comentado

   # MongoDB
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=hyperliquid_bot

   # Redis (cache)
   REDIS_URL=redis://localhost:6379


### 🎯 Arquivo YAML (btc_conservative.yaml):

   ┌─────────────────────────────────────┐
   │ name                   │ Nome bot    │
   │ active                 │ true/false  │
   │ exchange.testnet       │ true/false  │
   │ account.max_allocation │ % da conta  │
   │ grid.levels            │ Num ordens  │
   │ grid.price_range.auto  │ Range %     │
   │ risk_management        │ SL, TP, etc │
   │ monitoring.log_level   │ INFO/DEBUG  │
   └─────────────────────────────────────┘


### 🚀 Como usar cada estratégia:

   # Rodar Conservative (padrão):
   python3 src/run_bot.py

   # Rodar Conservative (explícito):
   python3 src/run_bot.py --config bots/btc_conservative.yaml

   # Rodar Scalper 5min:
   python3 src/run_bot.py --config bots/btc_scalper_5m.yaml

   # Paper trading (simular):
   python3 src/run_bot.py --paper

   # Paper trading com scalper:
   python3 src/run_bot.py --config bots/btc_scalper_5m.yaml --paper


═════════════════════════════════════════════════════════════════════════════
🔧 AJUSTANDO PARÂMETROS
═════════════════════════════════════════════════════════════════════════════

### Para deixar mais AGRESSIVO (mais risco, mais lucro):

   Na config YAML:
   
   1. Aumente range: range_pct: 5.0 → 10.0
   2. Mais ordens: levels: 1 → 5
   3. Mais capital: max_allocation_pct: 3.0 → 10.0
   4. Ative TP: take_profit_enabled: false → true
   5. Reduza drawdown: max_drawdown_pct: 15.0 → 10.0


### Para deixar mais CONSERVADOR (menos risco):

   Na config YAML:
   
   1. Reduza range: range_pct: 5.0 → 2.0
   2. Menos ordens: levels: 1 → 1 (já mínimo)
   3. Menos capital: max_allocation_pct: 3.0 → 1.0
   4. Aumente drawdown: max_drawdown_pct: 15.0 → 25.0


═════════════════════════════════════════════════════════════════════════════
❓ PERGUNTAS FREQUENTES
═════════════════════════════════════════════════════════════════════════════

P: Qual estratégia devo usar para começar?
R: Conservative (15min) - é a mais segura para iniciantes

P: Posso rodar ambas as estratégias ao mesmo tempo?
R: Não recomendado - compete por capital. Use uma por vez.

P: Como ativar o ML signal?
R: Descomente ML_MODEL_PATH em .env (atualmente desabilitado por featuremismatch)

P: Qual é o lucro esperado?
R: 1-3% por dia em mercados normais (varia muito)

P: Preciso monitorar constantemente?
R: Não - bot funciona 24/7 sozinho. Monitore periodicamente.

P: Como alterar o timeframe?
R: Edite a config YAML (timeframe: "5m" ou "15m")

P: Onde vejo histórico de operações?
R: Em MongoDB na coleção "trades"

P: Posso resetar o bot?
R: Parar com Ctrl+C, limpar base de dados, rodar novamente


═════════════════════════════════════════════════════════════════════════════

✨ Pronto! Agora você tem tudo centralizado aqui.

Próximos passos:
  1. Escolha uma estratégia (recomendo Conservative)
  2. Ajuste parâmetros conforme necessário
  3. Teste em paper trading: python3 src/run_bot.py --paper
  4. Monitore dados em MongoDB
  5. Inicie trading real quando confiante

═════════════════════════════════════════════════════════════════════════════
