Layer by layer
models/ — the frozen contracts (C1, C2)
The spine everything else speaks in. series.py defines SeriesPoint (one observation: source, series_id, timestamp, value, metadata) — every source normalizes onto this, so nothing downstream cares whether a number came from FRED or GDELT. event.py defines Event (what a tripped watcher emits) plus Severity (notable/significant) and WatcherType enums. These are the only types that cross plane boundaries.

sources/ — swap point #1 (add sources later)
base.py has a Source ABC (fetch(), describe(), backfill()) plus a registry. A new source is one file + @register_source("name") — nothing else changes. fred.py covers the 7 macro + market series; gdelt.py covers news tone per theme. Note describe() returns each series' release_pattern ('release'/'continuous'/'news') — that's what routes a series to the right watcher later.

store/ — swap point #2 (Postgres now, Timescale later)
base.py is the Store ABC: writes (upsert_points, write_event) and reads (latest, history, recent_events). postgres.py is the v1 backend over schema.sql; memory.py is an in-memory twin for fast tests. Because both honor the same ABC, swapping databases is a new subclass — the watcher engine and poller never know.

ingestion/ — the write path
poller.py is source-agnostic: hand it any Source and it runs fetch → store.upsert → bus.publish_data. bootstrap() does the first-run backfill to warm the watcher windows without publishing (so historical data doesn't fire fake live events). scheduler.py just runs each poller at its cadence (FRED hourly, GDELT 15-min).

events/ — the notification bus
bus.py carries the two flows: publish_data/on_data (poller → engine) and publish_event/on_event (engine → subscribers like the store annotation writer and P2's explainer). In-process for v1; the same surface can sit on a real broker later.

watchers/ — the detection logic
The key design choice: watchers are pure, the engine is stateful.

base.py — Watcher ABC + WatcherContext (the engine pre-fetches the windows, so watchers do zero I/O). Pure functions: window in → events out.
The 3 base watchers: surprise.py (z-score vs trailing window — the free consensus workaround), delta.py (% / bp moves + absolute level crossings), tone.py (news volume + tone z).
composites.py — the 4 cross-series rules (yield-curve, Sahm, risk-off, stagflation).
engine.py — subscribes to new data, builds the context, and owns the tuning mechanics watchers deliberately don't: warm-up, cooldown, hysteresis. Survivors get written to the store and published. Keeping these out of the watchers is what makes them trivially unit-testable.
config/ — config, not code
thresholds.yaml holds every threshold value (notable/significant tiers, windows, warm-up, cooldown, hysteresis) from design §7.3/§7.4 — tunable without a redeploy. thresholds.py parses it into typed objects; settings.py pulls secrets/URLs from env.

How a single data point flows through
Scheduler fires the FRED poller → source.fetch() returns new SeriesPoints.
Poller upsert_points to the store, then publish_data(DataUpdate).
Engine's on_data wakes, finds watchers whose series changed, pulls their windows via store.history.
Skips if window < warm-up; otherwise calls each watcher.evaluate(ctx).
Survivors pass cooldown/hysteresis → store.write_event + publish_event.
Subscribers (dashboard annotation, P2 explainer) react. The LLM only enters here — after the deterministic plane has already decided something matters.
The TDD layer
tests/ mirrors src/ one-to-one. Every stub has a failing test that is the spec — the watcher tests (warm-up, cooldown, hysteresis, each composite against fixture series in tests/fixtures/series.py) are the highest-value because watchers are pure. The store-contract suite is parametrized over backends so any future DB is "done" when it goes green.

The intended fill-in order, each unblocking the next: InMemoryStore → EventBus → load_thresholds → base watchers → engine → Poller → the two sources → PostgresStore.