import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    keitaro_url: str = ""
    keitaro_api_key: str = ""
    database_url: str = "sqlite:///./keitaro_wrapper.db"


settings = Settings()
# allow env overrides already handled by pydantic
# normalize
if settings.keitaro_url:
    settings.keitaro_url = settings.keitaro_url.rstrip("/")