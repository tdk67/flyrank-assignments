import json
import logging
import re
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
from storage.rag_exporter import RAGExporter

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
            logger.info("Page returned 'Keine Treffer' or error page.")
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
            except json.JSONDecodeError as e:
                logger.debug(f"JSON-LD parse error: {e}")
                continue

        return leads

    async def run(self, max_pages: int = 1, output_file: str | None = None, **kwargs) -> list[LeadRecord]:
        city = kwargs.get("city", "Berlin")
        street = kwargs.get("street", "Berliner Allee")

        logger.info(f"Starting B2B Leads Scraper for City: '{city}', Street: '{street}', Max Pages: {max_pages}")
        self.robots_parser.fetch_robots_txt(self.BASE_URL)

        records: list[LeadRecord] = []

        async with httpx.AsyncClient() as client:
            for page_num in range(1, max_pages + 1):
                page_url = build_dasoertliche_url(street, city, page_num)
                logger.info(f"Fetching leads page {page_num}/{max_pages}: {page_url}")

                html_content = await self.fetch_html(client, page_url)
                if not html_content:
                    logger.info("No content returned. Stopping pagination.")
                    break

                page_leads = self.parse_json_ld_from_html(html_content, city, street, page_url)
                if not page_leads:
                    logger.info(f"No B2B leads found on page {page_num}. Ending pagination.")
                    break

                logger.info(f"Extracted {len(page_leads)} B2B lead(s) from page {page_num}")
                for lead in page_leads:
                    records.append(lead)
                    logger.info(f"Extracted lead: [{lead.id}] {lead.business_name} ({lead.city}, {lead.phone_number or 'No Phone'})")

        out_path = output_file or "leads.jsonl"
        saved_file = RAGExporter.export_to_jsonl(records, out_path)
        logger.info(f"Successfully scraped {len(records)} B2B lead(s). Saved output to {saved_file}")

        # DB persistence (Postgres / local SQLite fallback)
        try:
            from storage.database import SessionLocal
            from storage.repository import Repository
            db = SessionLocal()
            saved_db_count = Repository(db).upsert_leads(records)
            db.close()
            logger.info(f"Persisted {saved_db_count} B2B lead record(s) to database.")
        except Exception as e:
            logger.warning(f"Could not persist to database: {e}")

        return records
