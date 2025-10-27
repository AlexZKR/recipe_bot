import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from recipebot.config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        raise Exception("Not chat in the update")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Initial bot message"
    )


if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_SETTINGS.token.get_secret_value())
        .build()
    )

    start_handler = CommandHandler("start", start)
    app.add_handler(start_handler)

    app.run_polling()
