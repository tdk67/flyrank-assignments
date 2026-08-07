import html
import re

RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}


def clean_text(raw_text: str | None) -> str:
    if not raw_text:
        return ""
    unescaped = html.unescape(raw_text)
    return re.sub(r"\s+", " ", unescaped).strip()


def parse_price(price_str: str | None) -> float:
    if not price_str:
        return 0.0
    match = re.search(r"[\d\.]+", price_str)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return 0.0
    return 0.0


def parse_rating(rating_class_str: str | None) -> int:
    if not rating_class_str:
        return 1
    lowered = rating_class_str.lower()
    for word, number in RATING_MAP.items():
        if word in lowered:
            return number
    return 1


def parse_stock_quantity(stock_str: str | None) -> int:
    if not stock_str:
        return 0
    match = re.search(r"\((\d+)\s+available\)", stock_str, re.IGNORECASE)
    if match:
        return int(match.group(1))
    if "in stock" in stock_str.lower():
        return 1
    return 0
