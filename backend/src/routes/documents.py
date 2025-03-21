from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# Mock data for testing
class Madhab(BaseModel):
    id: int
    name: str

class Category(BaseModel):
    id: int
    name: str

class Document(BaseModel):
    id: int
    title: str
    question: str
    answer: str
    prolog: Optional[str] = None
    mushoheh: Optional[str] = None
    source_document: Optional[str] = None
    historical_context: Optional[str] = None
    geographical_context: Optional[str] = None
    publication_date: Optional[datetime] = None
    madhabs: List[Madhab]
    categories: List[Category]

# Mock data
MADHABS = [
    {"id": 1, "name": "Hanafi"},
    {"id": 2, "name": "Maliki"},
    {"id": 3, "name": "Shafi'i"},
    {"id": 4, "name": "Hanbali"}
]

CATEGORIES = [
    {"id": 1, "name": "Ibadah"},
    {"id": 2, "name": "Muamalah"},
    {"id": 3, "name": "Nikah"},
    {"id": 4, "name": "Jinayah"}
]

DOCUMENTS = [
    {
        "id": 1,
        "title": "Hukum Shalat Jumat Virtual",
        "question": "Bagaimana hukum melaksanakan shalat Jumat secara virtual melalui media elektronik seperti zoom atau youtube pada masa pandemi?",
        "answer": "Shalat Jumat secara virtual tidak sah dan tidak dapat menggantikan kewajiban shalat Jumat yang harus dilakukan secara berjamaah di masjid.",
        "prolog": "Pertanyaan ini muncul pada masa pandemi COVID-19",
        "mushoheh": "Kitab I'anah at-Thalibin, Kitab al-Majmu",
        "source_document": "Bahtsul Masail NU 2020",
        "historical_context": "Pandemi COVID-19 2020",
        "geographical_context": "Indonesia",
        "publication_date": "2020-06-15",
        "madhabs": [MADHABS[2]],  # Shafi'i
        "categories": [CATEGORIES[0]]  # Ibadah
    }
]

@router.get("/api/madhabs")
async def get_madhabs():
    return MADHABS

@router.get("/api/categories")
async def get_categories():
    return CATEGORIES

@router.post("/api/documents/search")
async def search_documents(query: str = "", madhab_ids: List[int] = [], category_ids: List[int] = []):
    # Simple mock search implementation
    results = DOCUMENTS
    if query:
        results = [doc for doc in results if query.lower() in doc["title"].lower() or 
                  query.lower() in doc["question"].lower() or 
                  query.lower() in doc["answer"].lower()]
    if madhab_ids:
        results = [doc for doc in results if any(m["id"] in madhab_ids for m in doc["madhabs"])]
    if category_ids:
        results = [doc for doc in results if any(c["id"] in category_ids for c in doc["categories"])]
    return results

@router.get("/api/documents/{document_id}")
async def get_document(document_id: int):
    document = next((doc for doc in DOCUMENTS if doc["id"] == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document