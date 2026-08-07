import pytest
from core.politeness import RateLimiter, RobotsParser


def test_robots_parser_404_allows_all():
    parser = RobotsParser(user_agent="FlyrankBot/1.0")
    # books.toscrape.com returns 404 for robots.txt
    parser.fetch_robots_txt("https://books.toscrape.com/")
    assert parser.can_fetch("https://books.toscrape.com/catalogue/page-1.html") is True


@pytest.mark.asyncio
async def test_rate_limiter_delay():
    limiter = RateLimiter(delay_seconds=0.1)
    import time
    start = time.time()
    await limiter.wait()
    await limiter.wait()
    elapsed = time.time() - start
    assert elapsed >= 0.1
