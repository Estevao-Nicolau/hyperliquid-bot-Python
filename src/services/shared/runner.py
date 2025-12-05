from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from src.core.enhanced_config import EnhancedConfig
from src.core.engine import TradingEngine
from src.exchanges.hyperliquid.adapter import HyperliquidAdapter
from src.exchanges.hyperliquid.market_data import HyperliquidMarketData
from src.strategies.grid.basic_grid import BasicGridStrategy


def discover_config(config_arg: Optional[str], default_dir: Path) -> Path:
    if config_arg:
        p = Path(config_arg)
        if not p.exists():
            raise FileNotFoundError(f"Config not found: {p}")
        return p
    yamls = sorted(default_dir.glob("*.yaml"))
    if not yamls:
        raise FileNotFoundError(f"No YAML configs in {default_dir}")
    for y in yamls:
        cfg = EnhancedConfig.from_file(y)
        if cfg.active:
            return y
    return yamls[0]


def run(config_path: Path, service_timeframe: Optional[str] = None, validate_only: bool = False) -> int:
    cfg = EnhancedConfig.from_file(config_path)
    if service_timeframe:
        if getattr(cfg, "grid", None) and isinstance(cfg.grid, dict):
            cfg.grid["timeframe"] = service_timeframe
        elif hasattr(cfg, "grid") and hasattr(cfg.grid, "timeframe"):
            setattr(cfg.grid, "timeframe", service_timeframe)
    if validate_only:
        return 0
    market_data = HyperliquidMarketData()
    exchange = HyperliquidAdapter()
    strategy = BasicGridStrategy(cfg)
    engine = TradingEngine(exchange=exchange, market_data=market_data, strategy=strategy, risk_manager=None)
    engine.run()
    return 0


def main(default_config_dir: Path, service_timeframe: Optional[str] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    config_path = discover_config(args.config, default_config_dir)
    return run(config_path, service_timeframe=service_timeframe, validate_only=args.validate)
