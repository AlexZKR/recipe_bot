CREATE TABLE IF NOT EXISTS users_groups(
    user_id INTEGER REFERENCES users(tg_id),
    group_id INTEGER REFERENCES groups(tg_chat_id),
    PRIMARY KEY(user_id, group_id)
);
