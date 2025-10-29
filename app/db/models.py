"""
Modelos de dados para o MongoDB.
Define a estrutura dos documentos armazenados no banco.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class MessageDocument(BaseModel):
    """Modelo de uma mensagem individual."""
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationDocument(BaseModel):
    """Modelo de uma conversa completa."""
    conversation_id: str
    user_id: str
    title: Optional[str] = None
    model: str
    mode: Literal["low", "medium", "high"]
    messages: List[MessageDocument] = Field(default_factory=list)
    is_favorite: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123abc",
                "user_id": "user_456def",
                "title": "Discussão sobre IA",
                "model": "gpt-5",
                "mode": "medium",
                "messages": [
                    {
                        "role": "user",
                        "content": "O que é inteligência artificial?",
                        "timestamp": "2025-10-20T10:00:00"
                    },
                    {
                        "role": "assistant",
                        "content": "Inteligência artificial é...",
                        "timestamp": "2025-10-20T10:00:05"
                    }
                ],
                "is_favorite": False,
                "created_at": "2025-10-20T10:00:00",
                "updated_at": "2025-10-20T10:00:05"
            }
        }
