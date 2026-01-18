BEGIN;

CREATE TYPE recipe_category_new AS ENUM (
    'BREAKFAST',
    'MAIN_COURSE',
    'SALAD',
    'SOUP',
    'SNACK',
    'DESSERT',
    'DRINK',
    'SAUCE'
);

ALTER TABLE recipes
ALTER COLUMN category TYPE recipe_category_new USING (
    CASE category
        WHEN 'DINNER' THEN 'MAIN_COURSE'::text
        WHEN 'LUNCH' THEN 'MAIN_COURSE'::text
        WHEN 'COCKTAIL' THEN 'DRINK'::text
        WHEN 'DESERT' THEN 'DESSERT'::text
        ELSE category::text
    END
)::recipe_category_new;

DROP TYPE IF EXISTS recipe_category;

ALTER TYPE recipe_category_new RENAME TO recipe_category;

COMMIT;
