# Bibliotracker
![Unit Tests](https://github.com/kashyapm94/bibliotracker/actions/workflows/unittest.yml/badge.svg)

A modern, intelligent web application to track your **to-read list**. It goes beyond a simple list by automatically enriching book entries with deep metadata and context using AI, and visualizing your reading habits through an interactive stats dashboard.

## Features

### AI-Powered Intelligence
- **Smart Enrichment**: Uses **Claude** (`claude-opus-4-6`) to automatically fetch rich metadata at add-time — canonical title, author, description, region setting, subjects, and fiction/non-fiction classification.
- **Context Awareness**: Automatically extracts the **region** setting of a book to help you organize your list.
- **Subject Analysis**: Categorizes each book into up to 5 subjects/genres.

### Interactive Statistics Dashboard
- Visual insights powered by **Chart.js**:
  - Ownership status (owned vs. to-acquire)
  - Top authors on your list
  - Fiction vs. Non-Fiction split
  - Top subjects

### Ownership Tracking
- Mark books as "Owned" directly from the card (admin-only).
- Clear badges distinguish owned books at a glance.

### Smart Search & Management
- **Google Books Integration**: English-only results for relevant suggestions.
- **Infinite scroll** through search results.
- **Duplicate prevention**: Case-insensitive title matching.
- **Admin-only** book addition and deletion.

### UI
- Dark theme with colorful per-card gradients, glassmorphism card footers, gradient header text with shimmer animation, and a rainbow top stripe.
- Responsive, built with **Vanilla JS/CSS** (no frameworks) for fast performance.
- Google Fonts: Lora (book titles), Playfair Display (headings), Outfit (body).

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) (synchronous, psycopg3)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **AI**: [Anthropic Claude API](https://docs.anthropic.com/) (`claude-opus-4-6`)
- **Search API**: [Google Books API](https://developers.google.com/books)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Visualization**: [Chart.js](https://www.chartjs.org/)
- **Testing**: [Pytest](https://docs.pytest.org/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL running locally on port 5432
- Anthropic API key
- Google Books API key (optional but recommended — [obtain from Google Cloud Console](https://console.cloud.google.com/apis/library/books.googleapis.com))
- [uv](https://github.com/astral-sh/uv)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kashyapm94/bibliotracker.git
   cd bibliotracker
   ```

2. Install dependencies (including dev group):
   ```bash
   uv sync --all-groups
   ```

3. Create the database:
   ```sql
   CREATE DATABASE book_wishlist;
   ```

### Configuration

Create a `.env` file:
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=book_wishlist
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your_password

# AI & Search
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxx
GOOGLE_BOOKS_API_KEY=AIzaSyxxxxxxxxxxxxxxxxx   # optional
REFERER_URL=http://127.0.0.1:8000              # optional

# Security
ADMIN_PASSWORD=your_admin_password
```

### Database Migrations

```bash
uv run alembic upgrade head
```

### Running the Application

```bash
uv run uvicorn bibliotracker.app:app --reload
```

Open **http://127.0.0.1:8000**

### Running Tests

```bash
uv run pytest
```

### Production Deployment

```bash
uv run alembic upgrade head && uv run uvicorn bibliotracker.app:app --host 0.0.0.0 --port $PORT
```

## Project Structure

```
bibliotracker/
  app.py          FastAPI routes and admin auth middleware
  ai.py           Anthropic Claude integration (BookAI)
  config.py       Environment variable config
  books/          Google Books API client and lookup service
  storage/        SQLAlchemy models, PostgresClient, Alembic config
  static/         Frontend (index.html, stats.html, script.js, style.css)
alembic/          Migration scripts
tests/            Pytest suite
```
