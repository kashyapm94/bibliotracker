# Bibliotracker
![Unit Tests](https://github.com/kashyapm94/bibliotracker/actions/workflows/unittest.yml/badge.svg)

A modern, intelligent web application to track your **to-read list**. It goes beyond a simple list by automatically enriching book entries with deep metadata and context using AI, and visualizing your to-read list through an interactive dashboard.

## ✨ Features

### 🧠 AI-Powered Intelligence
- **Smart Enrichment**: Uses **Perplexity AI (Sonar model)** to automatically fetch rich metadata, including canonical titles, authors, and summaries.
- **Context Awareness**: Automatically extracts the **Region** setting of a book to help you organize your list effectively.
- **Subject Analysis**: Categorizes books into key subjects and genres (Fiction/Non-Fiction) for better organization.

### 📊 Interactive Statistics Dashboard
- **Visual Insights**: Specific visualizations powered by **Chart.js** to track your reading habits.
    - **Ownership Status**: See how many books you own vs. need to acquire.
    - **Top Authors**: Discover your to-read list's top authors.
    - **Genre Split**: Visualize the balance between Fiction and Non-Fiction.
    - **Top Subjects**: Identify your most to-read top subjects.

### ✅ Ownership Tracking
- **Track Your Collection**: Mark books as "Owned" directly from the card.
- **Admin Control**: Secure, admin-only toggle for updating ownership status to prevent accidental changes.
- **Visual Indicators**: Clear badges distinguish owned books at a glance.

### 🔎 Smart Search & Management
- **Google Books Integration**: Powered by the **Google Books API** for comprehensive and accurate book searching. **Strictly English-only results** to keep your suggestions relevant.
- **Infinite Scroll**: Seamlessly browse through search results with automated pagination and infinite scrolling.
- **Duplicate Prevention**: Intelligently prevents adding the same book twice (case-insensitive) to keep your list clean.
- **Admin-Only Access**: Book searching and addition are strictly restricted to authenticated administrators to maintain list quality.

### 🎨 Modern Experience
- **Literary Theme**: A refined, light "literary" aesthetic designed for book lovers.
- **Premium UI**: Clean, responsive interface built with **Vanilla CSS** and a focus on typography (Outfit font).
- **No-Bloat Frontend**: Built with **Vanilla JavaScript** (no heavy frameworks) for lightning-fast performance.

## 🛠 Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) (Async/Await)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **AI**: [Perplexity API](https://docs.perplexity.ai/)
- **Search API**: [Google Books API](https://developers.google.com/books)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Visualization**: [Chart.js](https://www.chartjs.org/)
- **Testing**: [Pytest](https://docs.pytest.org/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **PostgreSQL** (Running locally on port 5432)
- **Perplexity API Key** (For AI features)
- **Google Books API Key** ([Obtain from Google Cloud Console](https://console.cloud.google.com/apis/library/books.googleapis.com))
- **uv** (Recommended Python package manager)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/kashyapm94/bibliotracker.git
    cd bibliotracker
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Set up the Database**:
    Ensure you have a PostgreSQL database named `book_wishlist` created.
    ```sql
    CREATE DATABASE book_wishlist;
    ```

### Configuration

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

    # AI & Search Configuration
    PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxx
    GOOGLE_BOOKS_API_KEY=AIzaSyxxxxxxxxxxxxxxxxx
    # For Google Books API (Local: http://127.0.0.1:8000, Prod: your_app_url)
    REFERER_URL=http://127.0.0.1:8000
    
    # Security
    ADMIN_PASSWORD=secret_password
    ```

### Database Migrations

Run migrations to create/update your schema:

```bash
uv run alembic upgrade head
```

### Production Deployment

When deploying to production (e.g., Railway, Vercel, VPS), ensure you run migrations as part of your startup command to keep the database schema in sync:

```bash
uv run alembic upgrade head && uv run uvicorn bibliotracker.app:app --host 0.0.0.0 --port $PORT
```

### Running the Application

Start the backend server:

```bash
uv run uvicorn bibliotracker.app:app --reload
```

Open your browser and navigate to: **http://127.0.0.1:8000**

### Running Tests

Execute the test suite using pytest:

```bash
uv run pytest
```

## Project Structure

- `bibliotracker/`
    - `app.py`: Main FastAPI entry point and API routes.
    - `ai.py`: Perplexity AI integration service.
    - `books/`: Google Books API integration service.
    - `storage/`: Database connection, models, and migrations.
    - `static/`: Frontend assets (HTML, CSS, JS, Chart.js logic).
- `alembic/`: Database migration scripts and configuration.
- `tests/`: Pytest suite for API and service layers.
