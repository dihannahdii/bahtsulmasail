from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.bahtsul_masail import Document
from schemas.bahtsul_masail import DocumentSearch
from sqlalchemy.orm import Session
import os

class EnhancedSearchService:
    def __init__(self):
        # Initialize Elasticsearch client
        self.es = Elasticsearch([os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')])
        # Initialize BERT model for Indonesian/Arabic text
        self.bert_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        
        # Create index if not exists
        if not self.es.indices.exists(index='documents'):
            self.es.indices.create(
                index='documents',
                body={
                    'settings': {
                        'analysis': {
                            'analyzer': {
                                'arabic_indonesian': {
                                    'type': 'custom',
                                    'tokenizer': 'standard',
                                    'filter': [
                                        'lowercase',
                                        'arabic_normalization',
                                        'indonesian_stop',
                                        'indonesian_stemmer'
                                    ]
                                }
                            },
                            'filter': {
                                'indonesian_stop': {
                                    'type': 'stop',
                                    'stopwords': '_indonesian_'
                                },
                                'indonesian_stemmer': {
                                    'type': 'stemmer',
                                    'language': 'indonesian'
                                }
                            }
                        }
                    },
                    'mappings': {
                        'properties': {
                            'title': {'type': 'text', 'analyzer': 'arabic_indonesian'},
                            'question': {'type': 'text', 'analyzer': 'arabic_indonesian'},
                            'answer': {'type': 'text', 'analyzer': 'arabic_indonesian'},
                            'prolog': {'type': 'text', 'analyzer': 'arabic_indonesian'},
                            'mushoheh': {'type': 'text', 'analyzer': 'arabic_indonesian'},
                            'historical_context': {'type': 'text', 'analyzer': 'arabic_indonesian'},
                            'geographical_context': {'type': 'text', 'analyzer': 'arabic_indonesian'},
                            'publication_date': {'type': 'date'},
                            'madhab_ids': {'type': 'integer'},
                            'category_ids': {'type': 'integer'},
                            'text_embedding': {'type': 'dense_vector', 'dims': 768}
                        }
                    }
                }
            )
    
    def index_document(self, document: Document) -> None:
        """Index a document in Elasticsearch with BERT embeddings"""
        # Generate text embedding
        text_for_embedding = f"{document.title} {document.question} {document.answer}"
        embedding = self.bert_model.encode(text_for_embedding)
        
        # Prepare document for indexing
        doc = {
            'title': document.title,
            'question': document.question,
            'answer': document.answer,
            'prolog': document.prolog,
            'mushoheh': document.mushoheh,
            'historical_context': document.historical_context,
            'geographical_context': document.geographical_context,
            'publication_date': document.publication_date,
            'madhab_ids': [m.id for m in document.madhabs],
            'category_ids': [c.id for c in document.categories],
            'text_embedding': embedding.tolist()
        }
        
        self.es.index(index='documents', id=str(document.id), body=doc)
    
    def search_documents(self, search_params: DocumentSearch, semantic_search: bool = False) -> List[Dict[str, Any]]:
        """Enhanced search with both text-based and semantic search capabilities"""
        # Build base query
        query = {
            'bool': {
                'must': [],
                'filter': []
            }
        }
        
        if search_params.query:
            if semantic_search:
                # Semantic search using BERT embeddings
                query_embedding = self.bert_model.encode(search_params.query)
                query['bool']['must'].append({
                    'script_score': {
                        'query': {'match_all': {}},
                        'script': {
                            'source': "cosineSimilarity(params.query_vector, 'text_embedding') + 1.0",
                            'params': {'query_vector': query_embedding.tolist()}
                        }
                    }
                })
            else:
                # Text-based search with fuzzy matching
                query['bool']['must'].append({
                    'multi_match': {
                        'query': search_params.query,
                        'fields': ['title^3', 'question^2', 'answer', 'prolog', 'mushoheh', 
                                  'historical_context', 'geographical_context'],
                        'fuzziness': 'AUTO'
                    }
                })
        
        # Add filters
        if search_params.madhab_ids:
            query['bool']['filter'].append({'terms': {'madhab_ids': search_params.madhab_ids}})
        
        if search_params.category_ids:
            query['bool']['filter'].append({'terms': {'category_ids': search_params.category_ids}})
        
        if search_params.start_date or search_params.end_date:
            date_filter = {'range': {'publication_date': {}}}
            if search_params.start_date:
                date_filter['range']['publication_date']['gte'] = search_params.start_date
            if search_params.end_date:
                date_filter['range']['publication_date']['lte'] = search_params.end_date
            query['bool']['filter'].append(date_filter)
        
        # Execute search
        results = self.es.search(
            index='documents',
            body={
                'query': query,
                'size': search_params.limit if hasattr(search_params, 'limit') else 10,
                'from': search_params.offset if hasattr(search_params, 'offset') else 0
            }
        )
        
        return [hit['_source'] for hit in results['hits']['hits']]