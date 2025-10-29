"""
Endpoints relacionados ao gerenciamento de conversas.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from app.db.conversation_repository import get_conversation_repository, ConversationRepository
from app.db.models import ConversationDocument
from app.core.security import get_current_user
from app.api.v1.schemas import ConversationSummary


router = APIRouter()


class CreateConversationRequest(BaseModel):
    """Schema para criar uma nova conversa."""
    conversation_id: str
    title: str | None = None
    model: str
    mode: str


class UpdateTitleRequest(BaseModel):
    """Schema para atualizar o título de uma conversa."""
    title: str


@router.post("/conversations", response_model=ConversationDocument)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user),
    repo: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Cria uma nova conversa.
    
    Args:
        request: Dados da conversa a ser criada
        current_user: Usuário autenticado
        repo: Repositório de conversas
        
    Returns:
        Conversa criada
    """
    conversation = ConversationDocument(
        conversation_id=request.conversation_id,
        user_id=current_user["user_id"],
        title=request.title,
        model=request.model,
        mode=request.mode
    )
    
    return await repo.create(conversation)


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    limit: int = 50,
    skip: int = 0,
    favorites_only: bool = False,
    current_user: dict = Depends(get_current_user),
    repo: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Lista as conversas do usuário.
    
    Args:
        limit: Número máximo de conversas a retornar
        skip: Número de conversas a pular
        favorites_only: Se deve retornar apenas favoritas
        current_user: Usuário autenticado
        repo: Repositório de conversas
        
    Returns:
        Lista de conversas
    """
    conversations = await repo.list_by_user(
        user_id=current_user["user_id"],
        limit=limit,
        skip=skip,
        favorites_only=favorites_only
    )

    summaries: List[ConversationSummary] = []
    for conversation in conversations:
        last_message = conversation.messages[-1].content if conversation.messages else None
        preview = last_message[:200] if last_message else None
        summaries.append(
            ConversationSummary(
                conversation_id=conversation.conversation_id,
                title=conversation.title,
                model=conversation.model,
                mode=conversation.mode,
                is_favorite=conversation.is_favorite,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                message_count=len(conversation.messages),
                last_message_preview=preview
            )
        )

    return summaries


@router.get("/conversations/{conversation_id}", response_model=ConversationDocument)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    repo: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Busca uma conversa específica.
    
    Args:
        conversation_id: ID da conversa
        current_user: Usuário autenticado
        repo: Repositório de conversas
        
    Returns:
        Conversa encontrada
        
    Raises:
        HTTPException: Se a conversa não for encontrada
    """
    conversation = await repo.get_by_id(conversation_id, current_user["user_id"])
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return conversation


@router.put("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    request: UpdateTitleRequest,
    current_user: dict = Depends(get_current_user),
    repo: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Atualiza o título de uma conversa.
    
    Args:
        conversation_id: ID da conversa
        request: Novo título
        current_user: Usuário autenticado
        repo: Repositório de conversas
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se a conversa não for encontrada
    """
    success = await repo.update_title(
        conversation_id,
        current_user["user_id"],
        request.title
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return {"message": "Título atualizado com sucesso"}


@router.post("/conversations/{conversation_id}/favorite")
async def toggle_favorite(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    repo: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Alterna o status de favorito de uma conversa.
    
    Args:
        conversation_id: ID da conversa
        current_user: Usuário autenticado
        repo: Repositório de conversas
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se a conversa não for encontrada
    """
    success = await repo.toggle_favorite(conversation_id, current_user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return {"message": "Status de favorito alterado com sucesso"}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    repo: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Deleta uma conversa.
    
    Args:
        conversation_id: ID da conversa
        current_user: Usuário autenticado
        repo: Repositório de conversas
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se a conversa não for encontrada
    """
    success = await repo.delete(conversation_id, current_user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return {"message": "Conversa deletada com sucesso"}
