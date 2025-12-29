# Book Wishlist Tracker

A modern web application to track your book wishlist, automatically enriching entries with metadata and geopolitical context using AI.

## Features

- **Smart Search**: Integrated with Open Library to find books instantly.
- **AI-Powered Context**: Uses **Perplexity AI** to automatically extract the setting (Country & Region) of the book.
- **Duplicate Prevention**: Intelligently prevents adding the same book twice (case-insensitive).
- **English Editions First**: Prioritizes English editions when adding books.
- **Modern Stack**: Built with FastAPI, PostgreSQL, and SQLAlchemy.

## Prerequisites

- **Python 3.12+** (Managed via `uv`)
- **PostgreSQL** (Running locally on port 5432)
- **Perplexity API Key** (For AI features)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd book-wishlist-tracker
    ```

2.  **Install dependencies using `uv`**:
    ```bash
    uv sync
    ```

3.  **Set up the Database**:
    Ensure you have a PostgreSQL database named `book_wishlist` created.
    ```sql
    CREATE DATABASE book_wishlist;
    ```

## Configuration

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

2.  Edit `.env` with your credentials:
    ```bash
    # Database Configuration
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=book_wishlist
    POSTGRES_USERNAME=postgres
    POSTGRES_PASSWORD=your_password

    # AI Configuration (Perplexity)
    PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxx
    ```

## Running the Application

Start the backend server (which also serves the frontend):

```bash
uv run uvicorn book_wishlist_tracker.app:app --reload
```

Open your browser and navigate to: **http://127.0.0.1:8000**

## Project Structure

- `book_wishlist_tracker/`
    - `app.py`: Main FastAPI application entry point.
    - `ai.py`: AI service integration (Perplexity).
    - `books/`: Service for interacting with Open Library.
    - `storage/`: Database models and client (Postgres/SQLAlchemy).
    - `static/`: Frontend assets (HTML, CSS, JS).