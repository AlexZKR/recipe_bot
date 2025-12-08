import asyncio
from datetime import datetime

from telegram import Bot, Chat, MessageEntity, Update
from telegram import User as TGUser
from telegram._message import Message
from telegram.constants import ChatType
from telegram.ext._application import Application


def get_update(
    from_user: TGUser, text: str, bot: Bot, chat_type: ChatType = ChatType.PRIVATE
) -> Update:
    chat = Chat(id=1, type=chat_type)
    entities: tuple[MessageEntity, ...] = ()
    if text.startswith("/"):
        entities = (
            MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len(text)),
        )
    msg = Message(
        message_id=1,
        date=datetime.now(),
        chat=chat,
        text=text,
        from_user=from_user,
        entities=entities,
    )
    msg._bot = bot
    return Update(update_id=1, message=msg)


async def process_update(update: Update, app: Application):
    await app.update_queue.put(update)
    await asyncio.sleep(0.1)
