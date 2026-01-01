import os

from dotenv import load_dotenv
from pydantic import PostgresDsn, computed_field

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class to manage application environment variables.
    """

    DB_HOST: str = os.environ["POSTGRES_HOST"]
    DB_PORT: int = int(os.environ["POSTGRES_PORT"])
    DB_NAME: str = os.environ["POSTGRES_DB"]
    DB_USER: str = os.environ["POSTGRES_USERNAME"]
    DB_PASSWORD: str = os.environ["POSTGRES_PASSWORD"]
    PERPLEXITY_API_KEY: str = os.environ["PERPLEXITY_API_KEY"]
    ADMIN_PASSWORD: str = os.environ["ADMIN_PASSWORD"]
    GOOGLE_BOOKS_API_KEY: str | None = os.environ.get("GOOGLE_BOOKS_API_KEY")
    REFERER_URL: str = os.environ.get("REFERER_URL", "http://127.0.0.1:8000/")

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )
