# BE-06-Scraper — Progressive 3-Stage Multi-Target Web Scraper

`BE-06-Scraper` is a production-grade, extensible web scraping service built with Python 3.12+. It implements a 5-stage ETL data gathering pipeline (**Fetch $\rightarrow$ Parse $\rightarrow$ Extract $\rightarrow$ Clean $\rightarrow$ Structure $\rightarrow$ Store**) combined with a strict **Politeness & Ethics Layer** (`robots.txt` enforcement, token-bucket rate limiting, transparent `User-Agent` headers, and exponential backoff).

All extracted records are validated via Pydantic v2 models and persisted directly into a zero-setup **SQLite Database (`flyrank_scraper.db`)**.

---

## 1. Architecture & Strategy Design

To combine high learning value with software engineering best practices, `BE-06-Scraper` uses a **Strategy Pattern Engine** supporting a **3-Stage Progressive Pipeline**. New scraping targets are added in sequential stages without breaking backward compatibility for earlier stages.

```
                              ┌────────────────────────┐
                              │     CLI Engine (main)  │
                              │  python main.py scrape │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │  Politeness Middleware │
                              │ (Robots + RateLimiter) │
                              └───────────┬────────────┘
                                          │
                                          ▼
                ┌─────────────────────────┼─────────────────────────┐
                │                         │                         │
                ▼                         ▼                         ▼
    ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
    │  BooksTargetStrategy │  │  LeadsTargetStrategy │  │ KaggleTargetStrategy │
    │   (books.toscrape)   │  │   (dasoertliche.de)  │  │ (kaggle.com/datasets)│
    └───────────┬──────────┘  └───────────┬──────────┘  └───────────┬──────────┘
                │                         │                         │
                │     HTML Selectors      │    JSON-LD Microdata    │   Playwright / API
                │                         │                         │
                └─────────────────────────┼─────────────────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │   Pydantic Validation  │
                              │    (schemas.py)        │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │  SQLite Database Sink  │
                              │  (flyrank_scraper.db)  │
                              └────────────────────────┘
```

---

## 2. Source Code & File Structure

Here is a detailed breakdown of all files in the solution and their specific roles:

| File Path | Description / Responsibility |
| :--- | :--- |
| **`main.py`** | Primary application execution entrypoint. Invokes CLI parser and async main loop. |
| **`cli.py`** | Command-Line Interface module using `argparse`. Defines flags (`--target`, `--max-pages`, `--city`, `--street`, `--query`, `--limit`). |
| **`config.py`** | Settings manager using `pydantic-settings`. Loads `.env`, manages SQLite database URL. |
| **`schemas.py`** | Pydantic v2 data models (`BookRecord`, `LeadRecord`, `DatasetRecord`, `ScrapeLogRecord`) with `ConfigDict(extra="forbid")`. |
| **`core/politeness.py`** | Ethics middleware: `RobotsParser` (`robots.txt` compliance), `RateLimiter` (token-bucket delay), `UserAgentManager`, `RetryBackoff` (`tenacity`). |
| **`core/base_target.py`** | Abstract Base Class `BaseTargetStrategy` defining strategy interface and automated `ScrapeLog` session tracking. |
| **`targets/books_target.py`** | **Stage 1 Strategy**: Async HTTP fetcher & BeautifulSoup4 DOM parser for `books.toscrape.com`. |
| **`targets/leads_target.py`** | **Stage 2 Strategy**: German street URL transformer, JSON-LD microdata extractor, and B2B vs. Person filter for `dasoertliche.de`. |
| **`targets/kaggle_target.py`** | **Stage 3 Strategy**: Playwright headless browser / REST API interceptor for `kaggle.com/datasets`. |
| **`cleaner/books_cleaner.py`** | Cleaning utilities for books: currency float parser, rating word-to-int mapper, stock quantity regex, HTML unescaper. |
| **`cleaner/leads_cleaner.py`** | Cleaning utilities for leads: German street URL encoder, JSON-LD lead parser, phone number regex cleaner. |
| **`cleaner/kaggle_cleaner.py`** | Cleaning utilities for datasets: metric count parser (`"1.5k"` $\rightarrow$ `1500`), tag normalizer. |
| **`storage/models.py`** | SQLAlchemy ORM declarative models (`Book`, `Lead`, `Dataset`, `ScrapeLog`). |
| **`storage/database.py`** | SQLite database engine setup, auto-creation of tables, and session factory (`SessionLocal`). |
| **`storage/repository.py`** | Repository layer for database UPSERT operations (idempotent record persistence & scrape log tracking). |
| **`tests/unit/`** | Unit test suite for politeness engine, cleaners, and DOM parsing (`pytest`). |

---

## 3. Libraries & Dependencies Reference

| Library | Purpose & Role in Project |
| :--- | :--- |
| **`httpx`** | High-performance, async HTTP client used for non-blocking page fetching and REST API requests. |
| **`beautifulsoup4`** | HTML/XML parser used for navigating the DOM tree and extracting fields via CSS selectors. |
| **`pydantic`** | Data validation and typing library enforcing strict data contracts and rejecting unknown fields. |
| **`pydantic-settings`** | Environment variable management mapping `.env` files directly into typed Python settings objects. |
| **`sqlalchemy`** | SQL toolkit and Object-Relational Mapper (ORM) for interacting with SQLite database. |
| **`tenacity`** | Retrying library providing exponential backoff and jitter for network resilience against HTTP `429`/`5xx` errors. |
| **`playwright`** | Headless browser automation library used to render dynamic JavaScript Single Page Applications (SPAs). |
| **`pytest` & `pytest-asyncio`** | Testing framework and async plugin for running unit and integration test suites. |

---

## 4. Configuration & Environment Variables

All settings are configured via environment variables or `.env` files and loaded via `config.py`:

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./flyrank_scraper.db` | SQLite database connection string. |
| `USER_AGENT` | `FlyrankBot/1.0...` | Custom bot identification string sent in HTTP headers. |
| `DEFAULT_RATE_LIMIT_DELAY` | `0.5` | Minimum pause (in seconds) between consecutive requests to a host. |
| `MAX_RETRIES` | `3` | Maximum number of exponential backoff retry attempts for failed requests. |

---

## 5. Usage Section

### Environment Setup

1. **Create and Activate Virtual Environment**:
   ```bash
   cd BE-06-Scraper
   python -m venv .venv
   source .venv/bin/activate        # On Linux/macOS
   # .venv\Scripts\activate          # On Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```

### Running the Scraper CLI

Run `main.py` with the `scrape` subcommand:

#### 1. Stage 1: Run Books Scraper
```bash
python main.py scrape --target books --max-pages 1
```

#### 2. Stage 2: Run German B2B Leads Scraper
```bash
python main.py scrape --target leads --city Berlin --street "Berliner Allee" --max-pages 1
```

#### 3. Stage 3: Run Kaggle Datasets Scraper
```bash
python main.py scrape --target kaggle --query "machine learning" --limit 5
```

---

## 6. Testing Section

The project features a full test suite powered by `pytest` and `pytest-asyncio`.

### Running All Unit Tests

```bash
pytest
```

or using python module invocation:

```bash
python -m pytest
```
