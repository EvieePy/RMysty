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

CREATE TABLE IF NOT EXISTS paste_blocks (
    mid BIGINT PRIMARY KEY
)