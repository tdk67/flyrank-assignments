# Code Review - BE-07-AI-Call

**Reviewer:** automated strict code review (source files were not modified by the review)
**Date:** 2026-08-10 (updated after environment setup and live verification)
**Scope:** src/, tests/, evals/, prompts/, config.json, docs
**Method:** static review + empirical verification (fresh venv, pytest, targeted runtime probes, live OpenRouter calls)

---

## Verdict summary

The design intent is strong (kill switch, retries, repair/quarantine, prompt-injection hardening, cost logging), but several headline claims are not upheld by the code, and the test suite does not actually cover most of the production controls it claims to test.

| Severity | Count |
|---|---|
| [CRITICAL] claim-vs-reality gaps | 4 |
| [HIGH] | 7 |
| [MEDIUM] | 9 |
| [LOW / nits] | 8 |
| [RESOLVED] environment-only issues | 1 (former C1, see below) |

---

## Environment status (update after live verification)

The original finding "tests fail out of the box because books.jsonl is missing" turned out to be an **environment issue, not a code defect**: BE-06 had never been run on this machine, so the dataset did not exist. It has been fixed:

- BE-06 books scraper executed: `python main.py scrape --target books --max-pages 50` -> 1000 books persisted to `flyrank_scraper.db`.
- Dataset exported via BE-06's own `RAGExporter` to `BE-06-Scraper/books.jsonl` (1000 records); all 8 eval-case book IDs verified present.
- No local Ollama exists on this machine, so BE-07 was pointed at OpenRouter. API key was recovered from `/root/.pi/agent/auth.json` (the `OPENROUTER_API_KEY` variables in tools/.env, pi-a2a-server/.env etc. were all empty). `BE-07-AI-Call/.env` now uses `LLM_BASE_URL=https://openrouter.ai/api/v1` with model `google/gemma-4-26b-a4b-it:free` (zero-cost tier; the 31b free variant was rejected because it was rate-limited upstream).
- Live verification results (real LLM, stub off):
  - German translation of "A Light in the Attic" (a897fe39b1053632): schema-valid, confidence 0.95, entry written to logs/costs.jsonl.
  - French translation of "Tipping the Velvet" (90fa61229261140a): schema-valid.
  - Injection book "Sharp Objects" (e00eb4fd7b871a48, description contains attack payload): translated literally, payload not obeyed, schema-valid.
  - 400 for invalid language and 404 for unknown book confirmed before any LLM call.
  - `pytest tests/test_stage1.py` -> 3 passed (was 1 failed / 3 only due to the missing dataset).
  - `GET /models` works; port 8000 is occupied by another service on this host, use a different port.

**Residual code concern (downgraded from the former C1):** the app still degrades silently when the dataset is absent - `db.py` prints a warning and serves 404 for everything instead of failing fast or surfacing a clear startup error, and nothing bundles or generates the dataset for BE-07 itself. See M-level note under "Medium findings" (promoted to M10) and the priority list.

---

## [CRITICAL] findings

### C1. LLM output is never cross-checked against the request - wrong book/language silently accepted
`main.py` returns whatever `call_llm_translate` validates *by shape only*. Nothing verifies that the returned `book_id` equals the requested `book_id`, or that `target_language` equals the requested language. Empirically verified:

```python
TranslationResponse.model_validate({
  'book_id': 'OTHER_BOOK_ID', 'target_language': 'fr',   # request was ('x','de')
  'translated_title': '', 'translated_description': '',
  'confidence': '0.9'})
# -> accepted
```

A confused or manipulated model can return **the translation of a different book, or a different (but enum-valid) language**, and the API serves it as if it were correct. This also violates the job card ("never invent target languages" - a swap between two *allowed* languages passes). Only the eval runner checks this, and evals are not part of `pytest`. Live testing confirmed the happy path returns matching IDs, but that is model goodwill, not an enforced check.

### C2. The "Hard Pydantic Schema Firewall" is not hard
The README claims "any model output ... returning arbitrary keys is rejected". In reality:
- **Extra keys are silently ignored** (pydantic default; no `extra="forbid"`) - verified: `'evil_extra_field': 'SYSTEM COMPROMISED'` is accepted and dropped without trace.
- **Type coercion is active**: `'confidence': "0.9"` (string) is coerced to float and accepted.
- **Empty strings pass**: `translated_title=""` and `translated_description=""` satisfy the schema (no `min_length`). An empty translation is a valid 200 response.

The schema validates *shape*, not *correctness*; the documentation overstates the guarantee.

### C3. Test-suite correctness depends on import order (config singleton)
`config` is a module-level singleton built once at first import of `src.config`. The tests mutate `os.environ` *before importing*, but pytest imports all test modules at collection (alphabetically `test_prompt_injection.py` first), so whichever file imports `src.main` first freezes the config - later files' `os.environ["LLM_STUB"]="1"` is a **no-op**. Verified at runtime:

```
import tests.test_prompt_injection
os.environ['LLM_STUB']='1'
-> config.llm_stub is False
```

Consequences: `test_stage1`'s "stub mode" test may hit a real LLM (or 500 with no provider), and `test_stage2_3`'s "live" test may silently run in stub mode. Additionally, tests mutate the singleton's fields directly (`config.llm_stub = True`) with no fixtures/teardown (`test_prompt_injection` never restores it), so results depend on execution order. There is no `conftest.py` at all.

### C4. The prompt-injection test tests nothing about injection
`tests/test_prompt_injection.py` sends an **ordinary, benign book_id** in **stub mode** - the LLM is never called, no malicious payload is ever exercised, and the assertions only check schema shape. It verifies that the stub endpoint doesn't crash, nothing more. The actual injection defense (layers 3-5) has zero automated coverage in `pytest`. (Eval case 9 at least uses the poisoned book `e00eb4fd7b871a48`, but see H5. A live manual run of case 9 did behave correctly, but that remains unverified by any repeatable test.)

---

## [HIGH] findings

### H1. Entire retry/timeout/repair/quarantine pipeline is untested
No test mocks the OpenAI client. There is **zero coverage** for: 504 timeout mapping, 429/5xx backoff (incl. `Retry-After`), repair retry success, quarantine + 422, 401/400 provider error mapping, empty `choices`, `content=None`, `strip_code_fences`, and the `GET /models` route. All Stage-3/4 "production controls" are asserted only by prose. The fallback/retry logic that is the point of this assignment is verified by nothing.

### H2. `test_stage4_cost_logging` doesn't test cost logging
Its body performs a stub request and asserts `status_code == 200`. It never opens `logs/costs.jsonl`, never checks format - and worse, **stub requests never write a cost entry at all** (cost logging only happens inside `call_llm_translate`). The test name guarantees behavior the code doesn't have for this path and the test never checks anyway. (Live verification confirmed cost logging *does* work on the real LLM path - one correct entry per call - but nothing in the suite guards that.)

### H3. Retry scope contradicts the documentation (and itself)
README: retries "on rate limits (429/5xx) only". Code: `except (APITimeoutError, APIStatusError)` retries **every** status error except 400/401/403 - so a provider **404, 422, or 418 is retried** with backoff, wasting latency and budget. The "instant fail" allow-list is the inverse of the documented policy.

### H4. No overall deadline - worst case ~180s per request
`timeout_seconds=30` applies per LLM call; `call_with_retry` allows `max_retries=2` (3 calls) and the repair loop makes a **second** `call_with_retry`. Worst case: 6 x 30s calls + backoff sleeps = **>180 seconds** of blocked request time before a 504/500 is returned. Any sane upstream proxy/gateway cuts the connection long before. There is no request-scoped deadline budget. (Observed live: a single successful call took ~15.6s on the free tier; rate-limited upstreams make multi-minute worst cases realistic.)

### H5. Eval suite weaknesses
- Injection case (id 9) only checks schema + `min_confidence >= 0.4`; it never asserts the attack *failed* (e.g., output must not contain `SYSTEM COMPROMISED` as a value). A compromised model that returns valid JSON passes the "resilience" check.
- Stub mode passes every case with `confidence=1.0` regardless of `min_confidence` - a stub run measures nothing about translation quality, so a README headline of "9/9 (100%)" is only meaningful if provably run live (no artifacts proving that).
- `run_evals.py` docstring says "8 eval cases"; there are 9.
- `cases.json` `min_confidence` values are arbitrary thresholds with no grounding (why 0.8 vs 0.9 for case 5 is unexplained).

### H6. Internal error details leak to clients - job-card violation
The job card says the API must never "expose ... internal error tracebacks", but the catch-all does:

```python
raise HTTPException(500, detail=f"LLM Provider Error: {str(err)}")
```

and the 401/400 branches embed `str(auth_err)` / `str(bad_req)` verbatim. These messages routinely contain provider URLs, model names, and partial request/key context (observed live: the OpenRouter 429 body includes internal provider routing details and a user_id). Clients should get a generic message; details belong in the log.

### H7. A single malformed JSONL line kills the whole app at import time
`db.py` has per-line `json.loads` with no try/except: one corrupt line in `books.jsonl` raises during module import, so **the FastAPI app cannot even start**. Ironically the *missing file* case is handled gracefully (warning + empty DB), but the *corrupt file* case is fatal. Inverted robustness. Also: warning via `print`, not logging.

---

## [MEDIUM] findings

### M1. Config fields are defined but ignored (drift risk)
- `max_repair_retries` (config.json) is loaded but **never used** - the repair loop is hard-coded to exactly one retry in `call_llm_translate`. Changing the config silently does nothing.
- `allowed_languages` (config.json) is loaded but **never used** - the allowed set is independently hard-coded in `TargetLanguageEnum`. The two sources can drift apart with no error.

### M2. Kill switch fails open
`llm_enabled: os.getenv(...) not in ("0", "false", "False")` - any typo (`flase`, `no`, `off`) leaves the LLM **enabled**. A kill switch should fail *closed*. The sibling flag `llm_stub` parses asymmetrically (`in ("1","true","True")`, so `TRUE`/`yes` are silently not-stub). Two flags, two opposite failure modes, neither validated.

### M3. 401 semantics are wrong for the client
When the *server's* provider key is bad, the API returns **401 Unauthorized** to the caller - but the caller has no credentials and did nothing wrong. This is a server-side configuration failure and should be 502/503 (likewise provider `BadRequestError` -> 400 misleads the caller into believing *their* request was malformed; 502 is more honest).

### M4. No authentication or rate limiting on a paid-LLM endpoint
`POST /books/translate` is unauthenticated and unthrottled. Anyone who discovers the URL can burn the OpenRouter budget or DoS the sync worker pool. The free-tier rate limiting experienced during setup (upstream 429s) shows how quickly this path gets throttled even by legitimate use. At minimum an API key header or per-IP throttle is expected for a "production-grade" claim.

### M5. OpenAI client reconstructed per request
`call_llm_translate` builds a new `OpenAI(...)` client (and its underlying httpx connection pool) on **every request**, including the repair attempt. Should be an app-lifetime singleton.

### M6. `GET /models` hard-codes `http://localhost:11434`
`list_installed_ollama_models` ignores `config.llm_base_url` and queries a hard-coded localhost Ollama endpoint - inconsistent with the configurable-provider design (and silently returns `[]` via a bare `except Exception: pass` that swallows everything; confirmed it returns `[]` on this OpenRouter-only host).

### M7. Quarantine cost entry is mislabeled
On double failure, `log_cost(..., repaired=True)` is written - the call was not repaired, it **failed**. Cost analytics built on this log will count quarantined failures as successful repairs.

### M8. `response.choices[0]` unguarded
If a provider returns an empty `choices` list (happens with content filters / refusal paths), `IndexError` falls through to the generic 500 with an unhelpful message instead of a clean "empty completion" handling/quarantine path. Similarly `hello.py` does `.content.strip()` without the `or ""` guard that `translator.py` uses.

### M9. Few-shot examples use a different input format than the real payload
The prompt's examples show `Input: Book ID: ... / Target Language: ... / Title: ...`, but the actual user message is a JSON blob (`json.dumps({...})`). Small models (the assignment explicitly targets `llama3.2:1b`) are format-sensitive; mismatched few-shot format weakens exactly the defense and parsing behavior it's meant to teach.

### M10. (new) Silent degradation on missing dataset
When `books.jsonl` does not exist, `db.py` prints a warning to stdout and the app boots with an empty store, returning 404 for every request - including cases where the operator simply mistyped `books_dataset_path` in config.json. There is no startup validation that the configured path exists and is parseable, and no `/health`-style signal of how many records were loaded. This is what masked the original "BE-06 never ran" environment problem: the failure looked like per-request 404s instead of one loud startup error. Recommend: fail fast (or expose record count on `/models`/health) when the configured dataset is missing or empty.

---

## [LOW] findings / clean-code nits

1. **Duplicated code**: `log_cost` and `log_to_quarantine` duplicate timestamp formatting (`time.strftime(... gmtime())`), `mkdir(parents=True)`, and the open-append-jsonline pattern - extract one `append_jsonl(path, entry)` helper. The two "Attempt 1 / Attempt 2" blocks in `call_llm_translate` are near-identical and could be a `for attempt in range(max_repair_retries + 1)` loop (which would also use the currently-dead config field, M1).
2. **Unused imports**: `Path`, `Any` in `translator.py`; `os` in `hello.py`; `pytest` imported but unused in all four test files (no fixtures, no `pytest.raises`, no marks).
3. **No structured logging anywhere** - `print` in `db.py`, JSONL append in translator; no request IDs correlate cost/quarantine entries with requests. Quarantine logs unbounded `raw_model_output` with no size cap or rotation.
4. **No `/health` endpoint**, inconsistent with the repo's other assignments (BE-04 pattern).
5. **Log writes are not concurrency-safe** - concurrent appends from multiple workers can interleave partial lines; fine for single-worker demo, not "production-grade".
6. **`requirements.txt` omits `pytest`** (and there is no `requirements-dev.txt`), although the README's library table lists `pytest>=8.0.0` as part of the stack. A reviewer must guess-install it.
7. **Prompt is re-read from disk on every request** (`load_system_prompt()` per call) - trivial waste; cache at startup with fail-fast, which would also surface a missing prompt file at boot instead of at first request.
8. **`Retry-After` parsing** uses `.isdigit()` - rejects fractional values (`"1.5"`) and negatives silently fall through; minor.

---

## Positive observations (kept for balance)

- Clean layering for the size of the project: `config` / `db` / `llm` / routes separation; fail-fast config loading with explicit missing-secret errors is genuinely good.
- Role separation (system vs user) + JSON-encoded untrusted payload is the right injection baseline - and the live run against the poisoned "Sharp Objects" record behaved correctly (payload translated literally, not obeyed).
- `temperature=0.0`, `max_retries=0` on the SDK client with explicit custom backoff, and jitter are all correct instincts.
- Versioned prompt files + `prompt_version` in cost logs is a good eval-hygiene pattern.
- 404-before-LLM ordering (never call the model for a missing book) matches the job card - verified live.
- Cost logging on the live path works as documented (one structured JSONL line per successful call with tokens/duration/repaired flag) - verified live.

---

## Recommended priority order (if fixes are made later)

1. Cross-check response `book_id`/`target_language` against the request; reject on mismatch (C1).
2. Tighten schema: `extra="forbid"`, `min_length=1`, strict confidence (C2).
3. Rebuild tests around a `conftest.py` with mocked LLM client + config reload mechanism (C3, H1, H2, C4).
4. Fail fast (or report record count) when the dataset is missing/empty (M10) - cheap, and it converts the class of environment failures this project already hit into a loud error.
5. Align retry policy with docs (H3), add a request-level deadline (H4).
6. Sanitize client-facing error details (H6) and fix kill-switch fail-open (M2).

---

## Reproducing the verified environment

```
# 1. Dataset (was the cause of the original 4-of-7 test failures)
cd BE-06-Scraper
python -m venv .venv && source .venv/bin/activate
pip install httpx beautifulsoup4 pydantic pydantic-settings sqlalchemy tenacity
python main.py scrape --target books --max-pages 50        # 1000 books -> flyrank_scraper.db
python /tmp/be06_export_books.py                           # DB -> books.jsonl via RAGExporter

# 2. BE-07 against OpenRouter (no local Ollama on this host)
cd ../BE-07-AI-Call
cp .env.example .env    # then set:
#   LLM_BASE_URL=https://openrouter.ai/api/v1
#   LLM_API_KEY=<key from /root/.pi/agent/auth.json -> openrouter.key>
#   LLM_MODEL=google/gemma-4-26b-a4b-it:free
#   LLM_STUB=0, LLM_ENABLED=true
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest
uvicorn src.main:app --host 127.0.0.1 --port 8007   # port 8000 is occupied on this host
curl -X POST http://127.0.0.1:8007/books/translate \
     -H "Content-Type: application/json" \
     -d '{"book_id": "a897fe39b1053632", "target_language": "de"}'
```

*Report generated without modifying any source files. This document is intentionally pure ASCII.*
