from typing import List, Optional, Dict, Any, cast
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, DateTime, Integer, JSON, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Session
from domain.events.document_events import Event
from database.database import Base

class EventRecord(Base):
    __tablename__ = 'event_store'

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    version = Column(Integer, nullable=False)
    sequence = Column(Integer, nullable=False, default=0)
    aggregate_id = Column(PgUUID(as_uuid=True), nullable=False)
    aggregate_type = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)
    meta_data = Column(JSON, nullable=True)

class EventStore:
    def __init__(self, session: Session):
        self.session = session

    def append_event(self, event: Event) -> None:
        """Append a new event to the event store."""
        event_record = EventRecord(
            id=event.id,
            timestamp=event.timestamp,
            version=event.version,
            aggregate_id=event.aggregate_id,
            aggregate_type=event.aggregate_type,
            event_type=event.event_type,
            data=event.data,
            meta_data=event.metadata
        )
        self.session.add(event_record)
        self.session.commit()

    def get_events_by_aggregate_id(self, aggregate_id: UUID) -> List[EventRecord]:
        """Retrieve all events for a specific aggregate."""
        return self.session.query(EventRecord)\
            .filter(EventRecord.aggregate_id == aggregate_id)\
            .order_by(EventRecord.version)\
            .all()

    def get_events_by_type(self, event_type: str, start_date: Optional[datetime] = None) -> List[EventRecord]:
        """Retrieve all events of a specific type."""
        query = self.session.query(EventRecord)\
            .filter(EventRecord.event_type == event_type)
        
        if start_date:
            query = query.filter(EventRecord.timestamp >= start_date)
            
        return query.order_by(EventRecord.timestamp).all()

    def get_latest_version(self, aggregate_id: UUID) -> int:
        """Get the latest version number for an aggregate."""
        result = self.session.query(EventRecord)\
            .filter(EventRecord.aggregate_id == aggregate_id)\
            .order_by(EventRecord.version.desc())\
            .first()
        return result.version if result else 0

    def get_next_sequence(self) -> int:
        # Fix the return type by explicitly casting the result
        result = self.session.query(func.coalesce(func.max(EventRecord.sequence), 0)).scalar()
        return cast(int, result)