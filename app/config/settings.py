from pydantic import BaseSettings, Field, SecretStr


class PostgresSettings(BaseSettings):
    host: str = Field("localhost", env="DB_HOST")
    database_name: str = Field("auth", env="DB_NAME")
    user: SecretStr = Field("postgres", env="DB_USER")
    password: SecretStr = Field("postgres", env="DB_PASSWORD")
    min_size_pool: int = Field(2, env="DB_MIN_POOL_SIZE")
    max_size_pool: int = Field(10, env="DB_MAX_POOL_SIZE")


class JWTSettings(BaseSettings):
    expiration_minutes: int = Field(env="JWT_EXPIRATION_MINUTES", default=60 * 24 * 3)
    secret_key: str = Field(env="JWT_SECRET_KEY", default="super-secret-key##")
    crypto_algorithm: str = Field(env="JWT_CRYPTO_ALGORITHM", default="HS256")


class Settings(BaseSettings):
    app_name: str = "app"
    debug_mode: bool = False
    log_level: str = Field(env="LOG_LEVEL", default="DEBUG")

    postgres: PostgresSettings = PostgresSettings()
    jwt: JWTSettings = JWTSettings()


def get_settings() -> Settings:
    return Settings()
