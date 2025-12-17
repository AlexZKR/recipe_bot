import urllib.parse
from logging import getLogger

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from recipebot.config.enums import AppEnvironment

logger = getLogger(__name__)


class TelegramBotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="bot__",
        env_file=".env",
        extra="ignore",
    )
    token: SecretStr = SecretStr("token")


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
        password_part = (
            f":{urllib.parse.quote(self.password.get_secret_value())}"
            if self.password
            else ""
        )
        return f"postgresql://{self.user}{password_part}@{self.host}:{self.port}/{self.name}"


class HTTPTransportSettings(BaseSettings):
    chunk_size: int = 8192
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    default_timeout: int = 30
    follow_redirects: bool = False  # Disable auto-follow to capture redirect info

    @property
    def common_headers(self) -> dict[str, str]:
        return {"user-agent": self.user_agent}


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="app__", env_file=".env", extra="ignore"
    )
    env: AppEnvironment = AppEnvironment.DEV
    recipe_page_size: int = 5

    metrics_user: str = "metrics_user"
    metrics_pass: SecretStr = SecretStr("metrics_pass")

    testers_list: str = ""
    logging_level: str = "INFO"
    json_logging: bool = True

    @property
    def tester_ids(self) -> list[int]:
        """Parses the comma-separated string of IDs into a list of integers.

        Example: "12345678, 987654321, 112233445"
        """
        if not self.testers_list:
            return []
        try:
            return [int(uid.strip()) for uid in self.testers_list.split(",")]
        except ValueError:
            logger.error(
                "Failed to parse tester IDs. Ensure they are comma-separated integers."
            )
            return []


class GroqSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="groq__", env_file=".env", extra="ignore"
    )
    api_key: SecretStr = SecretStr("api_key")


class TiktokDescriptionParseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="tiktok_description_parse__", env_file=".env", extra="ignore"
    )
    model: str = "moonshotai/kimi-k2-instruct-0905"


class Settings(BaseSettings):
    TELEGRAM_BOT_SETTINGS: TelegramBotSettings = TelegramBotSettings()
    POSTGRESQL: PostgreSQLSettings = PostgreSQLSettings()
    HTTP_TRANSPORT: HTTPTransportSettings = HTTPTransportSettings()
    APP: AppSettings = AppSettings()
    GROQ_SETTINGS: GroqSettings = GroqSettings()
    TIKTOK_DESCRIPTION_PARSE_SETTINGS: TiktokDescriptionParseSettings = (
        TiktokDescriptionParseSettings()
    )
