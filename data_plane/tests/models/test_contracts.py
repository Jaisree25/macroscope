"""C1/C2 contract shape tests — these must stay green to keep mocks/consumers aligned."""

from __future__ import annotations

from datetime import datetime, timezone

from data_plane.models.event import Event, Severity, WatcherType
from data_plane.models.series import SeriesPoint


def test_series_point_minimal_fields():
    p = SeriesPoint(
        source="fred",
        series_id="CPIAUCSL",
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        value=315.6,
    )
    assert p.source == "fred"
    assert p.metadata == {}
    assert p.ingested_at is None


def test_event_payload_is_self_describing():
    """The explainer must be able to annotate from the Event alone (design §9B)."""
    e = Event(
        watcher=WatcherType.DELTA,
        source="fred",
        series_id="SP500",
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        severity=Severity.NOTABLE,
        magnitude=-2.4,
        value=4800.0,
        threshold=2.0,
        direction="down",
        context={"window": 20, "kind": "return_pct"},
    )
    assert e.severity is Severity.NOTABLE
    assert e.context["kind"] == "return_pct"
