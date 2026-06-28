"""Poller — one source's fetch → store.upsert → bus.publish_data cycle.

Source-agnostic: it's handed any `Source`, so FRED and GDELT (and future sources)
reuse the same orchestration. Knows nothing about *which* watchers exist.
"""

from __future__ import annotations

from data_plane.events.bus import DataUpdate, EventBus
from data_plane.sources.base import Source
from data_plane.store.base import Store


class Poller:
    def __init__(self, source: Source, store: Store, bus: EventBus) -> None:
        self._source = source
        self._store = store
        self._bus = bus

    async def bootstrap(self, lookback_days: int) -> int:
        """First-run warm-up: register series metadata + backfill history (design §7.5).

        TODO(P1): store.register_series(source.describe());
        points = source.backfill(lookback_days); store.upsert_points(points).
        Do NOT publish_data on bootstrap (no live event spam from history).
        """
        raise NotImplementedError

    async def poll_once(self) -> DataUpdate:
        """One cycle: fetch new points, upsert, publish a DataUpdate.

        TODO(P1):
          - since = store.latest(...) per series (or a watermark).
          - points = await source.fetch(since)
          - written = await store.upsert_points(points)
          - update = DataUpdate(source=source.key, points=points)
          - await bus.publish_data(update); return update.
        """
        raise NotImplementedError
