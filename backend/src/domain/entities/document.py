from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

@dataclass
class Document:
    """Document entity representing a Bahtsul Masail document in our domain."""
    id: UUID = field(default_factory=uuid4)
    title: str
    question: str
    answer: str
    prolog: Optional[str] = None
    mushoheh: Optional[str] = None
    source_document: Optional[str] = None
    historical_context: Optional[str] = None
    geographical_context: Optional[str] = None
    publication_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    madhab_ids: List[UUID] = field(default_factory=list)
    category_ids: List[UUID] = field(default_factory=list)
    version: int = 1

    def update(self, **kwargs) -> None:
        """Update document attributes and increment version."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.version += 1
        self.updated_at = datetime.utcnow()

    def add_madhab(self, madhab_id: UUID) -> None:
        """Add a madhab to the document."""
        if madhab_id not in self.madhab_ids:
            self.madhab_ids.append(madhab_id)
            self.version += 1
            self.updated_at = datetime.utcnow()

    def add_category(self, category_id: UUID) -> None:
        """Add a category to the document."""
        if category_id not in self.category_ids:
            self.category_ids.append(category_id)
            self.version += 1
            self.updated_at = datetime.utcnow()

    def remove_madhab(self, madhab_id: UUID) -> None:
        """Remove a madhab from the document."""
        if madhab_id in self.madhab_ids:
            self.madhab_ids.remove(madhab_id)
            self.version += 1
            self.updated_at = datetime.utcnow()

    def remove_category(self, category_id: UUID) -> None:
        """Remove a category from the document."""
        if category_id in self.category_ids:
            self.category_ids.remove(category_id)
            self.version += 1
            self.updated_at = datetime.utcnow()