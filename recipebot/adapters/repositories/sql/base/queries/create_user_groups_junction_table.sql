CREATE TABLE IF NOT EXISTS users_groups(
    user_id BIGINT REFERENCES users(tg_id),
    group_id BIGINT REFERENCES groups(tg_chat_id),
    PRIMARY KEY(user_id, group_id)
);
