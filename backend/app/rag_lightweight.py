"""
RAG Pipeline - Lightweight TF-IDF based retrieval for Render free tier
No PyTorch, no heavy ML models - just efficient text matching
"""

import os
from typing import List, Tuple, Optional
from pathlib import Path
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class Document:
    """Simple document class."""
    def __init__(self, content: str, metadata: dict = None):
        self.page_content = content
        self.metadata = metadata or {}


class RAGPipeline:
    """
    Lightweight RAG Pipeline using TF-IDF for retrieval.
    Memory efficient - works within 512MB RAM limit.
    """
    
    def __init__(self, data_directory: str = None):
        self.data_directory = data_directory or os.path.join(
            os.path.dirname(__file__), "..", "data"
        )
        self.vectorizer = None
        self.tfidf_matrix = None
        self.documents = []
        self.chunks = []
        
    async def initialize(self):
        """Initialize the RAG pipeline - load documents and create TF-IDF index."""
        print(f"📂 Loading documents from {self.data_directory}")
        
        # Load documents
        self.documents = self._load_documents()
        
        if not self.documents:
            print("⚠️ No documents found. Creating default knowledge base.")
            self.documents = self._create_default_documents()
        
        # Split documents into chunks
        self.chunks = self._split_documents(self.documents)
        print(f"📄 Created {len(self.chunks)} document chunks")
        
        # Create TF-IDF index
        self._create_tfidf_index()
        print("✅ TF-IDF index created successfully")
        
    def _load_documents(self) -> List[Document]:
        """Load documents from the data directory."""
        documents = []
        data_path = Path(self.data_directory)
        
        if not data_path.exists():
            print(f"⚠️ Data directory not found: {self.data_directory}")
            return documents
        
        # Load Markdown files
        md_files = list(data_path.glob("**/*.md"))
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                doc = Document(content=content, metadata={"source": md_file.name})
                documents.append(doc)
                print(f"  ✓ Loaded: {md_file.name}")
            except Exception as e:
                print(f"  ✗ Error loading {md_file.name}: {e}")
        
        # Load Text files
        txt_files = list(data_path.glob("**/*.txt"))
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                doc = Document(content=content, metadata={"source": txt_file.name})
                documents.append(doc)
                print(f"  ✓ Loaded: {txt_file.name}")
            except Exception as e:
                print(f"  ✗ Error loading {txt_file.name}: {e}")
        
        print(f"📚 Loaded {len(documents)} documents total")
        return documents
    
    def _create_default_documents(self) -> List[Document]:
        """Create default documents if none exist."""
        default_content = """
        # Shashi Bhushan Jha - AI Engineer Portfolio
        
        ## About
        AI/ML Engineer specializing in deep learning, NLP, and computer vision.
        Currently pursuing M.Tech at IIT Ropar.
        
        ## Skills
        - Python, TensorFlow, PyTorch
        - Machine Learning, Deep Learning
        - Natural Language Processing
        - Computer Vision
        - Signal Processing
        
        ## Contact
        - Email: bhushan.gate2022@gmail.com
        - Location: India
        """
        return [Document(content=default_content, metadata={"source": "default"})]
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks."""
        chunks = []
        chunk_size = 500
        chunk_overlap = 100
        
        for doc in documents:
            text = doc.page_content
            
            # Simple text splitting by paragraphs first, then by size
            paragraphs = text.split('\n\n')
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append(Document(
                            content=current_chunk.strip(),
                            metadata=doc.metadata.copy()
                        ))
                    current_chunk = para + "\n\n"
            
            # Don't forget the last chunk
            if current_chunk.strip():
                chunks.append(Document(
                    content=current_chunk.strip(),
                    metadata=doc.metadata.copy()
                ))
        
        return chunks
    
    def _create_tfidf_index(self):
        """Create TF-IDF vectorizer and matrix."""
        texts = [chunk.page_content for chunk in self.chunks]
        
        self.vectorizer = TfidfVectorizer(
            max_features=5000,  # Limit features to save memory
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            min_df=1,
            max_df=0.95
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        print(f"  TF-IDF matrix shape: {self.tfidf_matrix.shape}")
    
    async def retrieve(self, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        """
        Retrieve top-k most relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of (document, score) tuples
        """
        if self.vectorizer is None or self.tfidf_matrix is None:
            return []
        
        # Transform query to TF-IDF vector
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top-k indices
        top_k_indices = similarities.argsort()[-k:][::-1]
        
        results = []
        for idx in top_k_indices:
            if similarities[idx] > 0.01:  # Only include if there's some similarity
                results.append((self.chunks[idx], float(similarities[idx])))
        
        return results
    
    async def get_context(self, query: str, k: int = 3) -> str:
        """
        Get formatted context for a query.
        
        Args:
            query: User's question
            k: Number of context chunks to retrieve
            
        Returns:
            Formatted context string
        """
        results = await self.retrieve(query, k)
        
        if not results:
            return "No relevant context found in knowledge base."
        
        context_parts = []
        for doc, score in results:
            source = doc.metadata.get("source", "unknown")
            context_parts.append(f"[Source: {source}]\n{doc.page_content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_all_sources(self) -> List[str]:
        """Get list of all document sources."""
        sources = set()
        for doc in self.documents:
            source = doc.metadata.get("source", "unknown")
            sources.add(source)
        return list(sources)
