from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models.bahtsul_masail import Document
from schemas.bahtsul_masail import DocumentSearch
from datetime import datetime
from typing import List

def search_documents(db: Session, search_params: DocumentSearch) -> List[Document]:
    """
    Advanced search function that supports:
    - Full text search across title, question, and answer
    - Filtering by madhab and category
    - Date range filtering
    - Pagination (to be implemented)
    """
    query = db.query(Document)

    # Full text search
    if search_params.query:
        search_filter = or_(
            Document.title.ilike(f"%{search_params.query}%"),
            Document.question.ilike(f"%{search_params.query}%"),
            Document.answer.ilike(f"%{search_params.query}%"),
            Document.prolog.ilike(f"%{search_params.query}%"),
            Document.mushoheh.ilike(f"%{search_params.query}%"),
            Document.historical_context.ilike(f"%{search_params.query}%"),
            Document.geographical_context.ilike(f"%{search_params.query}%")
        )
        query = query.filter(search_filter)

    # Filter by madhabs
    if search_params.madhab_ids:
        query = query.filter(Document.madhabs.any(id=madhab_id) 
                           for madhab_id in search_params.madhab_ids)

    # Filter by categories
    if search_params.category_ids:
        query = query.filter(Document.categories.any(id=category_id) 
                           for category_id in search_params.category_ids)

    # Date range filter
    date_filters = []
    if search_params.start_date:
        date_filters.append(Document.publication_date >= search_params.start_date)
    if search_params.end_date:
        date_filters.append(Document.publication_date <= search_params.end_date)
    
    if date_filters:
        query = query.filter(and_(*date_filters))

    # Order by relevance (to be improved with proper text search ranking)
    query = query.order_by(Document.publication_date.desc())

    return query.all()