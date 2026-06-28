"""The source registry is the extension seam — adding a source must 'just register'."""

from __future__ import annotations

import pytest

from data_plane.sources.base import get_source, register_source, registered_sources


def test_fred_and_gdelt_are_registered():
    assert {"fred", "gdelt"} <= set(registered_sources())


def test_get_unknown_source_raises():
    with pytest.raises(KeyError):
        get_source("doesnotexist")


def test_duplicate_registration_is_rejected():
    with pytest.raises(ValueError):

        @register_source("fred")  # already taken
        class _Dupe:  # pragma: no cover
            pass
