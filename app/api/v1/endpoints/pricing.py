"""
Endpoints relacionados a precificação e custos.
"""
from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from app.services.pricing import PricingCalculator
from app.core.security import get_current_user


router = APIRouter()


class ModelPricing(BaseModel):
    """Schema de resposta com informações de preço de um modelo."""
    model: str
    api_cost_usd_per_1m: dict
    credits_per_1k_tokens: dict


@router.get("/pricing", response_model=List[ModelPricing])
async def get_pricing(current_user: dict = Depends(get_current_user)):
    """
    Lista os preços de todos os modelos disponíveis.
    
    Retorna o custo em créditos NexusAI por 1.000 tokens (input e output)
    para cada modelo.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        Lista com informações de preço de todos os modelos
    """
    return PricingCalculator.get_all_pricing()


@router.get("/pricing/{model}", response_model=ModelPricing)
async def get_model_pricing(
    model: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna informações de preço de um modelo específico.
    
    Args:
        model: Nome do modelo
        current_user: Usuário autenticado
        
    Returns:
        Informações de preço do modelo
    """
    return PricingCalculator.get_model_pricing(model)

