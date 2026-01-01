from pytest_mock import MockerFixture

from bibliotracker.books.service import BookLookupService


def test_search_books_success(mocker: MockerFixture) -> None:
    # Mock httpx.get
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "numFound": 1,
        "docs": [
            {
                "title": "Test Book",
                "author_name": ["Test Author"],
                "key": "/works/OL123",
                "subject": ["Fiction"],
            }
        ],
    }
    mock_response.raise_for_status.return_value = None
    mocker.patch("httpx.get", return_value=mock_response)

    service = BookLookupService()
    results, count = service.search_books("test")

    assert count == 1
    assert len(results) == 1
    assert results[0]["title"] == "Test Book"
    assert results[0]["authors"] == ["Test Author"]


def test_search_books_failure(mocker: MockerFixture) -> None:
    # Mock exception
    mocker.patch("httpx.get", side_effect=Exception("API Error"))

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

    # Patch the BookAI CLASS in the service module so __init__ uses our mock
    mocker.patch("bibliotracker.books.service.BookAI", return_value=mock_ai)

    service = BookLookupService()
    # service.ai should be our mock_ai instance (due to return_value above)

    details = service.get_book_metadata("Raw Title", "Author")
    assert details["title"] == "Clean Title"
