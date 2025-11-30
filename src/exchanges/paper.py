from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Any, Dict

from interfaces.exchange import (
    ExchangeAdapter,
    Order,
    OrderSide,
    OrderType,
    Balance,
    MarketInfo,
)
from interfaces.strategy import Position


class PaperExchange(ExchangeAdapter):
    def __init__(self, symbol: str, initial_balance: float = 100.0):
        super().__init__("PaperExchange")
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.position_size = 0.0
        self.position_price = 0.0
        self.last_price: Optional[float] = None
        self.realized_pnl = 0.0
        self.trade_log: list[dict[str, Any]] = []
        self.reports_dir = Path("paper_reports")
        self.reports_dir.mkdir(exist_ok=True)

    def update_price(self, price: float) -> None:
        self.last_price = price

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    async def disconnect(self) -> None:
        self.is_connected = False
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        report = self.get_summary()
        report["trades"] = self.trade_log
        path = self.reports_dir / f"session_{timestamp}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    async def get_balance(self, asset: str) -> Balance:
        if asset.upper() == "USD":
            return Balance(asset="USD", available=self.cash, locked=0.0, total=self.cash)
        return Balance(asset=asset, available=0.0, locked=0.0, total=0.0)

    async def get_market_price(self, asset: str) -> float:
        if self.last_price is None:
            raise RuntimeError("PaperExchange missing last price")
        return self.last_price

    async def place_order(self, order: Order) -> str:
        price = order.price or self.last_price
        if price is None:
            raise RuntimeError("Price unavailable for paper order")

        size = order.size
        signed = size if order.side == OrderSide.BUY else -size
        cost = price * signed
        self.cash -= cost

        previous_price = self.position_price
        previous_size = self.position_size
        new_size = previous_size + signed

        if previous_size == 0 or previous_size * signed > 0:
            total = abs(previous_size) + abs(signed)
            if total > 0:
                self.position_price = (
                    (previous_price * abs(previous_size) + price * abs(signed))
                    / total
                )
        else:
            closing = min(abs(signed), abs(self.position_size))
            pnl = 0.0
            if closing > 0:
                if previous_size > 0:
                    pnl = closing * (price - previous_price)
                else:
                    pnl = closing * (previous_price - price)
            self.realized_pnl += pnl
            if new_size == 0:
                self.position_price = 0.0
            elif previous_size * new_size < 0:
                self.position_price = price
            else:
                self.position_price = previous_price

        self.position_size = new_size
        trade = {
            "timestamp": time.time(),
            "side": order.side.value,
            "size": order.size,
            "price": price,
            "cash": self.cash,
            "position": self.position_size,
            "realized_pnl": self.realized_pnl,
            "equity": self._equity(),
        }
        self.trade_log.append(trade)
        return f"paper-{len(self.trade_log)}"

    async def cancel_order(self, exchange_order_id: str) -> bool:
        return True

    async def get_order_status(self, exchange_order_id: str) -> Order:
        return Order(
            id=exchange_order_id,
            asset=self.symbol,
            side=OrderSide.BUY,
            size=0.0,
            order_type=OrderType.MARKET,
        )

    async def get_market_info(self, asset: str) -> MarketInfo:
        return MarketInfo(
            symbol=asset,
            base_asset=asset,
            quote_asset="USD",
            min_order_size=0.0001,
            price_precision=2,
            size_precision=5,
            is_active=True,
        )

    async def get_positions(self) -> list[Position]:
        if self.position_size == 0 or self.last_price is None:
            return []
        return [
            Position(
                asset=self.symbol,
                size=self.position_size,
                entry_price=self.position_price,
                current_value=abs(self.position_size) * self.last_price,
                unrealized_pnl=(self.last_price - self.position_price)
                * self.position_size,
                timestamp=time.time(),
            )
        ]

    async def close_position(self, asset: str, size: Optional[float] = None) -> bool:
        if asset != self.symbol or self.position_size == 0:
            return True
        if self.last_price is None:
            raise RuntimeError("Cannot close paper position without price")
        close_amount = min(abs(self.position_size), size) if size else abs(self.position_size)
        side = OrderSide.SELL if self.position_size > 0 else OrderSide.BUY
        order = Order(
            id=f"paper-close-{int(time.time() * 1000)}",
            asset=self.symbol,
            side=side,
            size=close_amount,
            order_type=OrderType.MARKET,
            price=self.last_price,
            created_at=time.time(),
        )
        await self.place_order(order)
        return True

    async def get_account_metrics(self) -> Dict[str, Any]:
        equity = self._equity()
        unrealized = self._unrealized_pnl()
        return {
            "total_value": equity,
            "total_pnl": self.realized_pnl + unrealized,
            "unrealized_pnl": unrealized,
            "realized_pnl": self.realized_pnl,
            "drawdown_pct": 0.0,
            "positions_count": 1 if self.position_size else 0,
            "largest_position_pct": (
                abs(self.position_size * self.last_price) / equity if equity > 0 and self.last_price else 0.0
            ),
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "initial_balance": self.initial_balance,
            "cash": self.cash,
            "equity": self._equity(),
            "position_size": self.position_size,
            "position_price": self.position_price,
            "last_price": self.last_price,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self._unrealized_pnl(),
            "trade_count": len(self.trade_log),
        }

    def _equity(self) -> float:
        exposure = 0.0
        if self.last_price is not None:
            exposure = self.position_size * self.last_price
        return self.cash + exposure

    def _unrealized_pnl(self) -> float:
        if self.position_size == 0 or self.last_price is None:
            return 0.0
        return (self.last_price - self.position_price) * self.position_size
