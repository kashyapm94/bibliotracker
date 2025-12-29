import json
from typing import Dict, List, Optional

from perplexity import Perplexity

from book_wishlist_tracker.config import Config


class BookAI:
    def __init__(self):
        config = Config()
        if config.PERPLEXITY_API_KEY:
            self.client = Perplexity(api_key=config.PERPLEXITY_API_KEY)
        else:
            self.client = None

    def _query_ai(self, prompt: str) -> str:
        if not self.client:
            print("Perplexity API Key missing")
            return ""
        try:
            response = self.client.chat.completions.create(
                model="sonar", messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Perplexity Query Error: {e}")
            return ""

    def _clean_json(self, content: str) -> str:
        content = content.replace("```json", "").replace("```", "").strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        return content[start:end] if start != -1 and end != -1 else "{}"

    def _clean_json_list(self, content: str) -> str:
        content = content.replace("```json", "").replace("```", "").strip()
        start = content.find("[")
        end = content.rfind("]") + 1
        return content[start:end] if start != -1 and end != -1 else "[]"

    def get_book_details(self, title: str, author: str) -> Dict:
        """
        Get detailed metadata for a specific book.
        """
        if not self.client:
            return {}

        prompt = f"""Provide detailed metadata for the book "{title}" by "{author}".
        Return a JSON object with:
        - "title": Full canonical title
        - "authors": List of author names
        - "description": A concise English summary (max 100 words)
        - "country": Primary setting/origin country
        - "region": Continent/Region
        - "subjects": List of 3-5 main genres/subjects

        Data must be accurate. Description MUST be in English.
        Return ONLY valid JSON. No explanation."""

        response = self._query_ai(prompt)
        try:
            json_str = self._clean_json(response)
            return json.loads(json_str)
        except Exception as e:
            print(f"Error parsing book details: {e}")
            return {}
