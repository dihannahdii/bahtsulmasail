from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import os
import PyPDF2
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification
from sentence_transformers import SentenceTransformer
import torch
from torch import Tensor
from .logger import logger
from schemas.bahtsul_masail import DocumentCreate

class AdvancedNLPProcessor:
    def __init__(self):
        # Initialize text classification pipeline optimized for Indonesian
        self.classifier = pipeline(
            "text-classification",
            model="indolem/indobert-base-uncased",  # Specialized for Indonesian language
            return_all_scores=True
        )
        
        # Initialize NER pipeline with Indonesian-optimized model
        self.ner = pipeline(
            "token-classification",
            model="indolem/indobert-base-uncased-ner",
            aggregation_strategy="simple"
        )
        
        # Initialize sentence transformer with Indonesian support
        self.sentence_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # Initialize tokenizer optimized for Indonesian
        self.tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased")
        
        # Define section labels for fine-grained classification
        self.section_labels = [
            'prolog', 'question', 'answer', 'mushoheh', 'source_document',
            'historical_context', 'geographical_context'
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Enhanced PDF text extraction with better error handling and OCR fallback"""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        try:
            text = self._extract_text_with_pdfplumber(pdf_path)
            if text.strip():
                return text
                
            # If pdfplumber fails, try PyPDF2
            text = self._extract_text_with_pypdf2(pdf_path)
            if text.strip():
                return text
                
            # If both methods fail, try OCR
            text = self._extract_text_with_ocr(pdf_path)
            if text.strip():
                return text
                
            logger.error(f"No text content could be extracted from PDF: {pdf_path}")
            raise ValueError(f"No text content could be extracted from PDF: {pdf_path}")
                
        except Exception as e:
            logger.error(f"Unexpected error processing PDF {pdf_path}: {str(e)}")
            raise

    def _extract_text_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber for better accuracy"""
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ''
                for page in pdf.pages:
                    try:
                        text += page.extract_text() or ''
                    except Exception as e:
                        logger.warning(f"pdfplumber: Failed to extract text from page: {str(e)}")
                return text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
            return ''

    def _extract_text_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 as fallback"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page_num, page in enumerate(reader.pages):
                    try:
                        text += page.extract_text() or ''
                    except Exception as e:
                        logger.warning(f"PyPDF2: Failed to extract text from page {page_num}: {str(e)}")
                return text
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
            return ''

    def _extract_text_with_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR as last resort with enhanced error handling and language support"""
        try:
            import pdf2image
            import pytesseract
            from PIL import Image
            
            # Configure Tesseract for Indonesian language
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            custom_config = r'--oem 3 --psm 6 -l ind'
            
            # Convert PDF to images with optimal DPI
            images = pdf2image.convert_from_path(pdf_path, dpi=300)
            text = ''
            
            for i, image in enumerate(images):
                try:
                    # Preprocess image for better OCR
                    processed_image = self._preprocess_image_for_ocr(image)
                    # Perform OCR with Indonesian language support
                    page_text = pytesseract.image_to_string(processed_image, config=custom_config)
                    if page_text.strip():
                        text += page_text + '\n'
                    else:
                        logger.warning(f"OCR: No text extracted from page {i}")
                except Exception as e:
                    logger.warning(f"OCR: Failed to extract text from page {i}: {str(e)}")
                    continue
                    
            if not text.strip():
                logger.error("OCR: Failed to extract any text from the document")
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ''
            
    def _preprocess_image_for_ocr(self, image: Image) -> Image:
        """Preprocess image to improve OCR accuracy"""
        try:
            # Convert to grayscale
            image = image.convert('L')
            # Increase contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            # Denoise
            from PIL import ImageFilter
            image = image.filter(ImageFilter.MedianFilter())
            return image
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {str(e)}")
            return image

    def preprocess_text(self, text: str) -> str:
        """Preprocess text with Indonesian-specific handling"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
            
        if not text.strip():
            return ""
            
        import re
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Handle common Indonesian abbreviations
        text = re.sub(r'\b(yg|dgn|utk|tsb|dll|dst|sbb|a\.l|d\.l\.l)\b', 
                     lambda m: {'yg': 'yang', 'dgn': 'dengan', 'utk': 'untuk',
                               'tsb': 'tersebut', 'dll': 'dan lain-lain',
                               'dst': 'dan seterusnya', 'sbb': 'sebagai berikut',
                               'a.l': 'antara lain', 'd.l.l': 'dan lain-lain'}[m.group()], 
                     text, flags=re.IGNORECASE)
        
        # Normalize Indonesian diacritics
        text = text.replace('`', '\'')  # Replace backticks with apostrophes
        
        # Remove special characters except punctuation and Indonesian-specific characters
        text = ''.join(char for char in text if char.isalnum() or char.isspace() 
                      or char in '.,;:!?-\'' or char in 'āĀīĪūŪēĒōŌ')
        
        # Normalize multiple punctuation
        text = re.sub(r'([.,;:!?-])\1+', r'\1', text)
        
        # Normalize spaces around punctuation
        text = re.sub(r'\s*([.,;:!?-])\s*', r'\1 ', text)
        
        return text.strip()

    def classify_text_sections(self, text: str) -> Dict[str, str]:
        """Enhanced text section classification using advanced NLP techniques"""
        if not text or not text.strip():
            logger.error("Empty text provided for classification")
            raise ValueError("Empty text provided for classification")
            
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Split into more intelligent chunks based on content
            chunks = self._split_into_semantic_chunks(processed_text)
            
            sections = {label: '' for label in self.section_labels}
            
            # Use sliding window approach for better context awareness
            for i, chunk in enumerate(chunks):
                try:
                    # Get context by including neighboring chunks if available
                    context = ''
                    if i > 0:
                        context += chunks[i-1] + ' '
                    context += chunk
                    if i < len(chunks) - 1:
                        context += ' ' + chunks[i+1]
                    
                    # Classify with context
                    classification_result = self.classifier(chunk)
                    if classification_result and len(classification_result) > 0:
                        # Get top 2 predictions to handle ambiguous sections
                        top_predictions = sorted(classification_result[0], key=lambda x: x.get('score', 0), reverse=True)[:2]
                        
                        # If top prediction is very confident (>0.7), use it
                        if top_predictions[0]['score'] > 0.7:
                            section_type = top_predictions[0]['label']
                        # If top prediction is close to second, use semantic similarity to decide
                        elif len(top_predictions) > 1 and (top_predictions[0]['score'] - top_predictions[1]['score'] < 0.2):
                            section_type = self._resolve_ambiguous_classification(chunk, top_predictions)
                        else:
                            section_type = top_predictions[0]['label']
                        
                        if section_type in sections:
                            sections[section_type] += chunk + '\n'
                        else:
                            logger.warning(f"Unknown section type '{section_type}' for chunk {i}")
                except Exception as e:
                    logger.error(f"Failed to classify chunk {i}: {str(e)}")
                    continue
            
            # Validate that essential sections are present
            if not sections['question'].strip() or not sections['answer'].strip():
                logger.error("Required sections (question/answer) not found in text")
                raise ValueError("Required sections (question/answer) not found in text")
                
            return sections
            
        except Exception as e:
            logger.error(f"Error during text classification: {str(e)}")
            raise

    def extract_metadata(self, text: str) -> Dict[str, Optional[Union[str, date, List[str]]]]:
        """Enhanced metadata extraction with more advanced entity recognition"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
            
        if not text.strip():
            logger.warning("Empty text provided for metadata extraction")
            return self._get_empty_metadata()
            
        try:
            # Preprocess text for better entity recognition
            processed_text = self.preprocess_text(text)
            entities = self.ner(processed_text)
            
            metadata = self._get_empty_metadata()
            
            # Process recognized entities with confidence filtering and deduplication
            locations: Set[str] = set()
            dates: Set[str] = set()
            persons: Set[str] = set()
            organizations: Set[str] = set()
            
            if entities:
                for entity in entities:
                    if not isinstance(entity, dict) or 'entity_group' not in entity or 'word' not in entity:
                        continue
                        
                    # Only consider high-confidence predictions
                    confidence = entity.get('score', 0)
                    if confidence < 0.7:
                        continue
                        
                    word = entity['word'].strip()
                    if not word:
                        continue
                        
                    if entity['entity_group'] == 'LOC':
                        locations.add(word)
                    elif entity['entity_group'] == 'DATE':
                        dates.add(word)
                    elif entity['entity_group'] == 'PER':
                        persons.add(word)
                    elif entity['entity_group'] == 'ORG':
                        organizations.add(word)
            
            # Set geographical context (most frequent location)
            if locations:
                location_counts = Counter(locations)
                metadata['geographical_context'] = location_counts.most_common(1)[0][0]
            
            # Try to parse dates with extended format support
            date_formats = [
                '%Y-%m-%d', '%d %B %Y', '%B %d, %Y',
                '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y',
                '%Y.%m.%d', '%d.%m.%Y'
            ]
            
            for date_text in dates:
                try:
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(date_text, fmt)
                            metadata['publication_date'] = parsed_date
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    logger.warning(f"Failed to parse date {date_text}: {str(e)}")
                    continue
                    
                if metadata['publication_date']:
                    break
            
            # Store unique entities
            metadata['entities'] = list(persons | organizations)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error during metadata extraction: {str(e)}")
            return self._get_empty_metadata()
            
    def _get_empty_metadata(self) -> Dict[str, Optional[Union[str, datetime, List[str]]]]:
        """Return an empty metadata dictionary with proper typing"""
        return {
            'historical_context': None,
            'geographical_context': None,
            'publication_date': None,
            'keywords': [],
            'references': [],
            'entities': []
        }
            
        # Extract historical context from text
        # This is a simplified approach - could be enhanced with more sophisticated methods
        historical_markers = ['during', 'in the era of', 'at the time of', 'period of']
        for marker in historical_markers:
            if marker in text.lower():
                # Find the sentence containing the marker
                sentences = text.split('.')
                for sentence in sentences:
                        if marker in sentence.lower():
                            metadata['historical_context'] = sentence.strip()
                            break
                    if metadata['historical_context']:
                        break
            
            # Store entities for further processing
            metadata['entities'] = persons + organizations
            
            # Extract potential references
            reference_markers = ['kitab', 'book', 'reference', 'according to']
            sentences = text.split('.')
            for sentence in sentences:
                for marker in reference_markers:
                    if marker in sentence.lower():
                        metadata['references'].append(sentence.strip())
                        break
            
            # Extract keywords using TF-IDF or similar techniques
            # This is a placeholder - would need a more sophisticated implementation
            metadata['keywords'] = self._extract_keywords(text)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error during metadata extraction: {str(e)}")
            # Return empty metadata rather than failing completely
            return {
                'historical_context': None,
                'geographical_context': None,
                'publication_date': None,
                'keywords': [],
                'references': [],
                'entities': []
            }

    def _extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        """Extract keywords from text using sentence embeddings"""
        # This is a simplified implementation
        # A more sophisticated approach would use TF-IDF or TextRank
        words = [w for w in text.lower().split() if len(w) > 3]
        word_counts = {}
        for word in words:
            if word not in word_counts:
                word_counts[word] = 0
            word_counts[word] += 1
        
        # Sort by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:num_keywords]]

    def _resolve_ambiguous_classification(self, chunk: str, predictions: List[Dict[str, Any]]) -> str:
        """Resolve ambiguous classification using semantic similarity"""
        # Get embeddings for the chunk
        chunk_embedding = self.sentence_model.encode(chunk)
        
        # Define prototypical examples for each section type
        prototypes = {
            'prolog': "This question arose during the following context...",
            'question': "What is the ruling on...",
            'answer': "The ruling on this matter is...",
            'mushoheh': "This ruling is verified by the following sources...",
            'source_document': "This is referenced in the following books..."
        }
        
        # Get embeddings for prototypes of the top predicted classes
        similarities = {}
        for pred in predictions:
            label = pred['label']
            if label in prototypes:
                prototype_embedding = self.sentence_model.encode(prototypes[label])
                similarity = self._cosine_similarity(chunk_embedding, prototype_embedding)
                similarities[label] = similarity
        
        # Return the label with highest semantic similarity
        if similarities:
            return max(similarities.items(), key=lambda x: x[1])[0]
        else:
            # Fallback to highest score if no prototypes match
            return predictions[0]['label']

    def _cosine_similarity(self, a: Union[np.ndarray, Tensor], b: Union[np.ndarray, Tensor]) -> float:
        """Calculate cosine similarity between two vectors with type checking"""
        if not isinstance(a, (np.ndarray, Tensor)) or not isinstance(b, (np.ndarray, Tensor)):
            raise TypeError("Inputs must be numpy arrays or PyTorch tensors")
            
        try:
            # Convert tensors to numpy if needed
            if isinstance(a, Tensor):
                a = a.detach().cpu().numpy()
            if isinstance(b, Tensor):
                b = b.detach().cpu().numpy()
                
            # Check for NaN or Inf values
            if np.any(np.isnan(a)) or np.any(np.isnan(b)) or \
               np.any(np.isinf(a)) or np.any(np.isinf(b)):
                raise ValueError("Input vectors contain NaN or Inf values")
                
            # Check for zero vectors
            a_norm = np.linalg.norm(a)
            b_norm = np.linalg.norm(b)
            if a_norm == 0 or b_norm == 0:
                return 0.0
                
            similarity = np.dot(a, b) / (a_norm * b_norm)
            
            # Ensure the result is in [-1, 1]
            return float(np.clip(similarity, -1.0, 1.0))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0

    def _split_into_semantic_chunks(self, text: str, max_length: int = 512) -> List[str]:
        """Split text into semantically meaningful chunks"""
        # First try to split by paragraphs
        paragraphs = [p for p in text.split('\n') if p.strip()]
        
        chunks = []
        for paragraph in paragraphs:
            # If paragraph is short enough, keep it as is
            if len(paragraph.split()) <= max_length:
                chunks.append(paragraph)
            else:
                # Otherwise split into sentences
                sentences = [s.strip() + '.' for s in paragraph.split('.') if s.strip()]
                current_chunk = []
                current_length = 0
                
                for sentence in sentences:
                    sentence_length = len(sentence.split())
                    if current_length + sentence_length <= max_length:
                        current_chunk.append(sentence)
                        current_length += sentence_length
                    else:
                        # Add current chunk and start a new one
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                        current_chunk = [sentence]
                        current_length = sentence_length
                
                # Add the last chunk if it exists
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
        
        return chunks

    def _extract_additional_insights(self, text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract additional insights from document content"""
        insights = {}
        
        # Analyze sentiment
        insights['sentiment'] = self._analyze_sentiment(text)
        
        # Analyze complexity
        insights['complexity'] = self._analyze_complexity(text)
        
        # Extract topics
        insights['topics'] = self._extract_topics(text)
        
        # Extract related concepts
        insights['related_concepts'] = self._extract_related_concepts(text)
        
        # Extract references
        insights['references'] = self._extract_references(text)
        
        return insights
        
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of the text"""
        # This is a placeholder - would need a more sophisticated implementation
        # Could use a dedicated sentiment analysis model
        positive_words = ['allowed', 'permissible', 'recommended', 'good', 'beneficial']
        negative_words = ['forbidden', 'prohibited', 'disliked', 'harmful', 'bad']
        
        # Count occurrences of positive and negative words
        positive_count = sum(1 for word in text.lower().split() if word in positive_words)
        negative_count = sum(1 for word in text.lower().split() if word in negative_words)
        total = positive_count + negative_count
        
        if total == 0:
            return {'positive': 0.5, 'negative': 0.5, 'neutral': 1.0}
        
        positive_score = positive_count / total
        negative_score = negative_count / total
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': 1.0 - (positive_score + negative_score)
        }
    
    def _analyze_complexity(self, text: str) -> Dict[str, float]:
        """Analyze the complexity of the text"""
        # Calculate average sentence length
        sentences = [s for s in text.split('.') if s.strip()]
        if not sentences:
            return {'complexity_score': 0.0}
        
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Calculate lexical diversity (unique words / total words)
        words = [w.lower() for w in text.split() if w.strip()]
        if not words:
            return {'complexity_score': 0.0}
        
        lexical_diversity = len(set(words)) / len(words)
        
        # Combine metrics into a complexity score
        complexity_score = (avg_sentence_length / 20) * 0.5 + lexical_diversity * 0.5
        
        return {
            'complexity_score': min(complexity_score, 1.0),
            'avg_sentence_length': avg_sentence_length,
            'lexical_diversity': lexical_diversity
        }
    
    def _extract_topics(self, text: str, num_topics: int = 3) -> List[str]:
        """Extract main topics from the text using TF-IDF and semantic similarity"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
            
        if not text.strip() or num_topics < 1:
            return []
            
        try:
            # Get sentence embeddings for the text
            text_embedding = self.sentence_model.encode(text)
            
            # Extract candidate topics using TF-IDF
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=20, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([text])
            
            # Get top terms by TF-IDF score
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Sort terms by score
            sorted_idx = np.argsort(scores)[::-1]
            candidates = [feature_names[i] for i in sorted_idx[:num_topics * 2]]
            
            # Use semantic similarity to select final topics
            topics = []
            for candidate in candidates:
                # Check semantic similarity with existing topics
                candidate_embedding = self.sentence_model.encode(candidate)
                is_similar = False
                
                for topic in topics:
                    topic_embedding = self.sentence_model.encode(topic)
                    similarity = self._cosine_similarity(candidate_embedding, topic_embedding)
                    if similarity > 0.8:  # High similarity threshold
                        is_similar = True
                        break
                
                if not is_similar:
                    topics.append(candidate)
                    if len(topics) >= num_topics:
                        break
            
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return []
    
    def _extract_related_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Extract concepts related to the document content using semantic similarity"""
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
            
        if not text.strip():
            return []
            
        try:
            # Define Islamic jurisprudence concepts with their markers
            # Get text embedding
            text_embedding = self.sentence_model.encode(text)
            
            # Process each concept
            related_concepts = []
            for concept, markers in concept_markers.items():
                # Get embeddings for markers
                marker_embeddings = [self.sentence_model.encode(marker) for marker in markers]
                
                # Calculate average similarity
                similarities = [self._cosine_similarity(text_embedding, marker_embedding) 
                              for marker_embedding in marker_embeddings]
                avg_similarity = sum(similarities) / len(similarities)
                
                # If average similarity is high enough, consider it related
                if avg_similarity > 0.5:  # Adjustable threshold
                    related_concepts.append({
                        'concept': concept,
                        'confidence': float(avg_similarity),
                        'matched_markers': [markers[i] for i, sim in enumerate(similarities) if sim > 0.6]
                    })
            
            # Sort by confidence
            related_concepts.sort(key=lambda x: x['confidence'], reverse=True)
            
            return related_concepts
            
        except Exception as e:
            logger.error(f"Error extracting related concepts: {str(e)}")
            return []
        
        related = []
        text_lower = text.lower()
        
        for concept, markers in concept_markers.items():
            for marker in markers:
                if marker in text_lower:
                    related.append(concept)
                    break
        
        return related
    
    def _suggest_classifications(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Suggest madhabs and categories based on document content"""
        # Define mappings for classification
        madhab_keywords = {
            'hanafi': ['abu hanifa', 'hanafi', 'kufi'],
            'maliki': ['malik', 'maliki', 'madinah'],
            'shafii': ['shafi', "shafi'i", 'shafiiyah'],
            'hanbali': ['hanbal', 'hanbali', 'ahmad ibn hanbal']
        }
        
        category_keywords = {
            'ibadah': ['prayer', 'worship', 'salat', 'shalat', 'fast', 'fasting', 'zakat', 'hajj'],
            'muamalah': ['transaction', 'business', 'trade', 'sale', 'purchase', 'contract'],
            'nikah': ['marriage', 'wedding', 'spouse', 'dowry', 'mahr'],
            'jinayah': ['crime', 'punishment', 'hudud', 'qisas', 'penalty']
        }
        
        # Process text
        text_lower = text.lower()
        
        # Find madhab matches
        madhab_matches = []
        for madhab, keywords in madhab_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    madhab_matches.append({
                        'name': madhab.capitalize(),
                        'confidence': 0.8,  # Simplified confidence score
                        'matched_term': keyword
                    })
                    break
        
        # Find category matches
        category_matches = []
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    category_matches.append({
                        'name': category.capitalize(),
                        'confidence': 0.8,  # Simplified confidence score
                        'matched_term': keyword
                    })
                    break
        
        return {
            'madhabs': madhab_matches,
            'categories': category_matches
        }
    
    def _extract_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract references and citations from text"""
        references = []
        
        # Look for common reference patterns
        reference_patterns = [
            'kitab', 'book of', 'according to', 'as stated in',
            'as mentioned in', 'reference', 'source', 'citation'
        ]
        
        sentences = text.split('.')
        for sentence in sentences:
            for pattern in reference_patterns:
                if pattern.lower() in sentence.lower():
                    # Extract the reference
                    references.append({
                        'text': sentence.strip(),
                        'type': 'book' if 'kitab' in sentence.lower() or 'book' in sentence.lower() else 'general',
                        'confidence': 0.7  # Simplified confidence score
                    })
                    break
        
        return references
    
    def process_document(self, pdf_path: str) -> Tuple[DocumentCreate, Dict[str, Any]]:
        """Process document with enhanced extraction and classification"""
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        
        # Classify text into sections
        sections = self.classify_text_sections(text)
        
        # Extract metadata
        metadata = self.extract_metadata(text)
        
        # Extract additional insights
        insights = self._extract_additional_insights(text, sections)
        
        # Create document
        document = DocumentCreate(
            title=self._extract_title(text),
            prolog=sections.get('prolog', ''),
            question=sections.get('question', ''),
            answer=sections.get('answer', ''),
            mushoheh=sections.get('mushoheh', ''),
            source_document=sections.get('source_document', ''),