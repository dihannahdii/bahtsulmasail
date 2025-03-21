from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import os
import PyPDF2
from transformers import pipeline
from torch import Tensor
from .schemas import DocumentCreate
from .logger import logger

class PDFProcessor:
    def __init__(self):
        # Initialize text classification pipeline
        self.classifier = pipeline(
            "text-classification",
            model="bert-base-multilingual-cased",  # Supports Arabic and Indonesian
            return_all_scores=True
        )
        
        # Initialize NER pipeline for metadata extraction
        self.ner = pipeline(
            "token-classification",
            model="bert-base-multilingual-cased",
            aggregation_strategy="simple"
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if len(reader.pages) == 0:
                    logger.error(f"PDF file is empty: {pdf_path}")
                    raise ValueError(f"PDF file is empty: {pdf_path}")
                    
                text = ''
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        text += page_text
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num} in {pdf_path}: {str(e)}")
                        continue
                        
                if not text.strip():
                    logger.error(f"No text content extracted from PDF: {pdf_path}")
                    raise ValueError(f"No text content extracted from PDF: {pdf_path}")
                    
                return text
                
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"Invalid or corrupted PDF file {pdf_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing PDF {pdf_path}: {str(e)}")
            raise

    def classify_text_sections(self, text: str) -> Dict[str, str]:
        if not text or not text.strip():
            logger.error("Empty text provided for classification")
            raise ValueError("Empty text provided for classification")
            
        try:
            chunks = self._split_into_chunks(text)
            
            sections = {
                'prolog': '',
                'question': '',
                'answer': '',
                'mushoheh': '',
                'source_document': ''
            }
            
            for chunk_num, chunk in enumerate(chunks):
                try:
                    # Classify each chunk
                    classification_result = self.classifier(chunk)
                    if classification_result and len(classification_result) > 0:
                        section_type = self._get_highest_scoring_label(classification_result[0])
                        
                        if section_type not in sections:
                            logger.warning(f"Unknown section type '{section_type}' for chunk {chunk_num}")
                            continue
                            
                        sections[section_type] += chunk + '\n'
                except Exception as e:
                    logger.error(f"Failed to classify chunk {chunk_num}: {str(e)}")
                    continue
            
            # Validate that essential sections are present
            if not sections['question'].strip() or not sections['answer'].strip():
                logger.error("Required sections (question/answer) not found in text")
                raise ValueError("Required sections (question/answer) not found in text")
                
            return sections
            
        except Exception as e:
            logger.error(f"Error during text classification: {str(e)}")
            raise

    def extract_metadata(self, text: str) -> Dict[str, Optional[Union[str, datetime]]]:
        entities = self.ner(text)
        
        metadata: Dict[str, Optional[Union[str, datetime]]] = {
            'historical_context': None,
            'geographical_context': None,
            'publication_date': None
        }
        
        # Process recognized entities
        if entities:
            for entity in entities:
                if isinstance(entity, dict) and 'entity_group' in entity and 'word' in entity:
                    if entity['entity_group'] == 'LOC':
                        metadata['geographical_context'] = entity['word']
                    elif entity['entity_group'] == 'DATE':
                        try:
                            metadata['publication_date'] = datetime.strptime(entity['word'], '%Y-%m-%d').date()
                        except ValueError:
                            pass
        
        return metadata

    def _get_highest_scoring_label(self, classifications: List[Dict[str, Any]]) -> str:
        if not classifications:
            raise ValueError("Empty classifications list")
        return max(classifications, key=lambda x: x.get('score', 0))['label']

    def _split_into_chunks(self, text: str, chunk_size: int = 512) -> List[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= chunk_size:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def _extract_title(self, text: str) -> str:
        lines = text.split('\n')
        return lines[0] if lines else ''

    def process_document(self, pdf_path: str) -> DocumentCreate:
        text = self.extract_text_from_pdf(pdf_path)
        sections = self.classify_text_sections(text)
        metadata = self.extract_metadata(text)
        
        return DocumentCreate(
            title=self._extract_title(text),
            prolog=sections['prolog'],
            question=sections['question'],
            answer=sections['answer'],
            mushoheh=sections['mushoheh'],
            source_document=sections['source_document'],
            historical_context=metadata['historical_context'],
            geographical_context=metadata['geographical_context'],
            publication_date=metadata['publication_date'],
            madhab_ids=[],
            category_ids=[]
        )