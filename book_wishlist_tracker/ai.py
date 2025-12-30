import json
import re

from perplexity import Perplexity

from book_wishlist_tracker.config import Config


class BookAI:
    """
    Handles interactions with the Perplexity AI for fetching book metadata.
    """

    def __init__(self) -> None:
        """
        Initialize the BookAI with a Perplexity client using the API key from Config.
        """
        config = Config()
        self.client = Perplexity(api_key=config.PERPLEXITY_API_KEY)

    def _query_ai(self, prompt_text: str) -> str:
        """
        Send a prompt to the Perplexity AI and return the response content.

        Args:
            prompt_text (str): The prompt string to send to the AI.

        Returns:
            str: The raw text response from the AI, or an empty string on error.
        """
        if not self.client:
            print("Perplexity API Key missing")
            return ""
        try:
            response = self.client.chat.completions.create(
                model="sonar", messages=[{"role": "user", "content": prompt_text}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Perplexity Query Error: {e}")
            return ""

    def _clean_json(self, raw_content: str) -> str:
        """
        Extract and clean a JSON object string from the AI's response.

        Args:
            raw_content (str): The raw text response containing a JSON object.

        Returns:
            str: The cleaned JSON object string.
        """
        content = raw_content.replace("```json", "").replace("```", "").strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        return content[start:end] if start != -1 and end != -1 else "{}"

    def _clean_json_list(self, raw_content: str) -> str:
        """
        Extract and clean a JSON list string from the AI's response.

        Args:
            raw_content (str): The raw text response containing a JSON list.

        Returns:
            str: The cleaned JSON list string.
        """
        content = raw_content.replace("```json", "").replace("```", "").strip()
        start = content.find("[")
        end = content.rfind("]") + 1
        return content[start:end] if start != -1 and end != -1 else "[]"

    def _clean_description(self, text: str) -> str:
        """
        Remove citation markers (e.g., [1], [2]) and source artifacts.
        """
        if not text:
            return ""
        # Remove citations like [1], [12], [1, 2]
        return re.sub(r"\[\d+(?:,\s*\d+)*\]", "", text).strip()

    def get_book_details(self, book_title: str, book_author: str) -> dict:
        """
        Fetch rich metadata for a specific book using Perplexity AI.

        Args:
            book_title (str): The title of the book.
            book_author (str): The author(s) of the book.

        Returns:
            dict: A dictionary containing canonical title, authors, description,
                  region, subjects, and fiction/non-fiction status.
        """
        if not self.client:
            return {}

        prompt = f"""Provide detailed metadata for the book "{book_title}" by "{book_author}".
        Return a JSON object with:
        - "title": Full canonical title
        - "authors": List of author names
        - "description": A concise English summary (max 100 words). DO NOT include markdown citations (e.g. [1]) or source links.
        - "region": Up to 2 major regions/continents, comma-separated string
        - "subjects": List of 3 main genres/subjects
        - "is_fiction": Categorize as "Fiction" or "Non-Fiction"

        Data must be accurate. Description MUST be in English.
        Return ONLY valid JSON. No explanation."""

        response = self._query_ai(prompt)
        try:
            json_str = self._clean_json(response)
            details = json.loads(json_str)
            if "description" in details:
                details["description"] = self._clean_description(details["description"])
            return details
        except Exception as e:
            print(f"Error parsing book details: {e}")
            return {}
