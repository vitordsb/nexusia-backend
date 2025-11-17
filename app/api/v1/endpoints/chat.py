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
from app.services.credits_client import credits_client
from app.services.pricing import PricingCalculator


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
        min_required_credits = PricingCalculator.estimate_minimum_request_credits(
            request.model,
            request.mode,
        )
    except ValueError:
        min_required_credits = 1

    await credits_client.ensure_minimum_balance(
        current_user["user_id"],
        min_credits=min_required_credits,
    )

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

    usage = response.usage
    if usage and usage.cost_credits > 0:
        metadata = {
            "conversation_id": request.conversation_id,
            "model": request.model,
            "mode": request.mode,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "cost_brl": usage.cost_brl,
        }
        await credits_client.debit(
            user_id=current_user["user_id"],
            amount=usage.cost_credits,
            reference=f"chat:{response.id}",
            reason="chat_completion",
            metadata=metadata,
        )

    return response
