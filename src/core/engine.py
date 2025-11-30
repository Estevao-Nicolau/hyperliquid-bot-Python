"""
Trading Engine

Main orchestration component that connects strategies, exchanges, and infrastructure.
Clean, focused responsibility - no confusing naming like "enhanced" or "advanced".
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from interfaces.strategy import (
    TradingStrategy,
    TradingSignal,
    SignalType,
    MarketData,
    Position,
)
from interfaces.exchange import (
    ExchangeAdapter,
    Order,
    OrderSide,
    OrderType,
    OrderStatus,
)
from exchanges.hyperliquid import HyperliquidMarketData
from core.key_manager import key_manager
from core.risk_manager import RiskManager, RiskEvent, RiskAction, AccountMetrics
from ml.service import MLSignalService
from utils.pattern_helpers import classify_pattern


class TradingEngine:
    """
    Main trading engine that orchestrates everything

    Responsibilities:
    - Connect strategies to market data
    - Execute trading signals via exchange adapters
    - Manage order lifecycle
    - Coordinate between all components

    This is the main "bot" - clean and focused.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False

        # Core components
        self.strategy: Optional[TradingStrategy] = None
        self.exchange: Optional[ExchangeAdapter] = None
        self.market_data: Optional[HyperliquidMarketData] = None
        self.risk_manager: Optional[RiskManager] = None
        self.ml_service: Optional[MLSignalService] = None

        # State tracking
        self.current_positions: List[Position] = []
        self.pending_orders: Dict[str, Order] = {}
        self.executed_trades = 0
        self.total_pnl = 0.0
        self._ml_signal_cache: Optional[Dict[str, Any]] = None
        self._ml_last_eval = 0.0
        ml_config = self.config.get("ml", {}) or {}
        self._ml_enter_threshold = ml_config.get("enter_threshold", 0.6)
        self._ml_exit_threshold = ml_config.get("exit_threshold", 0.4)
        self._ml_eval_interval = ml_config.get("eval_interval", 60)
        self._paper_mode = bool((self.config.get("paper") or {}).get("enabled"))
        self._context_logged = False
        self._pattern_confirmation_required = max(
            1, int(ml_config.get("pattern_confirmation", 1))
        )
        self._pattern_confirmation_name: Optional[str] = None
        self._pattern_confirmation_count = 0
        indicator_filter = ml_config.get("indicator_filter") or {}
        self._indicator_filter_enabled = bool(indicator_filter.get("enabled"))
        self._indicator_filter = {
            "rsi_buy_min": float(indicator_filter.get("rsi_buy_min", 55.0)),
            "rsi_sell_max": float(indicator_filter.get("rsi_sell_max", 45.0)),
            "macd_margin": float(indicator_filter.get("macd_margin", 0.0)),
            "ema_ratio_buffer": float(indicator_filter.get("ema_ratio_buffer", 0.0)),
            "volume_ratio_min": float(indicator_filter.get("volume_ratio_min", 0.0)),
            "bb_width_min": float(indicator_filter.get("bb_width_min", 0.0)),
        }

        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=getattr(logging, config.get("log_level", "INFO")),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    async def initialize(self) -> bool:
        """Initialize all components"""

        try:
            self.logger.info("🚀 Initializing trading engine")

            # Initialize exchange adapter
            if not await self._initialize_exchange():
                return False

            # Initialize market data
            if not await self._initialize_market_data():
                return False

            # Initialize strategy
            if not self._initialize_strategy():
                return False

            # Initialize risk manager
            if not self._initialize_risk_manager():
                return False

            # Initialize ML service if configured
            if not self._initialize_ml_service():
                return False

            self.logger.info("✅ Trading engine initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize trading engine: {e}")
            return False

    async def _initialize_exchange(self) -> bool:
        """Initialize exchange adapter"""

        paper_config = self.config.get("paper", {}) or {}
        exchange_config = self.config.get("exchange", {})
        testnet = exchange_config.get("testnet", True)

        if paper_config.get("enabled"):
            try:
                from exchanges.paper import PaperExchange

                symbol = self.config.get("strategy", {}).get("symbol", "BTC")
                initial_balance = paper_config.get("initial_balance", 100.0)
                self.exchange = PaperExchange(symbol, initial_balance)
                if await self.exchange.connect():
                    self.logger.info(
                        "🧪 Paper trading enabled (balance: $%.2f)", initial_balance
                    )
                    return True
                self.logger.error("❌ Failed to initialize paper exchange")
                return False
            except Exception as exc:
                self.logger.error(f"❌ Failed to enable paper trading: {exc}")
                return False

        try:
            # Get private key using KeyManager
            bot_config = self.config.get("bot_config")  # Optional bot-specific config
            private_key = key_manager.get_private_key(testnet, bot_config)
        except ValueError as e:
            self.logger.error(f"❌ {e}")
            return False

        # Use factory pattern to create exchange adapter
        from exchanges import create_exchange_adapter

        exchange_type = exchange_config.get("type", "hyperliquid")
        exchange_config_with_key = {
            **exchange_config,
            "private_key": private_key,
            "symbol": self.config.get("strategy", {}).get("symbol", "BTC"),
        }
        self.exchange = create_exchange_adapter(exchange_type, exchange_config_with_key)

        if await self.exchange.connect():
            self.logger.info("✅ Exchange adapter connected")
            return True
        else:
            self.logger.error("❌ Failed to connect to exchange")
            return False

    async def _initialize_market_data(self) -> bool:
        """Initialize market data provider"""

        testnet = self.config.get("exchange", {}).get("testnet", True)
        self.market_data = HyperliquidMarketData(testnet)

        if await self.market_data.connect():
            self.logger.info("✅ Market data provider connected")
            return True
        else:
            self.logger.error("❌ Failed to connect to market data")
            return False

    def _initialize_strategy(self) -> bool:
        """Initialize trading strategy"""

        strategy_config = self.config.get("strategy", {})
        strategy_type = strategy_config.get("type", "basic_grid")

        try:
            from strategies import create_strategy

            self.strategy = create_strategy(strategy_type, strategy_config)

            self.strategy.start()
            self.logger.info(f"✅ Strategy initialized: {strategy_type}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize strategy: {e}")
            return False

    def _initialize_risk_manager(self) -> bool:
        """Initialize risk manager"""

        try:
            self.risk_manager = RiskManager(self.config)
            self.logger.info("✅ Risk manager initialized")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize risk manager: {e}")
            return False

    def _initialize_ml_service(self) -> bool:
        """Initialize optional ML signal service"""

        ml_config = self.config.get("ml", {}) or {}
        if not ml_config.get("enabled") or not ml_config.get("model_path"):
            return True

        try:
            self.ml_service = MLSignalService(
                model_path=ml_config["model_path"],
                lookback=ml_config.get("lookback", 48),
                symbol=self.config.get("strategy", {}).get("symbol", "BTC"),
                timeframe=self.config.get("strategy", {}).get("timeframe", "15m"),
                pattern_models=ml_config.get("pattern_models"),
                pattern_gain_pct=ml_config.get("pattern_gain_pct", 0.05),
                pattern_stop_pct=ml_config.get("pattern_stop_pct", 0.05),
                pattern_horizon=ml_config.get("pattern_horizon", 4),
                context_days=ml_config.get("context_days", 7),
            )
            self.logger.info(
                "✅ ML signal service enabled (model: %s)", ml_config["model_path"]
            )
            return True
        except Exception as exc:
            self.logger.error(f"❌ Failed to initialize ML service: {exc}")
            return False

    async def start(self) -> None:
        """Start the trading engine"""

        if not self.strategy or not self.exchange or not self.market_data:
            raise RuntimeError("Engine not initialized")

        self.running = True
        self.logger.info("🎬 Trading engine started")

        # Subscribe to market data for strategy asset
        asset = self.config.get("strategy", {}).get("symbol", "BTC")
        await self.market_data.subscribe_price_updates(asset, self._handle_price_update)

        # Main trading loop
        await self._trading_loop()

    async def stop(self) -> None:
        """Stop the trading engine gracefully"""

        self.running = False
        self.logger.info("🛑 Stopping trading engine")

        # Stop strategy
        if self.strategy:
            self.strategy.stop()

        # Handle positions and orders cleanup
        if self.exchange:
            try:
                # Get current positions before shutdown
                current_positions = await self.exchange.get_positions()

                if current_positions:
                    self.logger.info(
                        f"📊 Found {len(current_positions)} open positions"
                    )

                    # Option 1: Close all positions (more aggressive)
                    # for pos in current_positions:
                    #     await self.exchange.close_position(pos.asset)
                    #     self.logger.info(f"✅ Closed position: {pos.asset}")

                    # Option 2: Just cancel orders and leave positions (more conservative)
                    self.logger.info(
                        "⚠️ Leaving positions open - only cancelling orders"
                    )

                # Cancel all pending orders
                cancelled_orders = await self.exchange.cancel_all_orders()
                if cancelled_orders > 0:
                    self.logger.info(f"✅ Cancelled {cancelled_orders} pending orders")

            except Exception as e:
                self.logger.error(f"❌ Error during cleanup: {e}")

        # Disconnect components
        if self.market_data:
            await self.market_data.disconnect()
        if self.exchange:
            await self.exchange.disconnect()

        self.logger.info("✅ Trading engine stopped")

    async def _handle_price_update(self, market_data: MarketData) -> None:
        """Handle incoming price updates"""

        if not self.running or not self.strategy:
            return

        try:
            update_price = getattr(self.exchange, "update_price", None)
            if callable(update_price):
                update_price(market_data.price)
            # Update current positions from exchange
            self.current_positions = await self.exchange.get_positions()

            # Get current balance
            balance_info = await self.exchange.get_balance(
                "USD"
            )  # Assuming USD balance
            balance = balance_info.available

            # Risk management check
            if self.risk_manager:
                await self._handle_risk_events(market_data)

            ml_signal = await self._evaluate_ml_signal()
            if ml_signal:
                if self.strategy:
                    self.strategy.update_context({"ml_signal": ml_signal})
                if not self._context_logged:
                    self._log_context_overview(ml_signal)
                    self._context_logged = True
                probability = ml_signal.get("probability", 0.0)
                pattern_probs = ml_signal.get("pattern_predictions") or {}
                decision_prob = probability
                best_pattern = None
                if pattern_probs:
                    best_pattern = max(pattern_probs.items(), key=lambda kv: kv[1])
                    decision_prob = best_pattern[1]
                    self.logger.info(
                        "🤖 Melhor padrão %s prob %.3f",
                        best_pattern[0],
                        best_pattern[1],
                    )

                threshold = self._ml_enter_threshold
                if decision_prob < threshold:
                    self._reset_pattern_confirmation()
                    self._log_signal_waiting(
                        market_data,
                        probability,
                        decision_prob,
                        best_pattern[0] if best_pattern else None,
                        ml_signal.get("patterns"),
                        threshold,
                    )
                    return

                best_pattern_name = (
                    best_pattern[0]
                    if best_pattern
                    else ml_signal.get("best_pattern")
                )
                if not best_pattern_name:
                    active_names = [
                        name
                        for name, value in (ml_signal.get("patterns") or {}).items()
                        if value
                    ]
                    if active_names:
                        best_pattern_name = active_names[0]

                if not self._pattern_confirmation_ready(best_pattern_name):
                    return

                if not self._passes_indicator_filter(ml_signal, best_pattern_name):
                    return

            # Generate trading signals from strategy
            signals = self.strategy.generate_signals(
                market_data, self.current_positions, balance
            )

            # Execute signals
            for signal in signals:
                await self._execute_signal(signal)

        except Exception as e:
            self.logger.error(f"❌ Error handling price update: {e}")

    async def _evaluate_ml_signal(self) -> Optional[Dict[str, Any]]:
        """Evaluate ML signal with caching"""

        if not self.ml_service:
            return None

        now = time.time()
        if (
            self._ml_signal_cache
            and now - self._ml_last_eval < self._ml_eval_interval
        ):
            return self._ml_signal_cache

        loop = asyncio.get_running_loop()
        try:
            signal = await loop.run_in_executor(None, self.ml_service.evaluate_signal)
            self._ml_signal_cache = signal
            self._ml_last_eval = now
            probability = signal.get("probability", 0.0)
            active_patterns = [
                name for name, value in (signal.get("patterns") or {}).items() if value
            ]
            pattern_text = ", ".join(active_patterns) if active_patterns else "nenhum"
            detail = ""
            if signal.get("pattern_predictions"):
                best = max(signal["pattern_predictions"].items(), key=lambda kv: kv[1])
                detail = f" | melhor padrão {best[0]}({best[1]:.3f})"
            self.logger.info(
                "🤖 ML sinal: prob %.3f | padrões: %s%s",
                probability,
                pattern_text,
                detail,
            )
            return signal
        except Exception as exc:
            self.logger.warning(f"⚠️ ML signal evaluation failed: {exc}")
            return None

    def _log_signal_waiting(
        self,
        market_data: MarketData,
        probability: float,
        decision_prob: float,
        best_pattern: Optional[str],
        active_patterns: Optional[Dict[str, bool]],
        threshold: float,
    ) -> None:
        """Pretty multi-line block when ML is still waiting for confirmation."""

        candle_time = datetime.fromtimestamp(market_data.timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        pattern_text = best_pattern or "nenhum"
        hints = ", ".join(
            name for name, flag in (active_patterns or {}).items() if flag
        )
        lines = [
            "┌──────── ML aguardando ────────",
            self._format_log_row("Ativo", market_data.asset),
            self._format_log_row("Preço", f"${market_data.price:.2f}"),
            self._format_log_row("Candle", candle_time),
            self._format_log_row("Prob. geral", f"{probability*100:6.2f}%"),
            self._format_log_row("Melhor padrão", pattern_text),
            self._format_log_row("Prob. padrão", f"{decision_prob*100:6.2f}%"),
            self._format_log_row("Threshold", f"{threshold*100:6.2f}%"),
            self._format_log_row("Padrões ativos", hints if hints else "nenhum"),
            "└────────────────────────────────",
        ]
        self.logger.info("\n".join(lines))

    def _format_log_row(self, label: str, value: str) -> str:
        """Consistent column layout for multi-line status blocks."""

        padded = f"{label:<16}"
        return f"│ {padded}│ {value}"

    def _pattern_confirmation_ready(self, best_pattern: Optional[str]) -> bool:
        required = self._pattern_confirmation_required
        if required <= 1:
            return True
        if not best_pattern:
            self._reset_pattern_confirmation()
            self.logger.info("🤖 Aguardando padrão dominante para confirmar entrada")
            return False
        if best_pattern != self._pattern_confirmation_name:
            self._pattern_confirmation_name = best_pattern
            self._pattern_confirmation_count = 1
        else:
            self._pattern_confirmation_count = min(
                required, self._pattern_confirmation_count + 1
            )
        if self._pattern_confirmation_count < required:
            self.logger.info(
                "🤖 Confirmando padrão %s %d/%d",
                best_pattern,
                self._pattern_confirmation_count,
                required,
            )
            return False
        return True

    def _reset_pattern_confirmation(self) -> None:
        self._pattern_confirmation_name = None
        self._pattern_confirmation_count = 0

    def _passes_indicator_filter(
        self, ml_signal: Dict[str, Any], best_pattern: Optional[str]
    ) -> bool:
        if not self._indicator_filter_enabled:
            return True
        snapshot = ml_signal.get("indicator_snapshot") or {}
        if not snapshot:
            self._log_indicator_block("sem indicadores recentes", snapshot)
            return False
        bias = ml_signal.get("pattern_bias") or classify_pattern(best_pattern)
        if not bias:
            return True

        rsi = snapshot.get("rsi_14")
        macd = snapshot.get("macd")
        ema_ratio = snapshot.get("ema_ratio")
        volume_ratio = snapshot.get("volume_ratio")
        bb_width = snapshot.get("bb_width")
        cfg = self._indicator_filter
        if bias == "bullish":
            if rsi is not None and rsi < cfg["rsi_buy_min"]:
                self._log_indicator_block(
                    f"RSI {rsi:.2f} < {cfg['rsi_buy_min']:.2f}", snapshot
                )
                return False
            if macd is not None and macd < cfg["macd_margin"]:
                self._log_indicator_block(
                    f"MACD {macd:.4f} < alvo {cfg['macd_margin']:.4f}", snapshot
                )
                return False
            limit = 1.0 + cfg["ema_ratio_buffer"]
            if ema_ratio is not None and ema_ratio < limit:
                self._log_indicator_block(
                    f"EMA ratio {ema_ratio:.4f} < {limit:.4f}", snapshot
                )
                return False
        elif bias == "bearish":
            if rsi is not None and rsi > cfg["rsi_sell_max"]:
                self._log_indicator_block(
                    f"RSI {rsi:.2f} > {cfg['rsi_sell_max']:.2f}", snapshot
                )
                return False
            if macd is not None and macd > -cfg["macd_margin"]:
                self._log_indicator_block(
                    f"MACD {macd:.4f} > {-cfg['macd_margin']:.4f}", snapshot
                )
                return False
            limit = 1.0 - cfg["ema_ratio_buffer"]
            if ema_ratio is not None and ema_ratio > limit:
                self._log_indicator_block(
                    f"EMA ratio {ema_ratio:.4f} > {limit:.4f}", snapshot
                )
                return False
        if cfg["volume_ratio_min"] > 0 and (
            volume_ratio is None or volume_ratio < cfg["volume_ratio_min"]
        ):
            self._log_indicator_block(
                f"Volume ratio {volume_ratio if volume_ratio is not None else 0:.3f} < {cfg['volume_ratio_min']:.3f}",
                snapshot,
            )
            return False
        if cfg["bb_width_min"] > 0 and (
            bb_width is None or bb_width < cfg["bb_width_min"]
        ):
            self._log_indicator_block(
                f"Bollinger width {bb_width if bb_width is not None else 0:.4f} < {cfg['bb_width_min']:.4f}",
                snapshot,
            )
            return False
        return True

    def _log_indicator_block(
        self, reason: str, snapshot: Optional[Dict[str, Any]]
    ) -> None:
        details = ""
        if snapshot:
            rsi = snapshot.get("rsi_14")
            macd = snapshot.get("macd")
            ema_ratio = snapshot.get("ema_ratio")
            volume_ratio = snapshot.get("volume_ratio")
            bb_width = snapshot.get("bb_width")
            details = ""
            if rsi is not None:
                details += f" | RSI={rsi:.2f}"
            if macd is not None:
                details += f" | MACD={macd:.4f}"
            if ema_ratio is not None:
                details += f" | EMA ratio={ema_ratio:.4f}"
            if volume_ratio is not None:
                details += f" | Vol ratio={volume_ratio:.3f}"
            if bb_width is not None:
                details += f" | BB width={bb_width:.4f}"
        self.logger.info(f"🤖 Indicadores bloquearam entrada: {reason}{details}")

    def _log_context_overview(self, ml_signal: Dict[str, Any]) -> None:
        summary = ml_signal.get("context_summary")
        if not summary:
            return
        candles = summary.get("candles", 0)
        days = candles / 96 if candles else self.config.get("ml", {}).get("context_days", 0)
        ret = summary.get("return", 0.0)
        trend = summary.get("trend", "LATERAL")
        volatility = summary.get("volatility", 0.0)
        high = summary.get("high", 0.0)
        low = summary.get("low", 0.0)
        avg_volume = summary.get("avg_volume", 0.0)
        active = [
            name for name, flag in (ml_signal.get("patterns") or {}).items() if flag
        ]
        lines = [
            "┌──────── Contexto 15d ─────────",
            f"│ Janela analisada: {days:.1f} dias (~{candles} candles)",
            f"│ Tendência: {trend} | Retorno acumulado: {ret*100:6.2f}%",
            f"│ Volatilidade (σ): {volatility:.2f}",
            f"│ Faixa de preço: ${low:.2f} → ${high:.2f}",
            f"│ Volume médio: {avg_volume:.2f}",
            f"│ Padrões recorrentes: {', '.join(active) if active else 'nenhum'}",
            "└───────────────────────────────",
        ]
        self.logger.info("\n".join(lines))

    async def _handle_risk_events(self, market_data: MarketData) -> None:
        """Handle risk management events"""

        try:
            # Get account metrics
            account_metrics_data = await self.exchange.get_account_metrics()
            account_metrics = AccountMetrics(
                total_value=account_metrics_data.get("total_value", 0.0),
                total_pnl=account_metrics_data.get("total_pnl", 0.0),
                unrealized_pnl=account_metrics_data.get("unrealized_pnl", 0.0),
                realized_pnl=account_metrics_data.get("realized_pnl", 0.0),
                drawdown_pct=account_metrics_data.get("drawdown_pct", 0.0),
                positions_count=account_metrics_data.get("positions_count", 0),
                largest_position_pct=account_metrics_data.get(
                    "largest_position_pct", 0.0
                ),
            )

            # Evaluate risk events
            market_data_dict = {market_data.asset: market_data}
            risk_events = self.risk_manager.evaluate_risks(
                self.current_positions, market_data_dict, account_metrics
            )

            # Handle risk events
            for event in risk_events:
                await self._execute_risk_action(event)

        except Exception as e:
            self.logger.error(f"❌ Error handling risk events: {e}")

    async def _execute_risk_action(self, event: RiskEvent) -> None:
        """Execute action based on risk event"""

        try:
            self.logger.warning(f"🚨 Risk Event: {event.reason}")

            if event.action == RiskAction.CLOSE_POSITION:
                success = await self.exchange.close_position(event.asset)
                if success:
                    self.logger.info(f"✅ Position closed for {event.asset}")
                else:
                    self.logger.error(f"❌ Failed to close position for {event.asset}")

            elif event.action == RiskAction.REDUCE_POSITION:
                # For now, close 50% of position
                reduction_pct = 0.5
                current_positions = await self.exchange.get_positions()
                for pos in current_positions:
                    if pos.asset == event.asset:
                        reduce_size = abs(pos.size) * reduction_pct
                        success = await self.exchange.close_position(
                            event.asset, reduce_size
                        )
                        if success:
                            self.logger.info(
                                f"✅ Position reduced by {reduction_pct * 100}% for {event.asset}"
                            )
                        break

            elif event.action == RiskAction.CANCEL_ORDERS:
                cancelled = await self.exchange.cancel_all_orders()
                self.logger.info(f"✅ Cancelled {cancelled} orders")

            elif event.action == RiskAction.PAUSE_TRADING:
                self.logger.critical(f"⏸️ Trading paused due to: {event.reason}")
                if self.strategy:
                    self.strategy.is_active = False

            elif event.action == RiskAction.EMERGENCY_EXIT:
                self.logger.critical(f"🚨 EMERGENCY EXIT: {event.reason}")
                # Get fresh positions from exchange and close all
                current_positions = await self.exchange.get_positions()
                for pos in current_positions:
                    await self.exchange.close_position(pos.asset)
                # Cancel all orders
                await self.exchange.cancel_all_orders()
                # Stop trading
                if self.strategy:
                    self.strategy.is_active = False

        except Exception as e:
            self.logger.error(
                f"❌ Error executing risk action for {event.rule_name}: {e}"
            )

    async def _execute_signal(self, signal: TradingSignal) -> None:
        """Execute a trading signal"""

        try:
            if signal.signal_type in [SignalType.BUY, SignalType.SELL]:
                await self._place_order(signal)
            elif signal.signal_type == SignalType.CLOSE:
                await self._close_positions(signal)

        except Exception as e:
            self.logger.error(f"❌ Error executing signal: {e}")
            # Notify strategy of error
            if self.strategy:
                self.strategy.on_error(e, {"signal": signal})

    async def _place_order(self, signal: TradingSignal) -> None:
        """Place an order based on trading signal"""

        # Create order
        current_time = time.time()
        order = Order(
            id=f"order_{int(current_time * 1000)}",  # Simple ID generation
            asset=signal.asset,
            side=OrderSide.BUY
            if signal.signal_type == SignalType.BUY
            else OrderSide.SELL,
            size=signal.size,
            order_type=OrderType.LIMIT if signal.price else OrderType.MARKET,
            price=signal.price,
            created_at=current_time,
        )

        # Place order with exchange
        exchange_order_id = await self.exchange.place_order(order)
        if exchange_order_id == "filled":
            self.logger.info(
                f"📝 Placed {order.side.value} order: {order.size} {order.asset} (executada imediatamente)"
            )
            if self.strategy:
                executed_price = order.price or 0.0
                self.strategy.on_trade_executed(signal, executed_price, order.size)
            self.executed_trades += 1
        else:
            order.exchange_order_id = exchange_order_id
            order.status = OrderStatus.SUBMITTED
            self.pending_orders[order.id] = order
            self.logger.info(
                f"📝 Placed {order.side.value} order: {order.size} {order.asset} @ ${order.price}"
            )

    async def _close_positions(self, signal: TradingSignal) -> None:
        """Close positions (e.g., cancel all orders for rebalancing)"""

        if signal.metadata.get("action") == "cancel_all":
            cancelled = await self.exchange.cancel_all_orders()
            self.logger.info(f"🗑️ Cancelled {cancelled} orders for rebalancing")

    async def _trading_loop(self) -> None:
        """Main trading loop for periodic tasks"""

        while self.running:
            try:
                # Periodic health checks, order status updates, etc.
                await asyncio.sleep(60)  # Check every minute

                # Update order statuses (simplified)
                await self._update_order_statuses()

                # Log status
                if self.executed_trades > 0:
                    self.logger.info(f"📊 Total trades: {self.executed_trades}")

            except Exception as e:
                self.logger.error(f"❌ Error in trading loop: {e}")
                await asyncio.sleep(60)

    async def _update_order_statuses(self) -> None:
        """Update status of pending orders"""

        # This would query the exchange for order statuses
        # For now, we'll just clean up old orders
        current_time = time.time()

        for order_id in list(self.pending_orders.keys()):
            order = self.pending_orders[order_id]

            # Remove orders older than 1 hour (they're probably filled or cancelled)
            if current_time - order.created_at > 3600:
                del self.pending_orders[order_id]

    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""

        return {
            "running": self.running,
            "strategy": self.strategy.get_status() if self.strategy else None,
            "exchange": self.exchange.get_status() if self.exchange else None,
            "market_data": self.market_data.get_status() if self.market_data else None,
            "risk_manager": self.risk_manager.get_status()
            if self.risk_manager
            else None,
            "executed_trades": self.executed_trades,
            "pending_orders": len(self.pending_orders),
            "current_positions": len(self.current_positions),
            "total_pnl": self.total_pnl,
        }
