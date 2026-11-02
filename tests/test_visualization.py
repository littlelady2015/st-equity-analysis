import pandas as pd

from st_equity_analysis.visualization import save_price_chart


def test_save_price_chart_creates_parent_directories(tmp_path):
    bars = pd.DataFrame(
        {
            "close": [10, 11, 12],
            "volume": [100, 120, 110],
        },
        index=pd.date_range("2025-01-01", periods=3),
    )

    output = save_price_chart(bars, "sh600000", str(tmp_path / "charts" / "price.png"))

    assert output.is_file()
    assert output.stat().st_size > 0
