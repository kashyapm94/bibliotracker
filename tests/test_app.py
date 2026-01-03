from unittest.mock import MagicMock

from fastapi.testclient import TestClient


def test_read_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200


def test_search_api_empty(client: TestClient) -> None:
    response = client.get("/api/search?q=")
    assert response.status_code == 200
    assert response.json() == []


def test_search_api_results(
    client: TestClient, mock_book_service_for_app: MagicMock
) -> None:
    mock_book_service_for_app.search_books.return_value = (
        [
            {
                "title": "B1",
                "authors": ["A1"],
                "key": "k1",
                "subjects": [],
            }
        ],
        1,
    )

    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "B1"
    assert data[0]["authors"] == "A1"


def test_search_api_pagination(
    client: TestClient, mock_book_service_for_app: MagicMock
) -> None:
    mock_book_service_for_app.search_books.return_value = (
        [{"title": "B2", "authors": ["A2"], "key": "k2", "subjects": []}],
        10,
    )

    response = client.get("/api/search?q=test&page=2")
    assert response.status_code == 200

    # Verify mock called with correct page
    mock_book_service_for_app.search_books.assert_called_with("test", page_number=2)

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "B2"


def test_add_book_ignore_is_owned_without_auth(
    client: TestClient, mock_book_service_for_app: MagicMock, mock_db_client: MagicMock
) -> None:
    # Mock AI details extraction
    mock_book_service_for_app.get_book_metadata.return_value = {
        "title": "T1",
        "authors": ["A1"],
    }
    # Mock DB add
    mock_db_client.add_book.return_value = (True, "Added")

    # Send request with is_owned=True but NO admin header
    payload = {
        "book_key": "k1",
        "title": "T1",
        "authors_str": "A1",
        "subjects": [],
        "is_owned": True,
    }

    response = client.post("/api/add", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify db_client.add_book was called with is_owned=False
    call_args = mock_db_client.add_book.call_args
    assert call_args is not None
    # Check keyword arguments
    assert call_args.kwargs["is_owned"] is False


def test_add_book_success_with_ownership(
    client: TestClient, mock_book_service_for_app: MagicMock, mock_db_client: MagicMock
) -> None:
    # Mock AI details extraction
    mock_book_service_for_app.get_book_metadata.return_value = {
        "title": "T1",
        "authors": ["A1"],
    }
    # Mock DB add
    mock_db_client.add_book.return_value = (True, "Added")

    headers = {"x-admin-password": "secret_password"}
    payload = {
        "book_key": "k1",
        "title": "T1",
        "authors_str": "A1",
        "subjects": [],
        "is_owned": True,
    }

    response = client.post("/api/add", json=payload, headers=headers)
    assert response.status_code == 200

    # Verify db_client.add_book was called with is_owned=True
    call_args = mock_db_client.add_book.call_args
    assert call_args is not None
    assert call_args.kwargs["is_owned"] is True


def test_get_stats(client: TestClient, mock_db_client: MagicMock) -> None:
    mock_db_client.get_stats.return_value = {"total": 10}
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert response.json()["total"] == 10


def test_get_toread(client: TestClient, mock_db_client: MagicMock) -> None:
    # Mock DB response
    mock_book1 = MagicMock()
    mock_book1.id = 1
    mock_book1.title = "B1"
    mock_book1.author = "A1"
    mock_book1.subjects = "S1, S2"
    mock_book1.is_owned = False
    mock_book1.is_fiction = "Fiction"
    mock_book1.description = "Desc"
    mock_book1.region = "R1"

    mock_db_client.get_all_books.return_value = [mock_book1]
    mock_db_client.get_total_count.return_value = 1

    response = client.get("/api/toread?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "B1"
    assert data["items"][0]["is_owned"] is False


def test_delete_book_success(client: TestClient, mock_db_client: MagicMock) -> None:
    mock_db_client.delete_book.return_value = True

    headers = {"x-admin-password": "secret_password"}
    response = client.delete("/api/books/1", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify db_client.delete_book was called
    mock_db_client.delete_book.assert_called_with(1)
