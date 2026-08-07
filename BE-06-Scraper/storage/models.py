from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    upc = Column(String(64), primary_key=True)
    title = Column(String(512), nullable=False)
    category = Column(String(128), nullable=False, index=True)
    price_excl_tax = Column(Numeric(10, 2), nullable=False)
    price_incl_tax = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(8), nullable=False, default="GBP")
    availability_status = Column(String(64), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False, index=True)
    description = Column(Text, nullable=True)
    product_page_url = Column(String(1024), nullable=False)
    cover_image_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String(128), primary_key=True)
    business_name = Column(String(256), nullable=False)
    category_industry = Column(String(128), nullable=True)
    street_name = Column(String(128), nullable=False)
    house_number = Column(String(32), nullable=True)
    postal_code = Column(String(16), nullable=True)
    city = Column(String(128), nullable=False)
    phone_number = Column(String(64), nullable=True)
    website_url = Column(String(512), nullable=True)
    is_business = Column(Boolean, nullable=False, default=True, index=True)
    raw_json_ld_type = Column(String(128), nullable=True)
    detail_page_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Dataset(Base):
    __tablename__ = "datasets"

    dataset_url = Column(String(512), primary_key=True)
    dataset_title = Column(String(256), nullable=False, index=True)
    creator_username = Column(String(128), nullable=True)
    upvotes_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    downloads_count = Column(Integer, default=0)
    license_name = Column(String(128), nullable=True)
    summary_description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    last_updated_date = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    session_id = Column(String(64), primary_key=True)
    target_name = Column(String(64), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    end_time = Column(DateTime(timezone=True), nullable=True)
    total_pages_scraped = Column(Integer, default=0)
    total_records_extracted = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    status = Column(String(32), nullable=False, default="RUNNING")
