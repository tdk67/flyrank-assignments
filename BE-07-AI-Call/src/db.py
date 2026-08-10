import json
from pathlib import Path
from typing import Dict, Any, Optional

from src.config import config


def load_books() -> Dict[str, Dict[str, Any]]:
    """Loads books from books.jsonl (path configured in config.json) and indexes them by book_id / upc."""
    books = {}
    books_file_path = config.resolved_books_file_path

    if not books_file_path.exists():
        print(f"Warning: books file not found at {books_file_path}")
        return books

    with open(books_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            book_id = record.get("id") or record.get("metadata", {}).get("upc")
            if book_id:
                books[book_id] = record
    return books


# Singleton loaded books cache
_BOOKS_DB = load_books()


def get_book_by_id(book_id: str) -> Optional[Dict[str, Any]]:
    """Returns the book dict by book_id if found, else None."""
    return _BOOKS_DB.get(book_id)


def list_installed_ollama_models() -> list[str]:
    """Helper to query local Ollama tags API if available."""
    import httpx
    try:
        resp = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    return []
