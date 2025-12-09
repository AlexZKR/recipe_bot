SELECT r.id, r.title, r.ingredients, r.steps, r.category,
       r.description, r.estimated_time, r.servings, r.notes, r.link, r.user_id,
       ARRAY_AGG(rt.name) FILTER (WHERE rt.name IS NOT NULL) as tag_names
FROM recipes r
LEFT JOIN recipe_tag rt ON rt.id = ANY(r.tags)
WHERE r.user_id = $1
GROUP BY r.id, r.title, r.ingredients, r.steps, r.category,
         r.description, r.estimated_time, r.servings, r.notes, r.link, r.user_id
ORDER BY r.title;
