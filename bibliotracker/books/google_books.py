import logging

import httpx

from bibliotracker.config import Config

logger = logging.getLogger(__name__)


class GoogleBooksClient:
    """
    A client to search for books using the Google Books API.
    """

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, api_key: str | None = None) -> None:
        self.client = httpx.Client(
            timeout=10.0, headers={"Referer": Config.REFERER_URL}
        )
        self.api_key = api_key

    def search_books(
        self, query: str, max_results: int = 10, start_index: int = 0
    ) -> dict:
        """
        Search for books matching the query.

        Args:
            query (str): The search term.
            max_results (int): Max number of results to return (default 10, max 40).
            start_index (int): The index of the first result to return (for pagination).

        Returns:
            dict: The JSON response from Google Books API.
        """
        params = {
            "q": query,
            "maxResults": min(max_results, 40),  # API limit is 40
            "startIndex": start_index,
            "printType": "books",
            "langRestrict": "en",
        }
        if self.api_key:
            params["key"] = self.api_key

        try:
            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP Error searching Google Books: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {}

    def close(self) -> None:
        self.client.close()
