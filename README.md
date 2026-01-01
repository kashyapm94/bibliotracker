# Bibliotracker

A modern, intelligent web application to track your **to-read list**. It goes beyond a simple list by automatically enriching book entries with deep metadata and context using AI, and visualizing your wishlist through an interactive dashboard.

<div align="center">
  <video src="demo/demo.mp4" controls width="100%"></video>
  <br/>
  <a href="demo/demo.mp4">Watch the Demo Video</a>
</div>

## ✨ Features

### 🧠 AI-Powered Intelligence
- **Smart Enrichment**: Uses **Perplexity AI (Sonar model)** to automatically fetch rich metadata, including canonical titles, authors, and summaries.
- **Context Awareness**: Automatically extracts the **Region** and **Country** setting of a book to help you organize your list effectively.
- **Subject Analysis**: Categorizes books into key subjects and genres (Fiction/Non-Fiction) for better organization.

### 📊 Interactive Statistics Dashboard
- **Visual Insights**: specific visualizations powered by **Chart.js** to track your wishlist.
    - **Region Map**: See the distribution of your books across different continents/regions.
    - **Genre Split**: Visualize the balance between Fiction and Non-Fiction.
    - **Top Subjects**: Identify your most read topics.
- **Drill-Down Capability**: Click on any chart segment to see the specific list of books in that category.

### 🔎 Smart Search & Management
- **Instant Search**: Integrated with **Open Library** API to find books instantly.
- **English-First**: Prioritizes English editions in search results to ensure relevance.
- **Duplicate Prevention**: Intelligently prevents adding the same book twice (case-insensitive) to keep your list clean.
- **Secure Admin**: Protected by an admin password to prevent unauthorized additions to your curated list.

### 🎨 Modern Experience
- **Premium UI**: clean, responsive interface built with **Vanilla CSS** and a focus on typography (Outfit font).
- **No-Bloat Frontend**: Built with **Vanilla JavaScript** (no heavy frameworks) for lightning-fast performance.

## 🛠 Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) (Async/Await)
- **AI**: [Perplexity API](https://docs.perplexity.ai/)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Visualization**: [Chart.js](https://www.chartjs.org/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **PostgreSQL** (Running locally on port 5432)
- **Perplexity API Key** (For AI features)
- **uv** (Recommended Python package manager)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd book-wishlist-tracker
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

    # AI Configuration
    PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxx
    
    # Security
    ADMIN_PASSWORD=secret_password
    ```

### Running the Application

Start the backend server:

```bash
uv run uvicorn bibliotracker.app:app --reload
```

Open your browser and navigate to: **http://127.0.0.1:8000**

## Project Structure

- `bibliotracker/`
    - `app.py`: Main FastAPI entry point and API routes.
    - `ai.py`: Perplexity AI integration service.
    - `books/`: Open Library integration service.
    - `storage/`: Database connection and SQLAlchemy models.
    - `static/`: Frontend assets (HTML, CSS, JS, Chart.js logic).