from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramBotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="bot__",
        env_file=".env",
        extra="ignore",
    )
    token: SecretStr = SecretStr("token")


class PostgreSQLSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    HOST: str = "postgres"
    PORT: int = 5432
    USER: str = "postgres"
    PASSWORD: SecretStr | None = SecretStr("pass")
    NAME: str = "postgres"

    @property
    def dsn(self) -> str:
        """
        Returns a PostgreSQL DSN string in the format:
        postgresql://user:password@host:port/dbname
        """
        password_part = f":{self.PASSWORD.get_secret_value()}" if self.PASSWORD else ""
        return f"postgresql://{self.USER}{password_part}@{self.HOST}:{self.PORT}/{self.NAME}"


class Settings(BaseSettings):
    TELEGRAM_BOT_SETTINGS: TelegramBotSettings = TelegramBotSettings()
    POSTGRESQL: PostgreSQLSettings = PostgreSQLSettings()
