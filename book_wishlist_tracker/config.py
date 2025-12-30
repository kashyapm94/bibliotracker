import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class to manage application environment variables.
    """

    DB_HOST: str = os.environ["POSTGRES_HOST"]
    DB_PORT: str = os.environ["POSTGRES_PORT"]
    DB_NAME: str = os.environ["POSTGRES_DB"]
    DB_USER: str = os.environ["POSTGRES_USERNAME"]
    DB_PASSWORD: str = os.environ["POSTGRES_PASSWORD"]
    PERPLEXITY_API_KEY: str = os.environ["PERPLEXITY_API_KEY"]
    ADMIN_PASSWORD: str = os.environ["ADMIN_PASSWORD"]
