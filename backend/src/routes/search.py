from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database.database import get_db
from services.enhanced_search import EnhancedSearchService
from schemas.search import SearchParams, SearchResponse, SearchResult
import time

router = APIRouter()
search_service = EnhancedSearchService()

@router.post("/api/search", response_model=SearchResponse)
async def search_documents(
    search_params: SearchParams,
    db: Session = Depends(get_db)
) -> SearchResponse:
    """Enhanced search endpoint with support for semantic search and filtering"""
    try:
        # Validate search parameters
        if not search_params.query and not search_params.filters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either search query or filters must be provided"
            )

        start_time = time.time()
        
        try:
            # Perform search
            results = search_service.search_documents(
                search_params=search_params,
                semantic_search=search_params.semantic_search
            )
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Search engine error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Search engine encountered an error"
            )

        if not results:
            return SearchResponse(
                total=0,
                results=[],
                took=0,
                message="No documents found matching the search criteria"
            )
        
        try:
            # Convert results to response model
            search_results = [
                SearchResult(
                    id=doc['id'],
                    title=doc.get('title', ''),
                    question=doc.get('question', ''),
                    answer=doc.get('answer', ''),
                    prolog=doc.get('prolog'),
                    mushoheh=doc.get('mushoheh'),
                    historical_context=doc.get('historical_context'),
                    geographical_context=doc.get('geographical_context'),
                    publication_date=doc.get('publication_date'),
                    madhab_ids=doc.get('madhab_ids', []),
                    category_ids=doc.get('category_ids', []),
                    score=doc.get('_score', 0.0)
                ) for doc in results
            ]
        except KeyError as ke:
            logger.error(f"Malformed search result: {str(ke)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing search results"
            )
        
        # Calculate response time
        took = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return SearchResponse(
            total=len(search_results),
            results=search_results,
            took=took,
            message="Search completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during search"
        )

@router.post("/api/index")
async def index_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Index or reindex a document in Elasticsearch"""
    try:
        # Get document from database
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Index document
        search_service.index_document(document)
        
        return {"status": "success", "message": f"Document {document_id} indexed successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Indexing operation failed: {str(e)}"
        )