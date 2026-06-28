"""Watchers — deterministic functions over the store that decide what's material.

NO LLM here. A watcher reads a window and returns Events; the engine handles
warm-up / cooldown / hysteresis and emits them onto the bus (design §7).

3 base watchers (surprise, delta, tone) + 4 composites (yield-curve, Sahm,
risk-off, stagflation). Add a watcher = new class + register it with the engine.
"""

from data_plane.watchers.base import Watcher, WatcherContext
from data_plane.watchers.composites import (
    RiskOffWatcher,
    SahmWatcher,
    StagflationWatcher,
    YieldCurveWatcher,
)
from data_plane.watchers.delta import DeltaWatcher
from data_plane.watchers.engine import WatcherEngine
from data_plane.watchers.surprise import SurpriseWatcher
from data_plane.watchers.tone import ToneWatcher

__all__ = [
    "Watcher",
    "WatcherContext",
    "WatcherEngine",
    "SurpriseWatcher",
    "DeltaWatcher",
    "ToneWatcher",
    "YieldCurveWatcher",
    "SahmWatcher",
    "RiskOffWatcher",
    "StagflationWatcher",
]
