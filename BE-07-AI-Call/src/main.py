from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from openai import APITimeoutError, AuthenticationError, PermissionDeniedError, BadRequestError

from src.config import config
from src.db import get_book_by_id, list_installed_ollama_models
from src.llm.schema import TranslationRequest, TranslationResponse
from src.llm.translator import call_llm_translate

app = FastAPI(
    title="BE-07 Book Translation API",
    description="Translates book records using a production-grade LLM pipeline",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Custom 400 validation error handler that names the offending input field."""
    errors = exc.errors()
    first_err = errors[0] if errors else {}
    field_name = "->".join(str(loc) for loc in first_err.get("loc", []))
    msg = first_err.get("msg", "Invalid input value")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Validation error on field '{field_name}': {msg}", "errors": errors},
    )


@app.get("/models")
def get_models():
    """Returns local installed Ollama models and current active env settings."""
    return {
        "active_provider_base_url": config.llm_base_url,
        "active_model": config.llm_model,
        "timeout_seconds": config.timeout_seconds,
        "installed_ollama_models": list_installed_ollama_models(),
    }


@app.post("/books/translate", response_model=TranslationResponse)
def translate_book(req: TranslationRequest):
    # 0. Kill Switch Check (Stage 4 Requirement)
    if not config.llm_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Translation service is currently disabled via kill switch (LLM_ENABLED=false).",
        )

    # 1. Input Validation: Check if book exists in database (Stage 1)
    book = get_book_by_id(req.book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID '{req.book_id}' not found in database.",
        )

    metadata = book.get("metadata", {})
    original_title = metadata.get("title", "Untitled Book")
    original_desc = metadata.get("description", "No description available.")

    # 2. Stub Mode Check (Stage 1)
    if config.llm_stub:
        return TranslationResponse(
            book_id=req.book_id,
            target_language=req.target_language,
            translated_title=f"[STUB-{req.target_language.value.upper()}] {original_title}",
            translated_description=f"[STUB-{req.target_language.value.upper()}] {original_desc}",
            confidence=1.0,
        )

    # 3. Real LLM Translation with Stage 3 & Stage 4 Pipeline
    try:
        response = call_llm_translate(
            book_id=req.book_id,
            title=original_title,
            description=original_desc,
            target_lang=req.target_language.value,
        )
        return response
    except APITimeoutError:
        # Timeout -> HTTP 504 Gateway Timeout
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM model call timed out after {config.timeout_seconds} seconds.",
        )
    except (AuthenticationError, PermissionDeniedError) as auth_err:
        # Bad Key / Unauthorized -> HTTP 401 (Never retried!)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"LLM Provider Authentication Failed: {str(auth_err)}",
        )
    except BadRequestError as bad_req:
        # Bad Request -> HTTP 400 (Never retried!)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LLM Provider Bad Request: {str(bad_req)}",
        )
    except ValueError as val_err:
        # Validation/Repair Failure -> HTTP 422
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM Provider Error: {str(err)}",
        )
