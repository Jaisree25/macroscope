"""Tone watcher: volume vs trailing avg AND/OR tone z-score per theme."""

from __future__ import annotations

from data_plane.config.thresholds import IndicatorThreshold, Tier
from data_plane.watchers.base import WatcherContext
from data_plane.watchers.tone import ToneWatcher
from tests.fixtures.series import make_point

THRESH = IndicatorThreshold(
    series_id="tone.fed", watcher="tone", window=14, warmup=7,
    notable=Tier(volume_mult=2, tone_z=-2),
    significant=Tier(volume_mult=3, tone_z=-2),
)


def _window(tones, volumes):
    pts = [make_point("gdelt", "tone.fed", t, day=i, volume=v) for i, (t, v) in enumerate(zip(tones, volumes))]
    return WatcherContext(trigger=pts[-1], windows={"tone.fed": pts})


def test_calm_news_does_not_fire():
    w = ToneWatcher("tone.fed", THRESH)
    ctx = _window([0.1] * 8, [100] * 8)
    assert w.evaluate(ctx) == []


def test_volume_spike_and_negative_tone_is_significant():
    w = ToneWatcher("tone.fed", THRESH)
    ctx = _window([0.0] * 7 + [-3.5], [100] * 7 + [320])  # 3.2x volume AND tone z<=-2
    events = w.evaluate(ctx)
    assert events and events[0].severity.value == "significant"
