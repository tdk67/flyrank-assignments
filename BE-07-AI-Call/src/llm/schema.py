from enum import Enum
from pydantic import BaseModel, Field


class TargetLanguageEnum(str, Enum):
    DE = "de"
    FR = "fr"
    IT = "it"
    EN = "en"


class TranslationRequest(BaseModel):
    book_id: str = Field(..., description="Unique ID or UPC of the book in books.jsonl")
    target_language: TargetLanguageEnum = Field(
        ..., description="Target language ISO code: de (German), fr (French), it (Italian), en (English)"
    )


class TranslationResponse(BaseModel):
    book_id: str
    target_language: TargetLanguageEnum
    translated_title: str
    translated_description: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model self-assessed confidence score between 0.0 and 1.0")
