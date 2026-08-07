# Product Requirements Document (PRD): BE-06-Scraper

## 1. Product Overview & Vision

**BE-06-Scraper** is a clean, simplified, production-grade web scraping service built with Python 3.12+. It implements a 5-stage ETL data gathering pipeline (**Fetch $\rightarrow$ Parse $\rightarrow$ Extract $\rightarrow$ Clean $\rightarrow$ Structure $\rightarrow$ Store**) combined with a strict **Politeness & Ethics Layer** (`robots.txt` enforcement, token-bucket rate limiting, transparent `User-Agent` headers, and exponential backoff).

All extracted records are validated via Pydantic v2 models and persisted directly into a single, zero-setup **SQLite Database (`flyrank_scraper.db`)**.

---

## 2. Core Architectural Decision: 3-Stage Progressive Pipeline

We explicitly select a **3-step progressive implementation approach**:

```
 ───────────────► Stage 1: Beginner Target (books.toscrape.com)
                  • Static HTML + BeautifulSoup4 CSS Selectors
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
- **Scraped Fields**: `upc`, `title`, `category`, `price_excl_tax`, `price_incl_tax`, `tax`, `currency`, `availability_status`, `stock_quantity`, `rating` (1-5 int), `description`, `product_page_url`, `cover_image_url`.

### Target 2: `dasoertliche.de` B2B Leads (`--target leads`)
- **Query Inputs**: `--city <city_name>` and `--street <street_name>`.
- **Target Search Test Pairs**:
  1. `city="Berlin"`, `street="Berliner Allee"`
  2. `city="Berlin"`, `street="Friedrichstraße"`
  3. `city="München"`, `street="Leopoldstraße"`
  4. `city="Hamburg"`, `street="Reeperbahn"`
  5. `city="Frankfurt"`, `street="Kaiserstraße"`
- **Scraped Fields**: `business_name`, `category_industry`, `street_name`, `house_number`, `postal_code`, `city`, `phone_number`, `website_url`, `is_business` (bool), `raw_json_ld_type`, `detail_page_url`.

### Target 3: `kaggle.com/datasets` (`--target kaggle`)
- **Query Inputs**: `--query <search_term>` (e.g. `--query "machine learning"`), `--limit <n>`.
- **Scraped Fields**: `dataset_title`, `dataset_url`, `creator_username`, `upvotes_count`, `views_count`, `downloads_count`, `license_name`, `summary_description`, `tags` (list), `last_updated_date`.

---

## 4. Politeness & Bot Ethics Contract

Every target strategy strictly observes:
1. **`robots.txt` Compliance**: Automatically inspect `robots.txt` before fetching. Handle HTTP 404 as "Allow All" and 403 as "Disallow All".
2. **Identification**: Send transparent `User-Agent`: `FlyrankBot/1.0 (+https://github.com/flyrank/flyrank-assignments; bot@flyrank.ai)`.
3. **Token-Bucket Rate Limiter**: Enforce configurable inter-request delay ($0.5\text{s} - 1.5\text{s}$).
4. **Resilience & Retry**: Exponential backoff via `tenacity` on transient errors (`429`, `5xx`).

---

## 5. Storage Engine & Scrape Logging

- **SQLite Database (`flyrank_scraper.db`)**:
  - `books`: Table storing clean book records.
  - `leads`: Table storing B2B contact lead records.
  - `datasets`: Table storing Kaggle dataset metadata.
  - `scrape_logs`: Tracks session timing (`start_time`, `end_time`), pages scraped, extracted record count, error count, and status (`RUNNING`, `COMPLETED`, `FAILED`).

---

## 6. Live Demo UI Concept (Streamlit Hybrid Approach)

To make the scraper interactive and presentable, a **Streamlit Web Application (`app.py`)** will be built using a **Hybrid Integration Architecture**:

```
                       ┌──────────────────────────────────────────────┐
                       │          Streamlit Dashboard UI              │
                       └──────────────────────┬───────────────────────┘
                                              │
                        User Clicks [ 🚀 Start Live Scrape ]
                                              │
                                              ▼
                       ┌──────────────────────────────────────────────┐
                       │ 1. Direct Function Call: await strategy.run()│
                       │    (Runs in st.spinner with live logs)       │
                       └──────────────────────┬───────────────────────┘
                                              │
                          ┌───────────────────┴───────────────────┐
                          │                                       │
                          ▼                                       ▼
        ┌───────────────────────────────────┐   ┌───────────────────────────────────┐
        │ 2. Live Data Grid (Pandas/st.df)  │   │ 3. Database Session Logs Tab      │
        │    Renders in-memory/SQLite data  │   │    Queries scrape_logs table      │
        └───────────────────────────────────┘   └───────────────────────────────────┘
```

### UI Features & Layout:
1. **Sidebar Configuration**: Target selector dropdown (`Books`, `B2B Leads`, `Kaggle Datasets`), inputs for page depth, city, street, or query.
2. **Live Execution Panel**: Displays `robots.txt` status badge, active rate limiters, and a progress spinner.
3. **Tab 1 — 📊 Scraped Data Grid**: Interactive, searchable data table displaying clean records.
4. **Tab 2 — 🔍 Record Detail Inspector**: Inspects raw JSON attributes alongside pre-formatted text summaries.
5. **Tab 3 — 📜 Scraping Session History**: Queries `scrape_logs` from SQLite DB to show past execution sessions and statistics.

---

## 7. Test Plan

1. **Unit Tests**: Test cleaners (currency, stock, rating, street URL transformer, phone regex, Kaggle metric numbers) and DOM parsing against mock HTML fixtures.
2. **Integration Tests**: Verify SQLite DB idempotency and `scrape_logs` tracking via SQLAlchemy.
3. **Live Smoke Tests**: Run live CLI scrapes for all 3 targets and verify record insertion in `flyrank_scraper.db`.
