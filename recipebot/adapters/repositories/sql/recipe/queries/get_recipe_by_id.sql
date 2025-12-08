SELECT id, title, ingredients, steps, category, description, estimated_time, servings, notes, link, user_id
FROM recipes
WHERE id = $1;
