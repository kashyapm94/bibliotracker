from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from book_wishlist_tracker.config import Config
from book_wishlist_tracker.storage.models import Base, Book


class PostgresClient:
    def __init__(self, config: Config):
        # Construct Database URL
        # Format: postgresql+psycopg://user:password@host:port/dbname
        self.url = f"postgresql+psycopg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

        self.engine = create_engine(self.url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Ensure tables exist
        self.initialize_schema()

    def initialize_schema(self):
        Base.metadata.create_all(bind=self.engine)

    def check_book_exists(self, title: str) -> bool:
        """Check if a book with the given title already exists (case-insensitive)."""
        with self.SessionLocal() as session:
            stmt = select(Book).where(Book.title.ilike(title))
            result = session.execute(stmt).first()
            return result is not None

    def add_book(
        self,
        title: str,
        author: str,
        year: int | None = None,
        isbn: str | None = None,
        description: str | None = None,
        country: str | None = None,
        region: str | None = None,
        subjects: list[str] | None = None,
    ) -> tuple[bool, str]:
        """Add a book to the Postgres database. Returns (success, message)."""
        try:
            if self.check_book_exists(title):
                return True, f"Book '{title}' already exists."

            # Format subjects
            subjects_str = ", ".join(subjects[:5]) if subjects else None

            new_book = Book(
                title=title,
                author=author,
                year=year,
                isbn=isbn,
                description=description,
                country=country,
                region=region,
                subjects=subjects_str,
            )

            with self.SessionLocal() as session:
                session.add(new_book)
                session.commit()
                # session.refresh(new_book) # Optional, if we needed the ID back

            return True, "Book added successfully to Database."
        except Exception as e:
            print(f"DB Error: {e}")
            return False, str(e)
