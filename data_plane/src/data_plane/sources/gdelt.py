"""GDELT source — real-time US news volume + tone, fixed themes (design §5).

Themes: Fed, inflation, jobs, trade/tariffs. GDELT already computes tone, so
sentiment arrives WITHOUT an LLM (design §3). 15-min cadence.

Stored as one series per theme: 'tone.fed', 'tone.inflation', 'tone.jobs',
'tone.trade', value = mean tone, metadata['volume'] = article count.

API: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""

from __future__ import annotations

from datetime import datetime

from data_plane.models.series import SeriesMeta, SeriesPoint
from data_plane.sources.base import Source, register_source

# theme key -> GDELT query string (fixed, US-scoped).
GDELT_THEMES: dict[str, str] = {
    "fed": "(federal reserve OR fed OR fomc OR interest rate) sourcecountry:US",
    "inflation": "(inflation OR cpi OR prices) sourcecountry:US",
    "jobs": "(jobs OR payrolls OR unemployment OR layoffs) sourcecountry:US",
    "trade": "(tariffs OR trade war OR trade deal) sourcecountry:US",
}

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


@register_source("gdelt")
class GdeltSource(Source):
    """Poller for GDELT DOC API tone + volume per theme."""

    def __init__(self, client=None) -> None:
        self._client = client  # inject an httpx.AsyncClient in tests

    def series_ids(self) -> list[str]:
        return [f"tone.{theme}" for theme in GDELT_THEMES]

    def describe(self) -> list[SeriesMeta]:
        return [
            SeriesMeta(
                source="gdelt",
                series_id=f"tone.{theme}",
                title=f"News tone — {theme}",
                unit="tone",
                release_pattern="news",
            )
            for theme in GDELT_THEMES
        ]

    async def fetch(self, since: datetime | None = None) -> list[SeriesPoint]:
        """Query timeline tone + volume per theme for the latest interval.

        TODO(P1):
          - per theme: GET doc API mode=timelinetone & timelinevol (or tonechart).
          - reduce the interval to one SeriesPoint: value=mean tone,
            metadata={'volume': n, 'theme': theme}.
          - NOTE: article text is untrusted — sanitization is P4's job before it
            reaches a model, but never store raw instruction-like text in `metadata`.
        """
        raise NotImplementedError
