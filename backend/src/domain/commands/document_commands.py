from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

@dataclass
class CreateDocumentCommand:
    title: str
    question: str
    answer: str
    prolog: Optional[str] = None
    mushoheh: Optional[str] = None
    source_document: Optional[str] = None
    historical_context: Optional[str] = None
    geographical_context: Optional[str] = None
    publication_date: Optional[datetime] = None
    madhab_ids: List[UUID] = None
    category_ids: List[UUID] = None

@dataclass
class UpdateDocumentCommand:
    id: UUID
    title: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    prolog: Optional[str] = None
    mushoheh: Optional[str] = None
    source_document: Optional[str] = None
    historical_context: Optional[str] = None
    geographical_context: Optional[str] = None
    publication_date: Optional[datetime] = None

@dataclass
class DeleteDocumentCommand:
    id: UUID

@dataclass
class AddMadhabCommand:
    document_id: UUID
    madhab_id: UUID

@dataclass
class RemoveMadhabCommand:
    document_id: UUID
    madhab_id: UUID

@dataclass
class AddCategoryCommand:
    document_id: UUID
    category_id: UUID

@dataclass
class RemoveCategoryCommand:
    document_id: UUID
    category_id: UUID