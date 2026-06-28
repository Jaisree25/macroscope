"""Pluggable data sources.

Adding a source = one new module here + `@register_source(...)`. Nothing above
this layer (ingestion, store, watchers) knows which sources exist.
"""

from data_plane.sources.base import Source, get_source, register_source, registered_sources

# Import implementations so their @register_source decorators run on package import.
from data_plane.sources import fred, gdelt  # noqa: E402,F401

__all__ = ["Source", "register_source", "get_source", "registered_sources"]
