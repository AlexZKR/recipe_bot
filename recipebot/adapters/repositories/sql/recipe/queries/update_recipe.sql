UPDATE recipes
SET title = $1, ingredients = $2, steps = $3, category = $4,
    servings = $5, description = $6, estimated_time = $7,
    notes = $8, link = $9, tags = $10
WHERE id = $11 AND user_id = $12
RETURNING id, title, ingredients, steps, category, servings,
          description, estimated_time, notes, link, user_id, tags;
