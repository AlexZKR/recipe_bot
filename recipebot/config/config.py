from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramBotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="bot__",
        env_file=".env",
        extra="ignore",
    )
    token: SecretStr = SecretStr("token")


class Settings(BaseSettings):
    TELEGRAM_BOT_SETTINGS: TelegramBotSettings = TelegramBotSettings()
