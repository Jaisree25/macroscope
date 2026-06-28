"""Scheduler — drives each Poller at its cadence.

v1: a simple async loop per source (FRED hourly, GDELT 15-min). In prod this maps
to Cloud Scheduler hitting a poll endpoint; the Poller logic is identical either way.
"""

from __future__ import annotations

from data_plane.ingestion.poller import Poller


class Scheduler:
    def __init__(self) -> None:
        self._jobs: list[tuple[Poller, int]] = []

    def add(self, poller: Poller, interval_seconds: int) -> None:
        """Register a poller to run every `interval_seconds`."""
        self._jobs.append((poller, interval_seconds))

    async def run_forever(self) -> None:
        """Launch one loop per job. TODO(P1): asyncio.gather of per-job sleep/poll loops.

        Each loop: bootstrap once, then poll_once every interval; isolate failures so
        one source erroring doesn't kill the others.
        """
        raise NotImplementedError
