"""FRED source spec. HTTP is mocked (respx) — no live API in unit tests."""

from __future__ import annotations

import pytest

from data_plane.sources.fred import FRED_SERIES, FredSource


def test_describes_all_seven_indicator_series():
    src = FredSource(api_key="x")
    ids = set(src.series_ids())
    # The design's series set (§4) must all be present.
    assert {"DFF", "CPIAUCSL", "PAYEMS", "UNRATE", "GDPC1", "DGS10", "UMCSENT", "SP500", "VIXCLS"} <= ids
    assert set(m.series_id for m in src.describe()) == set(FRED_SERIES)


def test_release_pattern_routes_watcher():
    metas = {m.series_id: m.release_pattern for m in FredSource(api_key="x").describe()}
    assert metas["CPIAUCSL"] == "release"   # surprise watcher
    assert metas["SP500"] == "continuous"   # delta watcher


@pytest.mark.skip(reason="TODO(P1): implement FredSource.fetch with respx-mocked observations")
async def test_fetch_parses_observations_to_points():
    ...


@pytest.mark.skip(reason="TODO(P1): missing '.' values are skipped, timestamps tz-aware UTC")
async def test_fetch_skips_missing_values():
    ...
