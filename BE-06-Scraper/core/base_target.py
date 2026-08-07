import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, List
from schemas import ScrapeLogRecord


class BaseTargetStrategy(ABC):

    @property
    @abstractmethod
    def target_name(self) -> str:
        pass

    def create_scrape_log(self) -> ScrapeLogRecord:
        return ScrapeLogRecord(
            session_id=uuid.uuid4().hex[:12],
            target_name=self.target_name,
            start_time=datetime.now(timezone.utc),
            status="RUNNING"
        )

    def finalize_scrape_log(
        self,
        log: ScrapeLogRecord,
        pages_scraped: int,
        records_extracted: int,
        error_count: int = 0,
        status: str = "COMPLETED"
    ) -> ScrapeLogRecord:
        log.end_time = datetime.now(timezone.utc)
        log.total_pages_scraped = pages_scraped
        log.total_records_extracted = records_extracted
        log.error_count = error_count
        log.status = status
        return log

    @abstractmethod
    async def run(self, max_pages: int = 1, output_file: str | None = None, **kwargs) -> List[Any]:
        pass
