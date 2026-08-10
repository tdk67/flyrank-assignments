import json
import random
import time
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from openai import OpenAI, APITimeoutError, APIStatusError, AuthenticationError, BadRequestError, PermissionDeniedError
from pydantic import ValidationError

from src.config import config
from src.llm.schema import TranslationResponse


def load_system_prompt() -> str:
    """Loads system prompt from versioned file specified in config.json."""
    prompt_file = config.resolved_prompt_file_path
    if not prompt_file.exists():
        raise FileNotFoundError(f"System prompt file not found at {prompt_file}")
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read()


def strip_code_fences(text: str) -> str:
    """Strips markdown code fences (e.g., ```json ... ```) from LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def log_cost(
    model: str,
    prompt_version: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: float,
    repaired: bool,
):
    """Logs structured cost line to configured cost log file."""
    cost_log_file = config.resolved_cost_log_path
    cost_log_file.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prompt_version": prompt_version,
        "model": model,
        "input_tokens": prompt_tokens,
        "output_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "duration_ms": round(duration_ms, 2),
        "repaired": repaired,
    }
    with open(cost_log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def log_to_quarantine(book_id: str, target_lang: str, raw_output: str, error_msg: str):
    """Logs failed responses to configured quarantine log file."""
    quarantine_log_file = config.resolved_quarantine_log_path
    quarantine_log_file.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prompt_version": config.prompt_version,
        "book_id": book_id,
        "target_language": target_lang,
        "error": error_msg,
        "raw_model_output": raw_output,
    }
    with open(quarantine_log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


def parse_and_validate(raw_text: str) -> Tuple[Optional[TranslationResponse], Optional[str]]:
    """Strips fences, parses JSON, and validates against Pydantic schema."""
    cleaned = strip_code_fences(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return None, f"JSON Decode Error: {str(e)}"

    try:
        validated = TranslationResponse.model_validate(data)
        return validated, None
    except ValidationError as e:
        return None, f"Pydantic Validation Error: {str(e)}"


def call_with_retry(client: OpenAI, messages: list) -> Tuple[str, Dict[str, int]]:
    """Calls model with configurable timeout, exponential backoff + jitter on 429/5xx, and instant fail on 400/401/403."""
    max_retries = config.max_network_retries
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=config.llm_model,
                messages=messages,
                temperature=0.0,
                timeout=config.timeout_seconds,
            )
            raw_text = response.choices[0].message.content or ""
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
                "completion_tokens": getattr(response.usage, "completion_tokens", 0) if response.usage else 0,
            }
            return raw_text, usage
        except (AuthenticationError, BadRequestError, PermissionDeniedError) as err:
            # Immediate fail: Never retry on 400, 401, 403!
            raise err
        except (APITimeoutError, APIStatusError) as err:
            if attempt == max_retries:
                raise err
            # Check for Retry-After header on 429
            retry_after = None
            if isinstance(err, APIStatusError) and err.status_code == 429:
                headers = getattr(err.response, "headers", {})
                retry_after_hdr = headers.get("retry-after") or headers.get("Retry-After")
                if retry_after_hdr and retry_after_hdr.isdigit():
                    retry_after = float(retry_after_hdr)

            if retry_after is not None:
                sleep_time = retry_after
            else:
                # Exponential backoff with jitter: 1s, 2s, 4s + random(0, 0.5)
                sleep_time = (2 ** attempt) + random.uniform(0.0, 0.5)
            time.sleep(sleep_time)


def call_llm_translate(book_id: str, title: str, description: str, target_lang: str) -> TranslationResponse:
    """Executes LLM translation with Stage 3 & 4 pipeline: timeout, retries, cost log, repair, quarantine."""
    start_time = time.time()
    client = OpenAI(
        base_url=config.llm_base_url,
        api_key=config.llm_api_key,
        timeout=config.timeout_seconds,
        max_retries=0,  # Explicitly handled by custom backoff loop
    )
    system_prompt = load_system_prompt()

    user_payload = json.dumps({
        "book_id": book_id,
        "target_language": target_lang,
        "title": title,
        "description": description,
    }, ensure_ascii=False)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_payload},
    ]

    total_prompt_tokens = 0
    total_completion_tokens = 0

    # --- Attempt 1 ---
    raw_output1, usage1 = call_with_retry(client, messages)
    total_prompt_tokens += usage1.get("prompt_tokens", 0)
    total_completion_tokens += usage1.get("completion_tokens", 0)

    validated_res1, error1 = parse_and_validate(raw_output1)

    if validated_res1:
        duration_ms = (time.time() - start_time) * 1000.0
        log_cost(config.llm_model, config.prompt_version, total_prompt_tokens, total_completion_tokens, duration_ms, repaired=False)
        return validated_res1

    # --- Attempt 2: Repair Retry (Once and only once) ---
    repair_instruction = (
        f"Your previous answer was rejected for this reason: {error1}\n"
        f"Original raw answer was:\n{raw_output1}\n"
        f"Return ONLY corrected JSON matching the schema."
    )
    repair_messages = list(messages) + [
        {"role": "assistant", "content": raw_output1},
        {"role": "user", "content": repair_instruction},
    ]

    raw_output2, usage2 = call_with_retry(client, repair_messages)
    total_prompt_tokens += usage2.get("prompt_tokens", 0)
    total_completion_tokens += usage2.get("completion_tokens", 0)

    validated_res2, error2 = parse_and_validate(raw_output2)

    if validated_res2:
        duration_ms = (time.time() - start_time) * 1000.0
        log_cost(config.llm_model, config.prompt_version, total_prompt_tokens, total_completion_tokens, duration_ms, repaired=True)
        return validated_res2

    # --- Quarantine on double failure ---
    duration_ms = (time.time() - start_time) * 1000.0
    log_cost(config.llm_model, config.prompt_version, total_prompt_tokens, total_completion_tokens, duration_ms, repaired=True)
    log_to_quarantine(book_id, target_lang, raw_output2, f"Attempt 1 err: {error1} | Attempt 2 err: {error2}")
    raise ValueError(f"Model output failed validation after 1 repair attempt: {error2}")
