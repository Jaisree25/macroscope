"""Composite watchers (§7.4) — each cross-series rule against fixture series."""

from __future__ import annotations

from data_plane.config.thresholds import CompositeThreshold
from data_plane.watchers.base import WatcherContext
from data_plane.watchers.composites import (
    RiskOffWatcher,
    SahmWatcher,
    StagflationWatcher,
    YieldCurveWatcher,
)
from tests.fixtures.series import make_point, series_from_values


def test_yield_curve_inversion_fires_when_spread_negative():
    w = YieldCurveWatcher(CompositeThreshold(rule="yield_curve", inputs=["DGS10", "DFF"], params={"trigger_lt": 0.0}))
    ctx = WatcherContext(
        trigger=make_point("fred", "DGS10", 4.10),
        windows={
            "DGS10": [make_point("fred", "DGS10", 4.10)],
            "DFF": [make_point("fred", "DFF", 4.25)],   # spread = -0.15
        },
    )
    events = w.evaluate(ctx)
    assert events and events[0].watcher.value == "composite"


def test_yield_curve_normal_does_not_fire():
    w = YieldCurveWatcher(CompositeThreshold(rule="yield_curve", inputs=["DGS10", "DFF"], params={"trigger_lt": 0.0}))
    ctx = WatcherContext(
        trigger=make_point("fred", "DGS10", 4.50),
        windows={"DGS10": [make_point("fred", "DGS10", 4.50)], "DFF": [make_point("fred", "DFF", 3.00)]},
    )
    assert w.evaluate(ctx) == []


def test_sahm_rule_trips_on_half_point_rise():
    w = SahmWatcher(CompositeThreshold(rule="sahm", inputs=["UNRATE"], params={"rise_pp": 0.5, "avg_months": 3, "low_window_months": 12}))
    # 12-mo low ~3.5; recent 3-mo avg ~4.1 → +0.6pp → trips.
    vals = [3.5, 3.5, 3.6, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.0, 4.1, 4.2]
    ctx = WatcherContext(trigger=make_point("fred", "UNRATE", vals[-1], day=11),
                         windows={"UNRATE": series_from_values("fred", "UNRATE", vals)})
    assert w.evaluate(ctx)


def test_risk_off_requires_both_legs_same_day():
    w = RiskOffWatcher(CompositeThreshold(rule="risk_off", inputs=["SP500", "VIXCLS"], params={"sp_down_pct": 2.0, "vix_up_pct": 15.0}))
    ctx = WatcherContext(
        trigger=make_point("fred", "SP500", 4656, day=1),
        windows={
            "SP500": series_from_values("fred", "SP500", [4800, 4656]),    # -3%
            "VIXCLS": series_from_values("fred", "VIXCLS", [18, 22]),      # +22%
        },
    )
    assert w.evaluate(ctx)


def test_stagflation_needs_cpi_up_and_sentiment_down():
    w = StagflationWatcher(CompositeThreshold(rule="stagflation", inputs=["CPIAUCSL", "UMCSENT"], params={"cpi_surprise_up": True, "sentiment_down": True}))
    ctx = WatcherContext(
        trigger=make_point("fred", "CPIAUCSL", 330, day=1),
        windows={
            "CPIAUCSL": series_from_values("fred", "CPIAUCSL", [300] * 12 + [330]),  # surprise up
            "UMCSENT": series_from_values("fred", "UMCSENT", [70] * 12 + [58]),      # down
        },
    )
    assert w.evaluate(ctx)
