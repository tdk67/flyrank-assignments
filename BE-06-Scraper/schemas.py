from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BookRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    upc: str = Field(..., description="Unique Product Code")
    title: str = Field(..., description="Cleaned book title")
    category: str = Field(..., description="Genre / Category name")
    price_excl_tax: float = Field(..., description="Price excluding tax")
    price_incl_tax: float = Field(..., description="Price including tax")
    tax: float = Field(..., description="Tax amount")
    currency: str = Field(default="GBP", description="Currency symbol/code")
    availability_status: str = Field(..., description="Stock status text")
    stock_quantity: int = Field(..., description="Number of available copies in stock")
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    description: Optional[str] = Field(default=None, description="Book summary text")
    product_page_url: str = Field(..., description="Canonical product detail page URL")
    cover_image_url: Optional[str] = Field(default=None, description="Cover image absolute URL")


class LeadRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique Lead Identifier (hash or composite key)")
    business_name: str = Field(..., description="Name of the business entity")
    category_industry: Optional[str] = Field(default=None, description="Industry sector / category")
    street_name: str = Field(..., description="Street name")
    house_number: Optional[str] = Field(default=None, description="House / building number")
    postal_code: Optional[str] = Field(default=None, description="German 5-digit postal code")
    city: str = Field(..., description="City or locality")
    phone_number: Optional[str] = Field(default=None, description="Cleaned telephone number")
    website_url: Optional[str] = Field(default=None, description="External business website URL")
    is_business: bool = Field(default=True, description="True if business entity; False if private person")
    raw_json_ld_type: Optional[str] = Field(default=None, description="Raw JSON-LD @type attribute")
    detail_page_url: Optional[str] = Field(default=None, description="Listing page URL")


class DatasetRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_url: str = Field(..., description="Canonical dataset URL")
    dataset_title: str = Field(..., description="Dataset title")
    creator_username: Optional[str] = Field(default=None, description="Dataset creator handle")
    upvotes_count: int = Field(default=0, ge=0, description="Number of upvotes")
    views_count: int = Field(default=0, ge=0, description="Number of views")
    downloads_count: int = Field(default=0, ge=0, description="Number of downloads")
    license_name: Optional[str] = Field(default=None, description="License type")
    summary_description: Optional[str] = Field(default=None, description="Dataset summary text")
    tags: List[str] = Field(default_factory=list, description="Associated topic tags")
    last_updated_date: Optional[str] = Field(default=None, description="ISO date string")


class ScrapeLogRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    target_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_pages_scraped: int = 0
    total_records_extracted: int = 0
    error_count: int = 0
    status: str = "RUNNING"
