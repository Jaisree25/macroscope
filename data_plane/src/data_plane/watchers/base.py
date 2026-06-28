"""Watcher interface + the read context handed to it.

A Watcher is a pure-ish function: given a window of points and its thresholds,
return zero or more Events. It must NOT mutate the store or fire side effects —
the engine owns warm-up/cooldown/hysteresis and emission. This keeps watchers
trivially unit-testable against fixture series (plan §8).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from data_plane.config.thresholds import CompositeThreshold, IndicatorThreshold
from data_plane.models.event import Event
from data_plane.models.series import SeriesPoint


@dataclass
class WatcherContext:
    """Everything a watcher needs for one evaluation, pre-fetched by the engine.

    `windows` maps series_id -> trailing points (ascending). Single-series watchers
    read one entry; composites read several. No store handle = no I/O in watchers.
    """

    trigger: SeriesPoint                      # the point that prompted evaluation
    windows: dict[str, list[SeriesPoint]]     # series_id -> trailing window


class Watcher(ABC):
    """Base class for all watchers."""

    kind: str = ""  # 'surprise' | 'delta' | 'tone' | 'composite'

    @abstractmethod
    def series_ids(self) -> list[str]:
        """Series this watcher reads; the engine pre-fetches their windows."""

    @abstractmethod
    def evaluate(self, ctx: WatcherContext) -> list[Event]:
        """Return Events for any tier tripped this evaluation (may be empty).

        Pure: no store writes, no bus calls, no clock reads beyond ctx timestamps.
        """


class BaseIndicatorWatcher(Watcher):
    """A single-series watcher bound to one IndicatorThreshold row."""

    def __init__(self, series_id: str, threshold: IndicatorThreshold) -> None:
        self.series_id = series_id
        self.threshold = threshold

    def series_ids(self) -> list[str]:
        return [self.series_id]


class CompositeWatcher(Watcher):
    """A cross-series watcher bound to a CompositeThreshold row (design §7.4)."""

    kind = "composite"

    def __init__(self, config: CompositeThreshold) -> None:
        self.config = config

    def series_ids(self) -> list[str]:
        return list(self.config.inputs)
