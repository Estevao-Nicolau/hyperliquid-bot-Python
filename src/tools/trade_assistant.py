"""
Interactive 15m trade assistant using pattern-specific models.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import time
from pathlib import Path
from typing import Dict, Any

import numpy as np

from infrastructure.db import get_mongo_db
from core.endpoint_router import get_endpoint_router
from hyperliquid.info import Info
from ml.model_store import load_model, MODELS_DIR
from ml.features import compute_indicator_set, INDICATOR_KEYS
from ml.patterns import analyze_patterns

BULLISH_PATTERNS = {
    "hammer",
    "bullish_engulfing",
    "morning_star",
    "double_bottom",
    "inverse_head_and_shoulders",
    "ascending_triangle",
    "pennant",
    "triangle",
    "doji",
}

BEARISH_PATTERNS = {
    "bearish_engulfing",
    "evening_star",
    "double_top",
    "head_and_shoulders",
    "descending_triangle",
    "hanging_man",
}

INTERVAL_MS = 15 * 60 * 1000
BARS_PER_DAY = 96


def fetch_candles_db(symbol: str, timeframe: str, limit: int) -> list[Dict[str, Any]]:
    db = get_mongo_db()
    cursor = (
        db["candles"]
        .find({"symbol": symbol, "timeframe": timeframe})
        .sort("open_time", -1)
        .limit(limit)
    )
    candles = list(cursor)
    candles.reverse()
    return candles


def fetch_pattern_stats(symbol: str, timeframe: str, days: int) -> list[Dict[str, Any]]:
    db = get_mongo_db()
    cutoff_ms = int((time.time() - days * 86400) * 1000)
    cursor = db["pattern_signals"].find(
        {
            "symbol": symbol,
            "timeframe": timeframe,
            "entry_time": {"$gte": cutoff_ms},
        }
    )
    stats: Dict[str, Dict[str, float]] = {}
    for doc in cursor:
        pattern = doc["pattern"]
        entry = stats.setdefault(pattern, {"wins": 0.0, "total": 0.0})
        entry["total"] += 1
        if doc.get("outcome") == "target":
            entry["wins"] += 1
    ranking = []
    for pattern, info in stats.items():
        if info["total"] == 0:
            continue
        ranking.append(
            {
                "pattern": pattern,
                "success": info["wins"] / info["total"],
                "total": int(info["total"]),
            }
        )
    ranking.sort(key=lambda item: item["total"], reverse=True)
    return ranking


def _use_testnet() -> bool:
    return os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"


def _build_info_client() -> Info:
    testnet = _use_testnet()
    router = get_endpoint_router(testnet)
    info_url = router.get_endpoint_for_method("candles") or router.get_endpoint_for_method("meta")
    if not info_url:
        info_url = (
            "https://api.hyperliquid-testnet.xyz/info"
            if testnet
            else "https://api.hyperliquid.xyz/info"
        )
    base_url = info_url[:-5] if info_url.endswith("/info") else info_url
    return Info(base_url, skip_ws=True)


def fetch_live_candles(symbol: str, timeframe: str, limit: int) -> list[Dict[str, Any]]:
    try:
        client = _build_info_client()
        end_ts = int(time.time() * 1000)
        start_ts = end_ts - limit * INTERVAL_MS
        raw = client.candles_snapshot(symbol, timeframe, start_ts, end_ts)
        candles = []
        for entry in raw or []:
            candles.append(
                {
                    "open_time": int(entry.get("T")),
                    "open": float(entry.get("o")),
                    "high": float(entry.get("h")),
                    "low": float(entry.get("l")),
                    "close": float(entry.get("c")),
                }
            )
        candles.sort(key=lambda c: c["open_time"])
        return candles
    except Exception as exc:
        print(f"⚠️ Falha ao buscar candles ao vivo: {exc}")
        return []


def get_candles_with_fallback(symbol: str, timeframe: str, limit: int) -> list[Dict[str, Any]]:
    candles = fetch_candles_db(symbol, timeframe, limit)
    now_ms = int(time.time() * 1000)
    stale = True
    if candles:
        last_end = candles[-1]["open_time"] + INTERVAL_MS
        stale = now_ms - last_end > 30 * 60 * 1000  # 30 minutos
    if not candles or stale:
        live = fetch_live_candles(symbol, timeframe, limit)
        if live:
            return live
    return candles


def load_pattern_models(pattern_map: Dict[str, str]) -> Dict[str, Any]:
    models = {}
    for pattern, path in pattern_map.items():
        p = Path(path)
        if not p.is_absolute():
            p = (MODELS_DIR / p).resolve()
        model = load_model(str(p))
        if model:
            models[pattern] = model
    return models


def evaluate_assistant(
    candles: list[Dict[str, Any]],
    pattern_models: Dict[str, Any],
    gain_pct: float,
    stop_pct: float,
    context_candles: list[Dict[str, Any]],
    weekly_stats: list[Dict[str, Any]],
) -> Dict[str, Any]:
    patterns = analyze_patterns(candles)
    indicators = compute_indicator_set(candles)
    recommendations = []

    for pattern, model in pattern_models.items():
        if not patterns.get(pattern):
            continue

        feature_vector = [indicators[key] for key in INDICATOR_KEYS]
        feature_vector.extend([gain_pct, stop_pct, len(candles), 4])
        prob = model.predict_proba(np.array([feature_vector]))[0][1]
        entry = candles[-1]["close"]

        recommendations.append(
            {
                "pattern": pattern,
                "probability": float(prob),
                "entry": entry,
                "target": entry * (1 + gain_pct),
                "stop": entry * (1 - stop_pct),
            }
        )

    recommendations.sort(key=lambda r: r["probability"], reverse=True)
    if context_candles:
        closes = [c["close"] for c in context_candles]
        weekly_return = (closes[-1] - closes[0]) / max(1e-9, closes[0])
        up_days = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i - 1])
        volatility = np.std(closes) / max(1e-9, np.mean(closes))
    else:
        weekly_return = 0.0
        up_days = 0
        volatility = 0.0

    return {
        "recommendations": recommendations,
        "patterns": patterns,
        "indicators": indicators,
        "current_price": candles[-1]["close"],
        "candle_start": candles[-1]["open_time"],
        "candle_end": candles[-1]["open_time"] + 15 * 60 * 1000,
        "weekly_return": weekly_return,
        "weekly_up_days": up_days,
        "weekly_volatility": volatility,
        "weekly_stats": weekly_stats,
        "staleness_minutes": max(0.0, (time.time() * 1000 - (candles[-1]["open_time"] + 15 * 60 * 1000)) / 60000.0),
    }


def format_recommendations(result: Dict[str, Any]) -> str:
    recs = result["recommendations"]
    candle_start = time.strftime("%Y-%m-%d %H:%M", time.gmtime(result["candle_start"] / 1000))
    candle_end = time.strftime("%H:%M", time.gmtime(result["candle_end"] / 1000))
    weekly_return = result.get("weekly_return", 0.0)
    weekly_volatility = result.get("weekly_volatility", 0.0)
    weekly_stats = result.get("weekly_stats", [])

    trend_text = "ALTA" if weekly_return > 0.01 else "BAIXA" if weekly_return < -0.01 else "LATERAL"
    current_price = result.get("current_price", 0.0)

    lines = [
        f"🕒 Vela analisada: {candle_start} → {candle_end}",
        f"💰 Preço atual BTC: {current_price:.2f}",
        f"📊 Tendência semanal: {trend_text} ({weekly_return*100:.2f}% | vol {weekly_volatility*100:.2f}%)",
        "————————————————————————————"
    ]

    indicators = result.get("indicators", {})
    patterns = result.get("patterns", {})

    if not recs:
        lines.append("⚠️ Nenhum sinal forte agora. Aguarde o fechamento da vela atual.")
        if indicators:
            lines.append("📈 Indicadores:")
            lines.append(
                f"   • RSI: {indicators.get('rsi_14', 0):.1f} | MACD: {indicators.get('macd', 0):.4f}"
            )
            lines.append(
                f"   • ATR: {indicators.get('atr_14', 0):.2f} | Bollinger width: {indicators.get('bb_width', 0):.3f}"
            )
        inactive = [name for name, active in patterns.items() if not active]
        if inactive:
            lines.append(
                "🔍 Padrões observados (sem confirmação): "
                + ", ".join(sorted(inactive)[:5])
            )
        return "\n".join(lines)
    else:
        top = recs[0]
        bias = "ALTA" if top["pattern"] in BULLISH_PATTERNS else "BAIXA" if top["pattern"] in BEARISH_PATTERNS else "NEUTRO"
        strength = "FORTE" if top["probability"] >= 0.7 else "MÉDIO" if top["probability"] >= 0.55 else "FRACO"
        action = "COMPRA (Long)" if bias == "ALTA" else "VENDA (Short)" if bias == "BAIXA" else "AGUARDAR"
        if top["probability"] < 0.5:
            action = "AGUARDAR confirmação"

        lines.append(f"▶️ Ação recomendada: {action}")
        lines.append(
            f"🏁 Padrão dominante: {top['pattern']} — prob {top['probability']:.1%} ({strength})"
        )
        lines.append(f"🎯 Entrada: {top['entry']:.2f} | Alvo: {top['target']:.2f} | Stop: {top['stop']:.2f}")
        lines.append("ℹ️ Se faltar pouco para fechar, aguarde a próxima vela para confirmar.")

        if len(recs) > 1:
            lines.append("\n📌 Outros sinais relevantes:")
            for rec in recs[1:3]:
                sentiment = "ALTA" if rec["pattern"] in BULLISH_PATTERNS else "BAIXA" if rec["pattern"] in BEARISH_PATTERNS else "NEUTRO"
                lines.append(
                    f"   • {rec['pattern']}: prob {rec['probability']:.1%} ({sentiment}) | alvo {rec['target']:.2f} / stop {rec['stop']:.2f}"
                )

    staleness = result.get("staleness_minutes", 0.0)
    if staleness > 30:
        lines.append(f"⚠️ Dados desatualizados ({staleness:.1f} min atrás). Atualize a base de candles.")

    if weekly_stats:
        lines.append("\n📚 Histórico de padrões (últimos dias):")
        for stat in weekly_stats[:3]:
            lines.append(
                f"   • {stat['pattern']}: {stat['success']*100:.1f}% de acerto em {stat['total']} sinais"
            )

    return "\n".join(lines)


async def main_loop(args):
    pattern_map = {}
    for entry in args.pattern_models.split(";"):
        if not entry.strip() or "=" not in entry:
            continue
        pattern, path = entry.split("=", 1)
        pattern_map[pattern.strip()] = path.strip()

    models = load_pattern_models(pattern_map)
    if not models:
        raise RuntimeError("Nenhum modelo de padrão carregado. Configure --pattern-models.")

    context_bars = max(args.lookback, args.context_days * BARS_PER_DAY)
    last_candle_start = None

    while True:
        try:
            candles = get_candles_with_fallback(args.symbol, args.timeframe, context_bars)
            if len(candles) < args.lookback:
                print("Aguardando mais dados...")
            else:
                weekly_stats = fetch_pattern_stats(args.symbol, args.timeframe, args.context_days)
                context_window = candles[-context_bars:]
                recent = candles[-args.lookback :]
                result = evaluate_assistant(
                    recent,
                    models,
                    gain_pct=args.gain,
                    stop_pct=args.stop,
                    context_candles=context_window,
                    weekly_stats=weekly_stats,
                )
                if result["candle_start"] != last_candle_start:
                    last_candle_start = result["candle_start"]
                    print("=" * 60)
                    print(time.strftime("%Y-%m-%d %H:%M:%S"))
                    print(format_recommendations(result))
                else:
                    # Skip repeating same candle analysis
                    pass
        except Exception as exc:
            print(f"Erro ao avaliar sinais: {exc}")

        await asyncio.sleep(args.interval)


def main():
    parser = argparse.ArgumentParser(description="15m pattern trade assistant")
    parser.add_argument("--symbol", default="BTC")
    parser.add_argument("--timeframe", default="15m")
    parser.add_argument("--lookback", type=int, default=48)
    parser.add_argument(
        "--pattern-models",
        required=True,
        help="Formato pattern=model.pkl;pattern2=model2.pkl",
    )
    parser.add_argument("--gain", type=float, default=0.05)
    parser.add_argument("--stop", type=float, default=0.05)
    parser.add_argument("--interval", type=int, default=60, help="Segundos entre análises")
    parser.add_argument("--context-days", type=int, default=7, help="Dias para contexto/tendência")
    args = parser.parse_args()

    asyncio.run(main_loop(args))


if __name__ == "__main__":
    main()
