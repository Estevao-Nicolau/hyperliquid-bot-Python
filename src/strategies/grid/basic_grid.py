"""
Basic Grid Trading Strategy

Simple grid strategy that places buy and sell orders at regular intervals.
This is the main business logic for grid trading.
"""

import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from interfaces.strategy import (
    TradingStrategy,
    TradingSignal,
    SignalType,
    MarketData,
    Position,
)
from utils.pattern_helpers import (
    BULLISH_PATTERNS,
    BEARISH_PATTERNS,
    classify_pattern,
    infer_bias,
)


class GridState(Enum):
    """Grid states"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    REBALANCING = "rebalancing"
    STOPPED = "stopped"


@dataclass
class GridLevel:
    """Individual grid level"""

    price: float
    size: float
    level_index: int
    is_buy_level: bool  # True for buy levels, False for sell levels
    is_filled: bool = False


@dataclass
class GridConfig:
    """Grid configuration"""

    symbol: str
    levels: int = 10
    range_pct: float = 10.0  # ±10% from center price
    total_allocation: float = 1000.0  # USD

    # Price range (auto-calculated if not set)
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    # Rebalancing
    rebalance_threshold_pct: float = 15.0  # Rebalance if price moves 15% outside range


class BasicGridStrategy(TradingStrategy):
    """
    Basic Grid Trading Strategy

    Places buy and sell orders at regular price intervals:
    - Buy orders below current price
    - Sell orders above current price
    - Rebalances when price moves outside range

    Perfect for sideways/ranging markets.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("basic_grid", config)

        # Extract grid config
        self.grid_config = GridConfig(
            symbol=config.get("symbol", "BTC"),
            levels=config.get("levels", 10),
            range_pct=config.get("range_pct", 10.0),
            total_allocation=config.get("total_allocation", 1000.0),
            min_price=config.get("min_price"),
            max_price=config.get("max_price"),
            rebalance_threshold_pct=config.get("rebalance_threshold_pct", 15.0),
        )

        # Grid state
        self.state = GridState.INITIALIZING
        self.center_price: Optional[float] = None
        self.grid_levels: List[GridLevel] = []
        self.last_rebalance_time = 0.0
        self.market_bias: Optional[str] = None
        self.take_profit_pct = config.get("take_profit_pct", 0.05)
        self.stop_loss_pct = config.get("stop_loss_pct", 0.05)
        self.active_trade: Optional[Dict[str, Any]] = None

        # Performance tracking
        self.total_trades = 0
        self.total_profit = 0.0

    def generate_signals(
        self, market_data: MarketData, positions: List[Position], balance: float
    ) -> List[TradingSignal]:
        """Generate grid trading signals"""

        if not self.is_active:
            return []

        current_price = market_data.price

        if self.grid_config.levels == 1:
            return self._generate_single_trade_signals(current_price)

        signals = []

        # Initialize grid on first run
        if self.state == GridState.INITIALIZING:
            signals.extend(self._initialize_grid(current_price, balance))

        # Check if rebalancing is needed
        elif self.state == GridState.ACTIVE and self._should_rebalance(current_price):
            signals.extend(self._rebalance_grid(current_price, balance))

        return signals

    def update_context(self, context: Dict[str, Any]) -> None:
        signal = context.get("ml_signal")
        if not signal:
            self.market_bias = None
            return
        probability = signal.get("probability", 0.0)
        prediction_bias: Optional[str] = signal.get("pattern_bias")
        if not prediction_bias:
            pattern_predictions = signal.get("pattern_predictions") or {}
            if pattern_predictions:
                best_pattern = max(pattern_predictions.items(), key=lambda kv: kv[1])[0]
                prediction_bias = classify_pattern(best_pattern)
            else:
                active = [
                    name for name, flag in (signal.get("patterns") or {}).items() if flag
                ]
                prediction_bias = infer_bias(active)
        if prediction_bias:
            self.market_bias = prediction_bias
            return
        if probability >= 0.6:
            self.market_bias = "bullish"
        elif probability <= 0.4:
            self.market_bias = "bearish"
        else:
            self.market_bias = None

    def _generate_single_trade_signals(self, current_price: float) -> List[TradingSignal]:
        signals: List[TradingSignal] = []
        if self.active_trade:
            exit_signal = self._check_exit_signal(current_price)
            if exit_signal:
                signals.append(exit_signal)
            return signals

        if not self.market_bias:
            return signals

        entry_signal = self._build_entry_signal(current_price)
        if entry_signal:
            signals.append(entry_signal)
            self.state = GridState.ACTIVE
        return signals

    def _build_entry_signal(self, current_price: float) -> Optional[TradingSignal]:
        usd_alloc = self.grid_config.total_allocation
        # Cap por configuração explícita em metadata
        max_usd = self.config.get("max_usd_per_trade")
        if max_usd is not None:
            usd_alloc = float(max_usd)
        if usd_alloc <= 0 or current_price <= 0:
            return None
        size_btc = usd_alloc / current_price
        if self.market_bias == "bullish":
            return TradingSignal(
                signal_type=SignalType.BUY,
                asset=self.grid_config.symbol,
                size=size_btc,
                price=current_price,
                reason="Entrada única (viés de alta)",
                metadata={"trade_role": "entry", "bias": "bullish"},
            )
        if self.market_bias == "bearish":
            return TradingSignal(
                signal_type=SignalType.SELL,
                asset=self.grid_config.symbol,
                size=size_btc,
                price=current_price,
                reason="Entrada única (viés de baixa)",
                metadata={"trade_role": "entry", "bias": "bearish"},
            )
        return None

    def _check_exit_signal(self, current_price: float) -> Optional[TradingSignal]:
        trade = self.active_trade
        if not trade:
            return None

        bias = trade["bias"]
        target = trade["target_price"]
        stop = trade["stop_price"]

        if bias == "bullish":
            if current_price >= target:
                return TradingSignal(
                    signal_type=SignalType.SELL,
                    asset=self.grid_config.symbol,
                    size=trade["size"],
                    price=None,
                    reason="Take-profit 5%",
                    metadata={"trade_role": "exit", "reason": "take_profit"},
                )
            if current_price <= stop:
                return TradingSignal(
                    signal_type=SignalType.SELL,
                    asset=self.grid_config.symbol,
                    size=trade["size"],
                    price=None,
                    reason="Stop automático",
                    metadata={"trade_role": "exit", "reason": "stop_loss"},
                )
        elif bias == "bearish":
            if current_price <= target:
                return TradingSignal(
                    signal_type=SignalType.BUY,
                    asset=self.grid_config.symbol,
                    size=trade["size"],
                    price=None,
                    reason="Take-profit 5%",
                    metadata={"trade_role": "exit", "reason": "take_profit"},
                )
            if current_price >= stop:
                return TradingSignal(
                    signal_type=SignalType.BUY,
                    asset=self.grid_config.symbol,
                    size=trade["size"],
                    price=None,
                    reason="Stop automático",
                    metadata={"trade_role": "exit", "reason": "stop_loss"},
                )
        return None

    def on_trade_executed(
        self, signal: TradingSignal, executed_price: float, executed_size: float
    ) -> None:
        role = signal.metadata.get("trade_role")
        if role == "entry":
            entry_price = executed_price or signal.price or 0.0
            if entry_price <= 0:
                return
            if signal.signal_type == SignalType.BUY:
                target = entry_price * (1 + self.take_profit_pct)
                stop = entry_price * (1 - self.stop_loss_pct)
                bias = "bullish"
            else:
                target = entry_price * (1 - self.take_profit_pct)
                stop = entry_price * (1 + self.stop_loss_pct)
                bias = "bearish"
            self.active_trade = {
                "bias": bias,
                "size": executed_size,
                "entry_price": entry_price,
                "target_price": target,
                "stop_price": stop,
            }
        elif role == "exit":
            self.active_trade = None
            self.state = GridState.INITIALIZING

    def _initialize_grid(
        self, current_price: float, balance: float
    ) -> List[TradingSignal]:
        """Initialize the grid around current price"""

        self.center_price = current_price

        # Calculate price range
        if self.grid_config.min_price is None or self.grid_config.max_price is None:
            range_size = current_price * (self.grid_config.range_pct / 100)
            min_price = current_price - range_size
            max_price = current_price + range_size
        else:
            min_price = self.grid_config.min_price
            max_price = self.grid_config.max_price

        # Create grid levels
        self.grid_levels = self._create_grid_levels(min_price, max_price, current_price)

        # Generate initial signals
        signals = []
        for level in self.grid_levels:
            if level.is_buy_level and level.price < current_price:
                # Buy order below current price
                signals.append(
                    TradingSignal(
                        signal_type=SignalType.BUY,
                        asset=self.grid_config.symbol,
                        size=level.size,
                        price=level.price,
                        reason=f"Grid buy level at ${level.price:.2f}",
                        metadata={
                            "level_index": level.level_index,
                            "grid_type": "initial",
                        },
                    )
                )
            elif not level.is_buy_level and level.price > current_price:
                # Sell order above current price
                signals.append(
                    TradingSignal(
                        signal_type=SignalType.SELL,
                        asset=self.grid_config.symbol,
                        size=level.size,
                        price=level.price,
                        reason=f"Grid sell level at ${level.price:.2f}",
                        metadata={
                            "level_index": level.level_index,
                            "grid_type": "initial",
                        },
                    )
                )

        if signals:
            self.state = GridState.ACTIVE
        return signals

    def _create_grid_levels(
        self, min_price: float, max_price: float, current_price: float
    ) -> List[GridLevel]:
        """Create grid levels with geometric spacing"""

        levels: List[GridLevel] = []
        num_levels = max(1, self.grid_config.levels)
        size_per_level_usd = self.grid_config.total_allocation / num_levels

        if num_levels == 1:
            if self.market_bias == "bearish":
                price = max_price
                is_buy_level = False
            elif self.market_bias == "bullish":
                price = min_price
                is_buy_level = True
            else:
                return []
            size_btc = size_per_level_usd / price
            levels.append(
                GridLevel(
                    price=price,
                    size=size_btc,
                    level_index=0,
                    is_buy_level=is_buy_level,
                )
            )
            return levels

        price_ratio = (max_price / min_price) ** (1 / (num_levels - 1))

        for i in range(num_levels):
            price = min_price * (price_ratio**i)
            size_btc = size_per_level_usd / price
            is_buy_level = price < current_price
            levels.append(
                GridLevel(
                    price=price,
                    size=size_btc,
                    level_index=i,
                    is_buy_level=is_buy_level,
                )
            )

        return levels

    def _should_rebalance(self, current_price: float) -> bool:
        """Check if grid should be rebalanced"""

        if not self.center_price:
            return False

        # Check price movement threshold
        price_move_pct = (
            abs(current_price - self.center_price) / self.center_price * 100
        )

        return price_move_pct > self.grid_config.rebalance_threshold_pct

    def _rebalance_grid(
        self, current_price: float, balance: float
    ) -> List[TradingSignal]:
        """Rebalance grid around new center price"""

        self.state = GridState.REBALANCING

        # Cancel all existing orders (implementation will handle this)
        cancel_signals = [
            TradingSignal(
                signal_type=SignalType.CLOSE,
                asset=self.grid_config.symbol,
                size=0,  # Close all
                reason="Rebalancing grid",
                metadata={"action": "cancel_all"},
            )
        ]

        # Re-initialize grid at new price
        self.state = GridState.INITIALIZING
        init_signals = self._initialize_grid(current_price, balance)

        self.last_rebalance_time = time.time()

        return cancel_signals + init_signals

    def on_trade_executed(
        self, signal: TradingSignal, executed_price: float, executed_size: float
    ) -> None:
        """Handle trade execution"""

        self.total_trades += 1

        # Mark grid level as filled
        level_index = signal.metadata.get("level_index")
        if level_index is not None and level_index < len(self.grid_levels):
            level = self.grid_levels[level_index]
            level.is_filled = True

            # Calculate profit (simplified)
            if signal.signal_type == SignalType.SELL:
                # Estimate profit from buy-sell spread
                buy_price = executed_price * 0.99  # Approximate
                profit = (executed_price - buy_price) * executed_size
                self.total_profit += profit

    def get_status(self) -> Dict[str, Any]:
        """Get grid strategy status"""

        active_levels = sum(1 for level in self.grid_levels if not level.is_filled)
        filled_levels = len(self.grid_levels) - active_levels

        return {
            **super().get_status(),
            "state": self.state.value,  # Generic state key for compatibility
            "grid_state": self.state.value,  # Specific grid state
            "center_price": self.center_price,
            "total_levels": len(self.grid_levels),
            "active_levels": active_levels,
            "filled_levels": filled_levels,
            "total_trades": self.total_trades,
            "total_profit": self.total_profit,
            "last_rebalance": self.last_rebalance_time,
            "config": {
                "symbol": self.grid_config.symbol,
                "levels": self.grid_config.levels,
                "range_pct": self.grid_config.range_pct,
                "total_allocation": self.grid_config.total_allocation,
            },
        }
