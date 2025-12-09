import os
from typing import Optional

class Settings:
    """Конфигурация приложения"""
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    
    APP_NAME: str = "Redis Веб-приложение"
    APP_VERSION: str = "1.0.0"

settings = Settings()