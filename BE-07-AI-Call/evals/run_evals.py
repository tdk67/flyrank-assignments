import json
import os
import sys
import time
from pathlib import Path
from fastapi.testclient import TestClient

# Reconfigure stdout for UTF-8 on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.main import app

EVAL_CASES_FILE = Path(__file__).resolve().parent / "cases.json"

client = TestClient(app)


def run_evals():
    """Runs all 8 eval cases through the API and prints accuracy report."""
    if not EVAL_CASES_FILE.exists():
        print(f"Error: {EVAL_CASES_FILE} not found!")
        sys.exit(1)

    with open(EVAL_CASES_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print("==================================================")
    print(f"  RUNNING EVAL SUITE ({len(cases)} cases)")
    print(f"  Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: STUB={os.getenv('LLM_STUB', '0')}, ENABLED={os.getenv('LLM_ENABLED', 'true')}")
    print("==================================================")

    passed = 0
    failed_cases = []

    for c in cases:
        case_id = c["id"]
        name = c["name"]
        payload = {
            "book_id": c["book_id"],
            "target_language": c["target_language"],
        }

        start = time.time()
        res = client.post("/books/translate", json=payload)
        elapsed = round((time.time() - start) * 1000, 2)

        if res.status_code != 200:
            print(f"[FAIL] Case {case_id}: {name} -> FAILED (HTTP {res.status_code}: {res.json()})")
            failed_cases.append((case_id, name, f"HTTP {res.status_code}"))
            continue

        data = res.json()

        # Validation assertions
        is_valid = (
            data.get("book_id") == c["book_id"]
            and data.get("target_language") == c["expected_target_lang"]
            and isinstance(data.get("translated_title"), str)
            and isinstance(data.get("translated_description"), str)
            and len(data.get("translated_description", "")) > 0
            and data.get("confidence", 0.0) >= c["min_confidence"]
        )

        if is_valid:
            passed += 1
            print(f"[PASS] Case {case_id}: {name} -> PASSED ({elapsed}ms, conf={data.get('confidence')})")
        else:
            print(f"[FAIL] Case {case_id}: {name} -> FAILED validation checks")
            failed_cases.append((case_id, name, f"Invalid schema response: {data}"))

    total = len(cases)
    score_pct = round((passed / total) * 100, 1)

    print("\n--------------------------------------------------")
    print(f"EVAL SCORE: {passed}/{total} ({score_pct}%)")
    print("--------------------------------------------------")

    if failed_cases:
        print("Failed Cases Detail:")
        for fid, fname, reason in failed_cases:
            print(f"  - [{fid}] {fname}: {reason}")
    else:
        print("All eval test cases passed successfully!")


if __name__ == "__main__":
    run_evals()
