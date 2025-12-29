import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "book_wishlist")
    DB_USER = os.getenv("POSTGRES_USERNAME", "postgres")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
