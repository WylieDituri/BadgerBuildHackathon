from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Firebase Admin SDK
    firebase_project_id: str = "demo-project"
    firebase_private_key_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None
    firebase_client_id: Optional[str] = None
    firebase_auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    firebase_token_uri: str = "https://oauth2.googleapis.com/token"
    firebase_auth_provider_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    firebase_client_cert_url: Optional[str] = None

    # Application
    app_id: str = "demo-app"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
