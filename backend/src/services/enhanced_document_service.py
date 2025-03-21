from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from domain.aggregates.document_aggregate import DocumentAggregate
from domain.events.document_events import Event
from infrastructure.event_store.event_store import EventStore
from models.bahtsul_masail import Document, Madhab, Category
from services.advanced_nlp_processor import AdvancedNLPProcessor
from services.enhanced_search import EnhancedSearchService
from services.logger import logger

class EnhancedDocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.event_store = EventStore(db)
        self.nlp_processor = AdvancedNLPProcessor()
        self.search_service = EnhancedSearchService()

    def process_pdf_document(self, pdf_path: str) -> Tuple[Document, Dict[str, Any]]:
        """Process a PDF document with advanced NLP techniques"""
        try:
            # Use the advanced NLP processor to extract and classify document content
            document_create, additional_info = self.nlp_processor.process_document(pdf_path)
            
            # Create the document in the database
            document = self.create_document(document_create.dict())
            
            # Index the document for search
            self.search_service.index_document(document)
            
            return document, additional_info
        except Exception as e:
            logger.error(f"Error processing PDF document {pdf_path}: {str(e)}")
            raise

    def create_document(self, data: Dict[str, Any]) -> Document:
        """Create a document with enhanced metadata"""
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
            geographical_context=data.get('geographical_context'),
            publication_date=data.get('publication_date')
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        # Process madhab_ids if provided
        if 'madhab_ids' in data and data['madhab_ids']:
            for madhab_id in data['madhab_ids']:
                self.add_madhab(document.id, madhab_id)

        # Process category_ids if provided
        if 'category_ids' in data and data['category_ids']:
            for category_id in data['category_ids']:
                self.add_category(document.id, category_id)

        return document

    def update_document(self, document_id: int, changes: Dict[str, Any]) -> Document:
        """Update a document with enhanced metadata handling"""
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

        # Re-index the document for search
        self.search_service.index_document(document)

        return document

    def delete_document(self, document_id: int) -> None:
        """Delete a document and remove from search index"""
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

        # Remove from search index
        try:
            self.search_service.delete_document(document_id)
        except Exception as e:
            logger.warning(f"Failed to remove document {document_id} from search index: {str(e)}")

    def add_madhab(self, document_id: int, madhab_id: int) -> Document:
        """Add a madhab to a document"""
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

        # Re-index the document for search
        self.search_service.index_document(document)

        return document

    def add_category(self, document_id: int, category_id: int) -> Document:
        """Add a category to a document"""
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

        # Re-index the document for search
        self.search_service.index_document(document)

        return document

    def analyze_document(self, document_id: int) -> Dict[str, Any]:
        """Perform advanced analysis on an existing document"""
        # Get the document
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f'Document with id {document_id} not found')

        # Combine all text fields for analysis
        text = f"{document.title} {document.prolog or ''} {document.question} {document.answer} {document.mushoheh or ''}"
        
        # Extract metadata
        metadata = self.nlp_processor.extract_metadata(text)
        
        # Extract additional insights
        insights = self._extract_additional_insights(text)
        
        return {
            'metadata': metadata,
            'insights': insights,
            'suggested_classifications': self.nlp_processor._suggest_classifications(text)
        }
    
    def batch_process_documents(self, pdf_paths: List[str]) -> List[Tuple[Document, Dict[str, Any]]]:
        """Process multiple PDF documents in batch"""
        results = []
        
        for pdf_path in pdf_paths:
            try:
                document, insights = self.process_pdf_document(pdf_path)
                results.append((document, insights))
            except Exception as e:
                logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
                # Continue processing other documents even if one fails
        
        return results
    
    def _extract_additional_insights(self, text: str) -> Dict[str, Any]:
        """Extract additional insights from document text"""
        return {
            'sentiment': self.nlp_processor._analyze_sentiment(text),
            'complexity': self.nlp_processor._analyze_complexity(text),
            'topics': self.nlp_processor._extract_topics(text),
            'related_concepts': self.nlp_processor._extract_related_concepts(text)
        }
    
    def _load_aggregate(self, document_id: UUID) -> DocumentAggregate:
        # Get all events for the document
        events = self.event_store.get_events_by_aggregate_id(document_id)
        
        # Create and hydrate the aggregate
        aggregate = DocumentAggregate()
        for event in events:
            aggregate.apply(event)
            
        return aggregate