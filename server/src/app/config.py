import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL")
    EXTERNAL_API_USERNAME = os.getenv("EXTERNAL_API_USERNAME")
    EXTERNAL_API_PASSWORD = os.getenv("EXTERNAL_API_PASSWORD")

    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable is not set")
