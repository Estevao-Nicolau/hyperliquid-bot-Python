"""
Pattern backtest utility using cached pattern_signals.

Allows measuring how often each pattern would have dado gain/stop em um
intervalo específico (ex.: últimas 2 semanas), com estatísticas rápidas
para o trader analisar.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, Any

from infrastructure.db import get_mongo_db


def format_percent(value: float, width: int = 6, decimals: int = 2) -> str:
    formatted = f"{value*100:{width}.{decimals}f}"
    return formatted.replace(".", ",")


def parse_date(text: str) -> datetime:
    """Parse DD/MM/AAAA para datetime em UTC."""
    return datetime.strptime(text, "%d/%m/%Y").replace(tzinfo=timezone.utc)


def load_stats(
    start: datetime,
    end: datetime,
    symbol: str,
    timeframe: str,
) -> Dict[str, Dict[str, Any]]:
    """Aggregate stats from pattern_signals between start/end."""

    db = get_mongo_db()
    collection = db["pattern_signals"]
    cursor = collection.find(
        {
            "symbol": symbol,
            "timeframe": timeframe,
            "entry_time": {
                "$gte": int(start.timestamp() * 1000),
                "$lt": int(end.timestamp() * 1000),
            },
        }
    )

    stats: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "total": 0,
            "hits": 0,
            "stops": 0,
            "open": 0,
            "positive": 0,
            "sum_return": 0.0,
        }
    )

    for doc in cursor:
        pattern = doc["pattern"]
        rec = stats[pattern]
        rec["total"] += 1
        ret = float(doc.get("return", 0.0))
        rec["sum_return"] += ret
        if ret > 0:
            rec["positive"] += 1
        outcome = doc.get("outcome")
        if outcome == "target":
            rec["hits"] += 1
        elif outcome == "stop":
            rec["stops"] += 1
        else:
            rec["open"] += 1

    return stats


def format_stats(stats: Dict[str, Dict[str, Any]], top: int) -> str:
    """Format aggregated stats sorted by positive rate then avg return."""

    rows = []
    for pattern, rec in stats.items():
        total = rec["total"]
        if total == 0:
            continue
        pos_rate = rec["positive"] / total
        avg_return = rec["sum_return"] / total
        rows.append(
            (
                pattern,
                total,
                rec["hits"],
                rec["stops"],
                rec["open"],
                pos_rate,
                avg_return,
            )
        )

    rows.sort(key=lambda r: (r[5], r[6]), reverse=True)

    lines = []
    for pattern, total, hits, stops, open_cnt, pos_rate, avg_return in rows[:top]:
        lines.append(
            f"{pattern:>24}: {total:4d} sinais | ganhos>0 {format_percent(pos_rate, 6, 2)}% "
            f"| hits {hits:3d} | stops {stops:3d} | pend {open_cnt:3d} "
            f"| retorno médio {format_percent(avg_return, 7, 3)}%"
        )
    return "\n".join(lines) if lines else "Nenhum sinal no intervalo selecionado."


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Avaliar padrões gravados em pattern_signals para um intervalo."
    )
    parser.add_argument("--symbol", default="BTC")
    parser.add_argument("--timeframe", default="15m")
    parser.add_argument(
        "--start",
        required=False,
        help="Data inicial DD/MM/AAAA (default: fim - dias)",
    )
    parser.add_argument(
        "--end",
        required=False,
        help="Data final DD/MM/AAAA (default: agora)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=15,
        help="Intervalo em dias usado se start/end não forem definidos.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Quantos padrões mostrar ordenados pelo melhor desempenho.",
    )
    args = parser.parse_args()

    if args.end:
        end = parse_date(args.end)
    else:
        end = datetime.now(timezone.utc)
    if args.start:
        start = parse_date(args.start)
    else:
        start = end - timedelta(days=args.days)

    stats = load_stats(start, end, args.symbol, args.timeframe)

    def fmt_br(dt: datetime) -> str:
        return dt.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M")

    print(
        f"Período analisado: {fmt_br(start)} → {fmt_br(end)} "
        f"(gain/stop conforme pattern_snapshot)"
    )
    print(format_stats(stats, args.top))


if __name__ == "__main__":
    main()
