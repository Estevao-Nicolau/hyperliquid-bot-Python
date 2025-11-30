"""
Paper trading session runner that keeps the grid bot online for a fixed duration.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import time
from pathlib import Path
from typing import Optional

from exchanges.paper import PaperExchange
from run_bot import GridTradingBot, find_first_active_config


def _resolve_config(path_arg: Optional[str]) -> Path:
    if path_arg:
        config_path = Path(path_arg).expanduser()
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")
        return config_path
    discovered = find_first_active_config()
    if not discovered:
        raise FileNotFoundError("No active bot configuration found in bots/")
    return discovered


def _apply_environment(args: argparse.Namespace) -> None:
    os.environ["PAPER_TRADING"] = "true"
    os.environ["PAPER_INITIAL_BALANCE"] = str(args.initial_balance)
    os.environ.setdefault("HYPERLIQUID_TESTNET", "true")
    if args.model_path:
        os.environ["ML_MODEL_PATH"] = args.model_path
        os.environ["ML_LOOKBACK"] = str(args.lookback)
        os.environ["ML_ENTER_THRESHOLD"] = str(args.enter_threshold)
        os.environ["ML_EXIT_THRESHOLD"] = str(args.exit_threshold)
        os.environ["ML_EVAL_INTERVAL"] = str(args.eval_interval)


def _print_paper_summary(exchange: PaperExchange, elapsed: float) -> None:
    summary = exchange.get_summary()
    hours = elapsed / 3600.0
    print("\n🧪 Sessão de simulação encerrada")
    print(f"⏱️ Duração: {hours:.2f}h")
    print(f"💵 Saldo inicial: ${summary['initial_balance']:.2f}")
    print(f"💰 Caixa disponível: ${summary['cash']:.2f}")
    print(f"📈 Patrimônio líquido: ${summary['equity']:.2f}")
    print(
        f"📊 PnL realizado: ${summary['realized_pnl']:.2f} | "
        f"PnL não realizado: ${summary['unrealized_pnl']:.2f}"
    )
    if summary["position_size"]:
        direction = "Long" if summary["position_size"] > 0 else "Short"
        print(
            f"📦 Posição aberta: {direction} {abs(summary['position_size']):.4f} @ ${summary['position_price']:.2f}"
        )
    print(f"📝 Trades executados: {summary['trade_count']}")
    report_files = sorted(Path("paper_reports").glob("session_*.json"))
    if report_files:
        print(f"🗂 Report salvo em: {report_files[-1]}")


async def _run_session(args: argparse.Namespace) -> None:
    config_path = _resolve_config(args.config)
    _apply_environment(args)

    bot = GridTradingBot(str(config_path))
    session_task = asyncio.create_task(bot.run())
    timer = asyncio.create_task(asyncio.sleep(args.hours * 3600))
    start = time.time()

    done, pending = await asyncio.wait(
        {session_task, timer}, return_when=asyncio.FIRST_COMPLETED
    )

    if timer in done and session_task not in done:
        print("⏱️ Tempo limite atingido. Encerrando sessão em papel...")
        if bot.engine and bot.engine.running:
            await bot.engine.stop()
        await session_task
    else:
        timer.cancel()

    elapsed = time.time() - start
    if bot.engine and isinstance(bot.engine.exchange, PaperExchange):
        _print_paper_summary(bot.engine.exchange, elapsed)
    else:
        print("Sessão finalizada. Nenhum relatório em papel disponível.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rodar uma sessão em paper trading")
    parser.add_argument(
        "--config",
        help="Configuração YAML (default: primeiro arquivo ativo em bots/)",
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=6.0,
        help="Duração da simulação em horas (default: 6h)",
    )
    parser.add_argument(
        "--initial-balance",
        type=float,
        default=100.0,
        help="Saldo inicial fictício em USD (default: 100)",
    )
    parser.add_argument(
        "--model-path",
        help="Modelo ML principal (opcional, ativa o gate de ML durante a simulação)",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=48,
        help="Lookback usado pelo modelo ML (default: 48)",
    )
    parser.add_argument(
        "--enter-threshold",
        type=float,
        default=0.6,
        help="Threshold de entrada do modelo ML",
    )
    parser.add_argument(
        "--exit-threshold",
        type=float,
        default=0.4,
        help="Threshold de pausa do modelo ML",
    )
    parser.add_argument(
        "--eval-interval",
        type=int,
        default=60,
        help="Intervalo entre avaliações do modelo ML (segundos)",
    )
    args = parser.parse_args()

    try:
        asyncio.run(_run_session(args))
    except KeyboardInterrupt:
        print("\nSessão interrompida pelo usuário.")


if __name__ == "__main__":
    main()
