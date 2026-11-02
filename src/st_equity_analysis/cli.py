"""Command-line interface for Qlib research and Backtrader backtests."""

from __future__ import annotations

import argparse
from datetime import date, timedelta

from .analysis import build_observations, format_percent, summarize_prices
from .backtest import run_backtest
from .qlib_data import export_qlib_csv, load_qlib_bars
from .visualization import save_price_chart


DEFAULT_PROVIDER = "~/.qlib/qlib_data/cn_data"


def _add_qlib_arguments(parser: argparse.ArgumentParser) -> None:
    today = date.today()
    parser.add_argument("symbol", help="Qlib 股票代码，例如 SH600000 或 SZ000001")
    parser.add_argument("--start", default=(today - timedelta(days=365)).isoformat(), help="起始日期 YYYY-MM-DD")
    parser.add_argument("--end", default=today.isoformat(), help="结束日期 YYYY-MM-DD")
    parser.add_argument("--provider-uri", default=DEFAULT_PROVIDER, help="Qlib 中国日频数据目录")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Qlib 研究与 Backtrader 回测工具")
    commands = parser.add_subparsers(dest="command", required=True)

    research = commands.add_parser("research", help="分析 Qlib 历史价格指标")
    _add_qlib_arguments(research)

    export = commands.add_parser("export", help="将 Qlib OHLCV 导出为回测 CSV")
    _add_qlib_arguments(export)
    export.add_argument("--output", required=True, help="输出 CSV 文件路径")

    visualize = commands.add_parser("visualize", help="直接读取 Qlib 行情并绘制价格图")
    _add_qlib_arguments(visualize)
    visualize.add_argument("--output", required=True, help="输出图表文件路径")

    backtest = commands.add_parser("backtest", help="使用 Backtrader 运行双均线示例策略")
    backtest.add_argument("csv", help="由 export 命令生成的 OHLCV CSV")
    backtest.add_argument("--fast", type=int, default=10, help="快均线周期，默认 10")
    backtest.add_argument("--slow", type=int, default=30, help="慢均线周期，默认 30")
    backtest.add_argument("--cash", type=float, default=100_000, help="初始资金，默认 100000")
    backtest.add_argument("--commission", type=float, default=0.001, help="单边佣金率，默认 0.001")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        if args.command == "research":
            bars = load_qlib_bars(args.symbol, args.start, args.end, args.provider_uri)
            summary = summarize_prices(bars["close"])
            print(f"\n{args.symbol.upper()} 价格研究")
            print(f"数据区间：{args.start} 至 {bars.index[-1].date()}  |  样本：{summary.observations} 个交易日")
            print(f"最近收盘：{summary.latest_close:.2f}")
            print(f"20 日收益：{format_percent(summary.return_20d)}")
            print(f"60 日收益：{format_percent(summary.return_60d)}")
            print(f"20 日年化波动率：{format_percent(summary.volatility_20d)}")
            print(f"60 日最大回撤：{format_percent(summary.max_drawdown_60d)}")
            print("\n观察提示")
            for note in build_observations(summary):
                print(f"- {note}")
        elif args.command == "export":
            output = export_qlib_csv(args.symbol, args.start, args.end, args.provider_uri, args.output)
            print(f"已导出 {args.symbol.upper()} 的 OHLCV 数据：{output}")
        elif args.command == "visualize":
            bars = load_qlib_bars(args.symbol, args.start, args.end, args.provider_uri)
            output = save_price_chart(bars, args.symbol, args.output)
            print(f"已生成 {args.symbol.upper()} 的 Qlib 行情图：{output}")
        else:
            summary = run_backtest(args.csv, args.fast, args.slow, args.cash, args.commission)
            print("\nBacktrader 双均线回测")
            print(f"初始资金：{summary.starting_cash:,.2f}")
            print(f"期末资产：{summary.ending_value:,.2f}")
            print(f"区间收益：{format_percent(summary.total_return)}")
            print(f"最大回撤：{format_percent(summary.max_drawdown)}")
    except (ValueError, RuntimeError, FileNotFoundError) as error:
        raise SystemExit(f"运行失败：{error}") from error
    print("\n仅供学习研究参考，不构成投资建议。")


if __name__ == "__main__":
    main()