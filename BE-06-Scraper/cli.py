import argparse
import asyncio
import logging
import sys
from targets.books_target import BooksTargetStrategy

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("BE-06-Scraper")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BE-06-Scraper: Unified Multi-Target Progressive Scraper"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Run scraper against a target")
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
        help="Maximum catalog pages to scrape (default: 1)"
    )
    scrape_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSONL filepath"
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
        help="Maximum dataset items to retrieve for kaggle strategy (default: 5)"
    )

    return parser


async def main_async():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "scrape":
        if args.target == "books":
            strategy = BooksTargetStrategy()
            output = args.output or "books.jsonl"
            records = await strategy.run(max_pages=args.max_pages, output_file=output)
            print(f"\n[+] Completed Books Scrape: {len(records)} books exported to {output}")
        elif args.target == "leads":
            from targets.leads_target import LeadsTargetStrategy
            strategy = LeadsTargetStrategy()
            output = args.output or "leads.jsonl"
            records = await strategy.run(max_pages=args.max_pages, output_file=output, city=args.city, street=args.street)
            print(f"\n[+] Completed B2B Leads Scrape: {len(records)} leads exported to {output}")
        elif args.target == "kaggle":
            from targets.kaggle_target import KaggleTargetStrategy
            strategy = KaggleTargetStrategy()
            output = args.output or "kaggle.jsonl"
            records = await strategy.run(max_pages=args.max_pages, output_file=output, query=args.query, limit=args.limit)
            print(f"\n[+] Completed Kaggle Dataset Scrape: {len(records)} datasets exported to {output}")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
