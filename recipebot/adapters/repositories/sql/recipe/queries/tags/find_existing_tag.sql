SELECT id, name, group_id, user_id
FROM recipe_tag
WHERE name = $1 AND user_id = $2;
