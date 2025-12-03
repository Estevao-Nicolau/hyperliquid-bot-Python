import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.enhanced_config import (
    EnhancedBotConfig,
    AccountConfig,
    GridConfig,
    RiskManagementConfig,
    RiskLevel,
    AutoPriceRangeConfig,
    AutoPositionSizingConfig,
)


class TestEnhancedConfigValidation:
    """Test configuration validation and constraints"""

    def test_valid_minimal_config(self):
        """Test loading a valid minimal configuration"""
        config_dict = {
            "name": "test_bot",
            "active": True,
            "exchange": {"type": "hyperliquid", "testnet": True},
            "account": {"max_allocation_pct": 20.0, "risk_level": "moderate"},
            "grid": {
                "symbol": "BTC",
                "levels": 15,
                "price_range": {
                    "mode": "auto",
                    "auto": {
                        "range_pct": 10.0,
                        "min_range_pct": 5.0,
                        "max_range_pct": 25.0,
                    },
                },
                "position_sizing": {
                    "mode": "auto",
                    "auto": {"balance_reserve_pct": 50.0, "max_single_position_pct": 10.0},
                },
            },
            "risk_management": {
                "max_drawdown_pct": 15.0,
                "max_position_size_pct": 30.0,
                "stop_loss_enabled": False,
                "take_profit_enabled": False,
            },
        }

        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        config.validate()
        assert config.name == "test_bot"
        assert config.grid.symbol == "BTC"

    def test_account_max_allocation_pct_too_low(self):
        """Test that max_allocation_pct < 1.0 fails"""
        config_dict = {
            "name": "test_bot",
            "account": {"max_allocation_pct": 0.5},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="max_allocation_pct must be between"):
            config.validate()

    def test_account_max_allocation_pct_too_high(self):
        """Test that max_allocation_pct > 100.0 fails"""
        config_dict = {
            "name": "test_bot",
            "account": {"max_allocation_pct": 150.0},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="max_allocation_pct must be between"):
            config.validate()

    def test_grid_levels_too_low(self):
        """Test that grid.levels < 1 fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {"levels": 0},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="levels must be between"):
            config.validate()

    def test_grid_levels_too_high(self):
        """Test that grid.levels > 50 fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {"levels": 100},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="levels must be between"):
            config.validate()

    def test_price_range_auto_range_pct_too_low(self):
        """Test that auto.range_pct < 1.0 fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "price_range": {
                    "mode": "auto",
                    "auto": {"range_pct": 0.5},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="range_pct must be between"):
            config.validate()

    def test_price_range_auto_range_pct_too_high(self):
        """Test that auto.range_pct > 50.0 fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "price_range": {
                    "mode": "auto",
                    "auto": {"range_pct": 75.0},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="range_pct must be between"):
            config.validate()

    def test_price_range_auto_incoherent_range_pct(self):
        """Test that range_pct outside [min_range_pct, max_range_pct] fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "price_range": {
                    "mode": "auto",
                    "auto": {
                        "range_pct": 3.0,
                        "min_range_pct": 5.0,
                        "max_range_pct": 25.0,
                    },
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="range_pct must be between"):
            config.validate()

    def test_price_range_manual_min_max_invalid(self):
        """Test that manual.min >= manual.max fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "price_range": {
                    "mode": "manual",
                    "manual": {"min": 100.0, "max": 50.0},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="min price must be less than max"):
            config.validate()

    def test_price_range_manual_negative_prices(self):
        """Test that negative prices fail"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "price_range": {
                    "mode": "manual",
                    "manual": {"min": -100.0, "max": 50.0},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="prices must be positive"):
            config.validate()

    def test_risk_management_stop_loss_pct_invalid_when_enabled(self):
        """Test that stop_loss_pct outside [1.0, 20.0] fails when enabled"""
        config_dict = {
            "name": "test_bot",
            "risk_management": {
                "stop_loss_enabled": True,
                "stop_loss_pct": 0.5,
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="stop_loss_pct must be between"):
            config.validate()

    def test_risk_management_take_profit_pct_invalid_when_enabled(self):
        """Test that take_profit_pct outside [5.0, 100.0] fails when enabled"""
        config_dict = {
            "name": "test_bot",
            "risk_management": {
                "take_profit_enabled": True,
                "take_profit_pct": 2.0,
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="take_profit_pct must be between"):
            config.validate()

    def test_risk_management_max_drawdown_pct_invalid(self):
        """Test that max_drawdown_pct outside [5.0, 50.0] fails"""
        config_dict = {
            "name": "test_bot",
            "risk_management": {"max_drawdown_pct": 2.0},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="max_drawdown_pct must be between"):
            config.validate()

    def test_allocation_vs_reserve_conflict(self):
        """Test that max_allocation_pct conflicts with balance_reserve_pct"""
        config_dict = {
            "name": "test_bot",
            "account": {"max_allocation_pct": 80.0},
            "grid": {
                "position_sizing": {
                    "mode": "auto",
                    "auto": {"balance_reserve_pct": 70.0},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="max_allocation_pct.*conflicts"):
            config.validate()

    def test_private_key_format_valid_with_0x(self):
        """Test that valid private key with 0x prefix passes"""
        config_dict = {
            "name": "test_bot",
            "private_key": "0x" + "a" * 64,
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        config.validate()
        assert config.private_key == "0x" + "a" * 64

    def test_private_key_format_valid_without_0x(self):
        """Test that valid private key without 0x prefix passes"""
        config_dict = {
            "name": "test_bot",
            "private_key": "a" * 64,
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        config.validate()
        assert config.private_key == "a" * 64

    def test_private_key_format_invalid_length(self):
        """Test that invalid private key length is warned (not failed)"""
        config_dict = {
            "name": "test_bot",
            "private_key": "0x" + "a" * 32,
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        config.validate()

    def test_empty_bot_name_fails(self):
        """Test that empty bot name fails"""
        config_dict = {
            "name": "",
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="Bot name cannot be empty"):
            config.validate()

    def test_balance_reserve_pct_too_low(self):
        """Test that balance_reserve_pct < 10.0 fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "position_sizing": {
                    "mode": "auto",
                    "auto": {"balance_reserve_pct": 5.0},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="balance_reserve_pct must be between"):
            config.validate()

    def test_balance_reserve_pct_too_high(self):
        """Test that balance_reserve_pct > 90.0 fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "position_sizing": {
                    "mode": "auto",
                    "auto": {"balance_reserve_pct": 95.0},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="balance_reserve_pct must be between"):
            config.validate()

    def test_max_single_position_pct_invalid(self):
        """Test that max_single_position_pct outside [1.0, 50.0] fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "position_sizing": {
                    "mode": "auto",
                    "auto": {"max_single_position_pct": 0.5},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="max_single_position_pct must be between"):
            config.validate()

    def test_min_position_size_usd_invalid(self):
        """Test that min_position_size_usd <= 0 fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "position_sizing": {
                    "mode": "auto",
                    "auto": {"min_position_size_usd": 0.0},
                }
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="min_position_size_usd must be positive"):
            config.validate()

    def test_rebalance_price_move_threshold_invalid(self):
        """Test that rebalance price_move_threshold_pct outside [5.0, 50.0] fails"""
        config_dict = {
            "name": "test_bot",
            "risk_management": {
                "rebalance": {"price_move_threshold_pct": 2.0}
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="price_move_threshold_pct must be between"):
            config.validate()

    def test_rebalance_cooldown_minutes_invalid(self):
        """Test that rebalance cooldown_minutes < 1 fails"""
        config_dict = {
            "name": "test_bot",
            "risk_management": {
                "rebalance": {"cooldown_minutes": 0}
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="cooldown_minutes must be at least"):
            config.validate()

    def test_monitoring_log_level_invalid(self):
        """Test that invalid log_level fails"""
        config_dict = {
            "name": "test_bot",
            "monitoring": {"log_level": "INVALID"},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="log_level must be"):
            config.validate()

    def test_monitoring_report_interval_invalid(self):
        """Test that report_interval_minutes < 1 fails"""
        config_dict = {
            "name": "test_bot",
            "monitoring": {"report_interval_minutes": 0},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="report_interval_minutes must be at least"):
            config.validate()

    def test_exchange_type_empty_fails(self):
        """Test that empty exchange type fails"""
        config_dict = {
            "name": "test_bot",
            "exchange": {"type": ""},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="exchange type cannot be empty"):
            config.validate()

    def test_grid_symbol_empty_fails(self):
        """Test that empty grid symbol fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {"symbol": ""},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="symbol cannot be empty"):
            config.validate()

    def test_grid_timeframe_empty_fails(self):
        """Test that empty grid timeframe fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {"timeframe": ""},
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="timeframe cannot be empty"):
            config.validate()

    def test_position_sizing_mode_invalid(self):
        """Test that invalid position_sizing mode fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "position_sizing": {"mode": "invalid"}
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="mode must be"):
            config.validate()

    def test_price_range_mode_invalid(self):
        """Test that invalid price_range mode fails"""
        config_dict = {
            "name": "test_bot",
            "grid": {
                "price_range": {"mode": "invalid"}
            },
        }
        config = EnhancedBotConfig._dict_to_dataclass(config_dict)
        with pytest.raises(ValueError, match="mode must be"):
            config.validate()
