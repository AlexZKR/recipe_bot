import json
from collections.abc import Iterable

from groq.types.chat import ChatCompletionMessageParam


def get_tt_recipe_prompt(user_prompt: str) -> Iterable[ChatCompletionMessageParam]:
    system_prompt = """
You are a text extraction assistant. Analyze the following unstructured recipe text and extract it into the structured format.

Rules:
1. **TRANSLATE EVERYTHING TO ENGLISH.** The input is in Russian, but the output JSON must be English.
2. **For 'ingredients'**: Extract each ingredient as an object with `name`, `quantity`, `unit`, and `group`.
   - `name`, `quantity`, `unit`: Standard extraction. Translate names/units to English.
   - `group`: Look for section headers in the text (e.g., "Соус:" -> "Sauce", "Для кляра:" -> "Batter"). Assign this group name to all ingredients listed under it. If no header is present, use "Main".
3. Infer 'estimated_time' if mentioned.
"""
    return [
        {"role": "system", "content": system_prompt},
        # -------------------------------------------------------
        # FEW-SHOT EXAMPLE: TEACHING THE "GROUPING" LOGIC
        # -------------------------------------------------------
        {
            "role": "user",
            "content": "Рецепт курицы: - Курица 600 г. Соус: - Сахар 1,5 ст. л. - Соевый соус 3 ст. л.",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "title": "Chicken Recipe",
                    "ingredients": [
                        # The first item has no header, so it defaults to "Main"
                        {"name": "chicken", "qty": "600", "unit": "g", "group": "Main"},
                        # The model sees "Соус:", translates it, and applies it to following items
                        {
                            "name": "sugar",
                            "qty": "1.5",
                            "unit": "tbsp",
                            "group": "Sauce",
                        },
                        {
                            "name": "soy sauce",
                            "qty": "3",
                            "unit": "tbsp",
                            "group": "Sauce",
                        },
                    ],
                    "steps": [],
                    "desc": "Chicken with sauce",
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
