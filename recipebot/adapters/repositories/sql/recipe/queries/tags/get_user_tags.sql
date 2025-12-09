SELECT id, name, group_id, user_id
FROM recipe_tag
WHERE user_id = $1
ORDER BY name;
