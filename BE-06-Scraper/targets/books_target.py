import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import httpx
from cleaner.books_cleaner import (
    clean_text,
    parse_price,
    parse_rating,
    parse_stock_quantity,
)
from config import settings
from core.base_target import BaseTargetStrategy
from core.politeness import (
    RateLimiter,
    RobotsParser,
    UserAgentManager,
    get_retry_decorator,
)
from schemas import BookRecord
from storage.database import SessionLocal
from storage.repository import Repository

logger = logging.getLogger("BE-06-Scraper.BooksTarget")


class BooksTargetStrategy(BaseTargetStrategy):

    BASE_URL = "https://books.toscrape.com/"
    CATALOG_URL = "https://books.toscrape.com/catalogue/page-{}.html"

    def __init__(self):
        self.robots_parser = RobotsParser(user_agent=settings.USER_AGENT)
        self.rate_limiter = RateLimiter(delay_seconds=settings.DEFAULT_RATE_LIMIT_DELAY)
        self.ua_manager = UserAgentManager(user_agent=settings.USER_AGENT)

    @property
    def target_name(self) -> str:
        return "books"

    async def fetch_html(self, client: httpx.AsyncClient, url: str) -> str:
        if not self.robots_parser.can_fetch(url):
            logger.warning(f"Robots.txt disallows fetching {url}")
            return ""

        await self.rate_limiter.wait()

        @get_retry_decorator(max_attempts=settings.MAX_RETRIES)
        async def _do_fetch():
            res = await client.get(url, headers=self.ua_manager.get_headers(), timeout=10.0)
            res.raise_for_status()
            return res.text

        try:
            return await _do_fetch()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""

    def parse_detail_page(self, html_content: str, page_url: str) -> BookRecord | None:
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, "html.parser")
        main_div = soup.find("div", class_="product_main")
        if not main_div:
            return None

        title = clean_text(main_div.find("h1").get_text()) if main_div.find("h1") else "Unknown Title"

        # Rating
        rating_elem = main_div.find("p", class_=lambda c: c and "star-rating" in c)
        rating_class = " ".join(rating_elem.get("class", [])) if rating_elem else ""
        rating = parse_rating(rating_class)

        # Category from breadcrumb
        breadcrumb = soup.find("ul", class_="breadcrumb")
        category = "General"
        if breadcrumb:
            items = breadcrumb.find_all("li")
            if len(items) >= 3:
                category = clean_text(items[2].get_text())

        # Description
        desc_p = soup.find("div", id="product_description")
        description = ""
        if desc_p and desc_p.find_next_sibling("p"):
            description = clean_text(desc_p.find_next_sibling("p").get_text())

        # Product Table (UPC, Price, Tax, Availability)
        upc = ""
        price_excl_tax = 0.0
        price_incl_tax = 0.0
        tax = 0.0
        availability_status = "In stock"
        stock_quantity = 1

        table = soup.find("table", class_="table-striped")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                th = row.find("th")
                td = row.find("td")
                if not th or not td:
                    continue
                header = clean_text(th.get_text()).lower()
                val = clean_text(td.get_text())

                if "upc" in header:
                    upc = val
                elif "price (excl. tax)" in header:
                    price_excl_tax = parse_price(val)
                elif "price (incl. tax)" in header:
                    price_incl_tax = parse_price(val)
                elif "tax" in header:
                    tax = parse_price(val)
                elif "availability" in header:
                    availability_status = val
                    stock_quantity = parse_stock_quantity(val)

        if not upc:
            return None

        # Cover image
        cover_img = soup.find("div", class_="carousel-inner") or soup.find("div", class_="item")
        cover_url = None
        if cover_img and cover_img.find("img"):
            rel_src = cover_img.find("img").get("src")
            cover_url = urljoin(page_url, rel_src)

        return BookRecord(
            upc=upc,
            title=title,
            category=category,
            price_excl_tax=price_excl_tax,
            price_incl_tax=price_incl_tax,
            tax=tax,
            currency="GBP",
            availability_status=availability_status,
            stock_quantity=stock_quantity,
            rating=rating,
            description=description,
            product_page_url=page_url,
            cover_image_url=cover_url,
        )

    async def run(self, max_pages: int = 1, **kwargs) -> list[BookRecord]:
        logger.info(f"Starting Books Scraper run for max {max_pages} page(s)...")
        scrape_log = self.create_scrape_log()

        db = SessionLocal()
        repo = Repository(db)
        repo.save_scrape_log(scrape_log)

        self.robots_parser.fetch_robots_txt(self.BASE_URL)
        records: list[BookRecord] = []
        pages_scraped = 0
        error_count = 0

        try:
            async with httpx.AsyncClient() as client:
                for page_num in range(1, max_pages + 1):
                    page_url = self.CATALOG_URL.format(page_num)
                    logger.info(f"Fetching catalog page {page_num}/{max_pages}: {page_url}")
                    catalog_html = await self.fetch_html(client, page_url)
                    if not catalog_html:
                        break

                    pages_scraped += 1
                    soup = BeautifulSoup(catalog_html, "html.parser")
                    product_pods = soup.find_all("article", class_="product_pod")
                    if not product_pods:
                        break

                    for pod in product_pods:
                        h3 = pod.find("h3")
                        if not h3 or not h3.find("a"):
                            continue
                        rel_url = h3.find("a").get("href")
                        if not rel_url.startswith("catalogue/"):
                            rel_url = f"catalogue/{rel_url.lstrip('/')}"
                        detail_url = urljoin(self.BASE_URL, rel_url)

                        detail_html = await self.fetch_html(client, detail_url)
                        book_rec = self.parse_detail_page(detail_html, detail_url)
                        if book_rec:
                            records.append(book_rec)

            # Persist records to database
            repo.upsert_books(records)
            self.finalize_scrape_log(scrape_log, pages_scraped=pages_scraped, records_extracted=len(records), error_count=error_count, status="COMPLETED")
            repo.save_scrape_log(scrape_log)
            logger.info(f"Successfully scraped & stored {len(records)} books into database.")
        except Exception as e:
            error_count += 1
            logger.error(f"Books scraping failed: {e}")
            self.finalize_scrape_log(scrape_log, pages_scraped=pages_scraped, records_extracted=len(records), error_count=error_count, status="FAILED")
            repo.save_scrape_log(scrape_log)
        finally:
            db.close()

        return records
