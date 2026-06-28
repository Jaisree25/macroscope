"""Composite watchers — cross-series arithmetic, outsized signal (design §7.4).

Pure arithmetic over series already tracked, so they cost almost nothing:
  - YieldCurve : 10Y - FedFunds goes negative (inversion).
  - Sahm       : unemployment 3-mo avg rises +0.5pp above trailing 12-mo low.
  - RiskOff    : S&P down >=2% AND VIX up >=15% same day.
  - Stagflation: CPI surprise up AND sentiment down.
"""

from __future__ import annotations

from data_plane.models.event import Event
from data_plane.watchers.base import CompositeWatcher, WatcherContext


class YieldCurveWatcher(CompositeWatcher):
    """`DGS10 - DFF` < trigger (default 0) → inversion."""

    def evaluate(self, ctx: WatcherContext) -> list[Event]:
        # TODO(P1): spread = latest(DGS10) - latest(DFF); trip when spread < params['trigger_lt'].
        raise NotImplementedError


class SahmWatcher(CompositeWatcher):
    """Unemployment 3-mo avg minus trailing 12-mo low >= rise_pp."""

    def evaluate(self, ctx: WatcherContext) -> list[Event]:
        # TODO(P1): avg3 = mean(last 3 UNRATE); low12 = min(last 12); trip when avg3 - low12 >= 0.5.
        raise NotImplementedError


class RiskOffWatcher(CompositeWatcher):
    """Same-day S&P drop AND VIX spike → confirmed stress vs. quiet drift."""

    def evaluate(self, ctx: WatcherContext) -> list[Event]:
        # TODO(P1): sp_ret<=-sp_down_pct AND vix_jump>=vix_up_pct on the same date → trip.
        raise NotImplementedError


class StagflationWatcher(CompositeWatcher):
    """CPI surprise up AND sentiment down → rising costs into weakening demand."""

    def evaluate(self, ctx: WatcherContext) -> list[Event]:
        # TODO(P1): reuse surprise sign on CPI + direction on UMCSENT; trip when both hold.
        raise NotImplementedError
