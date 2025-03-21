# This file makes the routes directory a Python package
from .documents import router as documents_router
from .auth import router as auth_router
from .enhanced_documents import router as enhanced_documents_router
from .search import router as search_router