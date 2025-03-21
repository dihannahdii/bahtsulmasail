from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MadhabBase(BaseModel):
    name: str
    description: Optional[str] = None

class MadhabCreate(MadhabBase):
    pass

class Madhab(MadhabBase):
    id: int

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    prolog: Optional[str] = None
    question: str
    answer: str
    mushoheh: Optional[str] = None
    source_document: Optional[str] = None
    historical_context: Optional[str] = None
    geographical_context: Optional[str] = None
    publication_date: Optional[datetime] = None

class DocumentCreate(DocumentBase):
    madhab_ids: List[int] = []
    category_ids: List[int] = []

class Document(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    madhabs: List[Madhab] = []
    categories: List[Category] = []

    class Config:
        from_attributes = True

class DocumentSearch(BaseModel):
    query: str
    madhab_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None