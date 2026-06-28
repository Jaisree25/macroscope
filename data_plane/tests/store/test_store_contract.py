"""Backend-agnostic Store contract.

Every backend must pass this identical suite — that's what makes the DB swappable.
The in-memory backend runs in unit mode; Postgres runs only under `-m integration`
(spins up a container). A future Timescale backend is 'done' when it's green here.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from data_plane.models.series import SeriesMeta, SeriesPoint
from data_plane.store.memory import InMemoryStore


def _point(series_id: str, value: float, day: int) -> SeriesPoint:
    return SeriesPoint(
        source="fred",
        series_id=series_id,
        timestamp=datetime(2025, 1, day + 1, tzinfo=timezone.utc),
        value=value,
    )


async def _store_from_param(request):
    """Param hook: 'memory' always; 'postgres' only when integration is selected.

    TODO(P4/P1): yield a PostgresStore on a testcontainers Postgres for the
    'postgres' param; here we keep the in-memory path wired so the suite is real.
    """
    backend = request.param
    if backend == "memory":
        store = InMemoryStore()
        await store.init_schema()
        return store
    pytest.skip("postgres backend wired by P1 with testcontainers (mark: integration)")


@pytest.fixture(
    params=[
        "memory",
        pytest.param("postgres", marks=pytest.mark.integration),
    ]
)
async def store(request):
    return await _store_from_param(request)


async def test_upsert_is_idempotent(store):
    """Re-writing an overlapping window must not duplicate rows (key: source,series_id,ts)."""
    await store.register_series([SeriesMeta(source="fred", series_id="SP500", title="S&P 500")])
    pts = [_point("SP500", 100, 0), _point("SP500", 101, 1)]
    await store.upsert_points(pts)
    await store.upsert_points(pts)  # same points again
    hist = await store.history("fred", "SP500")
    assert len(hist) == 2


async def test_history_is_ascending_and_windowed(store):
    await store.upsert_points([_point("SP500", float(i), i) for i in range(5)])
    last3 = await store.history("fred", "SP500", limit=3)
    assert [p.value for p in last3] == [2.0, 3.0, 4.0]


async def test_latest_returns_newest(store):
    await store.upsert_points([_point("SP500", 1, 0), _point("SP500", 2, 1)])
    latest = await store.latest("fred", "SP500")
    assert latest is not None and latest.value == 2.0
