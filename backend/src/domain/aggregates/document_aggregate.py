from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from ..events.document_events import (
    Event,
    DocumentCreatedEvent,
    DocumentUpdatedEvent,
    DocumentDeletedEvent,
    MadhabAddedEvent,
    CategoryAddedEvent
)

class DocumentAggregate:
    def __init__(self):
        self.id: Optional[UUID] = None
        self.version: int = 0
        self.title: str = ""
        self.prolog: Optional[str] = None
        self.question: str = ""
        self.answer: str = ""
        self.mushoheh: Optional[str] = None
        self.source_document: Optional[str] = None
        self.historical_context: Optional[str] = None
        self.geographical_context: Optional[str] = None
        self.publication_date: Optional[datetime] = None
        self.madhabs: List[UUID] = []
        self.categories: List[UUID] = []
        self.is_deleted: bool = False

    @classmethod
    def create(cls, data: Dict[str, Any]) -> tuple['DocumentAggregate', Event]:
        aggregate = cls()
        aggregate.id = uuid4()
        event = DocumentCreatedEvent(aggregate.id, data)
        aggregate.apply(event)
        return aggregate, event

    def update(self, changes: Dict[str, Any]) -> Event:
        event = DocumentUpdatedEvent(self.id, changes, self.version + 1)
        self.apply(event)
        return event

    def delete(self) -> Event:
        event = DocumentDeletedEvent(self.id, self.version + 1)
        self.apply(event)
        return event

    def add_madhab(self, madhab_id: UUID) -> Event:
        event = MadhabAddedEvent(self.id, madhab_id, self.version + 1)
        self.apply(event)
        return event

    def add_category(self, category_id: UUID) -> Event:
        event = CategoryAddedEvent(self.id, category_id, self.version + 1)
        self.apply(event)
        return event

    def apply(self, event: Event) -> None:
        if isinstance(event, DocumentCreatedEvent):
            self._apply_created(event)
        elif isinstance(event, DocumentUpdatedEvent):
            self._apply_updated(event)
        elif isinstance(event, DocumentDeletedEvent):
            self._apply_deleted(event)
        elif isinstance(event, MadhabAddedEvent):
            self._apply_madhab_added(event)
        elif isinstance(event, CategoryAddedEvent):
            self._apply_category_added(event)

        self.version = event.version

    def _apply_created(self, event: DocumentCreatedEvent) -> None:
        self.id = event.aggregate_id
        self.title = event.data.get('title', '')
        self.prolog = event.data.get('prolog')
        self.question = event.data.get('question', '')
        self.answer = event.data.get('answer', '')
        self.mushoheh = event.data.get('mushoheh')
        self.source_document = event.data.get('source_document')
        self.historical_context = event.data.get('historical_context')
        self.geographical_context = event.data.get('geographical_context')
        self.publication_date = event.data.get('publication_date')

    def _apply_updated(self, event: DocumentUpdatedEvent) -> None:
        for key, value in event.data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _apply_deleted(self, event: DocumentDeletedEvent) -> None:
        self.is_deleted = True

    def _apply_madhab_added(self, event: MadhabAddedEvent) -> None:
        madhab_id = UUID(event.data['madhab_id'])
        if madhab_id not in self.madhabs:
            self.madhabs.append(madhab_id)

    def _apply_category_added(self, event: CategoryAddedEvent) -> None:
        category_id = UUID(event.data['category_id'])
        if category_id not in self.categories:
            self.categories.append(category_id)