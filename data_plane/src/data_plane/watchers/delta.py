"""Delta watcher — % / bp move bounds + absolute level crossings (design §7.1/§7.2).

For continuous/daily market series: 10Y (bp), S&P 500 (% + drawdown), VIX (level + jump).
Runs BOTH philosophies: relative (size of move) and absolute (crossed a line that
matters by itself, e.g. VIX>30, 10Y crosses 4/4.5/5%).
"""

from __future__ import annotations

from data_plane.models.event import Event
from data_plane.watchers.base import BaseIndicatorWatcher, WatcherContext


class DeltaWatcher(BaseIndicatorWatcher):
    kind = "delta"

    def evaluate(self, ctx: WatcherContext) -> list[Event]:
        """Check the latest move against pct/bp tiers AND configured level crossings.

        TODO(P1):
          - window = ctx.windows[self.series_id]; latest vs previous.
          - move = pct change (SP500), bp change (DGS10/DFF), or 1-day jump_pct (VIX).
          - relative trip: |move| >= tier.pct / tier.bp / tier.jump_pct.
          - absolute trip: value crosses tier.level_gt / level_lt or a level in extra['levels'].
            Hysteresis/cooldown are the engine's job — here just report the crossing.
          - drawdown (SP500): value <= recent_high * (1 - extra['drawdown_pct']/100).
          - emit at most one Event per evaluation, highest tier wins.
        """
        raise NotImplementedError
