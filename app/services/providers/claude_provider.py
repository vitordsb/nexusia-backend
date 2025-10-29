"""
Provider para Anthropic Claude usando a Messages API.
Implementa a interface BaseProvider do padrão Strategy.
"""
import time
from typing import Literal
from anthropic import AsyncAnthropic
from app.services.providers.base_provider import BaseProvider
from app.api.v1.schemas import ChatCompletionRequest, ChatCompletionResponse, ChatChoice, Message, Usage
from app.services.pricing import PricingCalculator


class ClaudeProvider(BaseProvider):
    """
    Provider para modelos Claude da Anthropic.
    
    Suporta:
    - Claude Opus 4.1, Claude Sonnet 4.5, Claude Haiku 4.5
    - Controle de temperature e max_tokens
    - Extended thinking para modo high
    - 3 modos de interação (low, medium, high)
    """
    
    def __init__(self, api_key: str):
        """
        Inicializa o provider Claude.
        
        Args:
            api_key: Chave de API da Anthropic
        """
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key)
    
    def _get_mode_params(self, mode: Literal["low", "medium", "high"]) -> dict:
        """
        Retorna os parâmetros de temperature e max_tokens para cada modo.
        
        Args:
            mode: Modo de interação solicitado
            
        Returns:
            Dicionário com temperature, max_tokens e opcionalmente thinking
        """
        mode_mapping = {
            "low": {
                "temperature": 0.3,
                "max_tokens": 512
            },
            "medium": {
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "high": {
                "temperature": 1.0,
                "max_tokens": 4096,
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": 2000
                }
            }
        }
        return mode_mapping.get(mode, mode_mapping["medium"])
    
    async def generate(
        self,
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Gera uma resposta usando a Anthropic Messages API.
        
        Args:
            request: Requisição de chat completion padronizada
            
        Returns:
            Resposta de chat completion padronizada
            
        Raises:
            Exception: Se houver erro na comunicação com a API da Anthropic
        """
        try:
            # Obter parâmetros do modo
            mode_params = self._get_mode_params(request.mode)
            
            # Separar system message das outras mensagens
            system_message = None
            messages = []
            
            for msg in request.messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Preparar parâmetros da chamada
            api_params = {
                "model": request.model,
                "messages": messages,
                "temperature": mode_params["temperature"],
                "max_tokens": mode_params["max_tokens"]
            }
            
            # Adicionar system message se existir
            if system_message:
                api_params["system"] = system_message
            
            # Adicionar thinking se estiver no modo high
            if "thinking" in mode_params:
                api_params["thinking"] = mode_params["thinking"]
            
            # Fazer chamada para a Messages API
            response = await self.client.messages.create(**api_params)
            
            # Extrair informações de uso de tokens
            prompt_tokens = response.usage.input_tokens if response.usage else 0
            completion_tokens = response.usage.output_tokens if response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            
            # Calcular custo em créditos e BRL
            cost_credits = PricingCalculator.calculate_credits(
                request.model,
                prompt_tokens,
                completion_tokens
            )
            cost_brl = PricingCalculator.calculate_cost_brl(
                request.model,
                prompt_tokens,
                completion_tokens
            )
            
            # Converter resposta para o formato padronizado
            return ChatCompletionResponse(
                id=response.id,
                object="chat.completion",
                created=int(time.time()),
                model=response.model,
                choices=[
                    ChatChoice(
                        index=0,
                        message=Message(
                            role="assistant",
                            content=response.content[0].text if response.content else ""
                        ),
                        finish_reason=response.stop_reason or "stop"
                    )
                ],
                usage=Usage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost_credits=cost_credits,
                    cost_brl=round(cost_brl, 4)
                )
            )
        
        except Exception as e:
            raise Exception(f"Erro ao chamar Anthropic API: {str(e)}")

