"""C1 — Store schema (the spine of everything).

A normalized point that every source maps onto. FRED prints, GDELT tone, and any
future source all land here so the store, dashboard, and watchers stay
source-agnostic. Freeze this early (design §4, plan §C1).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SeriesPoint(BaseModel):
    """One observation of one series at one instant — the atomic store row.

    Examples
    --------
    FRED CPI print:   source="fred",  series_id="CPIAUCSL", value=315.6
    GDELT tone:       source="gdelt", series_id="tone.inflation", value=-3.2,
                      metadata={"volume": 1240, "theme": "inflation"}
    """

    source: str = Field(..., description="Registered source key, e.g. 'fred', 'gdelt'.")
    series_id: str = Field(..., description="Canonical series id, unique within a source.")
    timestamp: datetime = Field(..., description="Observation time (UTC, tz-aware).")
    value: float = Field(..., description="Numeric value in the series' native unit.")
    ingested_at: datetime | None = Field(
        default=None, description="When the data plane wrote it (set by the store)."
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Source-specific extras (volume, units, release id, ...).",
    )

    # TODO(P1): __hash__ / dedupe key is (source, series_id, timestamp) for upsert.


class SeriesMeta(BaseModel):
    """Descriptive metadata for a series — drives the dashboard and watcher routing.

    `release_pattern` decides which watcher applies (design §7.2):
    'release' → surprise watcher, 'continuous' → delta+level, 'news' → tone.
    """

    source: str
    series_id: str
    title: str
    unit: str = ""
    release_pattern: str = Field(
        default="continuous", description="'release' | 'continuous' | 'news'"
    )
    # TODO(P1): seasonal adjustment flag, frequency, FRED native id aliases (DFF vs FEDFUNDS).
