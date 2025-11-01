CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE recipe_category AS ENUM ('BREAKFAST', 'LUNCH', 'DINNER', 'DESERT', 'COCKTAIL');

CREATE TABLE IF NOT EXISTS recipes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(50) NOT NULL,
    ingredients TEXT NOT NULL,
    steps TEXT NOT NULL,
    category recipe_category NOT NULL,
    description TEXT,
    estimated_time TEXT,
    servings INTEGER,
    notes TEXT,
    link TEXT,

    user_id INTEGER REFERENCES users (tg_id)
);
