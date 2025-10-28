INSERT INTO users (tg_id, username, first_name, last_name)
VALUES ($1, $2, $3, $4)
RETURNING tg_id, username, first_name, last_name, created_at;
