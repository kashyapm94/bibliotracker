import logging
import os

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bibliotracker.books.service import BookLookupService
from bibliotracker.config import Config
from bibliotracker.storage.client import PostgresClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Suppress httpx logs to prevent API key exposure in search URLs
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

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


async def verify_admin(x_admin_password: str = Header(None)):
    """
    Verify the admin password provided in the header.
    """
    if x_admin_password != config.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    return True


@app.get("/", response_class=HTMLResponse, response_model=None)
async def read_root() -> HTMLResponse | str:
    """
    Serve the main frontend application.

    Returns:
        The content of index.html if it exists, otherwise a simple Error message.
    """
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return "<h1>Frontend not found. Please create static/index.html</h1>"


@app.get("/api/search")
def search_books(
    query_string: str = Query(..., alias="q"), page: int = Query(1, alias="page")
) -> list[dict]:
    """
    Search for books using the OpenLibrary service.

    Args:
        query_string (str): The search query provided by the user.
        page (int): Page number for pagination.

    Returns:
        list[dict]: A list of formatted book objects for the frontend.
    """
    if not query_string:
        return []
    raw_results, _ = book_service.search_books(query_string, page_number=page)

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

    logger.info(
        f"Returning {len(formatted)} results to frontend for query: '{query_string}'"
    )
    return formatted


@app.post("/api/verify-admin", dependencies=[Depends(verify_admin)])
def verify_admin_status() -> dict:
    """
    Verify if the provided admin password is correct.
    """
    return {"status": "ok"}


@app.post("/api/add", dependencies=[Depends(verify_admin)])
def add_book(selection: BookSelection) -> dict:
    """
    Add a selected book to the wishlist. Fetches rich metadata using AI.

    Args:
        selection (BookSelection): The book selected by the user from search results.

    Returns:
        dict: A success message and status.

    Raises:
        HTTPException: If book details cannot be fetched or DB addition fails.
    """
    logger.info(f"Adding book: {selection.title}")

    # Fetch details via AI (single source of truth now)
    # We assume 'authors_str' is passed, or we can use the author list from search result if available.
    # The BookSelection model might need adjustment, but for now we'll use what we have.
    # key in BookSelection might be the AI generated key or title-author slug.

    details = book_service.get_book_metadata(selection.title, selection.authors_str)

    if not details:
        raise HTTPException(status_code=404, detail="Could not fetch book details.")

    # Add to Database
    added, msg = db_client.add_book(
        book_title=details.get("title", selection.title),
        book_author=", ".join(details.get("authors", []))
        if isinstance(details.get("authors"), list)
        else details.get("authors", selection.authors_str),
        book_description=details.get("description", ""),
        book_region=details.get("region", "Unknown"),
        book_subjects=details.get("subjects", []),
        is_fiction_category=details.get("is_fiction", "Unknown"),
    )

    if added:
        return {"status": "success", "message": msg}
    else:
        logger.error(f"DB Add Failed: {msg}")
        raise HTTPException(status_code=500, detail=msg)


@app.get("/api/stats")
def get_stats() -> dict:
    """
    Get aggregated statistics for charts.
    """
    return db_client.get_stats()


@app.get("/api/wishlist")
def get_wishlist(
    page_number: int = Query(1, alias="page"), page_size: int = Query(12, alias="size")
) -> dict:
    """
    Retrieve a paginated list of books from the wishlist.

    Args:
        page_number (int): The page number to fetch. Defaults to 1.
        page_size (int): The number of items per page. Defaults to 10.

    Returns:
        dict: Paginated results including items, total count, and pagination metadata.
    """
    skip = (page_number - 1) * page_size
    books = db_client.get_all_books(skip_records=skip, limit_records=page_size)
    total = db_client.get_total_count()

    formatted = []
    for book_record in books:
        formatted.append(
            {
                "id": book_record.id,
                "title": book_record.title,
                "author": book_record.author,
                "description": book_record.description,
                "region": book_record.region,
                "subjects": book_record.subjects.split(", ")
                if book_record.subjects
                else [],
                "is_fiction": book_record.is_fiction or "Unknown",
            }
        )
    return {
        "items": formatted,
        "total": total,
        "page": page_number,
        "size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
