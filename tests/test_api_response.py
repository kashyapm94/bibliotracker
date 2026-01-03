from unittest.mock import MagicMock

import pytest

from bibliotracker.app import get_toread


def test_get_toread_null_is_owned():
    # Mock the db_client
    mock_db_client = MagicMock()

    # Create a mock book object that mimics the SQLAlchemy model
    class MockBook:
        def __init__(
            self, id, title, author, description, region, subjects, is_fiction, is_owned
        ):
            self.id = id
            self.title = title
            self.author = author
            self.description = description
            self.region = region
            self.subjects = subjects
            self.is_fiction = is_fiction
            self.is_owned = is_owned

    # Return a book with is_owned=None
    mock_books = [
        MockBook(
            1, "Test Book", "Test Author", "Desc", "Region", "Subject", "Fiction", None
        )
    ]

    mock_db_client.get_all_books.return_value = mock_books
    mock_db_client.get_total_count.return_value = 1

    # Patch the db_client in app.py
    import bibliotracker.app as app

    original_client = app.db_client
    app.db_client = mock_db_client

    try:
        response = get_toread(page_number=1, page_size=10)

        # Verify the item
        item = response["items"][0]
        assert item["title"] == "Test Book"
        # CRITICAL CHECK: is_owned should be False, not None
        assert item["is_owned"] is False, (
            f"Expected is_owned to be False, got {item['is_owned']}"
        )
        print("Test Passed: is_owned converted from None to False correctly.")

    finally:
        # Restore
        app.db_client = original_client


if __name__ == "__main__":
    test_get_toread_null_is_owned()
