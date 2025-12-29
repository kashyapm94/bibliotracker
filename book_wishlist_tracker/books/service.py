import httpx

from book_wishlist_tracker.ai import BookAI


class BookLookupService:
    def __init__(self):
        self.ai = BookAI()
        self.search_url = "https://openlibrary.org/search.json"

    def search_books(self, book_title: str, page: int = 1, limit: int = 20):
        """Search for books matching the title using OpenLibrary API."""
        params = {
            "q": f"{book_title} language:eng",
            "page": page,
            "limit": limit,
            "fields": "key,title,author_name,subject",
        }

        try:
            response = httpx.get(self.search_url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            docs = data.get("docs", [])
            count = data.get("numFound", 0)

            # Normalize results to match standard dictionary format
            # { "title": ..., "authors": [...], "key": ... }
            results = []
            for doc in docs:
                results.append(
                    {
                        "title": doc.get("title"),
                        "authors": doc.get("author_name", []),
                        "key": doc.get("key"),
                        "subjects": doc.get("subject", []),
                    }
                )

            return results, count
        except Exception as e:
            print(f"OpenLibrary Search Error: {e}")
            return [], 0

    def get_book_metadata(self, title: str, author: str) -> dict:
        """Fetch detailed metadata for a book using Perplexity AI."""
        # Use AI for detailed metadata as requested
        return self.ai.get_book_details(title, author)
