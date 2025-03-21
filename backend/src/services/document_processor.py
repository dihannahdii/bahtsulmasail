from typing import Dict, List, Any, Tuple
from pathlib import Path
import json
import numpy as np
from PIL import Image
import pytesseract
import pdfplumber
from pdf2image import convert_from_path
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from models.document_chunk import DocumentChunk
from services.vector_store import VectorStore
from services.logger import logger

class DocumentProcessor:
    def __init__(self, db: Session):
        # Initialize OCR engine
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.ocr_config = r'--oem 3 --psm 6 -l ind+ara'
        
        # Initialize text embedding model
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        
        # Initialize layout analysis model
        self.layout_classifier = pipeline(
            'text-classification',
            model='microsoft/layoutlm-base-uncased',
            return_all_scores=True
        )
        
        # Initialize vector store
        self.vector_store = VectorStore(db)
        self.db = db
    
    def process_document(self, pdf_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Process document and return metadata and chunks with embeddings"""
        try:
            # Extract text with layout preservation
            pages = self._extract_pages(pdf_path)
            
            # Process document structure
            doc_structure = self._process_document_structure(pages)
            
            # Generate chunks with context preservation
            chunks = self._generate_chunks(doc_structure)
            
            # Generate embeddings for chunks
            chunk_embeddings = self._generate_embeddings(chunks)
            
            return doc_structure['metadata'], chunk_embeddings
            
        except Exception as e:
            logger.error(f"Error processing document {pdf_path}: {str(e)}")
            raise
    
    def _extract_pages(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text and layout from PDF pages"""
        pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text with layout
                    text = page.extract_text()
                    tables = page.extract_tables()
                    
                    # Process tables with OCR if needed
                    processed_tables = self._process_tables(tables)
                    
                    # Extract and process images
                    images = self._extract_images(page)
                    processed_images = self._process_images(images)
                    
                    pages.append({
                        'page_number': page_num,
                        'text': text,
                        'tables': processed_tables,
                        'images': processed_images,
                        'layout': self._analyze_layout(text)
                    })
                    
            return pages
        except Exception as e:
            logger.error(f"Error extracting pages from PDF: {str(e)}")
            raise
    
    def _process_tables(self, tables: List[List[str]]) -> List[Dict[str, Any]]:
        """Process tables with OCR if needed"""
        processed_tables = []
        
        for table in tables:
            # Convert table to structured format
            processed_table = {
                'content': table,
                'metadata': {
                    'rows': len(table),
                    'columns': len(table[0]) if table else 0
                }
            }
            processed_tables.append(processed_table)
            
        return processed_tables
    
    def _extract_images(self, page) -> List[Image.Image]:
        """Extract images from PDF page"""
        try:
            return page.images
        except Exception as e:
            logger.warning(f"Error extracting images: {str(e)}")
            return []
    
    def _process_images(self, images: List[Image.Image]) -> List[Dict[str, Any]]:
        """Process images with OCR"""
        processed_images = []
        
        for image in images:
            try:
                # Perform OCR on image
                text = pytesseract.image_to_string(image, config=self.ocr_config)
                
                processed_images.append({
                    'text': text,
                    'metadata': {
                        'width': image.width,
                        'height': image.height
                    }
                })
            except Exception as e:
                logger.warning(f"Error processing image with OCR: {str(e)}")
                continue
                
        return processed_images
    
    def _analyze_layout(self, text: str) -> Dict[str, Any]:
        """Analyze page layout and structure"""
        try:
            # Classify text blocks by type
            layout_scores = self.layout_classifier(text)
            
            return {
                'structure_type': max(layout_scores[0], key=lambda x: x['score'])['label'],
                'confidence': max(layout_scores[0], key=lambda x: x['score'])['score']
            }
        except Exception as e:
            logger.warning(f"Error analyzing layout: {str(e)}")
            return {'structure_type': 'unknown', 'confidence': 0.0}
    
    def _process_document_structure(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process overall document structure and hierarchy"""
        # Extract document metadata
        metadata = self._extract_metadata(pages)
        
        # Process document hierarchy
        hierarchy = self._process_hierarchy(pages)
        
        return {
            'metadata': metadata,
            'hierarchy': hierarchy,
            'pages': pages
        }
    
    def _extract_metadata(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract document metadata"""
        return {
            'total_pages': len(pages),
            'has_tables': any(page['tables'] for page in pages),
            'has_images': any(page['images'] for page in pages)
        }
    
    def _process_hierarchy(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process document hierarchy (chapters, sections, etc.)"""
        hierarchy = {
            'sections': [],
            'references': []
        }
        
        for page in pages:
            # Analyze text for section headers and references
            sections = self._identify_sections(page['text'])
            references = self._identify_references(page['text'])
            
            hierarchy['sections'].extend(sections)
            hierarchy['references'].extend(references)
        
        return hierarchy
    
    def _generate_chunks(self, doc_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate semantic chunks from document structure"""
        chunks = []
        
        for page in doc_structure['pages']:
            # Process main text
            text_chunks = self._chunk_text(page['text'])
            for chunk in text_chunks:
                chunks.append({
                    'content': chunk,
                    'type': 'text',
                    'page_number': page['page_number'],
                    'metadata': {
                        'layout_type': page['layout']['structure_type']
                    }
                })
            
            # Process tables
            for table in page['tables']:
                chunks.append({
                    'content': json.dumps(table['content']),
                    'type': 'table',
                    'page_number': page['page_number'],
                    'metadata': table['metadata']
                })
            
            # Process images
            for image in page['images']:
                if image['text'].strip():
                    chunks.append({
                        'content': image['text'],
                        'type': 'image',
                        'page_number': page['page_number'],
                        'metadata': image['metadata']
                    })
        
        return chunks
    
    def _generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for document chunks"""
        for chunk in chunks:
            try:
                # Generate embedding for chunk content
                embedding = self.embedding_model.encode(chunk['content'])
                chunk['embedding'] = embedding.tolist()
            except Exception as e:
                logger.warning(f"Error generating embedding for chunk: {str(e)}")
                chunk['embedding'] = None
        
        return chunks
    
    def _chunk_text(self, text: str, max_length: int = 512) -> List[str]:
        """Split text into semantic chunks"""
        # Split text into sentences
        sentences = text.split('.')
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip() + '.'
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > max_length and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify document sections and headers"""
        # Implement section identification logic
        return []
    
    def _identify_references(self, text: str) -> List[Dict[str, Any]]:
        """Identify references and citations"""
        # Implement reference identification logic
        return []