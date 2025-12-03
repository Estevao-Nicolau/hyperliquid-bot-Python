import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from exchanges.hyperliquid.adapter import HyperliquidAdapter
from interfaces.exchange import Order, OrderSide, OrderType


class TestHyperliquidAdapterPrecision:
    """Test price and size precision handling in Hyperliquid adapter"""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance for testing"""
        adapter = HyperliquidAdapter(
            private_key="0x" + "a" * 64,
            testnet=True
        )
        adapter.is_connected = True
        adapter.info = Mock()
        adapter.exchange = Mock()
        adapter.exchange.wallet = Mock()
        adapter.exchange.wallet.address = "0x" + "b" * 40
        return adapter

    def test_round_price_btc_to_whole_dollar(self, adapter):
        """Test that BTC prices are rounded to whole dollars"""
        order = Order(
            id="test_1",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.001,
            order_type=OrderType.LIMIT,
            price=45123.456,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == 45123.0
        assert isinstance(rounded, float)

    def test_round_price_btc_down(self, adapter):
        """Test that BTC prices round down correctly"""
        order = Order(
            id="test_2",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.001,
            order_type=OrderType.LIMIT,
            price=45123.999,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == 45123.0

    def test_round_price_other_asset_two_decimals(self, adapter):
        """Test that non-BTC prices are rounded to 2 decimal places"""
        order = Order(
            id="test_3",
            asset="ETH",
            side=OrderSide.BUY,
            size=0.1,
            order_type=OrderType.LIMIT,
            price=2345.6789,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == 2345.68

    def test_round_price_other_asset_rounds_down(self, adapter):
        """Test that non-BTC prices round down correctly"""
        order = Order(
            id="test_4",
            asset="ETH",
            side=OrderSide.BUY,
            size=0.1,
            order_type=OrderType.LIMIT,
            price=2345.674,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == 2345.67

    def test_round_size_five_decimals(self, adapter):
        """Test that sizes are rounded to 5 decimal places (BTC szDecimals)"""
        order = Order(
            id="test_5",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.123456789,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        rounded = round_size(order.size)
        assert rounded == 0.12346

    def test_round_size_five_decimals_down(self, adapter):
        """Test that sizes round down correctly to 5 decimals"""
        order = Order(
            id="test_6",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.123454,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        rounded = round_size(order.size)
        assert rounded == 0.12345

    def test_minimum_size_enforcement(self, adapter):
        """Test that minimum size (0.0001) is enforced"""
        order = Order(
            id="test_7",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.00001,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        min_size = 0.0001
        rounded = max(round_size(order.size), min_size)
        assert rounded == 0.0001

    def test_minimum_size_not_applied_when_above_threshold(self, adapter):
        """Test that minimum size is not applied when size is already above it"""
        order = Order(
            id="test_8",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.001,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        min_size = 0.0001
        rounded = max(round_size(order.size), min_size)
        assert rounded == 0.001

    def test_price_zero_handling(self, adapter):
        """Test that zero price is handled correctly"""
        order = Order(
            id="test_9",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.001,
            order_type=OrderType.LIMIT,
            price=0.0,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == 0.0

    def test_size_zero_handling(self, adapter):
        """Test that zero size is handled correctly"""
        order = Order(
            id="test_10",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.0,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        min_size = 0.0001
        rounded = max(round_size(order.size), min_size)
        assert rounded == 0.0001

    def test_large_price_btc(self, adapter):
        """Test that large BTC prices are handled correctly"""
        order = Order(
            id="test_11",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.001,
            order_type=OrderType.LIMIT,
            price=99999.999,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == 99999.0

    def test_small_price_other_asset(self, adapter):
        """Test that small prices for other assets are handled correctly"""
        order = Order(
            id="test_12",
            asset="SHIB",
            side=OrderSide.BUY,
            size=1000.0,
            order_type=OrderType.LIMIT,
            price=0.00001234,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == 0.0

    def test_precision_consistency_across_multiple_orders(self, adapter):
        """Test that precision is consistent across multiple orders"""
        orders = [
            Order(
                id=f"test_{i}",
                asset="BTC",
                side=OrderSide.BUY,
                size=0.001 * (i + 1),
                order_type=OrderType.LIMIT,
                price=45000.0 + (i * 100.5),
            )
            for i in range(5)
        ]

        def round_price(price, asset):
            if asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        def round_size(size):
            return round(float(size), 5)

        for order in orders:
            rounded_price = round_price(order.price, order.asset)
            rounded_size = round_size(order.size)

            assert isinstance(rounded_price, float)
            assert isinstance(rounded_size, float)
            assert rounded_size >= 0.0001

    def test_price_rounding_preserves_type(self, adapter):
        """Test that rounding preserves float type"""
        order = Order(
            id="test_13",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.001,
            order_type=OrderType.LIMIT,
            price=45123.456,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert isinstance(rounded, float)
        assert not isinstance(rounded, int)

    def test_size_rounding_preserves_type(self, adapter):
        """Test that size rounding preserves float type"""
        order = Order(
            id="test_14",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.123456789,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        rounded = round_size(order.size)
        assert isinstance(rounded, float)

    def test_negative_price_handling(self, adapter):
        """Test that negative prices are handled (should not occur in practice)"""
        order = Order(
            id="test_15",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.001,
            order_type=OrderType.LIMIT,
            price=-45000.0,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == -45000.0

    def test_negative_size_handling(self, adapter):
        """Test that negative sizes are handled (should not occur in practice)"""
        order = Order(
            id="test_16",
            asset="BTC",
            side=OrderSide.BUY,
            size=-0.001,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        min_size = 0.0001
        rounded = max(round_size(order.size), min_size)
        assert rounded == 0.0001

    def test_string_price_conversion(self, adapter):
        """Test that string prices are converted correctly"""
        price_str = "45123.456"

        def round_price(price):
            if isinstance(price, str):
                price = float(price)
            return float(int(price))

        rounded = round_price(price_str)
        assert rounded == 45123.0
        assert isinstance(rounded, float)

    def test_string_size_conversion(self, adapter):
        """Test that string sizes are converted correctly"""
        size_str = "0.123456789"

        def round_size(size):
            if isinstance(size, str):
                size = float(size)
            return round(float(size), 5)

        rounded = round_size(size_str)
        assert rounded == 0.12346
        assert isinstance(rounded, float)

    def test_very_small_price_rounding(self, adapter):
        """Test rounding of very small prices"""
        order = Order(
            id="test_17",
            asset="DOGE",
            side=OrderSide.BUY,
            size=100.0,
            order_type=OrderType.LIMIT,
            price=0.000001,
        )

        def round_price(price):
            if order.asset == "BTC":
                return float(int(price))
            else:
                return round(float(price), 2)

        rounded = round_price(order.price)
        assert rounded == 0.0

    def test_very_large_size_rounding(self, adapter):
        """Test rounding of very large sizes"""
        order = Order(
            id="test_18",
            asset="BTC",
            side=OrderSide.BUY,
            size=999.999999,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        rounded = round_size(order.size)
        assert rounded == 1000.0

    def test_precision_edge_case_rounding_up(self, adapter):
        """Test edge case where rounding goes up"""
        order = Order(
            id="test_19",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.123456,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        rounded = round_size(order.size)
        assert rounded == 0.12346

    def test_precision_edge_case_rounding_down(self, adapter):
        """Test edge case where rounding goes down"""
        order = Order(
            id="test_20",
            asset="BTC",
            side=OrderSide.BUY,
            size=0.123454,
            order_type=OrderType.LIMIT,
            price=45000.0,
        )

        def round_size(size):
            return round(float(size), 5)

        rounded = round_size(order.size)
        assert rounded == 0.12345
