import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
from typing import Optional

_db: Optional[firestore.Client] = None


def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    global _db

    if firebase_admin._apps:
        # Already initialized
        try:
            _db = firestore.client()
        except Exception:
            print("Warning: Firebase initialized but Firestore unavailable. Running in mock mode.")
            _db = None
        return

    # Use service account credentials from environment
    # For demo purposes, you can also use Application Default Credentials
    try:
        if settings.firebase_private_key and settings.firebase_client_email:
            cred_dict = {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                "private_key_id": settings.firebase_private_key_id,
                "private_key": settings.firebase_private_key.replace("\\n", "\n"),
                "client_email": settings.firebase_client_email,
                "client_id": settings.firebase_client_id,
                "auth_uri": settings.firebase_auth_uri,
                "token_uri": settings.firebase_token_uri,
                "auth_provider_x509_cert_url": settings.firebase_auth_provider_cert_url,
                "client_x509_cert_url": settings.firebase_client_cert_url,
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
        else:
            # Use Application Default Credentials (for local dev with gcloud)
            print("Warning: No Firebase credentials provided. Running in mock mode.")
            print("To connect to Firebase, add credentials to .env file.")
            _db = None
    except Exception as e:
        print(f"Warning: Firebase initialization failed: {e}")
        print("Running in mock mode without Firebase connection.")
        _db = None


def get_db() -> Optional[firestore.Client]:
    """Get the Firestore database client."""
    if _db is None:
        initialize_firebase()
    return _db
