from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: Optional[str] = None
    madhab_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    semantic_search: bool = False
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class SearchResult(BaseModel):
    id: int
    title: str
    question: str
    answer: str
    prolog: Optional[str] = None
    mushoheh: Optional[str] = None
    historical_context: Optional[str] = None
    geographical_context: Optional[str] = None
    publication_date: Optional[datetime] = None
    madhab_ids: List[int]
    category_ids: List[int]
    score: Optional[float] = None  # For ranking/relevance score

class SearchResponse(BaseModel):
    total: int
    results: List[SearchResult]
    took: float  # Time taken in milliseconds