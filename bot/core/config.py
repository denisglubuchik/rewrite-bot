from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int = 456222245


class CacheSettings(EnvBaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


class DatabaseSettings(EnvBaseSettings):
    DB_PATH: str = "test.db"


class LLMSettings(EnvBaseSettings):
    YANDEX_API_KEY: str


class Settings(BotSettings, CacheSettings, DatabaseSettings, LLMSettings):
    pass

settings = Settings()
