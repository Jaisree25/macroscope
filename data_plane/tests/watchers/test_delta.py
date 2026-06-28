"""Delta watcher: relative % / bp move AND absolute level crossings."""

from __future__ import annotations

from data_plane.config.thresholds import IndicatorThreshold, Tier
from data_plane.watchers.base import WatcherContext
from data_plane.watchers.delta import DeltaWatcher
from tests.fixtures.series import series_from_values

SP500 = IndicatorThreshold(
    series_id="SP500", watcher="delta", window=60, warmup=20,
    notable=Tier(pct=2.0), significant=Tier(pct=3.0, extra={"drawdown_pct": 10}),
)
VIX = IndicatorThreshold(
    series_id="VIXCLS", watcher="delta", window=20, warmup=20, hysteresis=2.0,
    notable=Tier(level_gt=20, jump_pct=15), significant=Tier(level_gt=30, jump_pct=25),
)


def _ctx(series_id, points):
    return WatcherContext(trigger=points[-1], windows={series_id: points})


def test_sp500_quiet_day_no_event():
    w = DeltaWatcher("SP500", SP500)
    pts = series_from_values("fred", "SP500", [4800 + (i % 2) * 4 for i in range(21)])  # ~<0.1%
    assert w.evaluate(_ctx("SP500", pts)) == []


def test_sp500_three_percent_drop_is_significant():
    w = DeltaWatcher("SP500", SP500)
    pts = series_from_values("fred", "SP500", [4800] * 20 + [4656])  # -3.0%
    events = w.evaluate(_ctx("SP500", pts))
    assert events and events[0].severity.value == "significant"
    assert events[0].direction == "down"


def test_vix_absolute_level_crossing_fires():
    """VIX above 30 trips on level alone, regardless of the day's move size."""
    w = DeltaWatcher("VIXCLS", VIX)
    pts = series_from_values("fred", "VIXCLS", [18] * 20 + [31])
    events = w.evaluate(_ctx("VIXCLS", pts))
    assert events and events[0].severity.value == "significant"
