UPDATE recipes
SET title = $1, ingredients = $2, steps = $3, category = $4,
    servings = $5, description = $6, estimated_time = $7,
    notes = $8, link = $9
WHERE id = $10 AND user_id = $11
RETURNING id, title, ingredients, steps, category, servings,
          description, estimated_time, notes, link, user_id;
