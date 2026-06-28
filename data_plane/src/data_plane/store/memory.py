"""In-memory Store — fast, dependency-free backend for unit tests and local dev.

Same contract as PostgresStore, so the watcher engine, poller, and bus can be
exercised without a database. The store-contract test suite runs against BOTH
this and Postgres to keep them honest.
"""

from __future__ import annotations

from datetime import datetime

from data_plane.models.event import Event
from data_plane.models.series import SeriesMeta, SeriesPoint
from data_plane.store.base import Store


class InMemoryStore(Store):
    def __init__(self) -> None:
        # (source, series_id) -> list[SeriesPoint] kept sorted by ts
        self._points: dict[tuple[str, str], list[SeriesPoint]] = {}
        self._meta: dict[tuple[str, str], SeriesMeta] = {}
        self._events: dict[str, Event] = {}

    async def init_schema(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def upsert_points(self, points: list[SeriesPoint]) -> int:
        """TODO(P1): dedupe on (source, series_id, ts), keep sorted, return written count."""
        raise NotImplementedError

    async def register_series(self, metas: list[SeriesMeta]) -> None:
        raise NotImplementedError

    async def write_event(self, event: Event) -> None:
        raise NotImplementedError

    async def latest(self, source: str, series_id: str) -> SeriesPoint | None:
        raise NotImplementedError

    async def history(
        self,
        source: str,
        series_id: str,
        *,
        limit: int | None = None,
        since: datetime | None = None,
    ) -> list[SeriesPoint]:
        raise NotImplementedError

    async def list_series(self) -> list[SeriesMeta]:
        raise NotImplementedError

    async def recent_events(
        self, *, series_id: str | None = None, since: datetime | None = None
    ) -> list[Event]:
        raise NotImplementedError
