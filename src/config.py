from pydantic_settings import BaseSettings, SettingsConfigDict
import os


os.environ.pop("DATABASE_URL", None)

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_ALGORITHM: str
    JWT_SECRET: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()