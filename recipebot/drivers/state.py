from typing import TypedDict, cast

from telegram.ext import ContextTypes

from recipebot.adapters.repositories.sql.base.base_asyncpg_repo import AsyncpgConnection
from recipebot.infra.groq.client import GroqClient
from recipebot.ports.repositories.recipe_repository import RecipeRepositoryABC
from recipebot.ports.repositories.user_repository import UserRepositoryABC


class BotState(TypedDict):
    user_repo: UserRepositoryABC
    recipe_repo: RecipeRepositoryABC
    asyncpg_conn: AsyncpgConnection
    groq_client: GroqClient


def get_state(context: ContextTypes.DEFAULT_TYPE) -> BotState:
    return cast(BotState, context.bot_data)
