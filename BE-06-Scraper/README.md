# BE-06-Scraper — Progressive 3-Stage Multi-Target Web Scraper & Streamlit Live Demo

`BE-06-Scraper` is a production-grade, extensible web scraping service built with Python 3.12+. It implements a 5-stage ETL data gathering pipeline (**Fetch $\rightarrow$ Parse $\rightarrow$ Extract $\rightarrow$ Clean $\rightarrow$ Structure $\rightarrow$ Store**) combined with a strict **Politeness & Ethics Layer** (`robots.txt` enforcement, token-bucket rate limiting, transparent `User-Agent` headers, and exponential backoff).

All extracted records are validated via Pydantic v2 models and persisted directly into a zero-setup **SQLite Database (`flyrank_scraper.db`)**. It includes a full-featured **Streamlit Interactive Web Application (`app.py`)** for live demonstration, data exploration, and session auditing.

---

## 1. Architecture & Strategy Design

To combine high learning value with software engineering best practices, `BE-06-Scraper` uses a **Strategy Pattern Engine** supporting a **3-Stage Progressive Pipeline**. New scraping targets are added in sequential stages without breaking backward compatibility for earlier stages.

```
                              ┌────────────────────────┐
                              │     Streamlit UI / CLI │
                              │   streamlit run app.py │
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
                              └───────────┬────────────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        │                                   │
                        ▼                                   ▼
             ┌─────────────────────┐             ┌─────────────────────┐
             │  Live Data Table    │             │  Scrape Session     │
             │  (books/leads/ds)   │             │  Audit Logs         │
             └─────────────────────┘             └─────────────────────┘
```

---

## 2. Benchmark Test Examples & Test Pairs

Below are 5 curated benchmark test pairs for Stage 2 (Das Örtliche German B2B Leads) demonstrating URL slug resolution, street abbreviation handling, and administrative city variant matching:

| # | Test City | Test Street | Target Das Örtliche URL | Key Handling Feature Tested |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `Neu-Isenburg` | `Frankfurter Straße` | [Frankfurter-Str/Neu--Isenburg.htm](https://www.dasoertliche.de/Themen/Frankfurter-Str/Neu--Isenburg.htm) | Abbreviation fallback (`Str` vs `Straße`) & Hyphenation |
| **2** | `Freiburg` | `Willy-Brandt-Allee` | [Willy--Brandt--Allee/Freiburg-im-Breisgau.htm](https://www.dasoertliche.de/Themen/Willy--Brandt--Allee/Freiburg-im-Breisgau.htm) | City variant resolution (`Freiburg` $\rightarrow$ `Freiburg im Breisgau`) |
| **3** | `Frankfurt am Main` | `Ludwig Erhard Anlage` | [Ludwig--Erhard--Anlage/Frankfurt-am-Main.htm](https://www.dasoertliche.de/Themen/Ludwig--Erhard--Anlage/Frankfurt-am-Main.htm) | Space-to-hyphen encoding & batch lead deduplication |
| **4** | `Bad Homburg von der Höhe` | `Kaiser-Friedrich-Promenade` | [Kaiser--Friedrich--Promenade/Bad-Homburg-v-d-Höhe.htm](https://www.dasoertliche.de/Themen/Kaiser--Friedrich--Promenade/Bad-Homburg-v-d-Höhe.htm) | Administrative prefix mapping (`von der` $\rightarrow$ `v-d-`) |
| **5** | `Dietzenbach` | `Max Planck Straße` | [Max--Planck--Str/Dietzenbach.htm](https://www.dasoertliche.de/Themen/Max--Planck--Str/Dietzenbach.htm) | Multi-word space encoding & `Str` fallback resolution |

### Testing Commands for Benchmark Examples:

```bash
# 1. Neu-Isenburg
python main.py scrape --target leads --city "Neu-Isenburg" --street "Frankfurter Straße"

# 2. Freiburg
python main.py scrape --target leads --city "Freiburg" --street "Willy-Brandt-Allee"

# 3. Frankfurt am Main
python main.py scrape --target leads --city "Frankfurt am Main" --street "Ludwig Erhard Anlage"

# 4. Bad Homburg von der Höhe
python main.py scrape --target leads --city "Bad Homburg von der Höhe" --street "Kaiser-Friedrich-Promenade"

# 5. Dietzenbach
python main.py scrape --target leads --city "Dietzenbach" --street "Max Planck Straße"
```

---

## 3. Source Code & File Structure

Here is a detailed breakdown of all files in the solution and their specific roles:

| File Path | Description / Responsibility |
| :--- | :--- |
| **`app.py`** | **Streamlit Live Demo Frontend**: Interactive dashboard featuring target launcher, live dataset grid, record inspector, and audit log viewer. |
| **`main.py`** | Primary application execution entrypoint. Invokes CLI parser and async main loop. |
| **`cli.py`** | Command-Line Interface module using `argparse`. Defines flags (`--target`, `--max-pages`, `--city`, `--street`, `--query`, `--limit`). |
| **`config.py`** | Settings manager using `pydantic-settings`. Loads `.env`, manages SQLite database URL. |
| **`schemas.py`** | Pydantic v2 data models (`BookRecord`, `LeadRecord`, `DatasetRecord`, `ScrapeLogRecord`) with `ConfigDict(extra="forbid")`. |
| **`core/exceptions.py`** | Custom domain exceptions (`InvalidSearchLocationError`, `TargetNotFoundError`, `ScraperError`). |
| **`core/politeness.py`** | Ethics middleware: `RobotsParser` (`robots.txt` compliance), `RateLimiter` (token-bucket delay), `UserAgentManager`, `RetryBackoff` (`tenacity`). |
| **`core/base_target.py`** | Abstract Base Class `BaseTargetStrategy` defining strategy interface and automated `ScrapeLog` session tracking. |
| **`targets/books_target.py`** | **Stage 1 Strategy**: Async HTTP fetcher & BeautifulSoup4 DOM parser for `books.toscrape.com`. |
| **`targets/leads_target.py`** | **Stage 2 Strategy**: German street & city URL transformer, JSON-LD microdata extractor, and B2B vs. Person filter for `dasoertliche.de`. |
| **`targets/kaggle_target.py`** | **Stage 3 Strategy**: Playwright headless browser / REST API interceptor for `kaggle.com/datasets`. |
| **`cleaner/books_cleaner.py`** | Cleaning utilities for books: currency float parser, rating word-to-int mapper, stock quantity regex, HTML unescaper. |
| **`cleaner/leads_cleaner.py`** | Cleaning utilities for leads: German street/city variant generator, JSON-LD lead parser, phone number regex cleaner. |
| **`cleaner/kaggle_cleaner.py`** | Cleaning utilities for datasets: metric count parser (`"1.5k"` $\rightarrow$ `1500`), tag normalizer. |
| **`storage/models.py`** | SQLAlchemy ORM declarative models (`Book`, `Lead`, `Dataset`, `ScrapeLog`). |
| **`storage/database.py`** | SQLite database engine setup, auto-creation of tables, and session factory (`SessionLocal`). |
| **`storage/repository.py`** | Repository layer for database UPSERT operations (idempotent record persistence & scrape log tracking). |
| **`tests/unit/`** | Unit test suite for politeness engine, cleaners, and DOM parsing (`pytest`). |

---

## 4. Libraries & Dependencies Reference

| Library | Purpose & Role in Project |
| :--- | :--- |
| **`streamlit`** | Interactive web application framework used to build the live demo dashboard (`app.py`). |
| **`pandas`** | Data analysis library used to format database query outputs into interactive data grids. |
| **`httpx`** | High-performance, async HTTP client used for non-blocking page fetching and REST API requests. |
| **`beautifulsoup4`** | HTML/XML parser used for navigating the DOM tree and extracting fields via CSS selectors. |
| **`pydantic`** | Data validation and typing library enforcing strict data contracts and rejecting unknown fields. |
| **`pydantic-settings`** | Environment variable management mapping `.env` files directly into typed Python settings objects. |
| **`sqlalchemy`** | SQL toolkit and Object-Relational Mapper (ORM) for interacting with SQLite database. |
| **`tenacity`** | Retrying library providing exponential backoff and jitter for network resilience against HTTP `429`/`5xx` errors. |
| **`playwright`** | Headless browser automation library used to render dynamic JavaScript Single Page Applications (SPAs). |
| **`pytest` & `pytest-asyncio`** | Testing framework and async plugin for running unit and integration test suites. |

---

## 5. Configuration & Environment Variables

All settings are configured via environment variables or `.env` files and loaded via `config.py`:

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./flyrank_scraper.db` | SQLite database connection string. |
| `USER_AGENT` | `FlyrankBot/1.0...` | Custom bot identification string sent in HTTP headers. |
| `DEFAULT_RATE_LIMIT_DELAY` | `0.5` | Minimum pause (in seconds) between consecutive requests to a host. |
| `MAX_RETRIES` | `3` | Maximum number of exponential backoff retry attempts for failed requests. |

---

## 6. Usage Section

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

---

### Running the Streamlit Live Demo UI

To launch the interactive visual dashboard:

```bash
python -m streamlit run app.py
```

This automatically opens your browser at **`http://localhost:8501`**, offering:
- **Interactive Scraper Launcher**: Run `Books`, `B2B Leads`, or `Kaggle Datasets` scrapers with custom parameters or preset test pairs.
- **Direct Results Tab**: View freshly extracted records from the active session.
- **SQLite Database Explorer**: Search, sort, and filter all historical records by city or target.
- **Detailed Record Inspector**: View structured fields side-by-side with metadata and original page links.
- **Scraping Session Audit Logs**: Monitor session start/end times, pages scraped, extracted record counts, and status (`COMPLETED` / `FAILED`).

---

### Running the CLI Scraper Engine

You can also execute the scrapers directly from the terminal via `main.py`:

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

## 7. Testing Section

The project features a full test suite powered by `pytest` and `pytest-asyncio`.

### Running All Unit Tests

```bash
pytest
```

or using python module invocation:

```bash
python -m pytest
```
