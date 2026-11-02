"""Backtrader example: long-only moving-average crossover backtest."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BacktestSummary:
    starting_cash: float
    ending_value: float
    total_return: float
    max_drawdown: float


def run_backtest(
    csv_path: str | Path,
    fast: int = 10,
    slow: int = 30,
    cash: float = 100_000,
    commission: float = 0.001,
) -> BacktestSummary:
    if fast < 1 or slow <= fast:
        raise ValueError("均线周期必须满足 1 <= fast < slow")
    if cash <= 0 or commission < 0:
        raise ValueError("初始资金必须大于零，佣金率不能小于零")
    path = Path(csv_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"找不到行情 CSV：{path}")

    try:
        import backtrader as bt
    except ImportError as error:
        raise RuntimeError("未安装 Backtrader，请先运行 pip install -e '.[dev]'") from error

    class SmaCrossStrategy(bt.Strategy):
        params = (("fast", fast), ("slow", slow))

        def __init__(self):
            fast_average = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.fast)
            slow_average = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.slow)
            self.crossover = bt.indicators.CrossOver(fast_average, slow_average)
            self.pending_order = None

        def next(self):
            if self.pending_order:
                return
            if not self.position and self.crossover > 0:
                self.pending_order = self.order_target_percent(target=0.95)
            elif self.position and self.crossover < 0:
                self.pending_order = self.close()

        def notify_order(self, order):
            if order.status in (order.Completed, order.Canceled, order.Margin, order.Rejected):
                self.pending_order = None

    cerebro = bt.Cerebro()
    data = bt.feeds.GenericCSVData(
        dataname=str(path),
        dtformat="%Y-%m-%d",
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
    )
    cerebro.adddata(data)
    cerebro.addstrategy(SmaCrossStrategy)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    starting_cash = cerebro.broker.getvalue()
    results = cerebro.run()
    ending_value = cerebro.broker.getvalue()
    max_drawdown = results[0].analyzers.drawdown.get_analysis().max.drawdown / 100
    total_return = ending_value / starting_cash - 1
    if not math.isfinite(total_return) or not math.isfinite(max_drawdown):
        raise RuntimeError("回测结果不是有限数值，请检查 CSV 行情数据")
    return BacktestSummary(starting_cash, ending_value, total_return, max_drawdown)