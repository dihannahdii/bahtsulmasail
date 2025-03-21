from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import tempfile
import shutil

from database.database import get_db
from services.enhanced_document_service import EnhancedDocumentService
from schemas.bahtsul_masail import Document, DocumentCreate
from schemas.search import SearchParams

router = APIRouter()

@router.post("/api/documents/upload", response_model=Document)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF document with advanced NLP"""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    try:
        # Save uploaded file to temp location
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        
        # Process the document
        document_service = EnhancedDocumentService(db)
        document, insights = document_service.process_pdf_document(temp_file.name)
        
        # Schedule background task to clean up temp file
        background_tasks.add_task(os.unlink, temp_file.name)
        
        return document
    except Exception as e:
        # Clean up temp file in case of error
        os.unlink(temp_file.name)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/documents/batch-upload")
async def batch_upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process multiple PDF documents with advanced NLP"""
    # Validate files
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Process each file
    results = []
    temp_files = []
    
    try:
        for file in files:
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_files.append(temp_file.name)
            
            # Save uploaded file to temp location
            shutil.copyfileobj(file.file, temp_file)
            temp_file.close()
        
        # Process all documents
        document_service = EnhancedDocumentService(db)
        processed_documents = document_service.batch_process_documents(temp_files)
        
        # Format results
        for document, insights in processed_documents:
            results.append({
                "document": document,
                "insights": insights
            })
        
        # Schedule background task to clean up temp files
        for temp_file in temp_files:
            background_tasks.add_task(os.unlink, temp_file)
        
        return {
            "total_processed": len(results),
            "results": results
        }
        
    except Exception as e:
        # Clean up temp files in case of error
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/documents/{document_id}/analyze")
async def analyze_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Perform advanced analysis on an existing document"""
    try:
        document_service = EnhancedDocumentService(db)
        analysis_results = document_service.analyze_document(document_id)
        
        return {
            "document_id": document_id,
            "analysis": analysis_results
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/documents/{document_id}/suggest-classifications")
async def suggest_document_classifications(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Suggest classifications (madhabs and categories) for a document based on content analysis"""
    try:
        document_service = EnhancedDocumentService(db)
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f'Document with id {document_id} not found')
            
        # Combine text for analysis
        text = f"{document.title} {document.prolog or ''} {document.question} {document.answer} {document.mushoheh or ''}"
        
        # Use NLP processor to analyze and suggest classifications
        suggestions = document_service.nlp_processor._suggest_classifications(text)
        
        return {
            "document_id": document_id,
            "suggested_madhabs": suggestions.get('madhabs', []),
            "suggested_categories": suggestions.get('categories', [])
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/documents/{document_id}/extract-references")
async def extract_document_references(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Extract references and citations from a document using advanced NLP"""
    try:
        document_service = EnhancedDocumentService(db)
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f'Document with id {document_id} not found')
            
        # Extract references from document text
        text = f"{document.answer} {document.mushoheh or ''}"
        references = document_service.nlp_processor._extract_references(text)
        
        return {
            "document_id": document_id,
            "references": references
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))