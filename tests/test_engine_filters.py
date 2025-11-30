from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.engine import TradingEngine
from interfaces.strategy import TradingStrategy, MarketData


class DummyStrategy(TradingStrategy):
    def __init__(self):
        super().__init__("dummy", {})
        self.calls = 0

    def generate_signals(self, market_data, positions, balance):
        self.calls += 1
        return []


class DummyExchange:
    def update_price(self, price):
        self.price = price

    async def get_positions(self):
        return []

    async def get_balance(self, asset):
        return SimpleNamespace(available=1000.0)


@pytest.mark.asyncio
async def test_pattern_confirmation_blocks_until_reached():
    engine = TradingEngine(
        {
            "log_level": "ERROR",
            "ml": {"enter_threshold": 0.6, "pattern_confirmation": 2},
            "strategy": {"symbol": "BTC"},
        }
    )
    engine.running = True
    engine.strategy = DummyStrategy()
    engine.exchange = DummyExchange()
    engine.risk_manager = None

    market_data = MarketData(asset="BTC", price=50000.0, volume_24h=0.0, timestamp=1.0)
    signal = {
        "probability": 0.72,
        "pattern_predictions": {"double_bottom": 0.72},
        "patterns": {"double_bottom": True},
        "indicator_snapshot": {
            "rsi_14": 60.0,
            "macd": 0.5,
            "ema_ratio": 1.01,
        },
    }

    engine._evaluate_ml_signal = AsyncMock(return_value=signal)

    await engine._handle_price_update(market_data)
    assert engine.strategy.calls == 0

    await engine._handle_price_update(market_data)
    assert engine.strategy.calls == 1


@pytest.mark.asyncio
async def test_indicator_filter_blocks_when_conditions_fail():
    engine = TradingEngine(
        {
            "log_level": "ERROR",
            "ml": {
                "enter_threshold": 0.6,
                "pattern_confirmation": 1,
                "indicator_filter": {
                    "enabled": True,
                    "rsi_buy_min": 55.0,
                    "rsi_sell_max": 45.0,
                    "macd_margin": 0.1,
                    "ema_ratio_buffer": 0.0,
                },
            },
            "strategy": {"symbol": "BTC"},
        }
    )
    engine.running = True
    engine.strategy = DummyStrategy()
    engine.exchange = DummyExchange()
    engine.risk_manager = None

    market_data = MarketData(asset="BTC", price=50000.0, volume_24h=0.0, timestamp=1.0)

    bad_signal = {
        "probability": 0.75,
        "pattern_predictions": {"double_bottom": 0.75},
        "patterns": {"double_bottom": True},
        "indicator_snapshot": {
            "rsi_14": 48.0,
            "macd": 0.05,
            "ema_ratio": 1.0,
        },
    }

    good_signal = {
        "probability": 0.75,
        "pattern_predictions": {"double_bottom": 0.75},
        "patterns": {"double_bottom": True},
        "indicator_snapshot": {
            "rsi_14": 60.0,
            "macd": 0.2,
            "ema_ratio": 1.01,
        },
    }

    engine._evaluate_ml_signal = AsyncMock(side_effect=[bad_signal, good_signal])

    await engine._handle_price_update(market_data)
    assert engine.strategy.calls == 0

    await engine._handle_price_update(market_data)
    assert engine.strategy.calls == 1
