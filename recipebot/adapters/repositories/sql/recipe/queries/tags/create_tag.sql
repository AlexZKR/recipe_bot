INSERT INTO recipe_tag (name, group_id, user_id)
VALUES ($1, $2, $3)
RETURNING id;
