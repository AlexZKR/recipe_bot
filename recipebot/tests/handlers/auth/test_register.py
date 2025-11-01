from unittest.mock import AsyncMock

import pytest
from telegram import User as TGUser
from telegram.ext._application import Application

from recipebot.drivers.handlers.auth.messages import REGISTER_SUCCESS
from recipebot.ports.repositories.user_repository import UserRepositoryABC
from recipebot.tests.utils import get_update, process_update


@pytest.mark.asyncio
async def test_register_ok(
    tg_user: TGUser, test_app: Application, mock_user_repo: UserRepositoryABC
) -> None:
    update = get_update(from_user=tg_user, text="/register", bot=test_app.bot)

    await process_update(update, test_app)

    assert update.effective_chat is not None

    mock: AsyncMock = test_app.bot.send_message
    mock.assert_called_once_with(
        chat_id=update.effective_chat.id,
        text=REGISTER_SUCCESS,
    )

    assert mock_user_repo.get_by_tg_user(tg_user) is not None
