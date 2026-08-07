# Implementation Tasklist & Progress Tracker (`TASKLIST.md`)

Use this tasklist to track implementation progress across all phases of **BE-06-Scraper**.

---

## Phase 0: Project Setup & Core Infrastructure Framework

- [x] **0.1** Environment & Dependencies
  - [x] Create `requirements.txt` (`httpx`, `beautifulsoup4`, `playwright`, `pydantic`, `sqlalchemy`, `tenacity`)
  - [x] Create `requirements-dev.txt` (`pytest`, `pytest-asyncio`)
  - [x] Create `.env.example` and `config.py` configuration loader

- [x] **0.2** SQLite Database Setup
  - [x] Configure SQLite engine (`flyrank_scraper.db`) in `storage/database.py`
  - [x] Define SQLAlchemy models for `Book`, `Lead`, `Dataset`, and `ScrapeLog` in `storage/models.py`

- [x] **0.3** Politeness & Ethics Engine (`core/politeness.py`)
  - [x] Implement `RobotsParser` (`urllib.robotparser` wrapper with 404/403 fallback handling)
  - [x] Implement `RateLimiter` (token-bucket delay per host)
  - [x] Implement `UserAgentManager` (`FlyrankBot/1.0` contact header)
  - [x] Implement `RetryBackoff` (`tenacity` exponential backoff for `429`/`5xx`)

- [x] **0.4** Strategy Engine & Storage Sinks
  - [x] Create `core/base_target.py` (`BaseTargetStrategy` ABC with `ScrapeLog` tracking)
  - [x] Create `storage/repository.py` (SQLite UPSERT repository for all 4 models)
  - [x] Create `main.py` & `cli.py` (Unified CLI entrypoint supporting `--target [books|leads|kaggle]`)

---

## Phase 1: Stage 1 — Books Target (`books.toscrape.com`)

- [x] **1.1** Implement `targets/books_target.py`
  - [x] Fetch catalog categories and paginated index pages
  - [x] Extract product detail pages using BeautifulSoup4 CSS selectors
  - [x] Extract UPC, title, category, price, tax, availability, stock, rating, description
- [x] **1.2** Data Cleaning & Pydantic Validation
  - [x] Implement `cleaner/books_cleaner.py` (Currency float conversion, rating word-to-int mapping, stock integer regex)
  - [x] Define `schemas.py` `BookRecord` model
- [x] **1.3** Testing & Verification
  - [x] Write `tests/unit/test_books_cleaner.py`
  - [x] Run live smoke test: `python main.py scrape --target books --max-pages 1`
  - [x] Verify SQLite `books` and `scrape_logs` table records

---

## Phase 2: Stage 2 — Leads Target (`dasoertliche.de` B2B Leads)

- [x] **2.1** Implement `targets/leads_target.py`
  - [x] Implement German street URL builder (`Karl-Marx-Straße` $\rightarrow$ `Karl--Marx--Straße`)
  - [x] Implement JSON-LD microdata tag extractor (`<script type="application/ld+json">`)
  - [x] Implement B2B vs. Private Person filter rules
  - [x] Extract name, industry category, street, house number, postal code, city, phone, website
- [x] **2.2** Data Cleaning & Pydantic Validation
  - [x] Implement `cleaner/leads_cleaner.py` (Phone regex cleaner, directory link stripper)
  - [x] Define `schemas.py` `LeadRecord` model
- [x] **2.3** Testing & Verification across Test Pairs
  - [x] Write `tests/unit/test_leads_cleaner.py`
  - [x] Test Pair 1: `Berlin + Berliner Allee`
  - [x] Test Pair 2: `Berlin + Friedrichstraße`
  - [x] Test Pair 3: `München + Leopoldstraße`
  - [x] Test Pair 4: `Hamburg + Reeperbahn`
  - [x] Test Pair 5: `Frankfurt + Kaiserstraße`
  - [x] Verify SQLite `leads` and `scrape_logs` table records

---

## Phase 3: Stage 3 — Kaggle Target (`kaggle.com/datasets`)

- [x] **3.1** Implement `targets/kaggle_target.py`
  - [x] Implement Playwright headless browser automation / API interceptor
  - [x] Wait for client-side React DOM hydration
  - [x] Extract title, dataset URL, creator, upvotes, views, downloads, license, description, tags, last updated date
- [x] **3.2** Data Cleaning & Pydantic Validation
  - [x] Implement `cleaner/kaggle_cleaner.py` (Metric parsing, tag list cleaning)
  - [x] Define `schemas.py` `DatasetRecord` model
- [x] **3.3** Testing & Verification
  - [x] Write `tests/unit/test_kaggle_cleaner.py`
  - [x] Run live smoke test: `python main.py scrape --target kaggle --query "machine learning" --limit 5`
  - [x] Verify SQLite `datasets` and `scrape_logs` table records

---

## Phase 4: Refactoring & Architecture Verification

- [x] **4.1** Full Test Suite Execution
  - [x] Run `pytest` (Unit tests across all target strategies)
  - [x] Verify 100% backward compatibility across all 3 CLI target modes
- [x] **4.2** SQLite Database Verification
  - [x] Verify `flyrank_scraper.db` untracked in `.gitignore`
  - [x] Verify `scrape_logs` populated on every scrape session

---

## Phase 5: Streamlit Live Demo Frontend (`app.py`)

- [x] **5.1** Dependencies
  - [x] Add `streamlit>=1.35.0` to `requirements.txt`
- [x] **5.2** Streamlit App (`app.py`)
  - [x] Implement Sidebar controls (Target selector, parameters)
  - [x] Implement Hybrid execution wrapper calling `asyncio.run(strategy.run(...))`
  - [x] Implement Tab 1: Live Data Grid (`st.dataframe`)
  - [x] Implement Tab 2: Record Detail Inspector
  - [x] Implement Tab 3: Scraping Session History Log Viewer (reading `scrape_logs` from SQLite DB)
- [x] **5.3** Testing & Verification
  - [x] Run Streamlit app (`streamlit run app.py`) and verify live scraping demo
