CREATE TABLE IF NOT EXISTS recipe_tag (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,

    group_id INTEGER REFERENCES groups (tg_chat_id),
    user_id INTEGER REFERENCES users (tg_id)

);
