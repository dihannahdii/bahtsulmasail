from typing import Dict, Any, List
from datetime import datetime
from uuid import UUID
from domain.events.document_events import Event

class DocumentProcessingStarted(Event):
    def __init__(self, aggregate_id: UUID, data: Dict[str, Any]):
        super().__init__(
            aggregate_id=aggregate_id,
            aggregate_type='Document',
            event_type='DocumentProcessingStarted',
            data=data
        )

class DocumentChunksGenerated(Event):
    def __init__(self, aggregate_id: UUID, data: Dict[str, Any]):
        super().__init__(
            aggregate_id=aggregate_id,
            aggregate_type='Document',
            event_type='DocumentChunksGenerated',
            data=data
        )

class DocumentEmbeddingsStored(Event):
    def __init__(self, aggregate_id: UUID, data: Dict[str, Any]):
        super().__init__(
            aggregate_id=aggregate_id,
            aggregate_type='Document',
            event_type='DocumentEmbeddingsStored',
            data=data
        )

class DocumentProcessingCompleted(Event):
    def __init__(self, aggregate_id: UUID, data: Dict[str, Any]):
        super().__init__(
            aggregate_id=aggregate_id,
            aggregate_type='Document',
            event_type='DocumentProcessingCompleted',
            data=data
        )

class DocumentProcessingFailed(Event):
    def __init__(self, aggregate_id: UUID, data: Dict[str, Any]):
        super().__init__(
            aggregate_id=aggregate_id,
            aggregate_type='Document',
            event_type='DocumentProcessingFailed',
            data=data
        )