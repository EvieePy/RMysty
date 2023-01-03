CREATE TABLE IF NOT EXISTS todo(
    id SERIAL NOT NULL,
    uid BIGINT NOT NULL,
    created TIMESTAMP NOT NULL,
    reminder TIMESTAMP,
    completetd BOOLEAN NOT NULL DEFAULT false,
    content TEXT NOT NULL,
    PRIMARY KEY(id, uid)
);