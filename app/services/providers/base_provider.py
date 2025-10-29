"""
Classe base abstrata para o Padrão Strategy.
Define a interface que todos os provedores de IA devem implementar.
"""
from abc import ABC, abstractmethod
from typing import Literal
from app.api.v1.schemas import ChatCompletionRequest, ChatCompletionResponse


class BaseProvider(ABC):
    """
    Interface abstrata para um provedor de LLM.
    
    Todos os provedores concretos (GPT, Claude, Gemini, Manus) devem herdar
    desta classe e implementar o método `generate`.
    """
    
    def __init__(self, api_key: str):
        """
        Inicializa o provedor com sua chave de API.
        
        Args:
            api_key: Chave de API do provedor
        """
        self.api_key = api_key
    
    @abstractmethod
    async def generate(
        self,
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Gera uma resposta de chat completion.
        
        Este método deve ser implementado por cada provedor concreto para:
        1. Converter o ChatCompletionRequest para o formato da API do provedor
        2. Fazer a chamada HTTP para a API externa
        3. Processar a resposta e convertê-la para ChatCompletionResponse
        4. Aplicar as configurações de modo (low, medium, high)
        
        Args:
            request: Requisição de chat completion padronizada
            
        Returns:
            Resposta de chat completion padronizada
            
        Raises:
            Exception: Se houver erro na comunicação com a API externa
        """
        pass
    
    def _get_mode_params(self, mode: Literal["low", "medium", "high"]) -> dict:
        """
        Retorna os parâmetros específicos do provedor para cada modo.
        
        Este método pode ser sobrescrito por provedores concretos para
        customizar os parâmetros de cada modo.
        
        Args:
            mode: Modo de interação solicitado
            
        Returns:
            Dicionário com parâmetros específicos do provedor
        """
        return {}

