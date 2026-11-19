import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    keitaro_url: str = ""
    keitaro_api_key: str = ""
    database_url: str = "sqlite:///./keitaro_wrapper.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
# allow env overrides already handled by pydantic
# normalize
if settings.keitaro_url:
    settings.keitaro_url = settings.keitaro_url.rstrip("/")