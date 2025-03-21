from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from domain.aggregates.document_aggregate import DocumentAggregate
from infrastructure.event_store.event_store import EventStore
from models.bahtsul_masail import Document, Madhab, Category

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.event_store = EventStore(db)

    def create_document(self, data: Dict[str, Any]) -> Document:
        # Create document aggregate and event
        aggregate, event = DocumentAggregate.create(data)

        # Store the event
        self.event_store.append_event(event)

        # Create and persist the document
        document = Document(
            title=data['title'],
            prolog=data.get('prolog'),
            question=data['question'],
            answer=data['answer'],
            mushoheh=data.get('mushoheh'),
            source_document=data.get('source_document'),
            historical_context=data.get('historical_context'),
            geographical_context=data.get('geographical_context')
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def update_document(self, document_id: int, changes: Dict[str, Any]) -> Document:
        # Get the document
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f'Document with id {document_id} not found')

        # Create and store the event
        aggregate = self._load_aggregate(UUID(str(document_id)))
        event = aggregate.update(changes)
        self.event_store.append_event(event)

        # Update the document
        for key, value in changes.items():
            if hasattr(document, key):
                setattr(document, key, value)

        self.db.commit()
        self.db.refresh(document)

        return document

    def delete_document(self, document_id: int) -> None:
        # Get the document
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f'Document with id {document_id} not found')

        # Create and store the event
        aggregate = self._load_aggregate(UUID(str(document_id)))
        event = aggregate.delete()
        self.event_store.append_event(event)

        # Delete the document
        self.db.delete(document)
        self.db.commit()

    def add_madhab(self, document_id: int, madhab_id: int) -> Document:
        # Get the document and madhab
        document = self.db.query(Document).filter(Document.id == document_id).first()
        madhab = self.db.query(Madhab).filter(Madhab.id == madhab_id).first()
        if not document or not madhab:
            raise ValueError('Document or Madhab not found')

        # Create and store the event
        aggregate = self._load_aggregate(UUID(str(document_id)))
        event = aggregate.add_madhab(UUID(str(madhab_id)))
        self.event_store.append_event(event)

        # Add madhab to document
        document.madhabs.append(madhab)
        self.db.commit()
        self.db.refresh(document)

        return document

    def add_category(self, document_id: int, category_id: int) -> Document:
        # Get the document and category
        document = self.db.query(Document).filter(Document.id == document_id).first()
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not document or not category:
            raise ValueError('Document or Category not found')

        # Create and store the event
        aggregate = self._load_aggregate(UUID(str(document_id)))
        event = aggregate.add_category(UUID(str(category_id)))
        self.event_store.append_event(event)

        # Add category to document
        document.categories.append(category)
        self.db.commit()
        self.db.refresh(document)

        return document

    def _load_aggregate(self, document_id: UUID) -> DocumentAggregate:
        # Get all events for the document
        events = self.event_store.get_events_by_aggregate_id(document_id)
        
        # Create and hydrate the aggregate
        aggregate = DocumentAggregate()
        for event in events:
            aggregate.apply(event)
            
        return aggregate