try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

from typing import Optional


class Settings(BaseSettings):
    # Application
    app_id: str = "demo-app"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    
    # Storage mode: "memory" (default, no setup needed) or "firebase" (requires credentials)
    storage_mode: str = "memory"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
