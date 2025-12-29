import json

from perplexity import Perplexity

from book_wishlist_tracker.config import Config


class LocationAI:
    def __init__(self):
        config = Config()
        self.client = Perplexity(api_key=config.PERPLEXITY_API_KEY)

    def extract_location(self, title: str, description: str) -> dict:
        """
        Analyze title and description to extract country and region.
        Returns a dict: {"country": "...", "region": "..."}
        """
        prompt = f"""Analyze the following book title and description to determine the primary Country and broader Region (Continent) where the book is set or is about.

        Book Title: {title}
        Description: {description}

        If the location is not clear, use "Unknown" for both.

        Return ONLY a valid JSON object in the following format:
        {{
            "country": "Country Name",
            "region": "Continent Name"
        }}

        Do not explain. Return only JSON."""

        try:
            response = self.client.chat.completions.create(
                model="sonar",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            content = response.choices[0].message.content

            # Remove markdown code blocks if present
            content = content.replace("```json", "").replace("```", "").strip()

            # Find closest braces
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                return {"country": "Unknown", "region": "Unknown"}

        except Exception as e:
            print(f"AI Extraction Error: {e}")
            return {"country": "Unknown", "region": "Unknown"}
