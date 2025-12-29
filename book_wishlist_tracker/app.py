import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from book_wishlist_tracker.ai import LocationAI
from book_wishlist_tracker.books.service import BookLookupService
from book_wishlist_tracker.config import Config
from book_wishlist_tracker.storage.client import PostgresClient

app = FastAPI()

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize services
config = Config()

db_client = PostgresClient(config)
book_service = BookLookupService()


class BookSelection(BaseModel):
    book_key: str
    title: str
    authors_str: str
    original_year: int
    subjects: list[str]


@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return "<h1>Frontend not found. Please create static/index.html</h1>"


@app.get("/api/search")
def search_books(q: str):
    if not q:
        return []
    results, _ = book_service.search_books(q, limit=20)

    # Format for frontend
    formatted_results = []
    for res in results:
        authors = ", ".join(res.get("authors", ["Unknown"]))
        formatted_results.append(
            {
                "title": res["title"],
                "authors": authors,
                "year": res.get("first_publish_year", 0),
                "key": res.get("key"),
                "subjects": res.get("subjects", []),
            }
        )
    return formatted_results


@app.post("/api/add")
def add_book(book: BookSelection):
    print(f"Adding book: {book.title} ({book.book_key})")

    # 1. Fetch Latest Edition for basic metadata (Year, ISBN)
    latest_edition = book_service.get_latest_edition(book.book_key)

    # 2. Fetch Work Details for Description (Work level usually has the description)
    work_details = book_service.get_work_details(book.book_key)
    description = work_details.get("description", "") if work_details else ""

    # Defaults from selection/work
    title = book.title
    year = book.original_year
    isbn = None
    subjects = book.subjects

    if latest_edition:
        print("  Latest edition found, updating metadata.")
        title = latest_edition.get("title", title)
        year = latest_edition.get("year", year)
        isbn_list = latest_edition.get("isbn")
        isbn = isbn_list[0] if isbn_list else None
        # pages = latest_edition.get("pages") # Removed as per requirement

    # 3. Extract Location via AI
    ai = LocationAI()  # Uses default llama3.2
    print(f"  Extracting location for '{title}'...")
    location = ai.extract_location(title, description)
    print(f"  Location found: {location}")

    # Add to Database
    added, msg = db_client.add_book(
        title=title,
        author=book.authors_str,
        year=year,
        isbn=isbn,
        description=description,
        country=location.get("country", "Unknown"),
        region=location.get("region", "Unknown"),
        subjects=subjects,
    )

    if added:
        return {"status": "success", "message": msg}
    else:
        print(f"DB Add Failed: {msg}")
        raise HTTPException(status_code=500, detail=msg)
