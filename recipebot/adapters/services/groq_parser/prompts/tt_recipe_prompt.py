import json
from collections.abc import Iterable

from groq.types.chat import ChatCompletionMessageParam

from recipebot.adapters.services.groq_parser.prompts.base import BASE_SYSTEM_PROMPT
from recipebot.adapters.services.groq_parser.prompts.ingredients import (
    INGREDIENT_EXTRACTION_PROMPT,
)
from recipebot.adapters.services.groq_parser.prompts.steps import (
    STEPS_EXTRACTION_RULES,
)


def get_tt_recipe_prompt(user_prompt: str) -> Iterable[ChatCompletionMessageParam]:
    system_prompt = f"""
    {BASE_SYSTEM_PROMPT}\n\n{INGREDIENT_EXTRACTION_PROMPT}\n\n{STEPS_EXTRACTION_RULES}\n
    **Additional Rules:**
    1. Infer 'estimated_time' and 'servings' if mentioned.
    """
    return [
        {"role": "system", "content": system_prompt},
        # -------------------------------------------------------
        # FEW-SHOT 1: Explicit Headers (Baseline)
        # -------------------------------------------------------
        {
            "role": "user",
            "content": "Fish and Chips. Fish: 500g cod. Batter: 100g flour, 1 egg, 100ml beer.",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "title": "Fish and Chips",
                    "ingredients": [
                        {"name": "cod", "qty": "500", "unit": "g", "group": "Main"},
                        {"name": "flour", "qty": "100", "unit": "g", "group": "Batter"},
                        {"name": "egg", "qty": "1", "unit": "pc", "group": "Batter"},
                        {"name": "beer", "qty": "100", "unit": "ml", "group": "Batter"},
                    ],
                    "steps": [],
                    "desc": "Fish in batter",
                    "time": None,
                    "notes": None,
                }
            ),
        },
        # -------------------------------------------------------
        # FEW-SHOT 2: Implicit Components
        # -------------------------------------------------------
        # This teaches the model to spot a "Marinade" even without a header
        {
            "role": "user",
            "content": "Grilled Chicken. You need 2 chicken breasts. Mix 2 tbsp soy sauce, 1 tbsp honey, and 1 tsp ginger. Marinate chicken. Garnish with sesame seeds and green onion.",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "title": "Grilled Chicken",
                    "ingredients": [
                        # Main Item
                        {
                            "name": "chicken breasts",
                            "qty": "2",
                            "unit": "pc",
                            "group": "Main",
                        },
                        # Implicit "Marinade" Group (Model infers this from "Mix... Marinate")
                        {
                            "name": "soy sauce",
                            "qty": "2",
                            "unit": "tbsp",
                            "group": "Marinade",
                        },
                        {
                            "name": "honey",
                            "qty": "1",
                            "unit": "tbsp",
                            "group": "Marinade",
                        },
                        {
                            "name": "ginger",
                            "qty": "1",
                            "unit": "tsp",
                            "group": "Marinade",
                        },
                        # Implicit "Garnish" Group (Model infers from "Garnish with")
                        {
                            "name": "sesame seeds",
                            "qty": None,
                            "unit": None,
                            "group": "Garnish",
                        },
                        {
                            "name": "green onion",
                            "qty": None,
                            "unit": None,
                            "group": "Garnish",
                        },
                    ],
                    "steps": [],
                    "desc": "Marinated chicken",
                    "time": None,
                    "notes": None,
                }
            ),
        },
        # -------------------------------------------------------
        # REAL REQUEST
        # -------------------------------------------------------
        {"role": "user", "content": user_prompt},
    ]
