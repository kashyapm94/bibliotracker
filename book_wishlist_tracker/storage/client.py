from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from book_wishlist_tracker.config import Config
from book_wishlist_tracker.storage.models import Base, Book


class PostgresClient:
    """
    Handles database operations for the book wishlist using SQLAlchemy.
    """

    def __init__(self, app_config: Config) -> None:
        """
        Initialize the PostgresClient with database connection settings.

        Args:
            app_config (Config): Configuration object containing database credentials and host.
        """
        # Construct Database URL
        # Format: postgresql+psycopg://user:password@host:port/dbname
        self.url = f"postgresql+psycopg://{app_config.DB_USER}:{app_config.DB_PASSWORD}@{app_config.DB_HOST}:{app_config.DB_PORT}/{app_config.DB_NAME}"

        self.engine = create_engine(self.url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Ensure tables exist
        self.initialize_schema()

    def initialize_schema(self) -> None:
        """
        Create all tables defined in the SQLAlchemy models.
        """
        Base.metadata.create_all(bind=self.engine)

    def check_book_exists(self, book_title: str) -> bool:
        """
        Check if a book with the given title already exists in the database.

        Args:
            book_title (str): The title of the book to check (case-insensitive).

        Returns:
            bool: True if the book exists, False otherwise.
        """
        with self.SessionLocal() as session:
            stmt = select(Book).where(Book.title.ilike(book_title))
            result = session.execute(stmt).first()
            return result is not None

    def add_book(
        self,
        book_title: str,
        book_author: str,
        book_description: str | None = None,
        book_region: str | None = None,
        book_subjects: list[str] | None = None,
        is_fiction_category: str | None = None,
    ) -> tuple[bool, str]:
        """
        Add a new book record to the wishlist.

        Args:
            book_title (str): The canonical title of the book.
            book_author (str): The author(s) of the book.
            book_description (str, optional): A brief summary. Defaults to None.
            book_region (str, optional): Geographical region. Defaults to None.
            book_subjects (list[str], optional): List of genres/subjects. Defaults to None.
            is_fiction_category (str, optional): "Fiction" or "Non-Fiction". Defaults to None.

        Returns:
            tuple[bool, str]: A tuple of (success_status, status_message).
        """
        try:
            if self.check_book_exists(book_title):
                return True, f"Book '{book_title}' already exists."

            # Format subjects
            subjects_str = ", ".join(book_subjects[:5]) if book_subjects else None

            new_book = Book(
                title=book_title,
                author=book_author,
                description=book_description,
                region=book_region,
                subjects=subjects_str,
                is_fiction=is_fiction_category,
            )

            with self.SessionLocal() as session:
                session.add(new_book)
                session.commit()
                # session.refresh(new_book) # Optional, if we needed the ID back

            return True, "Book added successfully to Database."
        except Exception as error:
            print(f"DB Error: {error}")
            return False, str(error)

    def get_all_books(
        self, skip_records: int = 0, limit_records: int = 10
    ) -> list[Book]:
        """
        Fetch a paginated list of books from the database.

        Args:
            skip_records (int): Number of records to skip for pagination. Defaults to 0.
            limit_records (int): Maximum number of records to return. Defaults to 10.

        Returns:
            list[Book]: A list of Book model instances, ordered by ID descending.
        """
        with self.SessionLocal() as session:
            stmt = (
                select(Book)
                .order_by(Book.id.desc())
                .offset(skip_records)
                .limit(limit_records)
            )
            results = session.execute(stmt).scalars().all()
            return results

    def get_total_count(self) -> int:
        """
        Get the total count of all books in the wishlist.

        Returns:
            int: The total number of book records.
        """
        from sqlalchemy import func

        with self.SessionLocal() as session:
            stmt = select(func.count(Book.id))
            return session.execute(stmt).scalar() or 0
