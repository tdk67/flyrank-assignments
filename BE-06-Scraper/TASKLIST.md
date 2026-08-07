# Implementation Tasklist & Progress Tracker (`TASKLIST.md`)

Use this tasklist to track implementation progress across the 4 execution phases of **BE-06-Scraper**.

---

## Phase 0: Project Setup & Core Infrastructure Framework

- [x] **0.1** Environment & Dependencies
  - [x] Create `requirements.txt` (`httpx`, `beautifulsoup4`, `playwright`, `pydantic`, `sqlalchemy`, `psycopg2-binary`, `tenacity`)
  - [x] Create `requirements-dev.txt` (`pytest`, `pytest-asyncio`)
  - [x] Create `.env.example` and `config.py` configuration loader

- [x] **0.2** Docker & Database Migrations (Liquibase)
  - [x] Create `docker-compose.yml` (Postgres 16 + `db-migrate` Liquibase service)
  - [x] Create `db/changelog/db.changelog-master.xml`
  - [x] Create `001_create_books_table.sql`
  - [x] Create `002_create_leads_table.sql`
  - [x] Create `003_create_datasets_table.sql`
  - [x] Create `004_create_scrape_logs_table.sql`

- [x] **0.3** Politeness & Ethics Engine (`core/politeness.py`)
  - [x] Implement `RobotsParser` (`urllib.robotparser` wrapper with 404/403 fallback handling)
  - [x] Implement `RateLimiter` (token-bucket delay per host)
  - [x] Implement `UserAgentManager` (`FlyrankBot/1.0` contact header)
  - [x] Implement `RetryBackoff` (`tenacity` exponential backoff for `429`/`5xx`)

- [x] **0.4** Strategy Engine & Storage Sinks
  - [x] Create `core/base_target.py` (`BaseTargetStrategy` Abstract Base Class)
  - [x] Create `storage/repository.py` (SQLAlchemy ORM models & UPSERT functions)
  - [x] Create `storage/rag_exporter.py` (JSONL RAG text chunk exporter)
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
  - [x] Verify PostgreSQL `books` table records and `books.jsonl` output

---

## Phase 2: Stage 2 — Leads Target (`dasoertliche.de` B2B Leads)

- [ ] **2.1** Implement `targets/leads_target.py`
  - [ ] Implement German street URL builder (`Karl-Marx-Straße` $\rightarrow$ `Karl--Marx--Straße`)
  - [ ] Implement JSON-LD microdata tag extractor (`<script type="application/ld+json">`)
  - [ ] Implement B2B vs. Private Person filter rules
  - [ ] Extract name, industry category, street, house number, postal code, city, phone, website
- [ ] **2.2** Data Cleaning & Pydantic Validation
  - [ ] Implement `cleaner/leads_cleaner.py` (Phone regex cleaner, directory link stripper)
  - [ ] Define `schemas.py` `LeadRecord` model
- [ ] **2.3** Testing & Verification across Test Pairs
  - [ ] Write `tests/unit/test_leads_cleaner.py`
  - [ ] Test Pair 1: `Berlin + Berliner Allee`
  - [ ] Test Pair 2: `Berlin + Friedrichstraße`
  - [ ] Test Pair 3: `München + Leopoldstraße`
  - [ ] Test Pair 4: `Hamburg + Reeperbahn`
  - [ ] Test Pair 5: `Frankfurt + Kaiserstraße`
  - [ ] Verify PostgreSQL `leads` table records and `leads.jsonl` output

---

## Phase 3: Stage 3 — Kaggle Target (`kaggle.com/datasets`)

- [ ] **3.1** Implement `targets/kaggle_target.py`
  - [ ] Implement Playwright headless browser automation / API interceptor
  - [ ] Wait for client-side React DOM hydration
  - [ ] Extract title, dataset URL, creator, upvotes, views, downloads, license, description, tags, last updated date
- [ ] **3.2** Data Cleaning & Pydantic Validation
  - [ ] Implement `cleaner/kaggle_cleaner.py` (Metric parsing, tag list cleaning)
  - [ ] Define `schemas.py` `DatasetRecord` model
- [ ] **3.3** Testing & Verification
  - [ ] Write `tests/unit/test_kaggle_cleaner.py`
  - [ ] Run live smoke test: `python main.py scrape --target kaggle --query "machine learning" --limit 5`
  - [ ] Verify PostgreSQL `datasets` table records and `kaggle.jsonl` output

---

## Phase 4: Final Verification, Multi-Target RAG Export & Docs

- [ ] **4.1** Full Test Suite Execution
  - [ ] Run `pytest` (Unit + Integration tests)
  - [ ] Verify 100% backward compatibility across all 3 CLI target modes
- [ ] **4.2** Final RAG Datasets Generation
  - [ ] Generate `rag_corpus_books.jsonl`
  - [ ] Generate `rag_corpus_leads.jsonl`
  - [ ] Generate `rag_corpus_kaggle.jsonl`
- [ ] **4.3** Project Documentation
  - [ ] Write `BE-06-Scraper/README.md` with setup, execution, architecture, and RAG export instructions.
