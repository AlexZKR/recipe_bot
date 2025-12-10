# recipebot/adapters/services/groq_tt_parser/prompts/steps.py
import json
from collections.abc import Iterable

from groq.types.chat import ChatCompletionMessageParam

from .base import BASE_SYSTEM_PROMPT

STEPS_EXTRACTION_RULES = """
**Rules for 'steps':**
1. Extract actionable cooking instructions.
2. **Format:** Output a valid JSON object with a single key `"steps"` containing the list of strings.
   - Example: `{"steps": ["Step 1", "Step 2"]}`
3. **Segmentation:** Split paragraph text into distinct, logical steps.
4. Remove anything except the steps (e.g., ingredient lists, "Enjoy!", "Subscribe").
5. Do NOT number the strings inside the list.
"""

STEPS_FEW_SHOTS: list[ChatCompletionMessageParam] = [
    # -------------------------------------------------------
    # FEW-SHOT 1: Simple Baseline
    # -------------------------------------------------------
    {
        "role": "user",
        "content": "First chop the onions. Then fry them. Thanks for watching!",
    },
    {
        "role": "assistant",
        # CHANGED: Wrapped in {"steps": ...}
        "content": json.dumps({"steps": ["Chop the onions.", "Fry the onions."]}),
    },
    # -------------------------------------------------------
    # FEW-SHOT 2: Complex (Translation + Noise Removal + Segmentation)
    # -------------------------------------------------------
    {
        "role": "user",
        "content": """Рецепт курицы в китайском стиле

нам понадобится:
- Курица 600 г (филе)
- Мука 3 ст. л.
- Яйцо 1 шт.
- Приправы по вкусу
Соус:
  - Сахар 1,5 ст. л.
  - Соевый соус 3 ст. л.
  - Кетчуп 3 ст. л.
  - Растительное масло 1,5 ст. л.

Нарежьте куриное филе на небольшие кусочки. В миске смешайте муку, яйцо и приправы. Обваляйте кусочки курицы в этой смеси.

Разогрейте сковороду с растительным маслом на среднем огне. Обжаривайте курицу до золотистой корочки, примерно 5-7 минут.

В миске смешайте соевый соус, сахар, кетчуп и растительное масло. Как только курица будет готова, залейте соусом и перемешайте. Уменьшите огонь и готовьте еще 2-3 минуты, чтобы соус хорошо пропитал курицу.

Подавайте горячей, украсив зеленью по желанию. Отлично сочетается с рисом или овощами.

Приятного аппетита!""",
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "steps": [
                    "Cut the chicken fillet into small pieces.",
                    "In a bowl mix flour, egg and seasonings.",
                    "Coat the chicken pieces in this mixture.",
                    "Heat a pan with vegetable oil over medium heat.",
                    "Fry the chicken until golden, about 5–7 minutes.",
                    "In a bowl mix soy sauce, sugar, ketchup and vegetable oil.",
                    "When the chicken is ready, pour in the sauce and stir.",
                    "Lower the heat and cook 2–3 minutes more so the sauce coats the chicken well.",
                    "Serve hot, garnished with herbs if desired.",
                ]
            }
        ),
    },
]


def get_tt_recipe_steps_prompt(user_text: str) -> Iterable[ChatCompletionMessageParam]:
    system_content = f"{BASE_SYSTEM_PROMPT}\n\n{STEPS_EXTRACTION_RULES}"

    return [
        {"role": "system", "content": system_content},
        *STEPS_FEW_SHOTS,
        {"role": "user", "content": user_text},
    ]
