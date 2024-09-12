CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

CREATE TABLE IF NOT EXISTS colours (
    name TEXT NOT NULL,
    hex TEXT NOT NULL,
    PRIMARY KEY (name, hex)
);

CREATE INDEX IF NOT EXISTS colour_names_idx ON colours (name);