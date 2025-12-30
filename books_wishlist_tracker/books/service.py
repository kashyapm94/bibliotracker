import httpx

from books_wishlist_tracker.ai import BookAI


class BookLookupService:
    """
    Provides functions to search for books and fetch detailed metadata.
    """

    def __init__(self) -> None:
        """
        Initialize the BookLookupService with an AI client and OpenLibrary URL.
        """
        self.ai = BookAI()
        self.search_url = "https://openlibrary.org/search.json"

    def search_books(
        self, search_query: str, page_number: int = 1, results_limit: int = 20
    ) -> tuple[list[dict], int]:
        """
        Search for books matching the query using the OpenLibrary API.

        Args:
            search_query (str): The book title or keywords to search for.
            page_number (int): The results page to fetch. Defaults to 1.
            results_limit (int): Max number of results per page. Defaults to 20.

        Returns:
            tuple[list[dict], int]: A tuple containing a list of normalized book results
                                   and the total number of books found.
        """
        params = {
            "q": f"{search_query} language:eng",
            "page": page_number,
            "limit": results_limit,
            "fields": "key,title,author_name,subject",
        }

        try:
            response = httpx.get(self.search_url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            docs = data.get("docs", [])
            total_matches = data.get("numFound", 0)

            # Normalize results to match standard dictionary format
            # { "title": ..., "authors": [...], "key": ... }
            normalized_results = []
            for doc in docs:
                normalized_results.append(
                    {
                        "title": doc.get("title"),
                        "authors": doc.get("author_name", []),
                        "key": doc.get("key"),
                        "subjects": doc.get("subject", []),
                    }
                )

            return normalized_results, total_matches
        except Exception as error:
            print(f"OpenLibrary Search Error: {error}")
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
