import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class to manage application environment variables.
    """

    DB_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME: str = os.getenv("POSTGRES_DB", "book_wishlist")
    DB_USER: str = os.getenv("POSTGRES_USERNAME", "postgres")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
