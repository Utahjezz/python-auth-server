from pydantic import BaseSettings, Field, SecretStr


class PostgresSettings(BaseSettings):
    host: str = Field("localhost", env="DB_HOST")
    database_name: str = Field("ocus", env="DB_NAME")
    user: SecretStr = Field("postgres", env="DB_USER")
    password: SecretStr = Field("postgres", env="DB_PASSWORD")
    min_size_pool: int = Field(2, env="DB_MIN_POOL_SIZE")
    max_size_pool: int = Field(10, env="DB_MAX_POOL_SIZE")


class Settings(BaseSettings):
    app_name: str = "app"
    debug_mode: bool = False
    log_level: str = Field(env="LOG_LEVEL", default="DEBUG")

    postgres: PostgresSettings = PostgresSettings()


def get_settings() -> Settings:
    return Settings()
