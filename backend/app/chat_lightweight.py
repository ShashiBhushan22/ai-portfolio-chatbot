"""
Chat Engine - Lightweight version using Groq API directly
No LangChain dependency - minimal memory footprint
"""

import os
from typing import List, Tuple, Optional, AsyncGenerator
from pydantic import BaseModel
from groq import Groq

from .prompts import SYSTEM_PROMPT, get_rag_prompt


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatEngine:
    """
    Lightweight chat engine using Groq API directly.
    Memory efficient - works within 512MB RAM limit.
    """
    
    def __init__(self, rag_pipeline=None):
        self.rag_pipeline = rag_pipeline
        self.client = self._initialize_client()
        self.model = "llama-3.3-70b-versatile"
        
    def _initialize_client(self):
        """Initialize the Groq client."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        print("🔷 Using Groq LLM (Llama 3.3 70B)")
        return Groq(api_key=api_key)
    
    def _convert_history(self, history: List[ChatMessage]) -> List[dict]:
        """Convert chat history to Groq message format."""
        messages = []
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        return messages
    
    async def get_response(
        self,
        message: str,
        conversation_history: List[ChatMessage] = None
    ) -> Tuple[str, List[str]]:
        """
        Get a response for the user message.
        
        Args:
            message: User's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            Tuple of (response_text, source_documents)
        """
        sources = []
        context = ""
        
        # Retrieve relevant context using RAG
        if self.rag_pipeline:
            context = await self.rag_pipeline.get_context(message)
            sources = self.rag_pipeline.get_all_sources()
        
        # Build the prompt with context
        system_prompt = get_rag_prompt(context)
        
        # Build messages list
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(self._convert_history(conversation_history))
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Get response from Groq
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content, sources
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return f"I apologize, but I encountered an error: {str(e)}", []
    
    async def get_response_stream(
        self,
        message: str,
        conversation_history: List[ChatMessage] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response for the user message.
        
        Args:
            message: User's message
            conversation_history: Previous messages in the conversation
            
        Yields:
            Response chunks as they're generated
        """
        sources = []
        context = ""
        
        # Retrieve relevant context using RAG
        if self.rag_pipeline:
            context = await self.rag_pipeline.get_context(message)
        
        # Build the prompt with context
        system_prompt = get_rag_prompt(context)
        
        # Build messages list
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(self._convert_history(conversation_history))
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Stream response from Groq
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            yield f"I apologize, but I encountered an error: {str(e)}"
