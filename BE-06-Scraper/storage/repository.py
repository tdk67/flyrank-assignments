import json
import logging
from sqlalchemy.orm import Session
from schemas import BookRecord, DatasetRecord, LeadRecord, ScrapeLogRecord
from storage.models import Book, Dataset, Lead, ScrapeLog

logger = logging.getLogger("BE-06-Scraper.Repository")


class Repository:

    def __init__(self, db: Session):
        self.db = db

    def upsert_books(self, books: list[BookRecord]) -> int:
        unique_books = {r.upc: r for r in books}.values()
        saved_count = 0
        try:
            for record in unique_books:
                book_dict = record.model_dump()
                existing = self.db.query(Book).filter(Book.upc == record.upc).first()
                if existing:
                    for k, v in book_dict.items():
                        setattr(existing, k, v)
                else:
                    self.db.add(Book(**book_dict))
                saved_count += 1
            self.db.commit()
            return saved_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during upsert_books: {e}")
            raise e

    def upsert_leads(self, leads: list[LeadRecord]) -> int:
        unique_leads = {r.id: r for r in leads}.values()
        saved_count = 0
        try:
            for record in unique_leads:
                lead_dict = record.model_dump()
                existing = self.db.query(Lead).filter(Lead.id == record.id).first()
                if existing:
                    for k, v in lead_dict.items():
                        setattr(existing, k, v)
                else:
                    self.db.add(Lead(**lead_dict))
                saved_count += 1
            self.db.commit()
            return saved_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during upsert_leads: {e}")
            raise e

    def upsert_datasets(self, datasets: list[DatasetRecord]) -> int:
        unique_datasets = {r.dataset_url: r for r in datasets}.values()
        saved_count = 0
        try:
            for record in unique_datasets:
                ds_dict = record.model_dump()
                tags_list = ds_dict.pop("tags", [])
                ds_dict["tags"] = json.dumps(tags_list)
                existing = self.db.query(Dataset).filter(Dataset.dataset_url == record.dataset_url).first()
                if existing:
                    for k, v in ds_dict.items():
                        setattr(existing, k, v)
                else:
                    self.db.add(Dataset(**ds_dict))
                saved_count += 1
            self.db.commit()
            return saved_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during upsert_datasets: {e}")
            raise e

    def save_scrape_log(self, log_record: ScrapeLogRecord) -> None:
        try:
            log_dict = log_record.model_dump()
            existing = self.db.query(ScrapeLog).filter(ScrapeLog.session_id == log_record.session_id).first()
            if existing:
                for k, v in log_dict.items():
                    setattr(existing, k, v)
            else:
                self.db.add(ScrapeLog(**log_dict))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during save_scrape_log: {e}")
            raise e
