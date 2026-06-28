"""The bus fans both notification flows out to all subscribers."""

from __future__ import annotations

from datetime import datetime, timezone

from data_plane.events.bus import DataUpdate, EventBus
from data_plane.models.event import Event, Severity, WatcherType


async def test_publish_data_reaches_every_subscriber(bus: EventBus):
    seen = []
    bus.on_data(lambda u: seen.append(u))  # type: ignore[arg-type]
    bus.on_data(lambda u: seen.append(u))  # type: ignore[arg-type]
    await bus.publish_data(DataUpdate(source="fred", points=[]))
    assert len(seen) == 2


async def test_publish_event_reaches_subscribers(bus: EventBus):
    seen = []
    bus.on_event(lambda e: seen.append(e))  # type: ignore[arg-type]
    e = Event(
        watcher=WatcherType.TONE,
        source="gdelt",
        series_id="tone.fed",
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        severity=Severity.SIGNIFICANT,
        magnitude=-2.5,
        value=-3.0,
        threshold=-2.0,
    )
    await bus.publish_event(e)
    assert seen == [e]
