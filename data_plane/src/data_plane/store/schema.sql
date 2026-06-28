-- C1 store schema (Postgres). Backend-specific DDL; the Store interface hides it.
-- Swappable: a Timescale backend would make `series_point` a hypertable here.

CREATE TABLE IF NOT EXISTS series_meta (
    source          TEXT NOT NULL,
    series_id       TEXT NOT NULL,
    title           TEXT NOT NULL,
    unit            TEXT NOT NULL DEFAULT '',
    release_pattern TEXT NOT NULL DEFAULT 'continuous',  -- 'release'|'continuous'|'news'
    PRIMARY KEY (source, series_id)
);

CREATE TABLE IF NOT EXISTS series_point (
    source       TEXT        NOT NULL,
    series_id    TEXT        NOT NULL,
    ts           TIMESTAMPTZ NOT NULL,
    value        DOUBLE PRECISION NOT NULL,
    metadata     JSONB       NOT NULL DEFAULT '{}',
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (source, series_id, ts)   -- dedupe / idempotent upsert key
);

-- Trailing-window reads (watchers) want the newest rows per series fast.
CREATE INDEX IF NOT EXISTS series_point_series_ts_desc
    ON series_point (source, series_id, ts DESC);

-- TODO(P1): on Timescale -> SELECT create_hypertable('series_point','ts');

CREATE TABLE IF NOT EXISTS event (
    id           TEXT        PRIMARY KEY,           -- hash(watcher, series_id, ts) — idempotent
    watcher      TEXT        NOT NULL,              -- surprise|delta|tone|composite
    source       TEXT        NOT NULL,
    series_id    TEXT        NOT NULL,
    ts           TIMESTAMPTZ NOT NULL,
    severity     TEXT        NOT NULL,              -- notable|significant
    magnitude    DOUBLE PRECISION NOT NULL,
    value        DOUBLE PRECISION NOT NULL,
    threshold    DOUBLE PRECISION NOT NULL,
    direction    TEXT        NOT NULL DEFAULT '',
    context      JSONB       NOT NULL DEFAULT '{}',
    fired_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS event_ts_desc ON event (ts DESC);
CREATE INDEX IF NOT EXISTS event_series_ts_desc ON event (series_id, ts DESC);
