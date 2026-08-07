from cleaner.books_cleaner import (
    clean_text,
    parse_price,
    parse_rating,
    parse_stock_quantity,
)


def test_clean_text():
    assert clean_text("  A Light in the &amp; Attic  \n ") == "A Light in the & Attic"


def test_parse_price():
    assert parse_price("£51.77") == 51.77
    assert parse_price("£0.00") == 0.0
    assert parse_price("invalid") == 0.0


def test_parse_rating():
    assert parse_rating("star-rating Three") == 3
    assert parse_rating("star-rating One") == 1
    assert parse_rating("star-rating Five") == 5
    assert parse_rating("unknown") == 1


def test_parse_stock_quantity():
    assert parse_stock_quantity("In stock (22 available)") == 22
    assert parse_stock_quantity("In stock (1 available)") == 1
    assert parse_stock_quantity("Out of stock") == 0
