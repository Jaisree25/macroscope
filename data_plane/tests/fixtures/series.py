"""Builders for synthetic SeriesPoint windows used across watcher tests.

Fixed base date (no Date.now / new Date — tests must be reproducible).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

BASE = datetime(2025, 1, 1, tzinfo=timezone.utc)


def make_point(source: str, series_id: str, value: float, day: int = 0, **metadata):
    """One SeriesPoint at BASE + `day` days."""
    from data_plane.models.series import SeriesPoint

    return SeriesPoint(
        source=source,
        series_id=series_id,
        timestamp=BASE + timedelta(days=day),
        value=value,
        metadata=metadata,
    )


def series_from_values(source: str, series_id: str, values: list[float], **md):
    """A window from a list of values, one point per day, ascending."""
    return [make_point(source, series_id, v, day=i, **md) for i, v in enumerate(values)]


def flat_series(source: str, series_id: str, value: float, n: int):
    """`n` identical points — std == 0, the warm-but-quiet baseline."""
    return series_from_values(source, series_id, [value] * n)


def spike_at_end(source: str, series_id: str, base: float, n: int, spike: float):
    """`n-1` flat points at `base`, then one `spike` point — the classic trip case."""
    return series_from_values(source, series_id, [base] * (n - 1) + [spike])
