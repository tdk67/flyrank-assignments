# BE-07 Assignment Tasklist & Progress Tracker

## Stage 0: Setup & Model Connectivity (~45 min)
- [x] Create `JOB-CARD.md` with input, output, "must never", and "when unsure" rules.
- [x] Configure `.env`, `.env.example`, and `.gitignore` (keep keys out of Git).
- [x] Write `src/llm/hello.py` sanity check script to verify model connectivity.
- [x] Verify local Ollama (`llama3.2:1b`) responds with "ready".

## Stage 1: Build Endpoint & Schema in Stub Mode (~45 min)
- [x] Define Pydantic request & response schemas in `src/llm/schema.py` with `TargetLanguageEnum` (`[de, fr, it, en]`).
- [x] Create `POST /books/translate` endpoint in `src/main.py`.
- [x] Implement input validation: HTTP 404 for unknown `book_id`, HTTP 400 for invalid `target_language`.
- [x] Implement Stub Mode (`LLM_STUB=1`) returning schema-compliant response without calling the model.
- [x] Create `GET /models` endpoint to list installed local Ollama models.
- [x] Write automated tests in `tests/test_stage1.py` (3/3 passed).

## Stage 2: Versioned System Prompt (~1h 15m)
- [x] Create system prompt file at `prompts/book-translate-v1.md`.
- [x] Include 5 required parts: Role/Job, Output Shape, Rules, When Unsure instruction, Few-shot Examples.
- [x] Keep user input separate in the `user` message to prevent prompt injection.
- [x] Set temperature to `0.0` for deterministic outputs.

## Stage 3: Parse, Validate, Repair & Quarantine (~1h 30m)
- [x] Build `src/llm/translator.py` with code fence stripping (` ```json `) and JSON parsing.
- [x] Validate output against `TranslationResponse` Pydantic schema.
- [x] Implement **Repair Once and Only Once**: Perform 1 repair retry feeding error back to model.
- [x] Implement **Quarantine**: Log double-failures to `logs/quarantine.jsonl` and return HTTP 422.
- [x] Write live model translation test in `tests/test_stage2_3.py` (passed).

## Stage 4: Production Readiness (~1h 15m)
- [x] Create `src/config.py` strict environment validator (fail fast on missing variables, no silent fallbacks).
- [x] Set explicit 30s timeout on client and return HTTP 504 Gateway Timeout on expiration.
- [x] Implement retry policy: exponential backoff with jitter on 429/5xx, **zero retries** on 400/401/403.
- [x] Implement structured cost logging to `logs/costs.jsonl` (tokens, duration, repair status).
- [x] Implement Kill Switch (`LLM_ENABLED=false`) returning HTTP 503 Service Unavailable.
- [x] Write tests in `tests/test_stage4.py` (passed).

## Stage 5: Evals & Documentation (~1h)
- [x] Create 8-case eval test set in `evals/cases.json`.
- [x] Create eval runner script `evals/run_evals.py` (achieved 8/8 100% pass score).
- [x] Write complete `README.md` with installation, file breakdown, library descriptions, usage, testing, cost logs, and eval score.

## Stretch Goal / Security: Guardrails & Prompt Injection Defense (OWASP LLM01)
- [x] Add Anti-Hijacking rule to `prompts/book-translate-v1.md`.
- [x] Add Prompt Injection Few-Shot Example to `prompts/book-translate-v1.md`.
- [x] Add Prompt Injection Attack test case to `evals/cases.json` (9 cases total).
- [x] Create automated prompt injection test in `tests/test_prompt_injection.py`.
- [x] Document 5-Layer Prompt Injection Defense Strategy in `README.md`.

## Code Review Hardening & Audit Resolution (`review.md` Fixes)
- [x] **C1 Fix**: Validate returned model `book_id` and `target_language` against original request in `parse_and_validate()`. Reject & repair on mismatch.
- [x] **C2 Fix**: Enforce `extra="forbid"`, `str_strip_whitespace=True`, and `min_length=1` for titles/descriptions in `TranslationResponse`.
- [x] **C3 Fix**: Created `conftest.py` pytest fixture with `reload_config()` and `reset_client()` to prevent import-order singleton test contamination.
- [x] **C4 Fix**: Updated `test_prompt_injection.py` to exercise attack payload defense with mocked LLM response.
- [x] **H1 & H2 Fix**: Created `tests/test_resilience_mocked.py` with 100% mocked coverage for timeouts (504), provider key errors (502), rate limit backoff (429), extra fields, mismatches, and verified `logs/costs.jsonl` entry creation.
- [x] **H3 & H4 Fix**: Narrowed retry policy to 429/5xx only, and added a 45s request-level deadline cap (`request_timeout_seconds`).
- [x] **H5 Fix**: Added forbidden substring assertions (`SYSTEM COMPROMISED`) to `run_evals.py` for Case 9 prompt injection.
- [x] **H6 & M3 Fix**: Sanitized client-facing error tracebacks to generic messages, mapping provider key/auth errors to HTTP 502 Bad Gateway.
- [x] **H7 & M10 Fix**: Handled corrupt JSONL dataset lines gracefully with `json.JSONDecodeError` logging; added `GET /health` endpoint returning loaded record count.
- [x] **M1 & M2 Fix**: Wired `config.max_repair_retries` into repair loop; parsed `llm_enabled` and `llm_stub` fail-closed (`"true"`, `"1"` -> True, all else -> False).
- [x] **M5 & Nit 7 Fix**: Reused application-lifetime `OpenAI` client singleton; cached system prompt in memory at startup.
- [x] **Deprecation Clean-up**: Replaced deprecated `HTTP_422_UNPROCESSABLE_ENTITY` with `HTTP_422_UNPROCESSABLE_CONTENT` and configured `pytest.ini` for clean 0-warning output.

## Future Architectural Enhancements (TODO List)
- [ ] **Decouple Dataset Dependency**: Make BE-07 fully standalone by copying/bundling a local seed dataset (e.g. `data/books.jsonl`) or SQLite database inside `BE-07-AI-Call`, so it does not strictly depend on the relative path `../BE-06-Scraper/books.jsonl`.
- [ ] **LRU Caching**: Add an in-memory or Redis LRU cache (`hash(book_id + target_language + prompt_version)`) to serve repeated translation requests in 0ms without hitting the LLM model again.
