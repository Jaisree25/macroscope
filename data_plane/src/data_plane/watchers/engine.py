"""Watcher engine — the stateful orchestrator around the pure watchers.

Subscribes to DataUpdate, evaluates the watchers whose series changed, applies the
tuning mechanics the watchers deliberately DON'T (design §7.5), persists + publishes
surviving events. This is where warm-up / cooldown / hysteresis live so watchers
stay pure and testable.
"""

from __future__ import annotations

from data_plane.config.thresholds import ThresholdConfig
from data_plane.events.bus import DataUpdate, EventBus
from data_plane.models.event import Event
from data_plane.store.base import Store
from data_plane.watchers.base import Watcher


class WatcherEngine:
    def __init__(self, store: Store, bus: EventBus, thresholds: ThresholdConfig) -> None:
        self._store = store
        self._bus = bus
        self._thresholds = thresholds
        self._watchers: list[Watcher] = []
        # series_id -> last fired ts / armed-state for cooldown + hysteresis bookkeeping.
        self._cooldown_state: dict[str, object] = {}
        self._armed_state: dict[str, bool] = {}

    # --- wiring ------------------------------------------------------------
    def register(self, watcher: Watcher) -> None:
        self._watchers.append(watcher)

    @classmethod
    def from_config(cls, store: Store, bus: EventBus, thresholds: ThresholdConfig) -> "WatcherEngine":
        """Build + register every base and composite watcher from the threshold table.

        TODO(P1): for each indicator -> Surprise/Delta/Tone by `watcher` field;
        for each composite -> the matching CompositeWatcher subclass. engine.register(...).
        """
        raise NotImplementedError

    def subscribe(self) -> None:
        """Attach to the bus so new data drives evaluation."""
        self._bus.on_data(self.on_data)

    # --- the loop ----------------------------------------------------------
    async def on_data(self, update: DataUpdate) -> None:
        """For each changed series, evaluate matching watchers and emit survivors.

        TODO(P1):
          - find watchers whose series_ids intersect the update's series.
          - build WatcherContext via store.history(...) for each needed window.
          - skip if window < warmup (WARM-UP).
          - events = watcher.evaluate(ctx).
          - drop events still inside COOLDOWN; apply HYSTERESIS on level crossings.
          - for survivors: await store.write_event(e); await bus.publish_event(e);
            update cooldown/armed state.
        """
        raise NotImplementedError

    # --- tuning mechanics (the engine's job, not the watcher's) ------------
    def _in_cooldown(self, event: Event) -> bool:
        """True if this series fired within its cooldown window. TODO(P1)."""
        raise NotImplementedError

    def _passes_hysteresis(self, event: Event) -> bool:
        """True if a level crossing has re-armed (crossed back by the margin). TODO(P1)."""
        raise NotImplementedError
