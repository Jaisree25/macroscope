"""GDELT source spec. HTTP mocked — themes are fixed (design §5)."""

from __future__ import annotations

import pytest

from data_plane.sources.gdelt import GDELT_THEMES, GdeltSource


def test_one_series_per_theme():
    ids = set(GdeltSource().series_ids())
    assert ids == {f"tone.{t}" for t in GDELT_THEMES}
    assert {"tone.fed", "tone.inflation", "tone.jobs", "tone.trade"} == ids


def test_all_series_are_news_pattern():
    assert all(m.release_pattern == "news" for m in GdeltSource().describe())


@pytest.mark.skip(reason="TODO(P1): fetch reduces interval to one point/theme, value=tone, metadata.volume")
async def test_fetch_returns_tone_and_volume():
    ...
