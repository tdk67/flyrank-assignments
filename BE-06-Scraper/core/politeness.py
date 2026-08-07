import asyncio
import logging
import time
import urllib.robotparser
from urllib.parse import urlparse
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

logger = logging.getLogger("BE-06-Scraper.Politeness")


class RobotsParser:

    def __init__(self, user_agent: str):
        self.user_agent = user_agent
        self.parsers: dict[str, urllib.robotparser.RobotFileParser] = {}

    def fetch_robots_txt(self, base_url: str) -> bool:
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        if domain in self.parsers:
            return True

        robots_url = f"{domain}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)

        try:
            with httpx.Client(timeout=5.0, headers={"User-Agent": self.user_agent}) as client:
                response = client.get(robots_url)
                if response.status_code == 200:
                    rp.parse(response.text.splitlines())
                    logger.info(f"Parsed robots.txt from {robots_url}")
                elif response.status_code == 404:
                    logger.info(f"No robots.txt found at {robots_url} (HTTP 404). Defaulting to Allow All.")
                    rp.allow_all = True
                elif response.status_code in (401, 403):
                    logger.warning(f"Robots.txt access forbidden at {robots_url} (HTTP {response.status_code}). Disallowing All.")
                    rp.disallow_all = True
                else:
                    logger.warning(f"Robots.txt returned HTTP {response.status_code}. Defaulting to Allow All.")
                    rp.allow_all = True
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt from {robots_url}: {e}. Defaulting to Allow All.")
            rp.allow_all = True

        self.parsers[domain] = rp
        return True

    def can_fetch(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        if domain not in self.parsers:
            self.fetch_robots_txt(url)
        
        rp = self.parsers.get(domain)
        if not rp:
            return True
        return rp.can_fetch(self.user_agent, url)


class RateLimiter:

    def __init__(self, delay_seconds: float = 0.5):
        self.delay_seconds = delay_seconds
        self.last_request_time: float = 0.0

    async def wait(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            sleep_time = self.delay_seconds - elapsed
            logger.debug(f"RateLimiter: Sleeping for {sleep_time:.3f}s")
            await asyncio.sleep(sleep_time)
        self.last_request_time = time.time()


class UserAgentManager:

    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    def get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }


def is_retryable_exception(exception: Exception) -> bool:
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in (429, 500, 502, 503, 504)
    if isinstance(exception, (httpx.TimeoutException, httpx.NetworkError)):
        return True
    return False


def get_retry_decorator(max_attempts: int = 3):
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(is_retryable_exception),
        reraise=True
    )
