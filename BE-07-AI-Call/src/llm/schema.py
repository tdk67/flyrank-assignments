from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TargetLanguageEnum(str, Enum):
    DE = "de"
    FR = "fr"
    IT = "it"
    EN = "en"


class TranslationRequest(BaseModel):
    book_id: str = Field(..., min_length=1, description="Unique ID or UPC of the book in books.jsonl")
    target_language: TargetLanguageEnum = Field(
        ..., description="Target language ISO code: de (German), fr (French), it (Italian), en (English)"
    )


class TranslationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    book_id: str = Field(..., min_length=1, description="Must match the requested book_id")
    target_language: TargetLanguageEnum = Field(..., description="Must match the requested target_language")
    translated_title: str = Field(..., min_length=1, description="Non-empty translated book title")
    translated_description: str = Field(..., min_length=1, description="Non-empty translated book description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model self-assessed confidence score between 0.0 and 1.0")
