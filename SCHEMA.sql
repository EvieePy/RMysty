CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

CREATE TABLE IF NOT EXISTS colours (
    name TEXT NOT NULL,
    hex TEXT NOT NULL,
    PRIMARY KEY (name, hex)
);

CREATE INDEX IF NOT EXISTS colour_names_idx ON colours (name);

CREATE TABLE IF NOT EXISTS pastes (
        id TEXT NOT NULL,
        uid BIGINT NOT NULL,
        mid BIGINT NOT NULL,
        vid BIGINT NOT NULL,
        TOKEN TEXT NOT NULL,
        CONSTRAINT pk_id_uid PRIMARY KEY (id, uid)
);

CREATE TABLE IF NOT EXISTS timezones (
    uid BIGINT PRIMARY KEY,
    timezone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paste_blocks (
    mid BIGINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS open_collective_sync (
    id BIGINT PRIMARY KEY, -- The discord user ID
    name TEXT NOT NULL, -- the open collective account name, at time of sync
    slug TEXT NOT NULL, -- the open collective slug, at time of sync
    account_id TEXT NOT NULL, -- the open collective account ID
    refresh_token TEXT NOT NULL, -- the Discord refresh token
    access_token TEXT NOT NULL, -- the Discord access token
    expires_at TIMESTAMP NOT NULL -- the time the access token expires
);

CREATE INDEX IF NOT EXISTS open_collective_sync_account_id_idx ON open_collective_sync (account_id);