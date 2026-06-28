"""Storage layer — the query layer P4's MCP wraps.

`Store` is the contract; the concrete backend is selected by config. Postgres now;
a TimescaleDB / other backend later is just another `Store` subclass.
"""

from __future__ import annotations

from data_plane.store.base import Store

__all__ = ["Store", "make_store"]


def make_store(backend: str | None = None, **kwargs) -> Store:
    """Factory: build the configured Store backend.

    TODO(P1): dispatch on backend ('postgres' -> PostgresStore, 'memory' ->
    InMemoryStore); default from config.settings. Keep callers backend-agnostic.
    """
    raise NotImplementedError
