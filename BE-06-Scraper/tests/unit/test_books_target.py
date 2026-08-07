import pytest
from targets.books_target import BooksTargetStrategy

MOCK_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<body>
  <ul class="breadcrumb">
    <li><a href="../../index.html">Home</a></li>
    <li><a href="../category/books_1/index.html">Books</a></li>
    <li><a href="../category/books/travel_2/index.html">Travel</a></li>
    <li class="active">It's Only Too Late If You Don't Start Now</li>
  </ul>

  <div class="product_main">
    <h1>It's Only Too Late If You Don't Start Now</h1>
    <p class="price_color">£26.83</p>
    <p class="star-rating Two"></p>
  </div>

  <div id="product_description">
    <h2>Product Description</h2>
  </div>
  <p>An inspiring story about starting over and pursuing dreams.</p>

  <table class="table table-striped">
    <tr><th>UPC</th><td>a86b124d1533e850</td></tr>
    <tr><th>Product Type</th><td>Books</td></tr>
    <tr><th>Price (excl. tax)</th><td>£26.83</td></tr>
    <tr><th>Price (incl. tax)</th><td>£26.83</td></tr>
    <tr><th>Tax</th><td>£0.00</td></tr>
    <tr><th>Availability</th><td>In stock (19 available)</td></tr>
    <tr><th>Number of reviews</th><td>0</td></tr>
  </table>
</body>
</html>
"""


def test_parse_detail_page_success():
    strategy = BooksTargetStrategy()
    url = "https://books.toscrape.com/catalogue/its-only-too-late_986/index.html"
    record = strategy.parse_detail_page(MOCK_DETAIL_HTML, url)

    assert record is not None
    assert record.upc == "a86b124d1533e850"
    assert record.title == "It's Only Too Late If You Don't Start Now"
    assert record.category == "Travel"
    assert record.price_incl_tax == 26.83
    assert record.price_excl_tax == 26.83
    assert record.tax == 0.0
    assert record.rating == 2
    assert record.stock_quantity == 19
    assert record.availability_status == "In stock (19 available)"
    assert "inspiring story" in record.description
