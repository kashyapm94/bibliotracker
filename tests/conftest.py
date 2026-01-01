import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set dummy env vars for testing
os.environ["PERPLEXITY_API_KEY"] = "dummy_key"
os.environ["ADMIN_PASSWORD"] = "secret_password"
os.environ["POSTGRES_DB"] = "test_db"

# Patch DB Client globally to safely import app without DB connection
patcher_db = patch("bibliotracker.storage.client.PostgresClient")
MockPostgresClient = patcher_db.start()
MockPostgresClient.return_value = MagicMock()

# Import app modules
from bibliotracker.app import app, db_client


@pytest.fixture
def mock_db_client() -> MagicMock:
    """Return the global db_client mock."""
    return db_client


@pytest.fixture
def mock_book_service_for_app(mocker) -> MagicMock:
    """
    Mock the book_service INSTANCE in the app module for integration tests.
    This does NOT affect the class definition in bibliotracker.books.service,
    so unit tests can still use the real class.
    """
    mock_service = mocker.Mock()
    mocker.patch("bibliotracker.app.book_service", mock_service)
    return mock_service


@pytest.fixture
def client(
    mock_db_client: MagicMock, mock_book_service_for_app: MagicMock
) -> TestClient:
    """Create a TestClient with mocked dependencies."""
    return TestClient(app)
