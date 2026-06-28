"""Source abstraction + registry — the seam that makes new sources cheap.

A Source knows how to pull raw data from one provider and normalize it into
`SeriesPoint`s. It does NOT know about the store, watchers, or scheduling — the
poller wires those together.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from data_plane.models.series import SeriesMeta, SeriesPoint

# --- Registry --------------------------------------------------------------
_REGISTRY: dict[str, type["Source"]] = {}


def register_source(key: str):
    """Class decorator: register a Source under a stable key ('fred', 'gdelt')."""

    def _decorate(cls: type["Source"]) -> type["Source"]:
        if key in _REGISTRY:
            raise ValueError(f"source key already registered: {key!r}")
        cls.key = key
        _REGISTRY[key] = cls
        return cls

    return _decorate


def get_source(key: str, **kwargs) -> "Source":
    """Instantiate a registered source by key."""
    try:
        cls = _REGISTRY[key]
    except KeyError as exc:
        raise KeyError(f"unknown source: {key!r}; registered: {sorted(_REGISTRY)}") from exc
    return cls(**kwargs)


def registered_sources() -> list[str]:
    return sorted(_REGISTRY)


# --- Interface -------------------------------------------------------------
class Source(ABC):
    """One external data provider, normalized to SeriesPoints.

    Lifecycle (driven by ingestion.poller):
        backfill()  once on first run — fill the trailing window so watchers start warm.
        fetch()     each poll — return new points since `since`.
    """

    key: str = ""  # set by @register_source

    @abstractmethod
    def series_ids(self) -> list[str]:
        """The canonical series this source provides (drives polling + dashboard)."""

    @abstractmethod
    def describe(self) -> list[SeriesMeta]:
        """Series metadata (title, unit, release pattern) for store + dashboard."""

    @abstractmethod
    async def fetch(self, since: datetime | None = None) -> list[SeriesPoint]:
        """Pull new observations at/after `since`. Normalized, deduped per call."""

    async def backfill(self, lookback_days: int) -> list[SeriesPoint]:
        """Historical pull to fill the warm-up window (design §7.5).

        Default: a `fetch` from `now - lookback_days`. Override if the provider
        has a cheaper bulk/history endpoint.
        """
        raise NotImplementedError
