from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from recipebot.config.enums import AppEnvironment


class TelegramBotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="bot__",
        env_file=".env",
        extra="ignore",
    )
    test_token: SecretStr = SecretStr("test_token")
    prod_token: SecretStr = SecretStr("prod_token")


class PostgreSQLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="db__", env_file=".env", extra="ignore"
    )

    host: str = "postgres"
    port: int = 5432
    user: str = "postgres"
    password: SecretStr | None = SecretStr("pass")
    name: str = "postgres"

    @property
    def dsn(self) -> str:
        """
        Returns a PostgreSQL DSN string in the format:
        postgresql://user:password@host:port/dbname
        """
        password_part = f":{self.password.get_secret_value()}" if self.password else ""
        return f"postgresql://{self.user}{password_part}@{self.host}:{self.port}/{self.name}"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="app__", env_file=".env", extra="ignore"
    )
    env: AppEnvironment = AppEnvironment.DEV
    recipe_page_size: int = 5


class Settings(BaseSettings):
    TELEGRAM_BOT_SETTINGS: TelegramBotSettings = TelegramBotSettings()
    POSTGRESQL: PostgreSQLSettings = PostgreSQLSettings()
    APP: AppSettings = AppSettings()
