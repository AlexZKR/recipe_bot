from unittest.mock import AsyncMock

from telegram import Bot, User


class MockBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._unfreeze()
        self.send_message = AsyncMock()

    async def get_me(self, *args, **kwargs) -> User:
        user = User(id=1, is_bot=True, first_name="Test Bot", username="test_bot")
        self._bot_user = user
        return user
