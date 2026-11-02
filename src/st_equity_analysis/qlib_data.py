"""Qlib provider access and export to a Backtrader-compatible CSV."""

from __future__ import annotations

from pathlib import Path


FIELDS = ["$open", "$high", "$low", "$close", "$volume"]


def load_qlib_bars(symbol: str, start: str, end: str, provider_uri: str):
    try:
        import pandas as pd
        import qlib
        from qlib.constant import REG_CN
        from qlib.data import D
    except ImportError as error:
        raise RuntimeError("未安装 Qlib 依赖，请先运行 pip install -e '.[dev]'") from error

    instrument = symbol.upper()
    qlib.init(provider_uri=str(Path(provider_uri).expanduser()), region=REG_CN)
    bars = D.features(
        [instrument],
        FIELDS,
        start_time=start,
        end_time=end,
        freq="day",
    )
    if bars.empty or not set(FIELDS).issubset(bars.columns):
        raise RuntimeError(f"没有读取到 {instrument} 在 {start} 至 {end} 期间的 OHLCV 数据")
    if isinstance(bars.index, pd.MultiIndex) and "instrument" in bars.index.names:
        bars = bars.xs(instrument, level="instrument")

    bars = bars.sort_index().rename(
        columns={
            "$open": "open",
            "$high": "high",
            "$low": "low",
            "$close": "close",
            "$volume": "volume",
        }
    )
    bars.index = pd.to_datetime(bars.index)
    bars.index.name = "date"
    bars = bars[["open", "high", "low", "close", "volume"]].dropna()
    if bars.empty:
        raise RuntimeError(f"{instrument} 的 OHLCV 数据为空")
    return bars.astype(float)


def export_qlib_csv(symbol: str, start: str, end: str, provider_uri: str, output: str) -> Path:
    bars = load_qlib_bars(symbol, start, end, provider_uri)
    destination = Path(output).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    bars.to_csv(destination, index_label="date", date_format="%Y-%m-%d")
    return destination