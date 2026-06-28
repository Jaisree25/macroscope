"""Surprise watcher: z-score vs trailing window, tiered notable/significant."""

from __future__ import annotations

from data_plane.config.thresholds import IndicatorThreshold, Tier
from data_plane.watchers.base import WatcherContext
from data_plane.watchers.surprise import SurpriseWatcher
from tests.fixtures.series import flat_series, series_from_values, spike_at_end

THRESH = IndicatorThreshold(
    series_id="CPIAUCSL",
    watcher="surprise",
    window=12,
    warmup=12,
    notable=Tier(z=2),
    significant=Tier(z=3),
)


def _ctx(points):
    return WatcherContext(trigger=points[-1], windows={"CPIAUCSL": points})


def test_quiet_series_does_not_fire():
    w = SurpriseWatcher("CPIAUCSL", THRESH)
    pts = flat_series("fred", "CPIAUCSL", 300.0, 13)
    assert w.evaluate(_ctx(pts)) == []


def test_big_print_trips_significant():
    """A print far off the trailing trend → |z|>=3 → significant."""
    w = SurpriseWatcher("CPIAUCSL", THRESH)
    pts = spike_at_end("fred", "CPIAUCSL", base=300.0, n=13, spike=330.0)
    events = w.evaluate(_ctx(pts))
    assert events and events[0].severity.value == "significant"


def test_moderate_print_trips_notable_only():
    w = SurpriseWatcher("CPIAUCSL", THRESH)
    # ~2-sigma move: tune the spike so |z| lands in [2,3).
    pts = series_from_values("fred", "CPIAUCSL", [300, 301, 299, 300, 301, 299, 300, 301, 299, 300, 301, 299, 305])
    events = w.evaluate(_ctx(pts))
    assert events and events[0].severity.value == "notable"
