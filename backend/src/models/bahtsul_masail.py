from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

# Association tables for many-to-many relationships
document_madhab = Table(
    'document_madhab',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id')),
    Column('madhab_id', Integer, ForeignKey('madhabs.id'))
)

document_category = Table(
    'document_category',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    prolog = Column(Text)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    mushoheh = Column(Text)  # Source verification/authentication
    source_document = Column(String(255))  # Reference document name
    historical_context = Column(Text)
    geographical_context = Column(String(255))
    publication_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    madhabs = relationship('Madhab', secondary=document_madhab, back_populates='documents')
    categories = relationship('Category', secondary=document_category, back_populates='documents')
    chunks = relationship('DocumentChunk', back_populates='document', cascade='all, delete-orphan')

class Madhab(Base):
    __tablename__ = 'madhabs'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    # Relationships
    documents = relationship('Document', secondary=document_madhab, back_populates='madhabs')

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    # Relationships
    documents = relationship('Document', secondary=document_category, back_populates='categories')