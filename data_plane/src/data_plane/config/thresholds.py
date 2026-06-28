"""Loader for the threshold config table (design §7.3–§7.5).

Thresholds are *config, not code* — tunable without a redeploy. This module just
parses `thresholds.yaml` into typed objects the watcher engine consumes.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_THRESHOLDS_PATH = Path(__file__).with_name("thresholds.yaml")


class Tier(BaseModel):
    """One severity tier's trigger values for a watcher (notable | significant)."""

    # Only the keys relevant to the watcher kind are set; the rest stay None.
    z: float | None = None              # surprise: |z| trigger
    pct: float | None = None            # delta: |return| %
    bp: float | None = None             # delta: basis-point move
    level_gt: float | None = None       # absolute level crossing (above)
    level_lt: float | None = None       # absolute level crossing (below)
    jump_pct: float | None = None       # VIX-style 1-day jump
    volume_mult: float | None = None    # tone: volume vs avg
    tone_z: float | None = None         # tone: tone z trigger
    extra: dict = Field(default_factory=dict)


class IndicatorThreshold(BaseModel):
    """Thresholds + tuning mechanics for one watched series."""

    series_id: str
    watcher: str                        # 'surprise' | 'delta' | 'tone' | 'composite'
    window: int = Field(..., description="Trailing window size (prints or trading days).")
    warmup: int = Field(..., description="Points required before the watcher may fire.")
    cooldown: int = Field(default=0, description="Suppress re-fire for N points after firing.")
    hysteresis: float = Field(
        default=0.0, description="Margin a level must re-cross before re-arming."
    )
    notable: Tier = Field(default_factory=Tier)
    significant: Tier = Field(default_factory=Tier)


class CompositeThreshold(BaseModel):
    """Thresholds for a cross-series composite rule (design §7.4)."""

    rule: str                           # 'yield_curve' | 'sahm' | 'risk_off' | 'stagflation'
    inputs: list[str] = Field(default_factory=list, description="Series ids it reads.")
    cooldown: int = 0
    params: dict = Field(default_factory=dict, description="Rule-specific trigger values.")


class ThresholdConfig(BaseModel):
    """The whole table, keyed for quick lookup by the engine."""

    indicators: dict[str, IndicatorThreshold] = Field(default_factory=dict)
    composites: dict[str, CompositeThreshold] = Field(default_factory=dict)

    def for_series(self, series_id: str) -> IndicatorThreshold | None:
        return self.indicators.get(series_id)


def load_thresholds(path: Path | None = None) -> ThresholdConfig:
    """Parse the YAML table into a ThresholdConfig.

    TODO(P1): read YAML (pyyaml), validate every series in §7.3 is present,
    and build the indicators/composites dicts.
    """
    raise NotImplementedError
