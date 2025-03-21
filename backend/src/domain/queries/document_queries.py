from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

@dataclass
class GetDocumentByIdQuery:
    id: UUID

@dataclass
class ListDocumentsQuery:
    page: int = 1
    page_size: int = 10
    sort_by: str = "created_at"
    sort_order: str = "desc"

@dataclass
class SearchDocumentsQuery:
    query: str
    madhab_ids: Optional[List[UUID]] = None
    category_ids: Optional[List[UUID]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 10

@dataclass
class GetDocumentsByMadhabQuery:
    madhab_id: UUID
    page: int = 1
    page_size: int = 10

@dataclass
class GetDocumentsByCategoryQuery:
    category_id: UUID
    page: int = 1
    page_size: int = 10

@dataclass
class GetDocumentHistoryQuery:
    document_id: UUID
    page: int = 1
    page_size: int = 10

@dataclass
class GetRelatedDocumentsQuery:
    document_id: UUID
    max_results: int = 5
    similarity_threshold: float = 0.7