"""FRED source — the 7 macro indicators + daily market series (design §4, §5).

Covers everything except news: FEDFUNDS/DFF, CPIAUCSL, PAYEMS, UNRATE, GDPC1,
DGS10, UMCSENT, SP500, VIXCLS. One API, normalized to SeriesPoint.

API: https://fred.stlouisfed.org/docs/api/fred/series_observations.html
"""

from __future__ import annotations

from datetime import datetime

from data_plane.models.series import SeriesMeta, SeriesPoint
from data_plane.sources.base import Source, register_source

# series_id -> (title, unit, release_pattern) — release_pattern routes the watcher (§7.2).
FRED_SERIES: dict[str, tuple[str, str, str]] = {
    "DFF": ("Federal Funds Effective Rate", "%", "release"),
    "CPIAUCSL": ("CPI (All Urban Consumers)", "index", "release"),
    "PAYEMS": ("Total Nonfarm Payrolls", "thousands", "release"),
    "UNRATE": ("Unemployment Rate", "%", "release"),
    "GDPC1": ("Real GDP", "billions", "release"),
    "DGS10": ("10-Year Treasury Yield", "%", "continuous"),
    "UMCSENT": ("U. Michigan Consumer Sentiment", "index", "release"),
    "SP500": ("S&P 500", "index", "continuous"),
    "VIXCLS": ("CBOE Volatility Index (VIX)", "index", "continuous"),
}

FRED_BASE_URL = "https://api.stlouisfed.org/fred"


@register_source("fred")
class FredSource(Source):
    """Poller for FRED series observations."""

    def __init__(self, api_key: str = "", client=None) -> None:
        self._api_key = api_key
        self._client = client  # inject an httpx.AsyncClient in tests

    def series_ids(self) -> list[str]:
        return list(FRED_SERIES)

    def describe(self) -> list[SeriesMeta]:
        return [
            SeriesMeta(
                source="fred",
                series_id=sid,
                title=title,
                unit=unit,
                release_pattern=pattern,
            )
            for sid, (title, unit, pattern) in FRED_SERIES.items()
        ]

    async def fetch(self, since: datetime | None = None) -> list[SeriesPoint]:
        """GET series/observations for each series, parse rows to SeriesPoint.

        TODO(P1):
          - one request per series_id (httpx), params: api_key, file_type=json,
            observation_start=since.
          - map row {date, value} -> SeriesPoint(source='fred', ...); skip '.' (missing).
          - timestamps tz-aware UTC.
        """
        raise NotImplementedError

    async def backfill(self, lookback_days: int) -> list[SeriesPoint]:
        """Bulk history to warm the watcher windows. TODO(P1): fetch(now - lookback)."""
        raise NotImplementedError
