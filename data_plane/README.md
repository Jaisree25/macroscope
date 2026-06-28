# Macro Watcher — Data Plane (P1)

The backbone: gets the numbers in, stores them, and flags what matters. **No LLM lives here** — detection is deterministic code (poll + SQL predicate + arithmetic). The reasoning/synthesis planes consume this plane's outputs through contracts, never by reaching inside.

## What this owns

- **Ingestion** — pluggable source pollers (FRED, GDELT today; more later) normalized to one series schema.
- **Store** — the hot time-series store + a clean read/query layer (what P4's MCP wraps). Postgres now, swappable.
- **Watchers** — 3 base (surprise / delta / tone) + 4 composite (yield-curve, Sahm, risk-off, stagflation), as pure deterministic functions.
- **Events** — the notification bus: ingestion → watcher engine (new data), and watchers → subscribers (tripped event).
- **Thresholds** — a config table (notable / significant tiers), tunable without a redeploy.

## Contracts this plane provides (frozen Day 1)

| # | Contract | Module |
|---|----------|--------|
| C1 | Store schema (series, timestamp, value, source) | `models/series.py`, `store/schema.sql` |
| C2 | Event-payload schema (series, magnitude, type, context) | `models/event.py` |
| —  | Query layer (what the MCP wraps) | `store/base.py` |

## Two swap points, by design

- **Sources** are pluggable: `Source` ABC + a registry. FRED and GDELT are just two implementations.
- **Storage** is pluggable: `Store` ABC. `PostgresStore` is the v1 backend; `InMemoryStore` backs fast unit tests. A TimescaleDB / other backend later is a new `Store` subclass — nothing above it changes.

## Layout

```
src/data_plane/
  models/        C1 SeriesPoint, C2 Event, severity/type enums
  sources/       Source ABC + registry; fred.py, gdelt.py  ← add new sources here
  ingestion/     poller (source.fetch → store.write) + scheduler
  store/         Store interface + Postgres impl + in-memory impl + schema.sql
  watchers/      Watcher ABC, engine (warm-up/cooldown/hysteresis), base + composite watchers
  events/        pub/sub bus for the two notification flows
  config/        settings (env) + thresholds.yaml + loader
tests/           mirrors src/ one-to-one — written first (TDD)
```

## TDD workflow

Every module ships with a failing test that encodes its spec **before** the implementation exists.

```bash
pip install -e ".[dev]"
pytest -m "not integration"   # pure unit tests (in-memory store, mocked HTTP) — no DB needed
pytest                        # includes the Postgres store-contract test (spins up a container)
pytest tests/watchers -q      # one slice at a time
```

Watchers are the highest-value tests (pure functions): cover warm-up, cooldown, hysteresis, and each composite against fixture series.

## Adding a new source later

1. Subclass `Source` in `sources/<name>.py`, implement `fetch()` → `list[SeriesPoint]`.
2. Register it: `@register_source("<name>")`.
3. Add its series ids + thresholds to `config/thresholds.yaml`.
4. Write `tests/sources/test_<name>.py` first.

No other module changes — ingestion, store, and watchers are source-agnostic.

## Swapping the database later

1. Subclass `Store` in `store/<backend>.py`, implement every abstract method.
2. Point `config.settings` at it.
3. Run `tests/store/test_store_contract.py` against it — the contract suite is backend-parametrized, so a new backend is "done" when it passes the same tests Postgres does.
