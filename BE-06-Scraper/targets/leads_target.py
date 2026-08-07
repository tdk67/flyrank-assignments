import json
import logging
from bs4 import BeautifulSoup
import httpx
from cleaner.leads_cleaner import build_dasoertliche_url, parse_json_ld_lead
from config import settings
from core.base_target import BaseTargetStrategy
from core.politeness import (
    RateLimiter,
    RobotsParser,
    UserAgentManager,
    get_retry_decorator,
)
from schemas import LeadRecord
from storage.database import SessionLocal
from storage.repository import Repository

logger = logging.getLogger("BE-06-Scraper.LeadsTarget")


class LeadsTargetStrategy(BaseTargetStrategy):

    BASE_URL = "https://www.dasoertliche.de/"

    def __init__(self):
        self.robots_parser = RobotsParser(user_agent=settings.USER_AGENT)
        self.rate_limiter = RateLimiter(delay_seconds=0.8)
        self.ua_manager = UserAgentManager(user_agent=settings.USER_AGENT)

    @property
    def target_name(self) -> str:
        return "leads"

    async def fetch_html(self, client: httpx.AsyncClient, url: str) -> str:
        if not self.robots_parser.can_fetch(url):
            logger.warning(f"Robots.txt disallows fetching {url}")
            return ""

        await self.rate_limiter.wait()

        @get_retry_decorator(max_attempts=settings.MAX_RETRIES)
        async def _do_fetch():
            res = await client.get(url, headers=self.ua_manager.get_headers(), timeout=10.0)
            if res.status_code == 410:
                logger.info(f"HTTP 410 Gone for {url} — end of pagination.")
                return ""
            res.raise_for_status()
            return res.text

        try:
            return await _do_fetch()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""

    def parse_json_ld_from_html(self, html_content: str, default_city: str, default_street: str, page_url: str) -> list[LeadRecord]:
        if not html_content:
            return []

        if "<title>Fehlermeldung</title>" in html_content or "Keine Treffer" in html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        script_tags = soup.find_all("script", type="application/ld+json")

        leads: list[LeadRecord] = []
        for tag in script_tags:
            if not tag.string:
                continue
            try:
                data = json.loads(tag.string)
                if isinstance(data, dict):
                    if data.get("@type") == "ItemList" and "itemListElement" in data:
                        for elem in data["itemListElement"]:
                            item = elem.get("item", elem) if isinstance(elem, dict) else elem
                            lead = parse_json_ld_lead(item, default_city, default_street, page_url)
                            if lead:
                                leads.append(lead)
                    else:
                        lead = parse_json_ld_lead(data, default_city, default_street, page_url)
                        if lead:
                            leads.append(lead)
                elif isinstance(data, list):
                    for item in data:
                        lead = parse_json_ld_lead(item, default_city, default_street, page_url)
                        if lead:
                            leads.append(lead)
            except json.JSONDecodeError:
                continue

        return leads

    async def run(self, max_pages: int = 1, **kwargs) -> list[LeadRecord]:
        city = kwargs.get("city", "Berlin")
        street = kwargs.get("street", "Berliner Allee")

        logger.info(f"Starting B2B Leads Scraper for City: '{city}', Street: '{street}', Max Pages: {max_pages}")
        scrape_log = self.create_scrape_log()

        db = SessionLocal()
        repo = Repository(db)
        repo.save_scrape_log(scrape_log)

        self.robots_parser.fetch_robots_txt(self.BASE_URL)
        records: list[LeadRecord] = []
        pages_scraped = 0
        error_count = 0

        try:
            async with httpx.AsyncClient() as client:
                for page_num in range(1, max_pages + 1):
                    page_url = build_dasoertliche_url(street, city, page_num)
                    logger.info(f"Fetching leads page {page_num}/{max_pages}: {page_url}")

                    html_content = await self.fetch_html(client, page_url)
                    if not html_content:
                        break

                    pages_scraped += 1
                    page_leads = self.parse_json_ld_from_html(html_content, city, street, page_url)
                    if not page_leads:
                        break

                    records.extend(page_leads)

            # Persist records to database
            repo.upsert_leads(records)
            self.finalize_scrape_log(scrape_log, pages_scraped=pages_scraped, records_extracted=len(records), error_count=error_count, status="COMPLETED")
            repo.save_scrape_log(scrape_log)
            logger.info(f"Successfully scraped & stored {len(records)} B2B leads into database.")
        except Exception as e:
            error_count += 1
            logger.error(f"Leads scraping failed: {e}")
            self.finalize_scrape_log(scrape_log, pages_scraped=pages_scraped, records_extracted=len(records), error_count=error_count, status="FAILED")
            repo.save_scrape_log(scrape_log)
        finally:
            db.close()

        return records
