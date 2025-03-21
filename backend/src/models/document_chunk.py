from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    content = Column(Text, nullable=False)
    chunk_type = Column(String(50))  # text, table, figure, etc.
    page_number = Column(Integer)
    section_title = Column(String(255))
    embedding = Column(ARRAY(Float))  # Store vector embeddings
    metadata = Column(Text)  # JSON field for additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship('Document', back_populates='chunks')