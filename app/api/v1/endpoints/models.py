"""
Endpoints relacionados a modelos de IA disponíveis.
"""
from fastapi import APIRouter, Depends
from typing import List
from app.services.llm_orchestrator import LLMOrchestrator
from app.core.security import get_current_user


router = APIRouter()


@router.get("/models", response_model=List[str])
async def list_models(current_user: dict = Depends(get_current_user)):
    """
    Lista todos os modelos de IA disponíveis.
    
    Args:
        current_user: Usuário autenticado (via JWT)
        
    Returns:
        Lista de IDs de modelos disponíveis
    """
    orchestrator = LLMOrchestrator()
    return orchestrator.get_available_models()

