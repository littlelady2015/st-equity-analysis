# ST Equity Analysis

一个结合 Microsoft Qlib 与 Backtrader 的 A 股研究和回测起步项目：Qlib 读取本地日频行情、计算价格观察指标并直接绘制图表，也可导出 OHLCV；Backtrader 使用导出的行情运行示例双均线策略。

## 环境安装

需要 Python 3.10 或更高版本。建议使用虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Windows PowerShell 激活命令：`.venv\\Scripts\\Activate.ps1`。

## 准备 Qlib 行情

默认数据目录为 `~/.qlib/qlib_data/cn_data`。按 Qlib 官方说明获取并解压中国日频数据：

```bash
python -m qlib.run get_data qlib_data --target_dir ~/.qlib/qlib_data/cn_data --region cn
```

也可以使用已有的 Qlib 数据目录，在以下命令中通过 `--provider-uri` 指定。代码格式使用 Qlib 市场代码，如 `SH600000`、`SZ000001`。

## 研究

读取 Qlib 收盘价并查看最近收盘价、20/60 日收益、20 日年化波动率及 60 日最大回撤：

```bash
st-equity research SH600000 --start 2023-01-01 --end 2025-01-01
```

## 导出回测数据

从 Qlib 导出 Backtrader 所需的日线 OHLCV CSV：

```bash
st-equity export SH600000 --start 2023-01-01 --end 2025-01-01 --output data/SH600000.csv
```

## Qlib 行情可视化

直接从 Qlib 读取行情并生成收盘价、20/60 日均线和成交量图，无需先导出 CSV：

```bash
st-equity visualize SH600000 --start 2023-01-01 --end 2025-01-01 --output reports/SH600000.png
```

图表输出支持 Matplotlib 支持的格式，例如 PNG、SVG 和 PDF。

## 回测

用 Backtrader 运行示例双均线交叉策略，默认快线 10 日、慢线 30 日、初始资金 100,000、佣金率 0.1%：

```bash
st-equity backtest data/SH600000.csv
```

调整策略与资金参数：

```bash
st-equity backtest data/SH600000.csv --fast 5 --slow 20 --cash 200000 --commission 0.001
```

研究或导出命令可用 `--provider-uri /path/to/cn_data` 指定 Qlib 数据目录。完整参数可通过 `st-equity --help` 及各子命令的 `--help` 查看。

## 测试

```bash
pytest
```

`index.html` 是独立的手工财务指标解读原型，不连接行情源。价格分析和示例回测仅供研究学习，不构成投资建议；实盘前请检查数据覆盖、复权口径、交易成本、停牌及涨跌停等假设。示例均线策略不代表有效交易策略。