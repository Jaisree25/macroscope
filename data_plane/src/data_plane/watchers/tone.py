"""Tone watcher — GDELT news volume + tone z-score per theme (design §7.2/§7.3).

notable:     volume >= 2x avg  OR  tone z <= -2
significant: volume >= 3x avg  AND tone z <= -2
Window is rolling 7–14 days per theme.
"""

from __future__ import annotations

from data_plane.models.event import Event
from data_plane.watchers.base import BaseIndicatorWatcher, WatcherContext


class ToneWatcher(BaseIndicatorWatcher):
    kind = "tone"

    def evaluate(self, ctx: WatcherContext) -> list[Event]:
        """Compare latest volume vs trailing avg and tone vs trailing z.

        TODO(P1):
          - window = ctx.windows[self.series_id] (value=tone, metadata['volume']).
          - vol_mult = latest.volume / mean(prior volumes); tone_z vs prior tone.
          - significant if vol_mult>=sig.volume_mult AND tone_z<=sig.tone_z.
          - notable if vol_mult>=notable.volume_mult OR tone_z<=notable.tone_z.
          - Event(watcher=TONE, magnitude=tone_z, value=latest tone,
            context={'theme': ..., 'volume_mult': ..., 'tone_z': ...}).
        """
        raise NotImplementedError
