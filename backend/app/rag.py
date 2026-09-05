"""
RAG Pipeline - Retrieval Augmented Generation for context-aware responses
"""

import os
from typing import List, Tuple, Optional
from pathlib import Path

from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


class RAGPipeline:
    """
    RAG Pipeline for retrieving relevant context from knowledge base.
    """
    
    def __init__(self, data_directory: str = None):
        self.data_directory = data_directory or os.path.join(
            os.path.dirname(__file__), "..", "data"
        )
        self.vector_store = None
        self.embeddings = None
        self.documents = []
        
    async def initialize(self):
        """Initialize the RAG pipeline - load documents and create vector store."""
        print(f"📂 Loading documents from {self.data_directory}")
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()
        
        # Load documents
        self.documents = self._load_documents()
        
        if not self.documents:
            print("⚠️ No documents found. Creating default knowledge base.")
            self.documents = self._create_default_documents()
        
        # Split documents into chunks
        chunks = self._split_documents(self.documents)
        print(f"📄 Created {len(chunks)} document chunks")
        
        # Create vector store
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        print("✅ Vector store created successfully")
        
    def _initialize_embeddings(self):
        """Initialize embeddings model."""
        
        # Try OpenAI embeddings first
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            print("🔷 Using OpenAI Embeddings")
            return OpenAIEmbeddings(
                api_key=openai_api_key,
                model="text-embedding-3-small"
            )
        
        # Fallback to free HuggingFace embeddings
        print("🔷 Using HuggingFace Embeddings (all-MiniLM-L6-v2)")
        from langchain_community.embeddings import HuggingFaceEmbeddings
        
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
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
                loader = TextLoader(str(md_file))
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = md_file.name
                documents.extend(docs)
                print(f"  ✓ Loaded: {md_file.name}")
            except Exception as e:
                print(f"  ✗ Error loading {md_file.name}: {e}")
        
        # Load Text files
        txt_files = list(data_path.glob("**/*.txt"))
        for txt_file in txt_files:
            try:
                loader = TextLoader(str(txt_file))
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = txt_file.name
                documents.extend(docs)
                print(f"  ✓ Loaded: {txt_file.name}")
            except Exception as e:
                print(f"  ✗ Error loading {txt_file.name}: {e}")
        
        # Load PDF files
        pdf_files = list(data_path.glob("**/*.pdf"))
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = pdf_file.name
                documents.extend(docs)
                print(f"  ✓ Loaded: {pdf_file.name}")
            except Exception as e:
                print(f"  ✗ Error loading {pdf_file.name}: {e}")
        
        return documents
    
    def _create_default_documents(self) -> List[Document]:
        """Create default documents if no data files exist."""
        default_content = """
        # About Shashi Bhushan Jha
        
        Shashi Bhushan Jha completed an M.Tech in Electrical Engineering
        (Communication and Signal Processing) at IIT Ropar in 2026 with a final
        CGPA of 7.78/10. His master's research used analytical derivations and
        MATLAB simulation to study generalized multi-user NOMA systems.

        ## Research interests
        - Quantum communication and quantum information networking
        - 6G and beyond, optical communication, ISAC, NTN, and satellite links
        - Multiple access and physical-layer signal processing

        These emerging fields are prospective interests and areas of active
        learning, not claims of completed quantum research.
        
        ## Contact
        Visit my portfolio at: https://shashibhushanjha.me
        """
        
        return [Document(
            page_content=default_content,
            metadata={"source": "default"}
        )]
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks for better retrieval."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        return text_splitter.split_documents(documents)
    
    async def retrieve(
        self,
        query: str,
        k: int = 3
    ) -> Tuple[str, List[str]]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: The search query
            k: Number of documents to retrieve
            
        Returns:
            Tuple of (combined_context, list_of_sources)
        """
        if not self.vector_store:
            return "", []
        
        # Perform similarity search
        docs = self.vector_store.similarity_search(query, k=k)
        
        # Combine context from retrieved documents
        context_parts = []
        sources = []
        
        for doc in docs:
            context_parts.append(doc.page_content)
            source = doc.metadata.get("source", "unknown")
            if source not in sources:
                sources.append(source)
        
        context = "\n\n---\n\n".join(context_parts)
        
        return context, sources
    
    async def add_document(self, content: str, metadata: dict = None):
        """Add a new document to the knowledge base."""
        doc = Document(
            page_content=content,
            metadata=metadata or {}
        )
        
        chunks = self._split_documents([doc])
        
        if self.vector_store:
            self.vector_store.add_documents(chunks)
        else:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
