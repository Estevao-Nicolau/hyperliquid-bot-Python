╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          🔍 ANÁLISE TÉCNICA - IMPLEMENTAÇÃO DAS ESTRATÉGIAS              ║
║                                                                            ║
║  Detalhes técnicos de como o bot implementa grid trading e sinais        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


═════════════════════════════════════════════════════════════════════════════
📂 ESTRUTURA DO CÓDIGO
═════════════════════════════════════════════════════════════════════════════

Arquivo principal: `src/strategies/grid/basic_grid.py` (543 linhas)

Componentes principais:

   1. GridState (enum)
      ├─ INITIALIZING: Preparando primeira grid
      ├─ ACTIVE: Grid ativa, monitorando preços
      ├─ REBALANCING: Ajustando posições
      └─ STOPPED: Grid parada

   2. GridLevel (dataclass)
      ├─ price: Preço da ordem
      ├─ size: Tamanho BTC
      ├─ level_index: Índice (0 a levels-1)
      ├─ is_buy_level: True se é compra, False se é venda
      └─ is_filled: Se a ordem foi preenchida

   3. GridConfig (dataclass)
      ├─ symbol: "BTC"
      ├─ levels: Número de ordens (1 ou mais)
      ├─ range_pct: ±X% do preço central
      ├─ total_allocation: USD total para usar
      ├─ min_price / max_price: Range manual (opcional)
      └─ rebalance_threshold_pct: Quando rebalancear

   4. BasicGridStrategy (classe principal)
      └─ Implementa interface TradingStrategy
         ├─ generate_signals(): Gera sinais de entrada/saída
         ├─ update_context(): Processa sinais ML
         ├─ _initialize_grid(): Cria primeira grid
         ├─ _should_rebalance(): Verifica se precisa rebalancear
         └─ _rebalance_grid(): Ajusta posições


═════════════════════════════════════════════════════════════════════════════
🎯 LÓGICA DE OPERAÇÃO - CASO 1 ORDEM (SINGLE TRADE)
═════════════════════════════════════════════════════════════════════════════

Este é o modo usado pela estratégia Conservative e Scalper (levels: 1)

### Estado Inicial:
   ┌────────────────────────────────────┐
   │ GridState: INITIALIZING            │
   │ active_trade: None                 │
   │ center_price: None                 │
   └────────────────────────────────────┘

### Passo 1: Inicialização (primeira execução)

   1. Bot recebe preço atual de BTC (ex: $45.000)
   2. Calcula range com base em config:
      └─ range_pct = 5% (Conservative)
      └─ min_price = $45.000 × (1 - 0.05) = $42.750
      └─ max_price = $45.000 × (1 + 0.05) = $47.250
   
   3. Cria centro da grid:
      └─ center_price = $45.000
   
   4. Define state = ACTIVE
   
   5. ENVIA SINAL: BUY 1 BTC @ $45.000 ✅

### Passo 2: Monitoramento (enquanto ordem está aberta)

   ⏱️  A cada 15 minutos, bot verifica:

   Cenário A - Preço dentro do range [$42.750 - $47.250]:
   └─ Mantém ordem aberta
   └─ Espera ser preenchida

   Cenário B - Preço saiu para CIMA de $47.250:
   └─ Calcula novo center = $46.000 (por exemplo)
   └─ Cancela ordem anterior
   └─ Cria novo range:
      ├─ min = $46.000 × 0.95 = $43.700
      ├─ max = $46.000 × 1.05 = $48.300
   └─ ENVIA SINAL: CANCEL + BUY novo @ $46.000 ✅

   Cenário C - Preço saiu para BAIXO de $42.750:
   └─ Cria novo range ao redor do novo preço
   └─ Rebalanceia (mesmo processo)

### Passo 3: Quando ordem é preenchida

   Ordem executada! Agora tem posição aberta.

   Verificações contínuas:

   📊 Take Profit:
      Se profit >= 25% → FECHA VENDA ✅
      (TAKE_PROFIT_ENABLED: false, então ignorado)

   🛑 Stop Loss:
      Se loss <= -8% → FECHA VENDA ✅
      (STOP_LOSS_ENABLED: false, então ignorado)

   💰 Max Drawdown:
      Se saldo total caiu >15% → PARA TUDO 🛑
      (Max drawdown global, não por trade)

### Passo 4: Fechamento

   ✅ Quando profit é OK ou usuário pressiona Ctrl+C:
      └─ Envia CLOSE order
      └─ Sai da posição
      └─ Volta ao estado ACTIVE (pronto para nova ordem)


═════════════════════════════════════════════════════════════════════════════
📊 EXEMPLO PRÁTICO - SCALPER 5 MINUTOS
═════════════════════════════════════════════════════════════════════════════

Configuração:
   - Timeframe: 5 minutos
   - Range: ±2%
   - Allocation: 3% = ~$30 USD

Horário: 14:00 UTC

14:00 - Preço BTC = $45.000
   └─ Grid range: $44.100 - $45.900
   └─ Bot coloca BUY @ $45.000
   └─ Status: WAITING

14:05 - Preço BTC = $45.800 (dentro do range)
   └─ Ordem ainda aberta
   └─ Status: WAITING

14:10 - Preço BTC = $46.500 (FORA do range!)
   └─ Sai do range: $46.500 > $45.900
   └─ Bot cancela ordem anterior
   └─ Novo range: $45.570 - $47.430
   └─ Coloca novo BUY @ $46.500
   └─ Status: REBALANCING

14:15 - Preço BTC = $46.800 (dentro do novo range)
   └─ Ordem aberta
   └─ Status: WAITING

14:20 - Preço BTC = $47.500 (FORA do range novamente)
   └─ Sai do range: $47.500 > $47.430
   └─ Bot rebalanceia mais uma vez
   └─ Novo range: $47.025 - $48.975
   └─ Coloca BUY @ $47.500
   └─ Status: REBALANCING

14:25 - Preço BTC = $47.100 (dentro do range)
   └─ Ordem finalmente preenchida! ✅
   └─ Bot comprou 0.000634 BTC @ $47.500
   └─ Custo: $30
   └─ Status: TRADE_OPEN

14:30 - Preço BTC = $47.850 (lucro!)
   └─ P&L: +$22.13 (+73,77%)
   └─ ✅ CLOSE POSITION (ordem de venda enviada)
   └─ Lucro realizado!
   └─ Status: WAITING (pronto para nova ordem)


═════════════════════════════════════════════════════════════════════════════
🧠 LÓGICA DE VIÉS DE MERCADO (BIAS)
═════════════════════════════════════════════════════════════════════════════

O bot detecta bias do mercado através de:

### 1️⃣ Momentum Analysis (análise de momentum)

   Janela de análise: últimas 12 horas (720 minutos por padrão)
   
   Detecção de DROPS (quedas):
   ├─ Se preço caiu 5% em 12h → BEARISH
   ├─ Se preço caiu 10% em 12h → MUITO BEARISH
   └─ Reduz orações nesse período

   Detecção de RALLIES (altas):
   ├─ Se preço subiu 5% em 12h → BULLISH
   ├─ Se preço subiu 10% em 12h → MUITO BULLISH
   └─ Aumenta agressividade

### 2️⃣ Pattern Recognition (reconhecimento de padrões)

   Padrões BULLISH:
   ├─ Hammer (martelo): mecha baixa, corpo no topo
   ├─ Bullish engulfing: vela anterior + vela maior para cima
   ├─ Double bottom: 2 mínimos seguidos
   ├─ Inverse H&S: 3 fundos com meio mais fundo
   └─ Pennant (bandeira): consolidação com breakout para cima

   Padrões BEARISH:
   ├─ Shooting star: mecha alta, corpo em baixo
   ├─ Bearish engulfing: vela anterior + vela maior para baixo
   ├─ Double top: 2 máximos seguidos
   ├─ Head & Shoulders: 3 picos com meio mais alto
   └─ Triangle: consolidação com breakout para baixo

### 3️⃣ ML Signal (se habilitado)

   Modelo treinado prediz:
   ├─ Probabilidade de SUBIDA
   ├─ Probabilidade de QUEDA
   └─ Padrão detectado + confiança

   Regra:
   ├─ Se probability >= 60% → BULLISH
   ├─ Se probability <= 40% → BEARISH
   └─ Senão → NEUTRAL (sem viés)

   ⚠️  ATUALMENTE DESABILITADO (model tem 13 features, dados têm 14)


═════════════════════════════════════════════════════════════════════════════
🎛️  COMO O BOT USA O VIÉS
═════════════════════════════════════════════════════════════════════════════

Com `levels: 1` (single trade):

   Se bias = BULLISH:
   └─ Coloca ordem BUY
   └─ Esperando subida

   Se bias = BEARISH:
   └─ Não coloca ordem (apenas espera)
   └─ Ou sai da posição se tiver

   Se bias = NEUTRAL:
   └─ Coloca ordem BUY mesmo assim
   └─ Segue a lógica de rebalanceamento puro


═════════════════════════════════════════════════════════════════════════════
📈 HISTÓRICO DE PREÇOS & VOLATILIDADE
═════════════════════════════════════════════════════════════════════════════

O bot mantém histórico em memória:

   self.price_history: Deque[tuple[float, float]]
   └─ Armazena (preço, timestamp) dos últimos eventos

Usado para:

   1. Calcular volatilidade:
      └─ Desvio padrão dos últimos 48 preços
      └─ Se alto: expande range
      └─ Se baixo: contrai range

   2. Momentum detection:
      └─ Compara preço de 12h atrás vs agora
      └─ Detecta tendências

   3. Pattern classification:
      └─ Analisa sequência de velas
      └─ Identifica padrões técnicos


═════════════════════════════════════════════════════════════════════════════
🔄 FLUXO COMPLETO DE SINAL
═════════════════════════════════════════════════════════════════════════════

1️⃣  Bot recebe novo preço via WebSocket

2️⃣  MarketData object criado com:
   ├─ asset: "BTC"
   ├─ price: 45000.50
   ├─ volume_24h: 25000000
   └─ timestamp: 2025-12-05 14:05:30

3️⃣  engine.py chama strategy.generate_signals(market_data)

4️⃣  BasicGridStrategy processa:
   ├─ Se state = INITIALIZING → cria primeira grid
   ├─ Se state = ACTIVE:
   │  ├─ Checa _should_rebalance()
   │  ├─ Se sim → chama _rebalance_grid()
   │  └─ Se não → retorna signals vazios
   └─ Também checa exit signals (TP, SL, etc)

5️⃣  Retorna lista de TradingSignal objects:
   └─ Cada signal tem:
      ├─ signal_type: BUY / SELL / CANCEL
      ├─ price: preço da ordem
      ├─ size: quantidade BTC
      ├─ confidence: 0-100%
      └─ metadata: dados adicionais

6️⃣  engine.py recebe signals e envia para exchange

7️⃣  Exchange executa ordens via API Hyperliquid

8️⃣  Bot monitora preenchimento em tempo real


═════════════════════════════════════════════════════════════════════════════
💾 BANCO DE DADOS - COLETA DE DADOS
═════════════════════════════════════════════════════════════════════════════

### Coleta Automática (MongoDB):

   1. **trades** - Cada trade executado
      └─ INSERT quando ordem preenchida
      └─ UPDATE quando fechada

   2. **orders** - Histórico de ordens
      └─ INSERT para cada ordem criada
      └─ UPDATE quando cancelada/preenchida

   3. **market_data** - Snapshot de preços
      └─ INSERT periódico (ex: a cada 1 min)
      └─ Para análise futura

   4. **metrics** - Métricas agregadas
      └─ INSERT a cada hora/dia
      └─ Win rate, profit total, Sharpe ratio, etc

### Exemplo de Trade salvo em DB:

   {
     "_id": ObjectId("6754ab1a2c3d4e5f6g7h8i9j"),
     "symbol": "BTC",
     "strategy": "grid",
     "timeframe": "15m",
     
     "entry_price": 45000.50,
     "exit_price": 45450.75,
     "quantity": 0.000667,
     
     "profit_usd": 30.15,
     "profit_pct": 1.01,
     
     "entry_time": ISODate("2025-12-05T14:05:30Z"),
     "exit_time": ISODate("2025-12-05T14:25:45Z"),
     "duration_minutes": 20,
     
     "status": "closed",
     "reason": "TP_HIT" | "SL_HIT" | "MANUAL" | "MAX_DRAWDOWN"
   }


═════════════════════════════════════════════════════════════════════════════
🚀 PRÓXIMOS PASSOS DE OTIMIZAÇÃO
═════════════════════════════════════════════════════════════════════════════

1. **Ativar ML Signal** (quando modelo for corrigido)
   └─ Fechar quando modelo tiver 14 features corretos
   └─ Então descomente ML_MODEL_PATH em .env

2. **Multi-level Grid** (levels > 1)
   └─ Coloca 5-10 ordens em vez de 1
   └─ Captura trades em diferentes preços

3. **Dynamic Position Sizing**
   └─ Ajusta tamanho conforme volatilidade
   └─ Menor em alta volatilidade

4. **Advanced Risk Management**
   └─ Take profit escalonado
   └─ Trailing stop loss

5. **Backtesting Framework**
   └─ Testar strategy em dados históricos
   └─ Otimizar parâmetros

═════════════════════════════════════════════════════════════════════════════
