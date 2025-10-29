"""
Endpoints relacionados a chat completions.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.schemas import ChatCompletionRequest, ChatCompletionResponse
from app.services.llm_orchestrator import LLMOrchestrator
from app.core.security import get_current_user
from app.db.conversation_repository import (
    get_conversation_repository,
    ConversationRepository,
)
from app.db.models import MessageDocument, ConversationDocument


router = APIRouter()


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    current_user: dict = Depends(get_current_user),
    repo: ConversationRepository = Depends(get_conversation_repository),
):
    """
    Cria uma chat completion usando o modelo especificado.
    
    Args:
        request: Requisição de chat completion
        current_user: Usuário autenticado (via JWT)
        repo: Repositório de conversas
        
    Returns:
        Resposta de chat completion
        
    Raises:
        HTTPException: Se houver erro na geração
    """
    orchestrator = LLMOrchestrator()

    conversation = None
    if request.conversation_id:
        conversation = await repo.get_by_id(
            request.conversation_id,
            current_user["user_id"],
        )

        if not conversation:
            conversation = ConversationDocument(
                conversation_id=request.conversation_id,
                user_id=current_user["user_id"],
                title=request.conversation_id,
                model=request.model,
                mode=request.mode,
            )
            await repo.create(conversation)

    try:
        response = await orchestrator.get_completion(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if request.conversation_id:
        # Captura a última mensagem do usuário enviada na requisição, se existir
        user_message = next(
            (
                MessageDocument(role=msg.role, content=msg.content)
                for msg in reversed(request.messages)
                if msg.role == "user"
            ),
            None,
        )

        if user_message:
            if not await repo.add_message(
                request.conversation_id,
                current_user["user_id"],
                user_message,
            ):
                raise HTTPException(
                    status_code=500,
                    detail="Falha ao registrar mensagem do usuário na conversa",
                )

        assistant_message = MessageDocument(
            role="assistant",
            content=response.choices[0].message.content,
        )
        if not await repo.add_message(
            request.conversation_id,
            current_user["user_id"],
            assistant_message,
        ):
            raise HTTPException(
                status_code=500,
                detail="Falha ao registrar resposta da IA na conversa",
            )

    return response
