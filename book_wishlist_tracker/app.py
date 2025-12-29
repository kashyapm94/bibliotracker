import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
    raw_results, _ = book_service.search_books(q)

    # Format for frontend
    # Frontend expects authors to be a string, and sends it back as authors_str
    formatted = []
    for book in raw_results:
        authors = book.get("authors", [])
        if isinstance(authors, list):
            authors_str = ", ".join(authors)
        else:
            authors_str = str(authors)

        formatted.append(
            {
                "title": book.get("title"),
                "authors": authors_str,
                "key": book.get("key"),
                "subjects": book.get("subjects", []),
            }
        )

    return formatted


@app.post("/api/add")
def add_book(book: BookSelection):
    print(f"Adding book: {book.title}")

    # Fetch details via AI (single source of truth now)
    # We assume 'authors_str' is passed, or we can use the author list from search result if available.
    # The BookSelection model might need adjustment, but for now we'll use what we have.
    # key in BookSelection might be the AI generated key or title-author slug.

    details = book_service.get_book_metadata(book.title, book.authors_str)

    if not details:
        raise HTTPException(status_code=404, detail="Could not fetch book details.")

    # Add to Database
    added, msg = db_client.add_book(
        title=details.get("title", book.title),
        author=", ".join(details.get("authors", []))
        if isinstance(details.get("authors"), list)
        else details.get("authors", book.authors_str),
        description=details.get("description", ""),
        country=details.get("country", "Unknown"),
        region=details.get("region", "Unknown"),
        subjects=details.get("subjects", []),
    )

    if added:
        return {"status": "success", "message": msg}
    else:
        print(f"DB Add Failed: {msg}")
        raise HTTPException(status_code=500, detail=msg)


@app.get("/api/wishlist")
def get_wishlist():
    books = db_client.get_all_books()

    formatted = []
    for b in books:
        formatted.append(
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "description": b.description,
                "country": b.country,
                "region": b.region,
                "subjects": b.subjects.split(", ") if b.subjects else [],
            }
        )
    return formatted
