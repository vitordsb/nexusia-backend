"""
Orquestrador de IA - Contexto do Padrão Strategy.
Gerencia a seleção e execução dos provedores de IA.
"""
from typing import Dict
from app.api.v1.schemas import ChatCompletionRequest, ChatCompletionResponse
from app.services.providers.base_provider import BaseProvider
from app.core.config import settings
from fastapi import HTTPException


class LLMOrchestrator:
    """
    Orquestrador responsável por selecionar e executar o provedor de IA correto.
    
    Este é o 'Contexto' no Padrão Strategy. Ele mantém uma referência para
    todos os provedores disponíveis e delega a tarefa de geração para o
    provedor apropriado com base no modelo solicitado.
    """
    
    def __init__(self):
        """Inicializa o orquestrador com todos os provedores disponíveis."""
        # Importações locais para evitar dependências circulares
        from app.services.providers.gpt_provider import GptProvider
        from app.services.providers.claude_provider import ClaudeProvider
        from app.services.providers.gemini_provider import GeminiProvider
        
        # Mapeamento de modelos para provedores
        self.providers: Dict[str, BaseProvider] = {
            # OpenAI GPT Models
            "gpt-5-pro": GptProvider(settings.OPENAI_API_KEY),
            "gpt-5": GptProvider(settings.OPENAI_API_KEY),
            "gpt-5-mini": GptProvider(settings.OPENAI_API_KEY),
            
            # Anthropic Claude Models
            "claude-opus-4-1": ClaudeProvider(settings.ANTHROPIC_API_KEY),
            "claude-sonnet-4-5": ClaudeProvider(settings.ANTHROPIC_API_KEY),
            "claude-haiku-4-5": ClaudeProvider(settings.ANTHROPIC_API_KEY),
            
            # Google Gemini Models
            "gemini-2-5-pro": GeminiProvider(settings.GOOGLE_API_KEY),
            "gemini-2-5-flash": GeminiProvider(settings.GOOGLE_API_KEY),
        }
    
    async def get_completion(
        self,
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Obtém uma resposta de chat completion do provedor apropriado.
        
        Args:
            request: Requisição de chat completion
            
        Returns:
            Resposta de chat completion
            
        Raises:
            HTTPException: Se o modelo não for suportado
        """
        provider = self.providers.get(request.model)
        
        if not provider:
            raise HTTPException(
                status_code=400,
                detail=f"Modelo '{request.model}' não suportado. "
                       f"Modelos disponíveis: {list(self.providers.keys())}"
            )
        
        # Delega a geração para o provedor selecionado
        return await provider.generate(request)
    
    def get_available_models(self) -> list:
        """
        Retorna a lista de modelos disponíveis.
        
        Returns:
            Lista de IDs de modelos disponíveis
        """
        return list(self.providers.keys())

