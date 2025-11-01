INSERT INTO recipes (id, title, ingredients, steps, category, description, estimated_time, servings, notes, link, user_id)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
RETURNING id, title, ingredients, steps, category, description, estimated_time, servings, notes, link, user_id;
