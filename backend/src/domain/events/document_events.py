from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

@dataclass
class Event:
    id: UUID
    timestamp: datetime
    version: int
    aggregate_id: UUID
    aggregate_type: str
    event_type: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DocumentCreatedEvent(Event):
    """Event emitted when a new document is created."""
    def __init__(self, document_id: UUID, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            id=UUID(),
            timestamp=datetime.utcnow(),
            version=1,
            aggregate_id=document_id,
            aggregate_type='Document',
            event_type='DocumentCreated',
            data=data,
            metadata=metadata
        )

@dataclass
class DocumentUpdatedEvent(Event):
    """Event emitted when a document is updated."""
    def __init__(self, document_id: UUID, changes: Dict[str, Any], version: int, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            id=UUID(),
            timestamp=datetime.utcnow(),
            version=version,
            aggregate_id=document_id,
            aggregate_type='Document',
            event_type='DocumentUpdated',
            data=changes,
            metadata=metadata
        )

@dataclass
class DocumentDeletedEvent(Event):
    """Event emitted when a document is deleted."""
    def __init__(self, document_id: UUID, version: int, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            id=UUID(),
            timestamp=datetime.utcnow(),
            version=version,
            aggregate_id=document_id,
            aggregate_type='Document',
            event_type='DocumentDeleted',
            data={},
            metadata=metadata
        )

@dataclass
class MadhabAddedEvent(Event):
    """Event emitted when a madhab is added to a document."""
    def __init__(self, document_id: UUID, madhab_id: UUID, version: int, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            id=UUID(),
            timestamp=datetime.utcnow(),
            version=version,
            aggregate_id=document_id,
            aggregate_type='Document',
            event_type='MadhabAdded',
            data={'madhab_id': str(madhab_id)},
            metadata=metadata
        )

@dataclass
class CategoryAddedEvent(Event):
    """Event emitted when a category is added to a document."""
    def __init__(self, document_id: UUID, category_id: UUID, version: int, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            id=UUID(),
            timestamp=datetime.utcnow(),
            version=version,
            aggregate_id=document_id,
            aggregate_type='Document',
            event_type='CategoryAdded',
            data={'category_id': str(category_id)},
            metadata=metadata
        )