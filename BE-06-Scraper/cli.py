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
            print(f"[!] Leads target strategy will be implemented in Stage 2.")
        elif args.target == "kaggle":
            print(f"[!] Kaggle target strategy will be implemented in Stage 3.")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
