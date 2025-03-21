from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from models.document_chunk import DocumentChunk
from services.logger import logger

class VectorStore:
    def __init__(self, db: Session):
        self.db = db
        self.dimension = 768  # Default dimension for multilingual-mpnet-base-v2

    def store_embeddings(self, document_id: int, chunks: List[Dict[str, Any]]) -> None:
        """Store document chunks with their embeddings"""
        try:
            for chunk in chunks:
                if not chunk.get('embedding'):
                    logger.warning(f"Chunk without embedding for document {document_id}")
                    continue

                doc_chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk['content'],
                    chunk_type=chunk['type'],
                    page_number=chunk.get('page_number'),
                    section_title=chunk.get('section_title'),
                    embedding=chunk['embedding'],
                    metadata=chunk.get('metadata', {})
                )
                self.db.add(doc_chunk)

            self.db.commit()
        except Exception as e:
            logger.error(f"Error storing embeddings for document {document_id}: {str(e)}")
            self.db.rollback()
            raise

    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[DocumentChunk]:
        """Find most similar chunks using cosine similarity"""
        try:
            # Convert query embedding to numpy array
            query_vector = np.array(query_embedding)

            # Get all chunks with embeddings
            chunks = self.db.query(DocumentChunk).filter(DocumentChunk.embedding.isnot(None)).all()
            
            if not chunks:
                return []

            # Calculate similarities
            similarities = []
            for chunk in chunks:
                chunk_vector = np.array(chunk.embedding)
                similarity = self._cosine_similarity(query_vector, chunk_vector)
                similarities.append((chunk, similarity))

            # Sort by similarity and return top matches
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [chunk for chunk, _ in similarities[:limit]]

        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            return []

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        return dot_product / (norm_v1 * norm_v2)

    def delete_document_embeddings(self, document_id: int) -> None:
        """Delete all embeddings for a document"""
        try:
            self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting embeddings for document {document_id}: {str(e)}")
            self.db.rollback()
            raise

    def get_document_chunks(self, document_id: int) -> List[DocumentChunk]:
        """Retrieve all chunks for a document"""
        return self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()