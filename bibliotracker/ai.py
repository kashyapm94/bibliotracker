import json
import logging
import re

import anthropic

from bibliotracker.config import Config

logger = logging.getLogger(__name__)


class BookAI:
    """
    Handles interactions with Claude AI for fetching book metadata.
    """

    def __init__(self) -> None:
        config = Config()
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def get_book_details(self, book_title: str, book_author: str) -> dict:
        """
        Fetch rich metadata for a specific book using Claude AI.

        Args:
            book_title (str): The title of the book.
            book_author (str): The author(s) of the book.

        Returns:
            dict: A dictionary containing canonical title, authors, description,
                  region, subjects, and fiction/non-fiction status.
        """
        prompt = f"""Provide detailed metadata for the book "{book_title}" by "{book_author}".
Return a JSON object with:
- "title": Full canonical title
- "authors": List of author names
- "description": A concise English summary (max 100 words). No markdown citations or source links.
- "region": Up to 2 major regions/continents, comma-separated string
- "subjects": List of 3 main genres/subjects
- "is_fiction": Categorize as "Fiction" or "Non-Fiction"

Data must be accurate. Description MUST be in English.
Return ONLY valid JSON. No explanation."""

        try:
            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            json_str = self._clean_json(raw)
            details = json.loads(json_str)
            if "description" in details:
                details["description"] = self._clean_description(details["description"])
            return details
        except Exception as e:
            logger.error(f"Claude AI Error: {e}")
            return {}

    def _clean_json(self, raw_content: str) -> str:
        """Extract and clean a JSON object string from the AI's response."""
        content = raw_content.replace("```json", "").replace("```", "").strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        return content[start:end] if start != -1 and end != -1 else "{}"

    def _clean_description(self, text: str) -> str:
        """Remove citation markers (e.g., [1], [2]) from description text."""
        if not text:
            return ""
        return re.sub(r"\[\d+(?:,\s*\d+)*\]", "", text).strip()
