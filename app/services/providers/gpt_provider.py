"""
Provider para OpenAI GPT usando a Responses API (recomendada para GPT-5).
Implementa a interface BaseProvider do padrão Strategy.

VERSÃO CORRIGIDA - Todas as correções aplicadas conforme relatório de testes
"""
import time
from typing import Literal
from openai import AsyncOpenAI
from app.services.providers.base_provider import BaseProvider
from app.api.v1.schemas import ChatCompletionRequest, ChatCompletionResponse, ChatChoice, Message, Usage
from app.services.pricing import PricingCalculator


class GptProvider(BaseProvider):
    """
    Provider para modelos GPT da OpenAI.

    Suporta:
    - GPT-5, GPT-5 Pro, GPT-5 Mini (usando Responses API)
    - Controle de reasoning_effort e verbosity
    - 3 modos de interação (low, medium, high)
    """

    def __init__(self, api_key: str):
        """
        Inicializa o provider GPT.

        Args:
            api_key: Chave de API da OpenAI
        """
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)

    def _get_mode_params(self, mode: Literal["low", "medium", "high"]) -> dict:
        """
        Retorna os parâmetros de reasoning e text para cada modo.

        CORREÇÃO: Formato correto da Responses API
        - reasoning={"effort": "minimal"|"medium"|"high"}
        - text={"verbosity": "low"|"medium"|"high"}

        Args:
            mode: Modo de interação solicitado

        Returns:
            Dicionário com reasoning e text no formato correto
        """
        mode_mapping = {
            "low": {
                "reasoning": {"effort": "minimal"},
                "text": {"verbosity": "low"}
            },
            "medium": {
                "reasoning": {"effort": "medium"},
                "text": {"verbosity": "medium"}
            },
            "high": {
                "reasoning": {"effort": "high"},
                "text": {"verbosity": "high"}
            }
        }
        return mode_mapping.get(mode, mode_mapping["medium"])

    def _messages_to_input(self, messages: list) -> str:
        """
        Converte array de mensagens para string única.

        CORREÇÃO: Responses API usa 'input' (string), não 'messages' (array)

        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "..."}]

        Returns:
            String formatada para o parâmetro 'input' da Responses API
        """
        # Concatenar todas as mensagens em uma string
        input_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                input_parts.append(f"System: {content}")
            elif role == "user":
                input_parts.append(f"User: {content}")
            elif role == "assistant":
                input_parts.append(f"Assistant: {content}")

        return "\n\n".join(input_parts)

    async def generate(
        self,
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Gera uma resposta usando a OpenAI Responses API.

        Args:
            request: Requisição de chat completion padronizada

        Returns:
            Resposta de chat completion padronizada

        Raises:
            Exception: Se houver erro na comunicação com a API da OpenAI
        """
        try:
            # Obter parâmetros do modo (formato correto)
            mode_params = self._get_mode_params(request.mode)

            # CORREÇÃO: Converter mensagens para formato 'input' (string)
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            input_text = self._messages_to_input(messages)

            # CORREÇÃO: Usar Responses API com parâmetros corretos
            response = await self.client.responses.create(
                model=request.model,
                input=input_text,  # CORREÇÃO: 'input' ao invés de 'messages'
                **mode_params  # CORREÇÃO: reasoning={"effort": ...}, text={"verbosity": ...}
            )

            # CORREÇÃO: Extrair texto da resposta no formato correto
            # Responses API retorna 'output_text', não 'choices[0].message.content'
            content = response.output_text

            # Extrair informações de uso de tokens (Responses API renomeou campos)
            prompt_tokens = completion_tokens = total_tokens = 0
            if response.usage:
                usage_data = {}
                if hasattr(response.usage, "model_dump"):
                    usage_data = response.usage.model_dump()
                elif hasattr(response.usage, "to_dict"):
                    usage_data = response.usage.to_dict()
                elif isinstance(response.usage, dict):
                    usage_data = response.usage

                prompt_tokens = usage_data.get("prompt_tokens") or usage_data.get("input_tokens") or 0
                completion_tokens = usage_data.get("completion_tokens") or usage_data.get("output_tokens") or 0
                total_tokens = usage_data.get("total_tokens") or (prompt_tokens + completion_tokens)

                prompt_tokens = int(prompt_tokens or 0)
                completion_tokens = int(completion_tokens or 0)
                total_tokens = int(total_tokens or (prompt_tokens + completion_tokens))

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

            # CORREÇÃO: Converter resposta para o formato padronizado
            # Responses API não retorna 'choices', então criamos manualmente
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
                            content=content
                        ),
                        finish_reason="stop"
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
            raise Exception(f"Erro ao chamar OpenAI Responses API: {str(e)}")
