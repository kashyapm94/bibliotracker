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
        [{"title": "B1", "authors": ["A1"], "key": "k1", "subjects": []}],
        1,
    )

    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "B1"
    assert data[0]["authors"] == "A1"


def test_add_book_no_auth(client: TestClient) -> None:
    response = client.post(
        "/api/add",
        json={"book_key": "k1", "title": "T1", "authors_str": "A1", "subjects": []},
    )
    assert response.status_code == 401


def test_add_book_success(
    client: TestClient, mock_book_service_for_app: MagicMock, mock_db_client: MagicMock
) -> None:
    # Mock AI details extraction
    mock_book_service_for_app.get_book_metadata.return_value = {
        "title": "T1",
        "authors": ["A1"],
        "description": "Desc",
        "region": "R1",
        "subjects": [],
        "is_fiction": "Fiction",
    }
    # Mock DB add
    mock_db_client.add_book.return_value = (True, "Added")

    headers = {"x-admin-password": "secret_password"}
    payload = {"book_key": "k1", "title": "T1", "authors_str": "A1", "subjects": []}

    response = client.post("/api/add", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_get_stats(client: TestClient, mock_db_client: MagicMock) -> None:
    mock_db_client.get_stats.return_value = {"total": 10}
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert response.json()["total"] == 10
