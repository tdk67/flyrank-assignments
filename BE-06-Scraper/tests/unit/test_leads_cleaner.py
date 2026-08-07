from cleaner.leads_cleaner import (
    build_dasoertliche_url,
    clean_phone_number,
    clean_website_url,
    encode_city_for_url,
    encode_street_for_url,
    parse_json_ld_lead,
)


def test_encode_street_for_url():
    assert encode_street_for_url("Karl-Marx-Straße") == "Karl--Marx--Straße"
    assert encode_street_for_url("Berliner Allee") == "Berliner-Allee"
    assert encode_street_for_url('"Berliner" Straße') == "Berliner-Straße"


def test_build_dasoertliche_url():
    url_p1 = build_dasoertliche_url("Berliner Allee", "Berlin", 1)
    assert url_p1 == "https://www.dasoertliche.de/Themen/Berliner-Allee/Berlin.htm"

    url_p2 = build_dasoertliche_url("Karl-Marx-Straße", "Berlin", 2)
    assert url_p2 == "https://www.dasoertliche.de/Themen/Karl--Marx--Straße/Berlin-Seite-2.htm"


def test_clean_phone_number():
    assert clean_phone_number("030 1234567") == "030 1234567"
    assert clean_phone_number("+49 (0)30 9876543") == "+49 (0)30 9876543"
    assert clean_phone_number("short") is None
    assert clean_phone_number(None) is None


def test_clean_website_url():
    assert clean_website_url("https://www.bistro-example.de") == "https://www.bistro-example.de"
    assert clean_website_url("www.bistro-example.de") == "https://www.bistro-example.de"
    assert clean_website_url("https://www.dasoertliche.de/details/123") is None


def test_parse_json_ld_lead_business_success():
    item = {
        "@type": ["LocalBusiness", "Restaurant"],
        "name": "Bistro Bella Vita",
        "telephone": "030 5551234",
        "url": "https://www.bellavita-berlin.de",
        "address": {
            "streetAddress": "Berliner Allee 42",
            "postalCode": "13088",
            "addressLocality": "Berlin"
        }
    }
    lead = parse_json_ld_lead(item, "Berlin", "Berliner Allee")
    assert lead is not None
    assert lead.business_name == "Bistro Bella Vita"
    assert lead.street_name == "Berliner Allee"
    assert lead.house_number == "42"
    assert lead.postal_code == "13088"
    assert lead.city == "Berlin"
    assert lead.phone_number == "030 5551234"
    assert lead.website_url == "https://www.bellavita-berlin.de"
    assert lead.is_business is True


def test_parse_json_ld_lead_person_filtered():
    item = {
        "@type": "Person",
        "name": "Max Mustermann",
        "telephone": "030 1111111",
        "address": {"streetAddress": "Berliner Allee 10"}
    }
    lead = parse_json_ld_lead(item, "Berlin", "Berliner Allee")
    assert lead is None
