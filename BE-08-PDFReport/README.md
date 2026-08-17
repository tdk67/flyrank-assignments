# BE-08: PDF Report Generator & Immediate Streaming API

An executive analytics and PDF reporting engine built as part of the FlyRank Backend Track. This project queries book scraping data collected in **BE-06-Scraper**, generates branded PDF reports formatted according to the **FL-05 Identity Kit**, and serves reports via both standard file links and an advanced **immediate PDF streaming endpoint**.

---

## 📌 Project Overview

- **Dataset**: Reuses the SQLite database from `BE-06-Scraper` (`flyrank_scraper.db`).
- **Brand System**: Designed using **FL-05 Identity Kit** (`Inter` & `JetBrains Mono` fonts, `#0284c7` Sky Blue, `#0f172a` Slate 900, `#f8fafc` Slate 50).
- **Template Decoupling**: Separation of presentation (`templates/report_template.html`) and backend logic. Design changes require zero backend code edits.
- **Performance at Scale**: SQL aggregations are computed directly in SQLite using indexes (`idx_books_category`, `idx_books_rating`, `idx_books_price`).
- **Dual Serving Modes**:
  1. **Standard Endpoint** (`POST /reports`): Generates & saves PDF to disk, returning a JSON link (`201 Created`). Supports **Idempotency** (duplicate same-day requests return existing file unless `force=true`).
  2. **Tricky Streaming Endpoint** (`GET /reports/stream`): Uses FastAPI `StreamingResponse` to begin sending HTTP response headers instantly upon call, streaming PDF bytes on the fly.

---

## 🛠️ Installation Instructions

```bash
# 1. Navigate to project directory
cd BE-08-PDFReport

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright Chromium browser engine
python -m playwright install chromium
```

---

## 🚀 Usage Guide

```bash
# Run database initialization & index creation
python db.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

### Endpoints
- `GET /health` — Health & Database connection check
- `POST /reports` — Generate & store PDF report (Idempotent)
- `GET /reports/{id}` — Retrieve report metadata
- `GET /reports/{id}/file` — Download stored PDF report
- `GET /reports/stream` — **Immediate PDF Streaming Download**

---

## 🧪 Comprehensive Test Plan

Before writing implementation code, we define our test criteria across 6 testing tiers:

### 1. Database & Seeding Tests
- [ ] **DB Connection Test**: Verify connection to `../BE-06-Scraper/flyrank_scraper.db`.
- [ ] **Table & Index Test**: Verify `reports` metadata table and performance indexes (`idx_books_category`, `idx_books_rating`, `idx_books_price`) exist.
- [ ] **Record Integrity Test**: Confirm `SELECT COUNT(*) FROM books` returns valid row counts.

### 2. SQL Aggregation Logic Tests
- [ ] **Summary KPIs Accuracy**: Test `total_books`, `avg_price`, `total_stock`, and `total_value` match raw table calculations.
- [ ] **Group By Correctness**: Test `rating` (1-5 stars) and `category` breakdowns produce correct group counts and non-null averages.
- [ ] **Top 5 Ranking Test**: Confirm `ORDER BY price_incl_tax DESC LIMIT 5` returns the top 5 most expensive books in descending order.

### 3. Template & Rendering Tests
- [ ] **Jinja2 Decoupling Test**: Verify `render_html_template()` populates all placeholders without missing variable exceptions.
- [ ] **FL-05 Styling Compliance**: Confirm HTML contains FL-05 colors (`#0284c7`, `#0f172a`), typography (`Inter`, `JetBrains Mono`), and TD Monogram badge.

### 4. PDF Layout & Print CSS Tests
- [ ] **Page Break Trap Test**: Verify table rows use `break-inside: avoid;` so no table row is sliced across page breaks.
- [ ] **Repeating Header Test**: Confirm `<thead>` repeats automatically at the top of page 2 for long tables.

### 5. Idempotency & API Endpoints Tests
- [ ] **Health Endpoint Test**: `GET /health` returns `200 OK` with DB record count.
- [ ] **Idempotency Test**: Sequential `POST /reports` calls on the same day return the existing report ID and produce only 1 file in `reports/`.
- [ ] **Force Override Test**: `POST /reports?force=true` bypasses idempotency check and generates a new report ID and file.
- [ ] **File Serving Test**: `GET /reports/{id}/file` correctly serves `application/pdf` binary content.

### 6. Immediate PDF Streaming Tests
- [ ] **Instant Response Header Test**: `curl -v GET http://localhost:8000/reports/stream` shows HTTP status `200 OK` and `Transfer-Encoding: chunked` immediately before full PDF binary transmission finishes.
- [ ] **Valid PDF Stream Test**: Piping streaming response to file (`curl -o stream_test.pdf http://localhost:8000/reports/stream`) yields a valid, readable PDF document.

---

## 📋 Tasklist / Progress Tracker

- [x] **Step 0: Setup & Structure**
  - [x] Create `.gitignore` and `requirements.txt`
  - [x] Create comprehensive `README.md` with Test Plan & Tasklist
  - [x] Create minimal `main.py` with `/health` endpoint
  - [x] Checkpoint 0: Verify `/health` endpoint returns 200 OK

- [x] **Step 1: Database & Performance Indexing**
  - [x] Create `config.json` and strict `config.py` without hardcoded fallbacks
  - [x] Create standalone `setup_db.py` script for one-time table & index setup
  - [x] Implement runtime `db.py` with human-readable error messages
  - [x] Checkpoint 1: Run `setup_db.py` and `pytest test_db.py`

- [x] **Step 2: SQL Aggregation Queries**
  - [x] Implement `get_report_data()` in `aggregations.py`
  - [x] Write SQL queries for KPIs, Top 5, Rating Breakdown, Category Breakdown
  - [x] Checkpoint 2: Run `pytest test_aggregations.py`

- [ ] **Step 3: Decoupled Jinja2 HTML Template & Print CSS**
  - [ ] Create `templates/report_template.html` using **FL-05 Identity Kit**
  - [ ] Implement Print CSS (`@page`, `break-inside: avoid`, repeating `<thead>`)
  - [ ] Checkpoint 3: Verify HTML rendering with sample data

- [ ] **Step 4: PDF Generation Engine & Storage**
  - [ ] Implement Playwright Chromium rendering engine (`pdf_generator.py`)
  - [ ] Render sample HTML to PDF file (`reports/test.pdf`)
  - [ ] Checkpoint 4: Open PDF and verify page breaks & repeating table header

- [ ] **Step 5: File-Serving Endpoints & Idempotency**
  - [ ] Implement `POST /reports` (Idempotent report generation)
  - [ ] Implement `GET /reports/{id}` and `GET /reports/{id}/file`
  - [ ] Checkpoint 5: Verify double-click idempotency with `curl`

- [ ] **Step 6: Immediate PDF Streaming Endpoint**
  - [ ] Implement `GET /reports/stream` using FastAPI `StreamingResponse`
  - [ ] Stream chunked PDF bytes directly upon request initiation
  - [ ] Checkpoint 6: Verify immediate chunked streaming download with `curl -v`
