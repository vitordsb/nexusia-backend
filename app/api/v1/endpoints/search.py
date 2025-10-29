"""
Endpoints relacionados a busca na web.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.web_search import WebSearch, SearchResponse
from app.core.security import get_current_user


router = APIRouter()


class SearchRequest(BaseModel):
    """Schema de requisição para busca na web."""
    query: str
    num_results: int = 10
    language: str = "pt-br"


class SearchResponseWithUsage(BaseModel):
    """Schema de resposta de busca com informações de custo."""
    query: str
    results: list[dict]
    total_results: int | None
    usage: dict


@router.post("/search", response_model=SearchResponseWithUsage)
async def web_search(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Realiza uma busca na web usando Google Search.
    
    Args:
        request: Requisição de busca
        current_user: Usuário autenticado
        
    Returns:
        Resultados da busca e informações de custo
        
    Raises:
        HTTPException: Se houver erro na busca ou se a API não estiver configurada
    """
    try:
        search_service = WebSearch()
        
        # Realizar busca
        response = await search_service.search(
            query=request.query,
            num_results=request.num_results,
            language=request.language
        )
        
        # Calcular custo
        cost_info = WebSearch.calculate_cost(request.num_results)
        
        return SearchResponseWithUsage(
            query=response.query,
            results=[result.model_dump() for result in response.results],
            total_results=response.total_results,
            usage=cost_info
        )
    
    except ValueError as e:
        # API key não configurada
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/pricing")
async def get_search_pricing(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações de preço para busca na web.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        Informações de preço
    """
    return {
        "service": "Google Search via SerpAPI",
        "pricing": WebSearch.calculate_cost(10)
    }

