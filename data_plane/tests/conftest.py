"""Shared fixtures. Pure-unit tests use the in-memory store; only the store-contract
test reaches for a real Postgres (marked `integration`)."""

from __future__ import annotations

import pytest

from data_plane.events.bus import EventBus
from data_plane.store.memory import InMemoryStore


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
async def memory_store() -> InMemoryStore:
    store = InMemoryStore()
    await store.init_schema()
    return store
