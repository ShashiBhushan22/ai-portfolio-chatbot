"""
Chat Engine - Handles conversation logic and LLM interactions
"""

import os
from typing import List, Tuple, Optional, AsyncGenerator
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .prompts import SYSTEM_PROMPT, get_rag_prompt
from .rag import RAGPipeline


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatEngine:
    """
    Chat engine that combines LLM with RAG for context-aware responses.
    """
    
    def __init__(self, rag_pipeline: RAGPipeline = None):
        self.rag_pipeline = rag_pipeline
        self.llm = self._initialize_llm()
        self.conversation_memory = {}
        
    def _initialize_llm(self):
        """Initialize the LLM based on available API keys."""
        
        # Try Groq first (free and fast)
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            print(f"Using Groq LLM ({os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')})")
            return ChatGroq(
                api_key=groq_api_key,
                model_name=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                temperature=0.7,
                max_tokens=1024,
            )
        
        # Fallback to OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            print("🔷 Using OpenAI LLM (GPT-4o-mini)")
            return ChatOpenAI(
                api_key=openai_api_key,
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=1024,
            )
        
        raise ValueError(
            "No LLM API key found. Please set GROQ_API_KEY or OPENAI_API_KEY"
        )
    
    def _convert_history(self, history: List[ChatMessage]) -> List:
        """Convert chat history to LangChain message format."""
        messages = []
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
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
            context, sources = await self.rag_pipeline.retrieve(message)
        
        # Build the prompt with context
        system_message = SystemMessage(content=get_rag_prompt(context))
        
        # Convert conversation history
        history_messages = []
        if conversation_history:
            history_messages = self._convert_history(conversation_history)
        
        # Build full message list
        messages = [system_message] + history_messages + [HumanMessage(content=message)]
        
        # Get response from LLM
        response = await self.llm.ainvoke(messages)
        
        return response.content, sources
    
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
        context = ""
        
        # Retrieve relevant context using RAG
        if self.rag_pipeline:
            context, _ = await self.rag_pipeline.retrieve(message)
        
        # Build the prompt with context
        system_message = SystemMessage(content=get_rag_prompt(context))
        
        # Convert conversation history
        history_messages = []
        if conversation_history:
            history_messages = self._convert_history(conversation_history)
        
        # Build full message list
        messages = [system_message] + history_messages + [HumanMessage(content=message)]
        
        # Stream response from LLM
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
