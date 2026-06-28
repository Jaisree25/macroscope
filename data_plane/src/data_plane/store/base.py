"""Store interface (C1 query layer).

Every backend implements this. Watchers and the dashboard read through it; the
poller writes through it; P4's MCP wraps a read-only subset. Keep it small and
backend-neutral so swapping Postgres -> Timescale is a drop-in.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from data_plane.models.event import Event
from data_plane.models.series import SeriesMeta, SeriesPoint


class Store(ABC):
    # --- lifecycle ---------------------------------------------------------
    @abstractmethod
    async def init_schema(self) -> None:
        """Create tables/indexes if absent (idempotent). Runs schema.sql for Postgres."""

    @abstractmethod
    async def close(self) -> None:
        """Release pools/connections."""

    # --- writes (ingestion) ------------------------------------------------
    @abstractmethod
    async def upsert_points(self, points: list[SeriesPoint]) -> int:
        """Insert/update observations keyed by (source, series_id, timestamp).

        Returns the number of rows written. Must be idempotent so a re-poll of an
        overlapping window doesn't duplicate.
        """

    @abstractmethod
    async def register_series(self, metas: list[SeriesMeta]) -> None:
        """Upsert series metadata (title, unit, release pattern)."""

    @abstractmethod
    async def write_event(self, event: Event) -> None:
        """Persist a tripped-watcher event (idempotent by event identity)."""

    # --- reads (watchers, dashboard, MCP) ----------------------------------
    @abstractmethod
    async def latest(self, source: str, series_id: str) -> SeriesPoint | None:
        """Most recent point for a series, or None."""

    @abstractmethod
    async def history(
        self,
        source: str,
        series_id: str,
        *,
        limit: int | None = None,
        since: datetime | None = None,
    ) -> list[SeriesPoint]:
        """Trailing observations ascending by timestamp — the watcher window source."""

    @abstractmethod
    async def list_series(self) -> list[SeriesMeta]:
        """All registered series (dashboard catalog)."""

    @abstractmethod
    async def recent_events(
        self, *, series_id: str | None = None, since: datetime | None = None
    ) -> list[Event]:
        """Recent events, optionally filtered — dashboard annotations + cooldown checks."""
