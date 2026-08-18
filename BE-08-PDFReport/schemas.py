from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    app: str = Field(..., json_schema_extra={"example": "BE-08 PDF Report Generator"})
    books_count: int = Field(..., json_schema_extra={"example": 40})


class ReportMetadataResponse(BaseModel):
    id: str = Field(..., description="Unique report identifier")
    report_date: str = Field(..., description="Date string YYYY-MM-DD")
    file: str = Field(..., description="Relative download URL path")
    created_at: str = Field(..., description="Creation timestamp")
    idempotent: bool = Field(False, description="True if served from existing pre-generated report")
