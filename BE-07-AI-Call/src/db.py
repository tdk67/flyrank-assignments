import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.config import config

logger = logging.getLogger("be07.db")


def load_books() -> Dict[str, Dict[str, Any]]:
    """Loads books from books.jsonl (path configured in config.json) and indexes them by book_id / upc."""
    books = {}
    books_file_path = config.resolved_books_file_path

    if not books_file_path.exists():
        logger.warning(f"⚠️ Dataset Warning: Books file not found at {books_file_path}")
        return books

    with open(books_file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Corrupt record skipped at line {line_num} in {books_file_path}: {e}")
                continue

            book_id = record.get("id") or record.get("metadata", {}).get("upc")
            if book_id:
                books[book_id] = record

    if not books:
        logger.warning(f"⚠️ Dataset Warning: Zero valid book records loaded from {books_file_path}")

    return books


# Singleton loaded books cache
_BOOKS_DB = load_books()


def get_loaded_books_count() -> int:
    """Returns number of valid loaded book records (for /health endpoint)."""
    global _BOOKS_DB
    _BOOKS_DB = load_books()
    return len(_BOOKS_DB)


def get_book_by_id(book_id: str) -> Optional[Dict[str, Any]]:
    """Returns the book dict by book_id if found. Reloads dataset from disk if cache miss occurs."""
    global _BOOKS_DB
    if book_id not in _BOOKS_DB:
        # Reload books database from disk in case dataset was updated
        _BOOKS_DB = load_books()
    return _BOOKS_DB.get(book_id)


def list_installed_ollama_models() -> list[str]:
    """Helper to query local Ollama tags API using configured base URL (M6 Fix)."""
    import httpx
    base_url = config.llm_base_url.rstrip("/")
    if "localhost" in base_url or "127.0.0.1" in base_url:
        tags_url = base_url.replace("/v1", "") + "/api/tags"
        try:
            resp = httpx.get(tags_url, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
    return []
