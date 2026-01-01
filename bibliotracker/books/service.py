import logging

from bibliotracker.ai import BookAI
from bibliotracker.books.google_books import GoogleBooksClient
from bibliotracker.config import Config

logger = logging.getLogger(__name__)


class BookLookupService:
    """
    Provides functions to search for books and fetch detailed metadata.
    """

    def __init__(self) -> None:
        """
        Initialize the BookLookupService with an AI client and Google Books client.
        """
        self.ai = BookAI()
        config = Config()
        self.google_client = GoogleBooksClient(api_key=config.GOOGLE_BOOKS_API_KEY)

    def search_books(
        self, search_query: str, page_number: int = 1, results_limit: int = 20
    ) -> tuple[list[dict], int]:
        """
        Search for books matching the query using the Google Books API.

        Args:
            search_query (str): The book title or keywords to search for.
            page_number (int): The results page to fetch. Defaults to 1.
            results_limit (int): Max number of results per page. Defaults to 20.

        Returns:
            tuple[list[dict], int]: A tuple containing a list of normalized book results
                                   and the total number of books found.
        """
        # Calculate start_index for Google Books (0-based)
        start_index = (page_number - 1) * results_limit

        try:
            data = self.google_client.search_books(
                search_query, max_results=results_limit, start_index=start_index
            )

            items = data.get("items", [])
            total_matches = data.get("totalItems", 0)

            # Normalize results to match standard dictionary format
            # { "title": ..., "authors": [...], "key": ... }
            normalized_results = []
            for item in items:
                info = item.get("volumeInfo", {})
                normalized_results.append(
                    {
                        "title": info.get("title"),
                        "authors": info.get("authors", []),
                        "key": item.get("id"),  # Using Google Books ID as key
                        "subjects": info.get("categories", []),
                    }
                )

            return normalized_results, total_matches
        except Exception as error:
            logger.error(f"Google Books Search Error: {error}")
            return [], 0

    def get_book_metadata(self, book_title: str, book_author: str) -> dict:
        """
        Fetch detailed AI-generated metadata for a specific book.

        Args:
            book_title (str): The title of the book.
            book_author (str): The author(s) of the book.

        Returns:
            dict: Detailed book metadata (summary, subjects, region, etc.).
        """
        # Use AI for detailed metadata as requested
        return self.ai.get_book_details(book_title, book_author)
