"""
Schemas Pydantic para validação de dados de requisições e respostas.
Define a estrutura de dados que a API aceita e retorna.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ============================================================================
# SCHEMAS DE MENSAGENS
# ============================================================================

class Message(BaseModel):
    """Representa uma mensagem em uma conversa."""
    role: Literal["user", "assistant", "system"]
    content: str


# ============================================================================
# SCHEMAS DE CHAT COMPLETION
# ============================================================================

class ChatCompletionRequest(BaseModel):
    """Request para o endpoint de chat completion."""
    model: str = Field(
        ...,
        description="ID do modelo a ser usado (ex: 'gpt-5-pro', 'claude-opus-4-1')",
        examples=["gpt-5-pro", "claude-sonnet-4-5", "gemini-2-5-pro"]
    )
    messages: List[Message] = Field(
        ...,
        description="Lista de mensagens da conversa"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="ID da conversa existente (para continuar uma conversa)"
    )
    mode: Literal["low", "medium", "high"] = Field(
        "medium",
        description="Modo de interação: low (rápido), medium (balanceado), high (máxima qualidade)"
    )
    stream: bool = Field(
        False,
        description="Se True, retorna a resposta em streaming (não implementado nesta versão)"
    )


class ChatChoice(BaseModel):
    """Representa uma escolha de resposta do modelo."""
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    """Informações de uso de tokens e créditos."""
    prompt_tokens: int = Field(..., description="Número de tokens do prompt")
    completion_tokens: int = Field(..., description="Número de tokens da resposta")
    total_tokens: int = Field(..., description="Total de tokens usados")
    cost_credits: int = Field(..., description="Custo em créditos NexusAI (1 crédito = R$ 0,01)")
    cost_brl: float = Field(..., description="Custo em Reais (BRL)")


class ChatCompletionResponse(BaseModel):
    """Response do endpoint de chat completion."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Optional[Usage] = None


# ============================================================================
# SCHEMAS DE CONVERSAS
# ============================================================================

class ConversationBase(BaseModel):
    """Schema base para conversas."""
    title: str = Field(..., description="Título da conversa")


class ConversationCreate(ConversationBase):
    """Schema para criação de uma nova conversa."""
    pass


class ConversationUpdate(BaseModel):
    """Schema para atualização de uma conversa."""
    title: Optional[str] = None
    is_favorite: Optional[bool] = None


class ConversationResponse(ConversationBase):
    """Schema de resposta para uma conversa."""
    id: str = Field(alias="_id")
    user_id: str
    created_at: datetime
    is_favorite: bool
    
    class Config:
        populate_by_name = True
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema de conversa com suas mensagens."""
    messages: List[Message]


class ConversationSummary(BaseModel):
    """Resumo de uma conversa para listagens."""
    conversation_id: str
    title: Optional[str] = None
    model: str
    mode: Literal["low", "medium", "high"]
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message_preview: Optional[str] = None


# ============================================================================
# SCHEMAS DE MODELOS
# ============================================================================

class ModelInfo(BaseModel):
    """Informações sobre um modelo de IA disponível."""
    id: str = Field(..., description="ID único do modelo")
    provider: str = Field(..., description="Provedor da IA (openai, anthropic, google, manus)")
    name: str = Field(..., description="Nome amigável do modelo")
    description: str = Field(..., description="Descrição do modelo")
    modes: List[str] = Field(..., description="Modos suportados (low, medium, high)")


class ModelsListResponse(BaseModel):
    """Lista de modelos disponíveis."""
    object: str = "list"
    data: List[ModelInfo]
