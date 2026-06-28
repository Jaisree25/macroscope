"""Poller wiring: fetch → upsert → publish_data, with a fake source.

Source-agnostic, so a stub Source proves the orchestration without any network.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from data_plane.events.bus import DataUpdate, EventBus
from data_plane.ingestion.poller import Poller
from data_plane.models.series import SeriesMeta, SeriesPoint
from data_plane.sources.base import Source
from data_plane.store.memory import InMemoryStore
from tests.fixtures.series import make_point


class FakeSource(Source):
    key = "fake"

    def __init__(self, points):
        self._points = points

    def series_ids(self):
        return ["X"]

    def describe(self):
        return [SeriesMeta(source="fake", series_id="X", title="X")]

    async def fetch(self, since: datetime | None = None) -> list[SeriesPoint]:
        return self._points

    async def backfill(self, lookback_days: int) -> list[SeriesPoint]:
        return self._points


async def test_poll_once_writes_and_publishes(memory_store: InMemoryStore, bus: EventBus):
    received: list[DataUpdate] = []
    bus.on_data(lambda u: received.append(u))  # type: ignore[arg-type]

    pts = [make_point("fake", "X", 1.0, day=0), make_point("fake", "X", 2.0, day=1)]
    poller = Poller(FakeSource(pts), memory_store, bus)

    update = await poller.poll_once()

    assert update.source == "fake"
    assert len(received) == 1
    assert (await memory_store.latest("fake", "X")).value == 2.0


async def test_bootstrap_backfills_but_does_not_publish(memory_store: InMemoryStore, bus: EventBus):
    """Backfill warms the store without spamming live events off historical data."""
    received = []
    bus.on_data(lambda u: received.append(u))  # type: ignore[arg-type]
    pts = [make_point("fake", "X", float(i), day=i) for i in range(30)]
    poller = Poller(FakeSource(pts), memory_store, bus)

    written = await poller.bootstrap(lookback_days=30)

    assert written == 30
    assert received == []  # no DataUpdate published on bootstrap
