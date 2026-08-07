import hashlib
import html
import re
from typing import Any, Dict
from schemas import LeadRecord

BUSINESS_TYPES = {
    "localbusiness", "organization", "restaurant", "foodestablishment",
    "store", "bar", "cafe", "hotel", "corporation", "company",
    "autorepair", "medicalclinic", "dentist", "hospital", "pharmacy",
    "realestate", "bank", "school", "gym", "salon", "lawyer",
    "accountant", "plumber", "electrician", "contractor", "lodgingbusiness",
    "financialservice", "professionalservice", "healthandbeautybusiness"
}


def encode_street_for_url(street: str) -> str:
    cleaned = re.sub(r"['\"]", "", street)
    doubled_hyphens = cleaned.replace("-", "--")
    spaced_hyphens = re.sub(r"\s+", "-", doubled_hyphens)
    return spaced_hyphens.strip("-")


def encode_city_for_url(city: str) -> str:
    cleaned = re.sub(r"['\"]", "", city)
    doubled_hyphens = cleaned.replace("-", "--")
    spaced_hyphens = re.sub(r"\s+", "-", doubled_hyphens)
    return spaced_hyphens.strip("-")


def build_dasoertliche_url(street: str, city: str, page_num: int = 1) -> str:
    encoded_street = encode_street_for_url(street)
    encoded_city = encode_city_for_url(city)
    if page_num <= 1:
        return f"https://www.dasoertliche.de/Themen/{encoded_street}/{encoded_city}.htm"
    return f"https://www.dasoertliche.de/Themen/{encoded_street}/{encoded_city}-Seite-{page_num}.htm"


def clean_phone_number(phone_str: str | None) -> str | None:
    if not phone_str:
        return None
    cleaned = html.unescape(phone_str).strip()
    if re.search(r"[\d\s\-\+\(\)]{7,}", cleaned):
        return cleaned
    return None


def clean_website_url(url_str: str | None) -> str | None:
    if not url_str:
        return None
    cleaned = html.unescape(url_str).strip()
    if "dasoertliche" in cleaned.lower() or "herold.at" in cleaned.lower():
        return None
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        return f"https://{cleaned}"
    return cleaned


def parse_json_ld_lead(item: Dict[str, Any], default_city: str, default_street: str, page_url: str = "") -> LeadRecord | None:
    if not isinstance(item, dict) or not item.get("name"):
        return None

    raw_type = item.get("@type", "")
    types_list = [t.lower() for t in (raw_type if isinstance(raw_type, list) else [raw_type]) if isinstance(t, str)]

    # 1. Filter out explicit private persons
    if "person" in types_list:
        return None

    # 2. Check if business
    is_business = any(any(bt in t for bt in BUSINESS_TYPES) for t in types_list)
    raw_phone = item.get("telephone") or item.get("phone")
    phone_number = clean_phone_number(raw_phone)

    # Require either business type OR valid phone number
    if not is_business and not phone_number:
        return None

    business_name = html.unescape(str(item["name"])).strip()
    category_industry = types_list[0].capitalize() if types_list else "LocalBusiness"

    # Address parsing
    address_obj = item.get("address", {})
    if isinstance(address_obj, str):
        address_obj = {"streetAddress": address_obj}

    street_name = default_street
    house_number = None
    postal_code = None
    city = default_city

    if isinstance(address_obj, dict):
        street_address = address_obj.get("streetAddress", "")
        if street_address:
            street_address = html.unescape(street_address).strip()
            # Split street and house number
            match = re.match(r"^(.+?)\s+(\d+[\w\-]*)$", street_address)
            if match:
                street_name = match.group(1).strip()
                house_number = match.group(2).strip()
            else:
                street_name = street_address

        postal_code = address_obj.get("postalCode")
        locality = address_obj.get("addressLocality")
        if locality:
            city = html.unescape(locality).strip()

    website_url = clean_website_url(item.get("url") or item.get("website"))
    detail_page_url = page_url or item.get("mainEntityOfPage") or item.get("sameAs")

    # Generate composite lead ID
    composite_str = f"{business_name.lower()}|{street_name.lower()}|{city.lower()}"
    lead_id = hashlib.sha256(composite_str.encode("utf-8")).hexdigest()[:16]

    return LeadRecord(
        id=lead_id,
        business_name=business_name,
        category_industry=category_industry,
        street_name=street_name,
        house_number=house_number,
        postal_code=postal_code,
        city=city,
        phone_number=phone_number,
        website_url=website_url,
        is_business=True,
        raw_json_ld_type=str(raw_type),
        detail_page_url=detail_page_url
    )
