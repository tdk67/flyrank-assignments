import html
import re
from typing import Any, List
from schemas import DatasetRecord


def parse_metric_number(val: Any) -> int:
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)

    s = str(val).strip().lower()
    match = re.search(r"([\d\.]+)\s*([kmb])?", s)
    if not match:
        return 0

    number = float(match.group(1))
    unit = match.group(2)

    if unit == "k":
        number *= 1_000
    elif unit == "m":
        number *= 1_000_000
    elif unit == "b":
        number *= 1_000_000_000

    return int(number)


def clean_tag_list(tags_input: Any) -> List[str]:
    if not tags_input:
        return []
    if isinstance(tags_input, str):
        parts = tags_input.split(",")
    elif isinstance(tags_input, list):
        parts = tags_input
    else:
        return []

    cleaned = []
    for tag in parts:
        if isinstance(tag, str):
            t = html.unescape(tag).strip().lower()
            if t and t not in cleaned:
                cleaned.append(t)
    return cleaned


def build_dataset_record(
    dataset_url: str,
    dataset_title: str,
    creator_username: str | None = None,
    upvotes_count: Any = 0,
    views_count: Any = 0,
    downloads_count: Any = 0,
    license_name: str | None = None,
    summary_description: str | None = None,
    tags: Any = None,
    last_updated_date: str | None = None,
) -> DatasetRecord:
    title_clean = html.unescape(dataset_title).strip()
    url_clean = dataset_url.strip()

    if not url_clean.startswith("http://") and not url_clean.startswith("https://"):
        url_clean = f"https://www.kaggle.com{url_clean if url_clean.startswith('/') else '/' + url_clean}"

    desc_clean = None
    if summary_description:
        unescaped = html.unescape(summary_description)
        desc_clean = re.sub(r"\s+", " ", unescaped).strip()

    return DatasetRecord(
        dataset_url=url_clean,
        dataset_title=title_clean,
        creator_username=creator_username.strip() if creator_username else None,
        upvotes_count=parse_metric_number(upvotes_count),
        views_count=parse_metric_number(views_count),
        downloads_count=parse_metric_number(downloads_count),
        license_name=html.unescape(license_name).strip() if license_name else None,
        summary_description=desc_clean,
        tags=clean_tag_list(tags),
        last_updated_date=last_updated_date.strip() if last_updated_date else None,
    )
