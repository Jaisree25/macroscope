"""In-process pub/sub bus.

Two topics, two payload types:
  - "data"  -> DataUpdate (newly-written points)        : poller publishes, engine subscribes
  - "event" -> models.event.Event (a watcher tripped)   : engine publishes, store/P2 subscribe
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from data_plane.models.event import Event
from data_plane.models.series import SeriesPoint


@dataclass
class DataUpdate:
    """A batch of points just written for one source — the engine's trigger."""

    source: str
    points: list[SeriesPoint] = field(default_factory=list)


DataHandler = Callable[[DataUpdate], Awaitable[None]]
EventHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    """Minimal async fan-out. v1: in-memory; later: broker-backed, same surface."""

    def __init__(self) -> None:
        self._data_subs: list[DataHandler] = []
        self._event_subs: list[EventHandler] = []

    # --- subscribe ---------------------------------------------------------
    def on_data(self, handler: DataHandler) -> None:
        """Register a new-data handler (the watcher engine)."""
        self._data_subs.append(handler)

    def on_event(self, handler: EventHandler) -> None:
        """Register a tripped-event handler (store annotation writer, P2 feed)."""
        self._event_subs.append(handler)

    # --- publish -----------------------------------------------------------
    async def publish_data(self, update: DataUpdate) -> None:
        """Fan out a DataUpdate to all data subscribers. TODO(P1): await all handlers."""
        raise NotImplementedError

    async def publish_event(self, event: Event) -> None:
        """Fan out an Event to all event subscribers. TODO(P1): await all handlers."""
        raise NotImplementedError
