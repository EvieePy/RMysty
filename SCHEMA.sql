CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    uid BIGINT NOT NULL,
    gid BIGINT NOT NULL,
    cid BIGINT,
    mid BIGINT,
    moderator BIGINT NOT NULL,
    event INT NOT NULL DEFAULT 0,
    note TEXT NOT NULL,
    additional TEXT,
    created_at TIMESTAMP NOT NULL
);