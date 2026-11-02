"""Price-series statistics and plain-language research observations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PriceSummary:
    latest_close: float
    observations: int
    return_20d: float | None
    return_60d: float | None
    volatility_20d: float | None
    max_drawdown_60d: float | None


def summarize_prices(prices: Iterable[float]) -> PriceSummary:
    """Calculate trailing statistics from chronological closing prices."""
    closes = [float(price) for price in prices]
    if not closes or any(not math.isfinite(price) or price <= 0 for price in closes):
        raise ValueError("收盘价必须是非空且大于零的有限数值序列")

    def period_return(period: int) -> float | None:
        if len(closes) <= period:
            return None
        return closes[-1] / closes[-period - 1] - 1

    volatility = None
    if len(closes) >= 21:
        daily_returns = [
            current / previous - 1
            for previous, current in zip(closes[-21:-1], closes[-20:])
        ]
        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((change - mean_return) ** 2 for change in daily_returns) / (len(daily_returns) - 1)
        volatility = math.sqrt(variance * 252)

    drawdown = None
    if len(closes) >= 61:
        window = closes[-61:]
        peak = window[0]
        drawdown = 0.0
        for close in window:
            peak = max(peak, close)
            drawdown = min(drawdown, close / peak - 1)

    return PriceSummary(
        latest_close=closes[-1],
        observations=len(closes),
        return_20d=period_return(20),
        return_60d=period_return(60),
        volatility_20d=volatility,
        max_drawdown_60d=drawdown,
    )


def format_percent(value: float | None) -> str:
    return "数据不足" if value is None else f"{value:+.2%}"


def build_observations(summary: PriceSummary) -> list[str]:
    notes = []
    if summary.return_60d is not None and summary.return_60d >= 0.10:
        notes.append(f"近 60 个交易日累计上涨 {format_percent(summary.return_60d)}，可结合成交与基本面判断趋势持续性。")
    elif summary.return_60d is not None and summary.return_60d <= -0.10:
        notes.append(f"近 60 个交易日累计下跌 {format_percent(summary.return_60d)}，建议核对区间内经营与市场变化。")
    if summary.volatility_20d is not None and summary.volatility_20d >= 0.50:
        notes.append(f"20 日年化波动率为 {format_percent(summary.volatility_20d)}，近期价格波动较大。")
    if summary.max_drawdown_60d is not None and summary.max_drawdown_60d <= -0.20:
        notes.append(f"60 日最大回撤为 {format_percent(summary.max_drawdown_60d)}，观察区间内出现较深回撤。")
    if not notes:
        notes.append("当前价格序列未触发明显的趋势或波动提示；短期价格指标不等同于公司基本面判断。")
    return notes