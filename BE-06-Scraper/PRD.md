# Product Requirements Document (PRD): BE-06-Scraper

## 1. Product Overview & Vision

**BE-06-Scraper** is a production-grade, extensible web scraping service built with Python 3.11+. It demonstrates the full data gathering pipeline (**Fetch $\rightarrow$ Parse $\rightarrow$ Extract $\rightarrow$ Clean $\rightarrow$ Structure $\rightarrow$ Store**) while strictly adhering to web ethics (`robots.txt`, rate limits, transparent identification, resilience backoff).

To maximize learning value, `BE-06-Scraper` is architected as a **3-Stage Progressive Multi-Target Scraper**. New capabilities are introduced in sequential stages without breaking backward compatibility for earlier stages.

---

## 2. Core Architectural Decision: 3-Stage Progressive Pipeline

We explicitly select a **3-step progressive implementation approach**:

```
 ───────────────► Stage 1: Beginner Target (books.toscrape.com)
                  • Static HTML + CSS Selectors
                  • Core Politeness Middleware & Pipeline Engine

 ───────────────► Stage 2: Intermediate Target (dasoertliche.de B2B Leads)
                  • JSON-LD Microdata Extraction
                  • URL Parameter Transformer + Business vs. Private Filter

 ───────────────► Stage 3: Advanced Target (kaggle.com/datasets)
                  • Playwright Headless Browser / Internal API Interceptor
                  • Dynamic SPA Rendering & JavaScript Hydration
```

---

## 3. Target Specifications & Exact Scraping Fields

### Target 1: `books.toscrape.com` (`--target books`)
- **Category & Pagination**: Scrapes books across category trees with multi-page navigation.
- **Scraped Fields**:
  | Field Name | Type | Extraction & Cleaning Rules |
  | :--- | :--- | :--- |
  | `upc` | `str` | 16-character unique hex identifier from product info table |
  | `title` | `str` | Clean string, HTML entities unescaped, whitespace trimmed |
  | `category` | `str` | Category name (e.g. `"Travel"`, `"Mystery"`) |
  | `price_excl_tax` | `float` | Parsed numeric float from currency string (e.g. `"£51.77"` $\rightarrow$ `51.77`) |
  | `price_incl_tax` | `float` | Parsed numeric float |
  | `tax` | `float` | Computed tax float |
  | `currency` | `str` | Extracted currency symbol code (`"GBP"`) |
  | `availability_status`| `str` | Normalized status string (`"In Stock"`) |
  | `stock_quantity` | `int` | Extracted integer from `"In stock (22 available)"` $\rightarrow$ `22` |
  | `rating` | `int` | Converted integer from star class (`"star-rating Three"` $\rightarrow$ `3`) |
  | `description` | `str` | Clean product summary text |
  | `product_page_url` | `str` | Absolute URL to detail page |
  | `cover_image_url` | `str` | Absolute URL to cover image |

---

### Target 2: `dasoertliche.de` B2B Leads (`--target leads`)
- **Query Inputs**: `--city <city_name>` and `--street <street_name>`.
- **URL Transformation Rules**:
  - `Base`: `https://www.dasoertliche.de/Themen/{STREET}/{CITY}.htm`
  - `Pagination`: `https://www.dasoertliche.de/Themen/{STREET}/{CITY}-Seite-{PAGE}.htm`
  - `Encoding`: Remove quotes, double existing hyphens (`-` $\rightarrow$ `--`), replace spaces with single hyphens (` ` $\rightarrow$ `-`).
- **Target Search Test Pairs**:
  1. `city="Berlin"`, `street="Berliner Allee"`
  2. `city="Berlin"`, `street="Friedrichstraße"`
  3. `city="München"`, `street="Leopoldstraße"`
  4. `city="Hamburg"`, `street="Reeperbahn"`
  5. `city="Frankfurt"`, `street="Kaiserstraße"`
- **Scraped Fields**:
  | Field Name | Type | Extraction & Cleaning Rules |
  | :--- | :--- | :--- |
  | `business_name` | `str` | Extracted from JSON-LD `name` attribute |
  | `category_industry` | `str` | Extracted business sector (e.g. `"Restaurant"`, `"MedicalClinic"`) |
  | `street_name` | `str` | Extracted street address line |
  | `house_number` | `str` | Extracted building number |
  | `postal_code` | `str` | 5-digit German postal code |
  | `city` | `str` | City / locality name |
  | `phone_number` | `str` | Cleaned phone number matching regex `[\d\s\-\+\(\)]{7,}` |
  | `website_url` | `str` | External business website (directory fallbacks stripped out) |
  | `is_business` | `bool` | Filter output: `True` if business type; `False` if private resident |
  | `raw_json_ld_type` | `str` | Extracted `@type` attribute string |
  | `detail_page_url` | `str` | Absolute listing URL |

---

### Target 3: `kaggle.com/datasets` (`--target kaggle`)
- **Query Inputs**: `--query <search_term>` (e.g. `--query "machine learning"`, `--query "computer vision"`).
- **Execution Mode**: Playwright Headless Browser OR internal REST API interceptor.
- **Scraped Fields**:
  | Field Name | Type | Extraction & Cleaning Rules |
  | :--- | :--- | :--- |
  | `dataset_title` | `str` | Title of the dataset |
  | `dataset_url` | `str` | Absolute canonical URL |
  | `creator_username` | `str` | Dataset author / organization handle |
  | `upvotes_count` | `int` | Integer vote count |
  | `views_count` | `int` | View metric count |
  | `downloads_count` | `int` | Download metric count |
  | `license_name` | `str` | Dataset license (e.g. `"CC0: Public Domain"`, `"MIT"`) |
  | `summary_description`| `str` | Extracted description text summary |
  | `tags` | `List[str]`| List of associated dataset topic tags |
  | `last_updated_date` | `str` | ISO date string of last modification |

---

## 4. Politeness & Bot Ethics Contract

Every target invocation must strictly observe the following politeness rules:

1. **`robots.txt` Compliance**: Automatically inspect `robots.txt` before fetching. Handle HTTP 404 as "Allow All" and 403 as "Disallow All".
2. **Identification**: Send transparent `User-Agent`:
   `FlyrankBot/1.0 (+https://github.com/flyrank/flyrank-assignments; bot@flyrank.ai)`
3. **Token-Bucket Rate Limiter**: Enforce configurable inter-request delay:
   - `books.toscrape.com`: 0.5s delay
   - `dasoertliche.de`: 1.5s delay between streets, 0.8s between pages
   - `kaggle.com`: 1.5s delay
4. **Resilience & Retry**: Exponential backoff via `tenacity` on transient errors (`429`, `500`, `502`, `503`, `504`, timeouts) up to 3 retries.

---

## 5. Persistence & RAG Export Engine

- **PostgreSQL Database**: Tables managed via Liquibase SQL migrations:
  - `books`: Stores clean book records.
  - `leads`: Stores B2B contact lead records.
  - `datasets`: Stores Kaggle dataset metadata.
  - `scrape_logs`: Tracks session timing, status codes, and item counts.
- **RAG Exporter (`rag_exporter.py`)**: Exports scraped records to `.jsonl` files where each line contains a pre-formatted `text_chunk` ready for Week 6 vector embedding.

---

## 6. Comprehensive Test Plan

### 6.1 Unit Tests (`tests/unit/`)
- `test_politeness.py`: Test `robots.txt` parser behavior for 200 OK, 404 Not Found, and 403 Forbidden scenarios. Test token-bucket rate limiter delay accuracy.
- `test_books_cleaner.py`: Test currency parsing, star rating conversion, stock integer extraction.
- `test_leads_cleaner.py`: Test street URL transformer (spaces, hyphens, quotes), JSON-LD microdata extraction, and B2B vs. Person filter.
- `test_kaggle_cleaner.py`: Test dataset metric integer conversions and tag parsing.

### 6.2 Integration Tests (`tests/integration/`)
- `test_database_repository.py`: Verify SQLAlchemy UPSERT idempotency for Books, Leads, and Datasets against test PostgreSQL database.
- `test_rag_exporter.py`: Verify generated `.jsonl` file structure, JSON syntax validity, and pre-formatted text chunk output.

### 6.3 Live Smoke Tests (`tests/smoke/` & CLI Manual Runs)
1. **Books Smoke Test**:
   `python main.py scrape --target books --max-pages 1 --output books_test.jsonl`
   *Verify*: At least 20 books parsed, database populated, `books_test.jsonl` generated.
2. **Leads Smoke Test**:
   `python main.py scrape --target leads --city Berlin --street "Berliner Allee" --max-pages 1 --output leads_test.jsonl`
   *Verify*: B2B leads extracted from JSON-LD, private persons filtered out, phone numbers valid.
3. **Kaggle Smoke Test**:
   `python main.py scrape --target kaggle --query "machine learning" --limit 5 --output kaggle_test.jsonl`
   *Verify*: Playwright/API hydration completes, 5 dataset metadata records saved.
