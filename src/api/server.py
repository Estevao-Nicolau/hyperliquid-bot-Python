"""
FastAPI server exposing candle data and stats for downstream consumers.

Run with:
    uv run uvicorn src.api.server:app --reload
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from typing import List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from infrastructure.db import get_mongo_db  # noqa: E402


class Candle(BaseModel):
    symbol: str
    timeframe: str
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class HighEntry(BaseModel):
    year: int
    month: Optional[int] = None
    day: Optional[int] = None
    max_close: float


app = FastAPI(title="Hyperliquid Data API")


@app.get("/candles", response_model=List[Candle])
def get_candles(
    symbol: str = "BTC",
    timeframe: str = "15m",
    limit: int = Query(500, gt=0, le=5000),
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
):
    db = get_mongo_db()
    query = {"symbol": symbol, "timeframe": timeframe}
    if start_time:
        query["open_time"] = {"$gte": start_time}
    if end_time:
        query.setdefault("open_time", {}).update({"$lte": end_time})

    cursor = (
        db["candles"]
            .find(query)
            .sort("open_time", -1)
            .limit(limit)
    )
    candles = list(cursor)
    return candles


def _aggregate_highs(granularity: str) -> List[HighEntry]:
    db = get_mongo_db()
    date_expr = {"$toDate": "$open_time"}
    group_fields = {"year": {"$year": date_expr}}
    sort_fields = {"_id.year": 1}

    if granularity in {"monthly", "daily"}:
        group_fields["month"] = {"$month": date_expr}
        sort_fields["_id.month"] = 1
    if granularity == "daily":
        group_fields["day"] = {"$dayOfMonth": date_expr}
        sort_fields["_id.day"] = 1

    pipeline = [
        {"$match": {"symbol": "BTC", "timeframe": "15m"}},
        {"$addFields": group_fields},
        {
            "$group": {
                "_id": {k: f"${k}" for k in group_fields.keys()},
                "max_close": {"$max": "$close"},
            }
        },
        {"$sort": sort_fields},
    ]
    rows = db["candles"].aggregate(pipeline)

    entries = []
    for row in rows:
        idx = row["_id"]
        entries.append(
            HighEntry(
                year=idx["year"],
                month=idx.get("month"),
                day=idx.get("day"),
                max_close=row["max_close"],
            )
        )
    return entries


@app.get("/stats/highs/yearly", response_model=List[HighEntry])
def highs_yearly():
    return _aggregate_highs("yearly")


@app.get("/stats/highs/monthly", response_model=List[HighEntry])
def highs_monthly():
    return _aggregate_highs("monthly")


@app.get("/stats/highs/daily", response_model=List[HighEntry])
def highs_daily():
    return _aggregate_highs("daily")
