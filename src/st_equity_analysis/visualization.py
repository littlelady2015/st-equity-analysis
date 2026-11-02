"""Charts for price data loaded from Qlib."""

from __future__ import annotations

from pathlib import Path


def save_price_chart(bars, symbol: str, output: str) -> Path:
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
    except ImportError as error:
        raise RuntimeError("未安装 Matplotlib，请先运行 pip install -e '.[dev]'") from error

    destination = Path(output).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)

    figure = Figure(figsize=(12, 8), layout="constrained")
    FigureCanvasAgg(figure)
    price_axis, volume_axis = figure.subplots(
        2,
        1,
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )
    close = bars["close"]
    price_axis.plot(bars.index, close, label="Close", linewidth=1.2)
    price_axis.plot(close.rolling(20).mean(), label="MA 20", linewidth=1)
    price_axis.plot(close.rolling(60).mean(), label="MA 60", linewidth=1)
    price_axis.set_title(f"{symbol.upper()} Qlib Price")
    price_axis.set_ylabel("Price")
    price_axis.grid(alpha=0.25)
    price_axis.legend()

    volume_axis.bar(bars.index, bars["volume"], width=1.0, color="tab:blue", alpha=0.55)
    volume_axis.set_ylabel("Volume")
    volume_axis.grid(axis="y", alpha=0.25)
    figure.savefig(destination, dpi=150)
    return destination
