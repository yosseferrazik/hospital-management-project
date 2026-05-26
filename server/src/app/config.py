"""Application configuration — loads settings from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask configuration loaded from .env / environment variables."""

    # Database connection
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # Verify connections before use
        "pool_recycle": 300,     # Recycle connections every 5 min
    }

    # JWT authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # External API for visit data forwarding
    EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL")
    EXTERNAL_API_USERNAME = os.getenv("EXTERNAL_API_USERNAME")
    EXTERNAL_API_PASSWORD = os.getenv("EXTERNAL_API_PASSWORD")

    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable is not set")
