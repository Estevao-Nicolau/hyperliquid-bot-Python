#!/usr/bin/env python3
"""
Grid Trading Bot Runner

Clean, simple entry point for running grid trading strategies.
No confusing naming - just "run_bot.py".
"""

import asyncio
import argparse
import sys
import os
import signal
from pathlib import Path
import yaml
from typing import Optional

# Load .env file if it exists
from dotenv import load_dotenv

load_dotenv()

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from core.engine import TradingEngine
from core.enhanced_config import EnhancedBotConfig


class GridTradingBot:
    """
    Simple grid trading bot runner

    Clean interface - no "enhanced" or "advanced" confusion.
    Just a bot that runs grid trading strategies.
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None
        self.engine = None
        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}, shutting down...")
        self.running = False
        if self.engine:
            asyncio.create_task(self.engine.stop())

    async def run(self) -> None:
        """Run the bot"""

        try:
            # Load configuration
            print(f"📁 Loading configuration: {self.config_path}")
            self.config = EnhancedBotConfig.from_yaml(Path(self.config_path))
            print(f"✅ Configuration loaded: {self.config.name}")

            # Convert to engine config format
            engine_config = self._convert_config()

            # Initialize trading engine
            self.engine = TradingEngine(engine_config)

            if not await self.engine.initialize():
                print("❌ Failed to initialize trading engine")
                return

            # Start trading
            print(f"🚀 Starting {self.config.name}")
            self.running = True
            await self.engine.start()

        except KeyboardInterrupt:
            print("\n📡 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if self.engine and self.engine.running:
                await self.engine.stop()

    def _convert_config(self) -> dict:
        """Convert EnhancedBotConfig to engine config format"""

        testnet = os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"

        # Calculate total allocation in USD from account balance percentage
        # Note: This is a simplified approach - in production, you'd get actual account balance
        # For now, using a default base amount of $1000 USD
        base_allocation_usd = 1000.0
        total_allocation_usd = base_allocation_usd * (
            self.config.account.max_allocation_pct / 100.0
        )

        ml_model_path = os.getenv("ML_MODEL_PATH")
        pattern_models_env = os.getenv("ML_PATTERN_MODELS")
        pattern_models = {}
        if pattern_models_env:
            entries = [item.strip() for item in pattern_models_env.split(";") if item.strip()]
            for entry in entries:
                if "=" not in entry:
                    continue
                name, path = entry.split("=", 1)
                pattern_models[name.strip()] = path.strip()

        ml_config = {
            "enabled": bool(ml_model_path),
            "model_path": ml_model_path,
            "lookback": int(os.getenv("ML_LOOKBACK", "48")),
            "enter_threshold": float(os.getenv("ML_ENTER_THRESHOLD", "0.6")),
            "exit_threshold": float(os.getenv("ML_EXIT_THRESHOLD", "0.4")),
            "eval_interval": int(os.getenv("ML_EVAL_INTERVAL", "60")),
            "pattern_models": pattern_models,
            "pattern_gain_pct": float(os.getenv("ML_PATTERN_GAIN_PCT", "0.05")),
            "pattern_stop_pct": float(os.getenv("ML_PATTERN_STOP_PCT", "0.05")),
            "pattern_horizon": int(os.getenv("ML_PATTERN_HORIZON", "4")),
            "context_days": int(os.getenv("ML_CONTEXT_DAYS", "7")),
            "pattern_confirmation": int(os.getenv("ML_PATTERN_CONFIRMATIONS", "2")),
            "indicator_filter": {
                "enabled": os.getenv("ML_FILTER_ENABLED", "false").lower() == "true",
                "rsi_buy_min": float(os.getenv("ML_FILTER_RSI_BUY_MIN", "55")),
                "rsi_sell_max": float(os.getenv("ML_FILTER_RSI_SELL_MAX", "45")),
                "macd_margin": float(os.getenv("ML_FILTER_MACD_MARGIN", "0.0")),
                "ema_ratio_buffer": float(os.getenv("ML_FILTER_EMA_RATIO_BUFFER", "0.0")),
                "volume_ratio_min": float(os.getenv("ML_FILTER_VOLUME_RATIO_MIN", "0.0")),
                "bb_width_min": float(os.getenv("ML_FILTER_BB_WIDTH_MIN", "0.0")),
            },
        }
        paper_trading = os.getenv("PAPER_TRADING", "false").lower() == "true"
        paper_cfg = {
            "enabled": paper_trading,
            "initial_balance": float(os.getenv("PAPER_INITIAL_BALANCE", "100.0")),
        }

        return {
            "exchange": {
                "type": self.config.exchange.type,
                "testnet": self.config.exchange.testnet,
            },
            "strategy": {
                "type": "basic_grid",  # Default to basic grid
                "symbol": self.config.grid.symbol,
                "timeframe": getattr(self.config.grid, "timeframe", "15m"),
                "levels": self.config.grid.levels,
                "range_pct": self.config.grid.price_range.auto.range_pct,
                "total_allocation": total_allocation_usd,
                "rebalance_threshold_pct": self.config.risk_management.rebalance.price_move_threshold_pct,
                "take_profit_pct": float(os.getenv("GRID_TAKE_PROFIT_PCT", "0.05")),
                "stop_loss_pct": float(os.getenv("GRID_STOP_LOSS_PCT", "0.05")),
                "max_usd_per_trade": float(os.getenv("GRID_MAX_USD", str(total_allocation_usd))),
            },
            "bot_config": {
                # Pass through the entire config so KeyManager can look for bot-specific keys
                "name": self.config.name,
                "private_key_file": getattr(self.config, "private_key_file", None),
                "testnet_key_file": getattr(self.config, "testnet_key_file", None),
                "mainnet_key_file": getattr(self.config, "mainnet_key_file", None),
                "private_key": getattr(self.config, "private_key", None),
                "testnet_private_key": getattr(
                    self.config, "testnet_private_key", None
                ),
                "mainnet_private_key": getattr(
                    self.config, "mainnet_private_key", None
                ),
            },
            "log_level": self.config.monitoring.log_level,
            "ml": ml_config,
            "paper": paper_cfg,
        }


def find_first_active_config() -> Optional[Path]:
    """Find the first active config in the bots folder"""

    # Look for bots folder relative to the script location
    script_dir = Path(__file__).parent
    bots_dir = script_dir.parent / "bots"

    if not bots_dir.exists():
        return None

    # Scan for YAML files
    yaml_files = list(bots_dir.glob("*.yaml")) + list(bots_dir.glob("*.yml"))

    for yaml_file in sorted(yaml_files):
        try:
            with open(yaml_file, "r") as f:
                data = yaml.safe_load(f)

            # Check if config is active
            if data and data.get("active", False):
                print(f"📁 Found active config: {yaml_file.name}")
                return yaml_file

        except Exception as e:
            print(f"⚠️ Error reading {yaml_file.name}: {e}")
            continue

    return None


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Grid Trading Bot")
    parser.add_argument(
        "config",
        nargs="?",
        help="Configuration file path (optional - will auto-discover if not provided)",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate configuration only"
    )

    args = parser.parse_args()

    # Determine config file
    config_path = None
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"❌ Config file not found: {args.config}")
            return 1
    else:
        # Auto-discover first active config
        print("🔍 No config specified, auto-discovering active config...")
        config_path = find_first_active_config()
        if not config_path:
            print("❌ No active config found in bots/ folder")
            print("💡 Create a config file in bots/ folder with 'active: true'")
            return 1

    if args.validate:
        # Just validate the config
        try:
            config = EnhancedBotConfig.from_yaml(config_path)
            config.validate()
            print("✅ Configuration is valid")
            return 0
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return 1

    # Run the bot
    bot = GridTradingBot(str(config_path))
    await bot.run()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
