from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "app"
    debug_mode: bool = False
    log_level: str = Field(env="LOG_LEVEL", default="DEBUG")
