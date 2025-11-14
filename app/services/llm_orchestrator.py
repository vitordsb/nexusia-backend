"""
Orquestrador de IA - Contexto do Padrão Strategy.
Gerencia a seleção e execução dos provedores de IA.
"""
import asyncio
from typing import Dict, Optional
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
        self.timeout_seconds = max(0, settings.LLM_REQUEST_TIMEOUT_SECONDS)
        self.enable_fallback = settings.LLM_ENABLE_FALLBACK
        self.fallback_model = settings.LLM_FALLBACK_MODEL

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

        try:
            return await self._execute_with_timeout(provider, request)
        except asyncio.TimeoutError:
            error_detail = f"O modelo {request.model} demorou demais para responder."
        except Exception as exc:  # pragma: no cover
            error_detail = f"Falha ao gerar resposta com {request.model}: {exc}"
        else:  # pragma: no cover
            error_detail = ""

        # Tentativa de fallback em caso de erro/timeout
        if self.enable_fallback:
            fallback_model = self._resolve_fallback_model(request.model)
            if fallback_model:
                fallback_provider = self.providers.get(fallback_model)
                if fallback_provider:
                    fallback_request = request.model_copy(update={"model": fallback_model})
                    try:
                        return await self._execute_with_timeout(
                            fallback_provider,
                            fallback_request,
                        )
                    except Exception:
                        pass

        raise HTTPException(
            status_code=503,
            detail=error_detail or "Não foi possível gerar resposta no momento.",
        )
    
    async def _execute_with_timeout(
        self,
        provider: BaseProvider,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        if self.timeout_seconds <= 0:
            return await provider.generate(request)
        return await asyncio.wait_for(provider.generate(request), timeout=self.timeout_seconds)
    
    def _resolve_fallback_model(self, current_model: str) -> Optional[str]:
        if self.fallback_model and self.fallback_model in self.providers:
            if self.fallback_model != current_model:
                return self.fallback_model
        # Encontrar o primeiro modelo diferente disponível
        for model_name in self.providers.keys():
            if model_name != current_model:
                return model_name
        return None
    
    def get_available_models(self) -> list:
        """
        Retorna a lista de modelos disponíveis.
        
        Returns:
            Lista de IDs de modelos disponíveis
        """
        return list(self.providers.keys())
