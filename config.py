
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    # Flask security
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            "FLASK_SECRET_KEY is missing. "
            "Please configure it in your .env file."
        )

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.getenv("COOKIE_SECURE", "False").lower() == "true"
    )
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    TEMPLATES_AUTO_RELOAD = True

    # Database settings
    TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
    TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


def get_config():
    environment = os.getenv("FLASK_ENV", "development").lower()

    if environment == "production":
        return ProductionConfig

    return DevelopmentConfig
