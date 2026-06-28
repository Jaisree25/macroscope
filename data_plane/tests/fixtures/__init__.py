"""Deterministic fixture series for watcher tests — no network, no clock."""

from tests.fixtures.series import (
    flat_series,
    make_point,
    series_from_values,
    spike_at_end,
)

__all__ = ["make_point", "series_from_values", "flat_series", "spike_at_end"]
