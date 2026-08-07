import json
import os
from typing import Any, List
from schemas import BookRecord, DatasetRecord, LeadRecord


class RAGExporter:

    @staticmethod
    def export_to_jsonl(records: List[Any], file_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            for record in records:
                if isinstance(record, BookRecord):
                    item_data = record.model_dump()
                    text_chunk = (
                        f"Book: {record.title}\n"
                        f"Category: {record.category}\n"
                        f"Rating: {record.rating}/5 stars\n"
                        f"Price: {record.currency} {record.price_incl_tax:.2f} (excl: {record.price_excl_tax:.2f}, tax: {record.tax:.2f})\n"
                        f"Stock: {record.availability_status} ({record.stock_quantity} available)\n"
                        f"UPC: {record.upc}\n"
                        f"Description: {record.description or 'N/A'}"
                    )
                elif isinstance(record, LeadRecord):
                    item_data = record.model_dump()
                    text_chunk = (
                        f"Business Lead: {record.business_name}\n"
                        f"Category/Industry: {record.category_industry or 'General'}\n"
                        f"Address: {record.street_name} {record.house_number or ''}, {record.postal_code or ''} {record.city}\n"
                        f"Phone: {record.phone_number or 'N/A'}\n"
                        f"Website: {record.website_url or 'N/A'}\n"
                        f"Type: {'Business' if record.is_business else 'Private Resident'}"
                    )
                elif isinstance(record, DatasetRecord):
                    item_data = record.model_dump()
                    tags_str = ", ".join(record.tags) if record.tags else "None"
                    text_chunk = (
                        f"Dataset: {record.dataset_title}\n"
                        f"Author: {record.creator_username or 'N/A'}\n"
                        f"Metrics: Upvotes: {record.upvotes_count}, Views: {record.views_count}, Downloads: {record.downloads_count}\n"
                        f"License: {record.license_name or 'N/A'}\n"
                        f"Tags: {tags_str}\n"
                        f"Summary: {record.summary_description or 'N/A'}"
                    )
                else:
                    item_data = record if isinstance(record, dict) else str(record)
                    text_chunk = str(item_data)

                payload = {
                    "id": getattr(record, "upc", getattr(record, "id", getattr(record, "dataset_url", None))),
                    "metadata": item_data,
                    "text_chunk": text_chunk
                }
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")

        return file_path
