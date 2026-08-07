# Web Scraping Brainstorming & Architecture Reference (`ideas.md`)

## 1. Overview & Context

This document captures the complete brainstorming, site analysis, technical paradigms, and commercial ecosystem options explored during the design phase of the **BE-06-Scraper** assignment for Flyrank.

The core purpose of this project is to master the full end-to-end data gathering pipeline:
$$\text{Fetch} \longrightarrow \text{Parse} \longrightarrow \text{Extract} \longrightarrow \text{Clean} \longrightarrow \text{Structure \& Store}$$

while enforcing a strict **Professionalism & Politeness Layer** (`robots.txt` enforcement, custom `User-Agent` identification, rate-limiting, and resilience backoff).

---

## 2. Technical Analysis of Discussed Web Targets

During our brainstorming, we evaluated 5 distinct web scraping targets spanning different architectural levels:

| # | Target Site | Architecture Type | Scraping Technique | `robots.txt` Status | Anti-Bot Shields | RAG Corpus Utility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **`books.toscrape.com`** | Static HTML Sandbox | CSS Selectors (BeautifulSoup4) | HTTP 404 (Explicitly Open) | None (Official Sandbox) | Book recommendation & literary QA |
| **2** | **`dasoertliche.de`** | Live Public Directory | **JSON-LD Microdata** + HTML | `Disallow:` (No path restrictions) | Low (Rate limit sensitive) | **B2B Local Lead Finder & Contact QA** |
| **3** | **`kaggle.com/datasets`** | Dynamic React SPA | Playwright / Internal API | HTTP 404 (No robots.txt restrictions) | Medium (Cloudflare, Google Auth) | AI/ML Dataset catalog discovery assistant |
| **4** | **`ebay.de`** | Hybrid Commercial | HTML + JSON-LD Microdata | Strict (`Disallow` search, bans LLM bots) | High (Akamai Bot Manager) | E-Commerce pricing & auction evaluation |
| **5** | **`booking.com`** | Sitemaps + React SPA | **XML Sitemaps** + Microdata | Welcoming (`Sitemap` index encouraged) | Medium (Dynamic date pricing) | Travel concierge & hotel QA assistant |

---

## 3. Universal Web Scraping Design Patterns

Rather than writing ad-hoc scripts tied to fragile HTML layouts, production scrapers rely on **6 Universal Architectural Layers**:

1. **Target Discovery Strategy**:
   - *Static URL Generation*: Formatting parametric URLs (e.g. `/Themen/{street}/{city}-Seite-{page}.htm`).
   - *Link Traversal / Crawler Queue*: BFS/DFS URL queue with visited set deduplication.
   - *XML Sitemap Index Parsing*: Traversing `sitemap.xml` indices for canonical URLs.
2. **Politeness & Resilience Middleware**:
   - *Robots Inspector*: Reading `robots.txt` via `urllib.robotparser`.
   - *Token-Bucket Rate Limiter*: Enforcing minimum inter-request delays ($0.5\text{s} - 1.5\text{s}$).
   - *Exponential Backoff Retry*: Handling `429 Too Many Requests`, `5xx`, and timeouts via `tenacity`.
   - *User-Agent & Identity Manager*: Identifying the bot transparently with contact details.
3. **Content Fetcher Strategy**:
   - *Lightweight HTTP Client* (`httpx`, `requests`, `aiohttp`) for static HTML & REST APIs.
   - *Headless Browser Engine* (`Playwright`, `Selenium`) for client-side JavaScript SPAs.
4. **Parser & Extractor Strategy**:
   - *Microdata Extractor*: Extracting `<script type="application/ld+json">` schema tags (universal across 40%+ of web).
   - *CSS / XPath Selector Extractor*: Site-specific DOM parsing fallback.
   - *Generic Readability Extractor* (`trafilatura`, `readability`): Extracting main article body without custom selectors.
5. **Cleaner & Schema Validator**:
   - Regex string normalization, type conversions (currency to float, star text to int), and Pydantic v2 validation.
6. **Storage Sink Adapter**:
   - Idempotent database UPSERT (PostgreSQL via SQLAlchemy) + JSONL RAG file export.

---

## 4. Commercial & Open Source Web Scraping Ecosystem

In production environments, engineers often leverage third-party tools and managed APIs alongside custom scrapers:

### Managed LLM Scraping & Search APIs
- **Tavily / DuckDuckGo API**: Web search APIs tailored for AI agents to retrieve ranked search result snippets and URLs.
- **Firecrawl / Crawl4AI / Jina Reader / Smallfish**: Managed endpoints that take any web URL and handle proxy rotation, CAPTCHA solving, and JavaScript execution, returning clean formatted Markdown ready for LLM prompts.

### Headless Browser & Crawler Frameworks
- **Playwright / Puppeteer**: Automation frameworks for controlling headless Chromium/Firefox to render complex Single Page Applications (SPAs).
- **Scrapy**: High-throughput Python crawling framework with built-in pipelines and middleware.

### Anti-Bot & Proxy Networks
- **Bright Data / ZenRows / ScrapingBee**: Proxy rotation services that bypass Akamai, Imperva, Datadome, and Cloudflare bot detection.

---

## 5. Architectural Vision for BE-06-Scraper

To combine maximum learning value with clean software design, **BE-06-Scraper** implements a **Strategy Pattern Engine** supporting a progressive 3-stage capability expansion:

```
[CLI Runner: python main.py --target [books|leads|kaggle]]
                           │
                           ▼
             [Politeness & Retry Middleware]
                           │
                           ▼
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   [BooksTarget]    [LeadsTarget]    [KaggleTarget]
   (Static HTML)    (JSON-LD B2B)    (Playwright SPA)
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
            [Pydantic Schema Validation]
                           │
                           ▼
            [Postgres DB + JSONL RAG Sink]
```

This ensures that adding advanced targets (Leads, Kaggle) keeps early targets (Books) 100% functional and backward-compatible.
