import pytest

from st_equity_analysis.analysis import build_observations, summarize_prices


def test_summarize_flat_then_rising_prices():
    summary = summarize_prices([100] * 60 + [110])

    assert summary.latest_close == 110
    assert summary.observations == 61
    assert summary.return_20d == pytest.approx(0.1)
    assert summary.return_60d == pytest.approx(0.1)
    assert summary.volatility_20d is not None
    assert summary.max_drawdown_60d == 0
    assert any("累计上涨" in note for note in build_observations(summary))


def test_summarize_prices_reports_insufficient_history():
    summary = summarize_prices([100, 101, 99])

    assert summary.return_20d is None
    assert summary.return_60d is None
    assert summary.volatility_20d is None
    assert summary.max_drawdown_60d is None


def test_summarize_prices_calculates_drawdown():
    summary = summarize_prices([100] * 59 + [120, 90])

    assert summary.max_drawdown_60d == pytest.approx(-0.25)


def test_summarize_prices_rejects_invalid_values():
    with pytest.raises(ValueError, match="收盘价"):
        summarize_prices([100, 0, 101])