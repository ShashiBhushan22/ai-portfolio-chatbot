"""
AI Portfolio Chatbot - Main FastAPI Application
Author: Shashi Bhushan Jha
Lightweight version for Render free tier (512MB RAM)
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import os
import asyncio
from dotenv import load_dotenv

# Use lightweight versions (no PyTorch, no LangChain)
from .chat_lightweight import ChatEngine
from .rag_lightweight import RAGPipeline

# Load environment variables
load_dotenv()

# Initialize components
rag_pipeline = None
chat_engine = None
initialization_complete = False


async def initialize_components():
    """Initialize RAG pipeline and chat engine in background."""
    global rag_pipeline, chat_engine, initialization_complete
    
    print("🚀 Initializing AI Portfolio Chatbot (Lightweight)...")
    
    # Initialize RAG pipeline with knowledge base
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    data_dir = os.path.abspath(data_dir)
    rag_pipeline = RAGPipeline(data_directory=data_dir)
    await rag_pipeline.initialize()
    
    # Initialize chat engine
    chat_engine = ChatEngine(rag_pipeline=rag_pipeline)
    
    initialization_complete = True
    print("✅ Chatbot ready!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager - start background initialization."""
    # Start initialization in background (non-blocking)
    asyncio.create_task(initialize_components())
    yield
    # Cleanup (if needed)
    print("👋 Shutting down chatbot...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="AI Portfolio Chatbot",
    description="An intelligent chatbot showcasing AI engineering skills",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Allow your website
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shashibhushanjha.me",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "*"  # Remove in production for security
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []


# Simple in-memory rate limiting
from collections import defaultdict
from datetime import datetime, timedelta

request_counts = defaultdict(list)
RATE_LIMIT = 20  # requests per minute
RATE_WINDOW = 60  # seconds


def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = datetime.now()
    cutoff = now - timedelta(seconds=RATE_WINDOW)
    
    # Clean old requests
    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if t > cutoff
    ]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return False
    
    request_counts[client_ip].append(now)
    return True


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "message": "AI Portfolio Chatbot API",
        "version": "1.0.0",
        "ready": initialization_complete
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy" if initialization_complete else "initializing",
        "rag_initialized": rag_pipeline is not None,
        "chat_engine_ready": chat_engine is not None,
        "ready": initialization_complete
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """
    Main chat endpoint - handles user messages and returns AI responses.
    """
    # Check if initialization is complete
    if not initialization_complete:
        raise HTTPException(
            status_code=503,
            detail="Chatbot is still initializing. Please try again in a few seconds."
        )
    
    # Get client IP for rate limiting
    client_ip = req.client.host if req.client else "unknown"
    
    # Check rate limit
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait a moment before sending more messages."
        )
    
    if not chat_engine:
        raise HTTPException(
            status_code=503,
            detail="Chat engine not initialized. Please try again in a moment."
        )
    
    try:
        # Get response from chat engine
        response, sources = await chat_engine.get_response(
            message=request.message,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(response=response, sources=sources)
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message."
        )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, req: Request):
    """
    Streaming chat endpoint - returns response as Server-Sent Events.
    """
    client_ip = req.client.host if req.client else "unknown"
    
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded."
        )
    
    if not chat_engine:
        raise HTTPException(
            status_code=503,
            detail="Chat engine not initialized."
        )
    
    async def generate():
        try:
            async for chunk in chat_engine.get_response_stream(
                message=request.message,
                conversation_history=request.conversation_history
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/info")
async def get_info():
    """Get information about the chatbot capabilities."""
    return {
        "name": "Shashi's AI Assistant",
        "description": "I'm an AI assistant that can answer questions about Shashi Bhushan Jha's background, skills, projects, and experience.",
        "capabilities": [
            "Answer questions about my skills and experience",
            "Discuss my projects and technical work",
            "Explain my background in AI/ML",
            "Provide contact information"
        ],
        "suggested_questions": [
            "What are your key technical skills?",
            "Tell me about your AI/ML projects",
            "What's your educational background?",
            "How can I contact you?"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
