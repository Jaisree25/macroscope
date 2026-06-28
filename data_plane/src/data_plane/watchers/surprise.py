"""Surprise watcher — z-score of the new print vs. the trailing window (design §7.1/§7.2).

The free consensus workaround: approximate "surprise" as deviation from the
trailing trend (FRED-only, no paid forecast feed). Applies to release-based
series: CPI, payrolls, unemployment, GDP, sentiment.

Upgrade path: swap baseline from trailing-mean to `actual - consensus`; tiers keep
the same |z| shape.
"""

from __future__ import annotations

from data_plane.models.event import Event
from data_plane.watchers.base import BaseIndicatorWatcher, WatcherContext


class SurpriseWatcher(BaseIndicatorWatcher):
    kind = "surprise"

    def evaluate(self, ctx: WatcherContext) -> list[Event]:
        """Compute the transform (MoM% / monthly Δ per series), z-score it vs the
        trailing window, and emit if |z| crosses notable/significant.

        TODO(P1):
          - window = ctx.windows[self.series_id]; need len >= threshold.warmup (engine guards too).
          - transform the level series per indicator (CPI: MoM %, PAYEMS: monthly Δ, ...).
          - z = (latest_transform - mean(prior)) / std(prior).
          - tier = significant if |z|>=sig.z else notable if |z|>=notable.z else none.
          - build Event(watcher=SURPRISE, magnitude=z, value=latest, threshold=tier.z,
            direction by sign, context={'window': n, 'z': z, 'transform': '...'}).
        """
        raise NotImplementedError
