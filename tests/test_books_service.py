import pytest
from pytest_mock import MockerFixture

from bibliotracker.books.service import BookLookupService


def test_search_books_success(mocker: MockerFixture) -> None:
    # Mock GoogleBooksClient instance
    mock_client_instance = mocker.Mock()
    mock_client_instance.search_books.return_value = {
        "totalItems": 1,
        "items": [
            {
                "id": "k1",
                "volumeInfo": {
                    "title": "Test Book",
                    "authors": ["Test Author"],
                    "categories": ["Fiction"],
                    "language": "en",
                },
            }
        ],
    }

    # Patch modules
    mocker.patch(
        "bibliotracker.books.service.GoogleBooksClient",
        return_value=mock_client_instance,
    )
    mocker.patch("bibliotracker.books.service.Config")

    service = BookLookupService()
    results, count = service.search_books("test")

    assert count == 1
    assert len(results) == 1
    assert results[0]["title"] == "Test Book"
    assert results[0]["authors"] == ["Test Author"]
    assert results[0]["key"] == "k1"


def test_search_books_failure(mocker: MockerFixture) -> None:
    # Mock exception
    mock_client_instance = mocker.Mock()
    mock_client_instance.search_books.side_effect = Exception("API Error")

    mocker.patch(
        "bibliotracker.books.service.GoogleBooksClient",
        return_value=mock_client_instance,
    )
    mocker.patch("bibliotracker.books.service.Config")

    service = BookLookupService()
    results, count = service.search_books("test")

    assert count == 0
    assert results == []


def test_get_book_metadata(mocker: MockerFixture) -> None:
    # Mock BookAI
    mock_ai = mocker.Mock()
    mock_ai.get_book_details.return_value = {
        "title": "Clean Title",
        "description": "Summary",
        "is_fiction": "Fiction",
    }

    mocker.patch("bibliotracker.books.service.BookAI", return_value=mock_ai)
    # Also need to patch Config/GoogleBooksClient as they are init-ed
    mocker.patch("bibliotracker.books.service.Config")
    mocker.patch("bibliotracker.books.service.GoogleBooksClient")

    service = BookLookupService()
    details = service.get_book_metadata("Raw Title", "Author")
    assert details["title"] == "Clean Title"
