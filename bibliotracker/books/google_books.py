import logging

import httpx

from bibliotracker.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
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


def main() -> None:
    """
    Main execution entry point for interactive search.
    """
    print("--- Google Books Search Tool ---")
    query = input("Enter book name to search: ").strip()
    if not query:
        print("Empty query. Exiting.")
        return

    client = GoogleBooksClient()
    start_index = 0
    page_size = 10

    try:
        while True:
            print(f"\nSearching for '{query}' (Page {start_index // page_size + 1})...")
            results = client.search_books(
                query, max_results=page_size, start_index=start_index
            )

            total_items = results.get("totalItems", 0)
            items = results.get("items", [])

            if not items:
                print("No more books found.")
                break

            print(
                f"\nFound {total_items} total matches. Showing results {start_index + 1} to {start_index + len(items)}:\n"
            )

            for i, item in enumerate(items, 1):
                info = item.get("volumeInfo", {})
                title = info.get("title", "Unknown Title")
                authors = ", ".join(info.get("authors", ["Unknown Author"]))
                published_date = info.get("publishedDate", "N/A")
                print(f"{start_index + i}. {title} by {authors} ({published_date})")

            # Check if we've reached the end
            if start_index + len(items) >= total_items:
                print("\nEnd of results.")
                break

            choice = input("\nShow next 10 results? (y/n): ").strip().lower()
            if choice != "y":
                print("Exiting search.")
                break

            start_index += page_size

    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSearch cancelled.")
