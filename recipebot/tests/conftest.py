from collections.abc import AsyncGenerator

import pytest_asyncio
from telegram import Bot
from telegram import User as TGUser
from telegram.ext import ApplicationBuilder
from telegram.ext._application import Application

from recipebot.domain.auth.user import User
from recipebot.drivers.handlers import add_handlers
from recipebot.ports.repositories.recipe_repository import RecipeRepositoryABC
from recipebot.ports.repositories.user_repository import UserRepositoryABC
from recipebot.tests.mocks.mock_bot import MockBot
from recipebot.tests.mocks.mock_recipe_repo import MockRecipeRepo
from recipebot.tests.mocks.mock_user_repo import MockUserRepo


@pytest_asyncio.fixture
async def mock_user_repo() -> UserRepositoryABC:
    return MockUserRepo()


@pytest_asyncio.fixture
async def mock_recipe_repo() -> RecipeRepositoryABC:
    return MockRecipeRepo()


@pytest_asyncio.fixture
async def tg_user() -> TGUser:
    return TGUser(
        id=1,
        username="test_user",
        first_name="Test User",
        is_bot=False,
    )


@pytest_asyncio.fixture
async def test_bot():
    bot = MockBot(token="XXXX_TEST_TOKEN_XXXX")
    async with bot:
        yield bot


@pytest_asyncio.fixture
async def test_app(
    test_bot: Bot,
    mock_user_repo: UserRepositoryABC,
    mock_recipe_repo: RecipeRepositoryABC,
) -> AsyncGenerator[Application]:
    async def on_startup(
        app: Application,
    ):
        app.bot_data["user_repo"] = mock_user_repo
        app.bot_data["recipe_repo"] = mock_recipe_repo

    async def on_shutdown(app: Application):
        app.bot_data.clear()

    app: Application = (
        ApplicationBuilder()
        .bot(test_bot)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    add_handlers(app)

    await app.initialize()
    if app.post_init:
        await app.post_init(app)
    await app.start()

    yield app

    await app.stop()
    await app.shutdown()


@pytest_asyncio.fixture
async def registered_user(tg_user: TGUser, mock_user_repo: UserRepositoryABC) -> User:
    return await mock_user_repo.add(tg_user)
