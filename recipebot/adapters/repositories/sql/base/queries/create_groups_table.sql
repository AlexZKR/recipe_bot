CREATE TABLE IF NOT EXISTS groups (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    owner_id BIGINT REFERENCES users(tg_id) ON DELETE SET NULL,
    invite_code_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
