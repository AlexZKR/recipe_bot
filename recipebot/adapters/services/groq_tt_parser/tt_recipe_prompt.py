import json
from collections.abc import Iterable

from groq.types.chat import ChatCompletionMessageParam


def get_tt_recipe_prompt(user_prompt: str) -> Iterable[ChatCompletionMessageParam]:
    system_prompt = """
You are a text extraction assistant. Analyze the unstructured recipe text and extract it into structured JSON.

Rules:
1. **TRANSLATE EVERYTHING TO ENGLISH.**
2. **For 'ingredients'**: Extract `name`, `quantity`, `unit`, and `group`.
   - `group` logic (Priority Order):
     a) **Explicit Headers:** If the text has clear headers (e.g., "For the sauce:"), use them.
     b) **Implicit Components:** Identify functional sub-components that are mixed in but distinct.
        - Valid Implicit Groups: "Marinade", "Batter", "Breading", "Garnish", "Sauce", "Seasonings".
        - **Condition:** Only create a group if 3+ ingredients clearly belong to it.
     c) **Default / Catch-All:** EVERYTHING else must go to "Main".
     d) **FORBIDDEN:** Do NOT create groups like "Other", "Misc", "Rest", or "Assembly". If unsure, use "Main".
3. Infer 'estimated_time' if mentioned.
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
        # FEW-SHOT 2: Implicit Components (The new "Smart" logic)
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
