import logging
from collections import defaultdict

from sqlalchemy import create_engine, delete, func, select, update
from sqlalchemy.orm import sessionmaker

from bibliotracker.config import Config
from bibliotracker.storage.models import Base, Book

logger = logging.getLogger(__name__)


class PostgresClient:
    """
    Handles database operations for the book to-read list using SQLAlchemy.
    """

    def __init__(self, app_config: Config) -> None:
        """
        Initialize the PostgresClient with database connection settings.

        Args:
            app_config (Config): Configuration object containing database credentials and host.
        """
        self.engine = create_engine(str(app_config.SQLALCHEMY_DATABASE_URI))
        self.session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

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
        with self.session() as session:
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
        is_owned: bool = False,
    ) -> tuple[bool, str]:
        """
        Add a new book record to the to-read list.

        Args:
            book_title (str): The canonical title of the book.
            book_author (str): The author(s) of the book.
            book_description (str, optional): A brief summary. Defaults to None.
            book_region (str, optional): Geographical region. Defaults to None.
            book_subjects (list[str], optional): List of genres/subjects. Defaults to None.
            is_fiction_category (str, optional): "Fiction" or "Non-Fiction". Defaults to None.
            is_owned (bool, optional): Whether the user owns this book. Defaults to False.

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
                is_owned=is_owned,
            )

            with self.session() as session:
                session.add(new_book)
                session.commit()
                # session.refresh(new_book) # Optional, if we needed the ID back

            return True, "Added to the To-Read List"
        except Exception as error:
            logger.error(f"DB Error: {error}")
            return False, str(error)

    def update_book_ownership(self, book_id: int, is_owned: bool) -> bool:
        """
        Update the ownership status of a book.

        Args:
            book_id (int): The ID of the book to update.
            is_owned (bool): The new ownership status.

        Returns:
            bool: True if successful, False if book not found.
        """

        try:
            with self.session() as session:
                stmt = (
                    update(Book)
                    .where(Book.id == book_id)
                    .values(is_owned=is_owned)
                    .execution_options(synchronize_session="fetch")
                )
                result = session.execute(stmt)
                session.commit()
                return result.rowcount > 0
        except Exception as error:
            logger.error(f"DB Update Error: {error}")
            return False

    def delete_book(self, book_id: int) -> bool:
        """
        Delete a book record from the database.

        Args:
            book_id (int): The ID of the book to delete.

        Returns:
            bool: True if successful, False if book not found or error.
        """
        try:
            with self.session() as session:
                stmt = delete(Book).where(Book.id == book_id)
                result = session.execute(stmt)
                session.commit()
                return result.rowcount > 0
        except Exception as error:
            logger.error(f"DB Delete Error: {error}")
            return False

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
        with self.session() as session:
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
        Get the total count of all books in the to-read list.

        Returns:
            int: The total number of book records.
        """

        with self.session() as session:
            stmt = select(func.count(Book.id))
            return session.execute(stmt).scalar() or 0

    def get_stats(self) -> dict:
        """
        Aggregate stats for regions and fiction/non-fiction distribution.
        Returns dictionaries mapping categories/regions to lists of books.
        """
        with self.session() as session:
            # Fetch all books to process in python (dataset is small)
            stmt = select(Book)
            books = session.execute(stmt).scalars().all()

            region_map = defaultdict(list)
            category_map = defaultdict(list)
            subject_map = defaultdict(list)
            authors_map = defaultdict(list)
            ownership_map = defaultdict(list)
            authors_set = set()

            for book in books:
                item = {"title": book.title, "author": book.author}

                # Track unique authors
                authors_set.add(book.author)

                # Category Stats
                cat = book.is_fiction if book.is_fiction else "Uncategorized"
                category_map[cat].append(item)

                # Region Stats (Split comma-separated)
                if book.region:
                    regions = [r.strip() for r in book.region.split(",")]
                    for region in regions:
                        if region:
                            region_map[region].append(item)
                else:
                    region_map["Unknown"].append(item)

                # Subject Stats (Split comma-separated)
                if book.subjects:
                    subjects = [s.strip() for s in book.subjects.split(",")]
                    for subject in subjects:
                        if subject:
                            subject_map[subject].append(item)

                # Ownership Stats
                status = "Owned" if book.is_owned else "Not Owned"
                ownership_map[status].append(item)

                # Author Stats (Split comma-separated)
                if book.author:
                    authors_list = [a.strip() for a in book.author.split(",")]
                    for author in authors_list:
                        if author:
                            authors_map[author].append(item)

            # Get top 5 subjects
            top_subjects = dict(
                sorted(subject_map.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            )

            # Get top 5 authors
            top_authors = dict(
                sorted(authors_map.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            )

            return {
                "total_books": len(books),
                "unique_authors": len(authors_set),
                "regions": dict(region_map),
                "categories": dict(category_map),
                "top_subjects": top_subjects,
                "top_authors": top_authors,
                "ownership": dict(ownership_map),
            }
