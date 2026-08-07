class ScraperError(Exception):
    """Base exception for all scraper errors."""
    pass


class InvalidSearchLocationError(ScraperError):
    """Raised when a city/street location is invalid, misspelled, or returns HTTP 404/410/Keine Treffer."""
    pass


class TargetNotFoundError(ScraperError):
    """Raised when a target page or catalog resource is not found."""
    pass
