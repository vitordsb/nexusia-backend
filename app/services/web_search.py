"""
Serviço de busca na web usando SerpAPI (Google Search).
"""
import httpx
from typing import Optional
from pydantic import BaseModel
from app.core.config import settings


class SearchResult(BaseModel):
    """Resultado individual de busca."""
    title: str
    link: str
    snippet: str
    position: int


class SearchResponse(BaseModel):
    """Response da busca na web."""
    query: str
    results: list[SearchResult]
    total_results: Optional[int] = None


class WebSearch:
    """
    Serviço de busca na web usando SerpAPI.
    
    Nota: Requer SERPAPI_API_KEY nas variáveis de ambiente.
    """
    
    SERPAPI_BASE_URL = "https://serpapi.com/search"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o serviço de busca.
        
        Args:
            api_key: Chave da SerpAPI (opcional, usa settings se não fornecido)
        """
        self.api_key = api_key or getattr(settings, 'SERPAPI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError(
                "SERPAPI_API_KEY não configurada. "
                "Adicione SERPAPI_API_KEY ao arquivo .env para habilitar web search."
            )
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        language: str = "pt-br"
    ) -> SearchResponse:
        """
        Realiza uma busca na web.
        
        Args:
            query: Termo de busca
            num_results: Número de resultados a retornar (máximo 10)
            language: Idioma dos resultados
            
        Returns:
            Resultados da busca
            
        Raises:
            Exception: Se houver erro na busca
        """
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": min(num_results, 10),
                "hl": language,
                "gl": "br"  # Geolocalização Brasil
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.SERPAPI_BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
            
            # Extrair resultados orgânicos
            organic_results = data.get("organic_results", [])
            
            results = [
                SearchResult(
                    title=result.get("title", ""),
                    link=result.get("link", ""),
                    snippet=result.get("snippet", ""),
                    position=result.get("position", idx + 1)
                )
                for idx, result in enumerate(organic_results)
            ]
            
            return SearchResponse(
                query=query,
                results=results,
                total_results=len(results)
            )
        
        except httpx.HTTPStatusError as e:
            raise Exception(f"Erro na API de busca: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Erro ao realizar busca: {str(e)}")
    
    @staticmethod
    def calculate_cost(num_results: int) -> dict:
        """
        Calcula o custo de uma busca na web.
        
        Args:
            num_results: Número de resultados solicitados
            
        Returns:
            Dicionário com custo em créditos e BRL
        """
        from app.services.pricing import AdditionalServicesPricing
        
        cost_credits = AdditionalServicesPricing.get_search_cost()
        cost_brl = cost_credits * 0.01  # 1 crédito = R$ 0,01
        
        return {
            "cost_credits": cost_credits,
            "cost_brl": round(cost_brl, 2)
        }

