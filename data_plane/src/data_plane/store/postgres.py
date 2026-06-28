"""Postgres backend (v1 default).

Implements Store over psycopg3 + an async connection pool. Swap to TimescaleDB
by changing schema.sql (hypertable) — this class's queries stay the same.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from data_plane.models.event import Event
from data_plane.models.series import SeriesMeta, SeriesPoint
from data_plane.store.base import Store

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class PostgresStore(Store):
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._pool = None  # psycopg_pool.AsyncConnectionPool, opened in init_schema/connect

    async def init_schema(self) -> None:
        """Open the pool and run schema.sql. TODO(P1)."""
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError

    async def upsert_points(self, points: list[SeriesPoint]) -> int:
        """INSERT ... ON CONFLICT (source, series_id, ts) DO UPDATE. TODO(P1).

        Use executemany / COPY for batches; return rowcount.
        """
        raise NotImplementedError

    async def register_series(self, metas: list[SeriesMeta]) -> None:
        raise NotImplementedError

    async def write_event(self, event: Event) -> None:
        """INSERT ... ON CONFLICT (id) DO NOTHING — idempotent. TODO(P1)."""
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
