"""Notification bus for the two data-plane flows.

  1. ingestion --(new SeriesPoints)--> watcher engine
  2. watcher engine --(tripped Event)--> subscribers (store annotation, P2 explainer feed)

Deterministic, in-process pub/sub for v1. Swap for a real broker (Pub/Sub) later
without touching publishers/subscribers.
"""

from data_plane.events.bus import DataUpdate, EventBus

__all__ = ["EventBus", "DataUpdate"]
