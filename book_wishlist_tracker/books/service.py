import httpx


class BookLookupService:
    BASE_URL = "https://openlibrary.org/search.json"

    def search_books(self, book_title: str, page: int = 1, limit: int = 20):
        """Search for books by title and return a tuple: (list of candidates with metadata, total_count)."""
        if not book_title:
            return [], 0
        try:
            response = httpx.get(
                self.BASE_URL,
                params={"q": book_title, "limit": limit, "page": page},
            )
            response.raise_for_status()
            data = response.json()

            candidates = []
            for doc in data.get("docs", []):
                candidates.append(
                    {
                        "title": doc.get("title"),
                        "authors": doc.get("author_name", []),
                        "first_publish_year": doc.get("first_publish_year"),
                        "isbn": doc.get("isbn", [])[
                            :1
                        ],  # Just take the first ISBN for now
                        "number_of_pages": doc.get("number_of_pages_median"),
                        "subjects": doc.get("subject", [])[:5],  # First 5 subjects
                        "key": doc.get("key"),
                    }
                )

            total_count = data.get("numFound", 0)
            return candidates, total_count
        except Exception as e:
            print(f"Error searching for '{book_title}': {e}")
            return [], 0

    def get_author(self, book_title: str) -> str | None:
        """Deprecated: Use search_books for more control. Kept for backward compatibility if needed."""
        results = self.search_books(book_title)[0]  # search_books returns a tuple now
        if not results:
            return None
        # Return first author of first result as a fallback
        authors = results[0].get("authors", [])
        return authors[0] if authors else None

    @staticmethod
    def _extract_year(entry: dict) -> int:
        """Extract year from publish_date string."""
        date_str = entry.get("publish_date", "")
        if not date_str:
            return 0
        # Basic parsing: look for 4 digit year
        import re

        match = re.search(r"\d{4}", date_str)
        return int(match.group(0)) if match else 0

    def get_latest_edition(self, work_key: str) -> dict | None:
        """Fetch all editions for a work and return metadata for the latest one based on publish date."""
        if not work_key:
            return None

        try:
            # work_key usually looks like "/works/OL123W", editions endpoint is /works/OL123W/editions.json
            url = f"https://openlibrary.org{work_key}/editions.json"
            response = httpx.get(url, params={"limit": 100})  # Fetch top 100 editions
            response.raise_for_status()
            data = response.json()

            entries = data.get("entries", [])
            if not entries:
                return None

            # Filter for English editions
            def is_english(entry):
                langs = entry.get("languages", [])
                return any(lang.get("key") == "/languages/eng" for lang in langs)

            english_entries = [e for e in entries if is_english(e)]

            if english_entries:
                entries = english_entries

            # Sort by year descending
            entries.sort(key=self._extract_year, reverse=True)
            latest = entries[0]

            return {
                "title": latest.get("title"),
                "year": self._extract_year(latest),
                "isbn": latest.get("isbn_13", latest.get("isbn_10", []))[:1],
                "pages": latest.get("number_of_pages"),
                "publishers": latest.get("publishers", []),
                "key": latest.get("key"),
            }

        except Exception as e:
            print(f"Error fetching editions for '{work_key}': {e}")
            return None

    def get_work_details(self, work_key: str) -> dict | None:
        """Fetch details for a specific work, including description."""
        if not work_key:
            return None
        try:
            url = f"https://openlibrary.org{work_key}.json"
            response = httpx.get(url)
            response.raise_for_status()
            data = response.json()

            description = data.get("description")
            if isinstance(description, dict):
                description = description.get("value", "")
            elif not description:
                description = ""

            return {
                "description": str(description),
                "title": data.get("title"),
                "key": data.get("key"),
            }
        except Exception as e:
            print(f"Error fetching work details for '{work_key}': {e}")
            return None
