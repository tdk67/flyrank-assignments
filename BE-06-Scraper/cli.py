import argparse
import asyncio
import logging
import sys
from core.exceptions import InvalidSearchLocationError, ScraperError
from targets.books_target import BooksTargetStrategy
from targets.kaggle_target import KaggleTargetStrategy
from targets.leads_target import LeadsTargetStrategy

# Silence Windows asyncio Proactor socket shutdown WinError 10054 connection reset exception
if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _orig_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost

        def _silenced_call_connection_lost(self, exc):
            try:
                _orig_call_connection_lost(self, exc)
            except (ConnectionResetError, OSError):
                pass

        _ProactorBasePipeTransport._call_connection_lost = _silenced_call_connection_lost
    except Exception:
        pass

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("BE-06-Scraper")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BE-06-Scraper: Unified SQLite-First Multi-Target Scraper"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    scrape_parser = subparsers.add_parser("scrape", help="Run scraper strategy against a target")
    scrape_parser.add_argument(
        "--target",
        type=str,
        default="books",
        choices=["books", "leads", "kaggle"],
        help="Target scraper strategy (default: books)"
    )
    scrape_parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Maximum catalog/search pages to scrape (default: 1)"
    )
    scrape_parser.add_argument(
        "--city",
        type=str,
        default="Berlin",
        help="City name for leads strategy (default: Berlin)"
    )
    scrape_parser.add_argument(
        "--street",
        type=str,
        default="Berliner Allee",
        help="Street name for leads strategy (default: Berliner Allee)"
    )
    scrape_parser.add_argument(
        "--query",
        type=str,
        default="machine learning",
        help="Search query for kaggle strategy (default: machine learning)"
    )
    scrape_parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum items to retrieve for kaggle strategy (default: 5)"
    )

    return parser


async def main_async():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "scrape":
        try:
            if args.target == "books":
                strategy = BooksTargetStrategy()
                records = await strategy.run(max_pages=args.max_pages)
                print(f"\n[+] Completed Books Scrape: {len(records)} record(s) persisted to SQLite database.")
            elif args.target == "leads":
                strategy = LeadsTargetStrategy()
                records = await strategy.run(max_pages=args.max_pages, city=args.city, street=args.street)
                print(f"\n[+] Completed B2B Leads Scrape: {len(records)} record(s) persisted to SQLite database.")
            elif args.target == "kaggle":
                strategy = KaggleTargetStrategy()
                records = await strategy.run(max_pages=args.max_pages, query=args.query, limit=args.limit)
                print(f"\n[+] Completed Kaggle Dataset Scrape: {len(records)} record(s) persisted to SQLite database.")
        except InvalidSearchLocationError as e:
            print(f"\n[!] INVALID LOCATION ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        except ScraperError as e:
            print(f"\n[!] SCRAPER ERROR: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
