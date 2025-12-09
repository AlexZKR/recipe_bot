CREATE TABLE IF NOT EXISTS users (
    tg_id BIGINT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
