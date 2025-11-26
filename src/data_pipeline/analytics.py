"""
Quick analytics helpers powered by MongoDB.

Usage examples:
    uv run python -m src.data_pipeline.analytics --yearly-highs
    uv run python -m src.data_pipeline.analytics --monthly-highs
"""

from __future__ import annotations

import argparse
from typing import List, Dict, Any, Optional

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from infrastructure.db import get_mongo_db  # noqa: E402


def format_currency(value: float) -> str:
    """
    Format floats using the requested style ($123.456,78).
    """

    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"${formatted}"


def _aggregate(
    group_fields: Dict[str, Any],
    sort_fields: Dict[str, int],
    year_filter: Optional[int] = None,
) -> List[Dict[str, Any]]:
    db = get_mongo_db()
    pipeline = [
        {"$match": {"symbol": "BTC", "timeframe": "15m"}},
        {"$addFields": group_fields},
        {
            "$group": {
                "_id": {key: f"${key}" for key in group_fields.keys()},
                "max_close": {"$max": "$close"},
                "max_time": {"$first": "$open_time"},
            }
        },
    ]
    if year_filter is not None:
        pipeline.append({"$match": {"_id.year": year_filter}})
    pipeline.append({"$sort": sort_fields})
    return list(db["candles"].aggregate(pipeline))


def yearly_highs(year: Optional[int] = None) -> List[Dict[str, Any]]:
    return _aggregate(
        {"year": {"$year": {"$toDate": "$open_time"}}}, {"_id.year": 1}, year_filter=year
    )


def monthly_highs(year: Optional[int] = None) -> List[Dict[str, Any]]:
    return _aggregate(
        {
            "year": {"$year": {"$toDate": "$open_time"}},
            "month": {"$month": {"$toDate": "$open_time"}},
        },
        {"_id.year": 1, "_id.month": 1},
        year_filter=year,
    )


def daily_highs(year: Optional[int] = None) -> List[Dict[str, Any]]:
    return _aggregate(
        {
            "year": {"$year": {"$toDate": "$open_time"}},
            "month": {"$month": {"$toDate": "$open_time"}},
            "day": {"$dayOfMonth": {"$toDate": "$open_time"}},
        },
        {"_id.year": 1, "_id.month": 1, "_id.day": 1},
        year_filter=year,
    )


def format_date(idx: Dict[str, Any]) -> str:
    year = idx.get("year")
    month = idx.get("month")
    day = idx.get("day")

    if day is not None and month is not None:
        return f"{day:02d}/{month:02d}/{year}"
    if month is not None:
        return f"{month:02d}/{year}"
    return str(year)


def main() -> None:
    parser = argparse.ArgumentParser(description="BTC stats explorer")
    parser.add_argument("--yearly-highs", action="store_true", help="Show yearly highs")
    parser.add_argument("--monthly-highs", action="store_true", help="Show monthly highs")
    parser.add_argument("--daily-highs", action="store_true", help="Show daily highs")
    parser.add_argument("--year", type=int, help="Filter results to a specific year")
    args = parser.parse_args()

    if args.yearly_highs:
        rows = yearly_highs(args.year)
    elif args.monthly_highs:
        rows = monthly_highs(args.year)
    elif args.daily_highs:
        rows = daily_highs(args.year)
    else:
        parser.error("Choose one of --yearly-highs/--monthly-highs/--daily-highs")
        return

    for row in rows:
        label = format_date(row["_id"])
        print(f"{label}: max_close={format_currency(row['max_close'])}")


if __name__ == "__main__":
    main()
