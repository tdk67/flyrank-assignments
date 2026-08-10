import json
import logging
import random
import time
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

import httpx
from openai import OpenAI, APITimeoutError, APIStatusError, AuthenticationError, BadRequestError, PermissionDeniedError
from pydantic import ValidationError

from src.config import config
from src.llm.schema import TranslationResponse

logger = logging.getLogger("be07.translator")

_CACHED_SYSTEM_PROMPT: Optional[str] = None
_CLIENT_INSTANCE: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """Returns application-lifetime OpenAI client instance configured with httpx timeout."""
    global _CLIENT_INSTANCE
    if _CLIENT_INSTANCE is None:
        http_client = httpx.Client(
            timeout=httpx.Timeout(config.timeout_seconds, connect=10.0),
        )
        _CLIENT_INSTANCE = OpenAI(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
            http_client=http_client,
            max_retries=0,  # Handled by custom backoff loop
        )
    return _CLIENT_INSTANCE


def reset_client():
    """Resets client instance on config reload (C3 Fix)."""
    global _CLIENT_INSTANCE, _CACHED_SYSTEM_PROMPT
    _CLIENT_INSTANCE = None
    _CACHED_SYSTEM_PROMPT = None


def load_system_prompt() -> str:
    """Loads and caches system prompt from versioned file specified in config.json."""
    global _CACHED_SYSTEM_PROMPT
    if _CACHED_SYSTEM_PROMPT is None:
        prompt_file = config.resolved_prompt_file_path
        if not prompt_file.exists():
            raise FileNotFoundError(f"System prompt file not found at {prompt_file}")
        with open(prompt_file, "r", encoding="utf-8") as f:
            _CACHED_SYSTEM_PROMPT = f.read()
    return _CACHED_SYSTEM_PROMPT


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


def append_jsonl(filepath: Path, data: Dict[str, Any]):
    """Helper to append structured JSON log lines to a file safely."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")


def log_cost(
    model: str,
    prompt_version: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: float,
    repaired: bool,
    success: bool = True,
):
    """Logs structured cost line to logs/costs.jsonl."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prompt_version": prompt_version,
        "model": model,
        "input_tokens": prompt_tokens,
        "output_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "duration_ms": round(duration_ms, 2),
        "repaired": repaired,
        "success": success,
    }
    append_jsonl(config.resolved_cost_log_path, entry)


def log_to_quarantine(book_id: str, target_lang: str, raw_output: str, error_msg: str):
    """Logs failed responses to logs/quarantine.jsonl."""
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prompt_version": config.prompt_version,
        "book_id": book_id,
        "target_language": target_lang,
        "error": error_msg,
        "raw_model_output": raw_output,
    }
    append_jsonl(config.resolved_quarantine_log_path, log_entry)


def parse_and_validate(
    raw_text: str,
    req_book_id: str,
    req_target_lang: str,
) -> Tuple[Optional[TranslationResponse], Optional[str]]:
    """Strips fences, parses JSON, validates schema, and verifies book_id/target_language match."""
    cleaned = strip_code_fences(raw_text)
    if not cleaned:
        return None, "Empty completion content returned by model"

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return None, f"JSON Decode Error: {str(e)}"

    if not isinstance(data, dict):
        return None, f"JSON output must be an object, got {type(data).__name__}"

    try:
        validated = TranslationResponse.model_validate(data)
    except ValidationError as e:
        return None, f"Pydantic Validation Error: {str(e)}"

    if validated.book_id != req_book_id:
        return None, f"Book ID mismatch: Model returned '{validated.book_id}', expected '{req_book_id}'"

    if validated.target_language.value != req_target_lang:
        return None, f"Target language mismatch: Model returned '{validated.target_language.value}', expected '{req_target_lang}'"

    return validated, None


def call_with_retry(
    client: OpenAI,
    messages: list,
    overall_start_time: float,
) -> Tuple[str, Dict[str, int]]:
    """Calls model with strict overall wall-clock deadline enforcement and backoff on 429/5xx only."""
    max_retries = config.max_network_retries
    for attempt in range(max_retries + 1):
        elapsed_so_far = time.time() - overall_start_time
        remaining_timeout = config.timeout_seconds - elapsed_so_far
        if remaining_timeout <= 0:
            logger.error(f"Overall request timeout deadline reached ({elapsed_so_far:.2f}s >= {config.timeout_seconds}s)")
            raise APITimeoutError(request=None)

        try:
            response = client.chat.completions.create(
                model=config.llm_model,
                messages=messages,
                temperature=0.0,
                timeout=max(0.1, remaining_timeout),
            )

            total_elapsed = time.time() - overall_start_time
            # HARD OVERALL WALL-CLOCK TIMEOUT CHECK:
            if total_elapsed > config.timeout_seconds:
                logger.error(f"Overall request duration ({total_elapsed:.2f}s) exceeded configured timeout ({config.timeout_seconds}s)")
                raise APITimeoutError(request=None)

            if not response.choices:
                raise ValueError("Model provider returned empty choices array")

            choice = response.choices[0]
            raw_text = getattr(choice.message, "content", None) or ""

            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
                "completion_tokens": getattr(response.usage, "completion_tokens", 0) if response.usage else 0,
            }
            return raw_text, usage
        except (AuthenticationError, BadRequestError, PermissionDeniedError) as err:
            raise err
        except (APITimeoutError, APIStatusError) as err:
            is_retriable = isinstance(err, APITimeoutError) or (
                isinstance(err, APIStatusError) and err.status_code in (429, 500, 502, 503, 504)
            )

            if not is_retriable or attempt == max_retries:
                raise err

            retry_after = None
            if isinstance(err, APIStatusError) and err.status_code == 429:
                headers = getattr(err.response, "headers", {})
                retry_after_hdr = headers.get("retry-after") or headers.get("Retry-After")
                if retry_after_hdr:
                    try:
                        retry_after = float(retry_after_hdr)
                    except ValueError:
                        pass

            if retry_after is not None and retry_after > 0:
                sleep_time = min(retry_after, 10.0)
            else:
                sleep_time = (2 ** attempt) + random.uniform(0.0, 0.5)

            if (time.time() - overall_start_time + sleep_time) >= config.timeout_seconds:
                logger.error("Backoff sleep duration would exceed overall request timeout cap")
                raise APITimeoutError(request=None)

            time.sleep(sleep_time)


def call_llm_translate(book_id: str, title: str, description: str, target_lang: str) -> TranslationResponse:
    """Executes LLM translation with Stage 3 & 4 pipeline: overall 30s timeout cap, retries, cost log, repair, quarantine."""
    overall_start_time = time.time()
    client = get_client()
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

    max_repairs = config.max_repair_retries
    current_messages = list(messages)
    last_raw_output = ""
    last_error = ""

    try:
        for repair_attempt in range(max_repairs + 1):
            if (time.time() - overall_start_time) >= config.timeout_seconds:
                logger.error("Overall request timeout deadline reached before repair attempt")
                raise APITimeoutError(request=None)

            raw_output, usage = call_with_retry(client, current_messages, overall_start_time)
            total_prompt_tokens += usage.get("prompt_tokens", 0)
            total_completion_tokens += usage.get("completion_tokens", 0)
            last_raw_output = raw_output

            validated, error_msg = parse_and_validate(raw_output, book_id, target_lang)
            if validated:
                duration_ms = (time.time() - overall_start_time) * 1000.0
                log_cost(
                    config.llm_model,
                    config.prompt_version,
                    total_prompt_tokens,
                    total_completion_tokens,
                    duration_ms,
                    repaired=(repair_attempt > 0),
                    success=True,
                )
                return validated

            last_error = error_msg or "Validation error"

            if repair_attempt < max_repairs:
                repair_instruction = (
                    f"Your previous answer was rejected for this reason: {last_error}\n"
                    f"Original raw answer was:\n{raw_output}\n"
                    f"Return ONLY corrected JSON matching the schema for book_id '{book_id}' and target_language '{target_lang}'."
                )
                current_messages.append({"role": "assistant", "content": raw_output})
                current_messages.append({"role": "user", "content": repair_instruction})

        # --- Quarantine on exhausted repair attempts ---
        duration_ms = (time.time() - overall_start_time) * 1000.0
        log_cost(
            config.llm_model,
            config.prompt_version,
            total_prompt_tokens,
            total_completion_tokens,
            duration_ms,
            repaired=True,
            success=False,
        )
        log_to_quarantine(book_id, target_lang, last_raw_output, f"Validation failed after {max_repairs} repair attempts: {last_error}")
        raise ValueError(f"Model output failed validation after {max_repairs} repair attempt(s): {last_error}")

    except APITimeoutError as timeout_err:
        duration_ms = (time.time() - overall_start_time) * 1000.0
        log_cost(
            config.llm_model,
            config.prompt_version,
            total_prompt_tokens,
            total_completion_tokens,
            duration_ms,
            repaired=False,
            success=False,
        )
        log_to_quarantine(
            book_id,
            target_lang,
            last_raw_output,
            f"LLM model call timed out after {config.timeout_seconds} seconds",
        )
        raise timeout_err
