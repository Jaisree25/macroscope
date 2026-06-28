"""C2 — Event payload (what a tripped watcher emits).

Consumed by P2's explainer and by P4. Keep it self-describing: the explainer
should be able to write a useful annotation from this object alone, without a
second round-trip to the store (design §9B, plan §C2).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Tiered severity (design §7.3/§7.5)."""

    NOTABLE = "notable"          # quiet dashboard annotation
    SIGNIFICANT = "significant"  # push/alert; explainer writes more


class WatcherType(str, Enum):
    """Which deterministic rule tripped (design §7)."""

    SURPRISE = "surprise"        # z-score vs trailing window
    DELTA = "delta"             # % / bp move + absolute level crossing
    TONE = "tone"              # GDELT volume + tone spike
    COMPOSITE = "composite"     # cross-series arithmetic (§7.4)


class Event(BaseModel):
    """A material move flagged by a watcher.

    Examples
    --------
    S&P -2.4% day:   watcher="delta", series_id="SP500", magnitude=-2.4,
                     severity="notable", context={"window": 20, "kind": "return_pct"}
    Yield inversion: watcher="composite", series_id="yield_curve_10y_ff",
                     magnitude=-0.15, context={"rule": "yield_curve", "ten_y": 4.1, "ff": 4.25}
    """

    watcher: WatcherType
    source: str = Field(..., description="Originating source, or 'composite' for cross-series.")
    series_id: str = Field(..., description="Primary series, or the composite's synthetic id.")
    timestamp: datetime = Field(..., description="Observation time that tripped the watcher.")
    severity: Severity
    magnitude: float = Field(..., description="Signed size of the move in the rule's unit.")
    value: float = Field(..., description="The observed value at trip time.")
    threshold: float = Field(..., description="The threshold that was crossed.")
    direction: str = Field(default="", description="'up' | 'down' | '' where signed-ness matters.")
    context: dict = Field(
        default_factory=dict,
        description="Everything the explainer needs: window, z-score, contributing series, rule name.",
    )
    fired_at: datetime | None = Field(
        default=None, description="When the engine emitted it (set on emit)."
    )

    # TODO(P1): stable event id = hash(watcher, series_id, timestamp) for idempotent annotation writes.
