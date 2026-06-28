"""Engine: the tuning mechanics watchers deliberately don't do (design §7.5).

These are the highest-value tests — warm-up, cooldown, hysteresis, and the
new-data → evaluate → emit wiring.
"""

from __future__ import annotations

import pytest

from data_plane.config.thresholds import ThresholdConfig
from data_plane.events.bus import DataUpdate, EventBus
from data_plane.store.memory import InMemoryStore
from data_plane.watchers.engine import WatcherEngine


@pytest.fixture
async def engine(memory_store: InMemoryStore, bus: EventBus) -> WatcherEngine:
    # TODO(P1): real ThresholdConfig from a small fixture once load_thresholds lands.
    eng = WatcherEngine(memory_store, bus, ThresholdConfig())
    eng.subscribe()
    return eng


async def test_warmup_suppresses_until_window_filled(engine, memory_store):
    """A z-score watcher must NOT fire before its trailing window is full (§7.5)."""
    pytest.skip("TODO(P1): seed < warmup points, publish DataUpdate, assert no event written")


async def test_cooldown_suppresses_refire(engine, memory_store):
    """After firing on a series, re-firing is suppressed for the cooldown window."""
    pytest.skip("TODO(P1): trip twice within cooldown, assert exactly one event emitted")


async def test_hysteresis_requires_recross_before_rearm(engine):
    """VIX must drop below 28 before '>30' can fire again — no flapping."""
    pytest.skip("TODO(P1): cross 30, stay high, assert single fire; drop<28, re-cross, assert refire")


async def test_new_data_triggers_only_relevant_watchers(engine):
    """A DataUpdate for SP500 shouldn't evaluate the CPI surprise watcher."""
    pytest.skip("TODO(P1): publish SP500 update, assert only delta/risk_off watchers ran")
