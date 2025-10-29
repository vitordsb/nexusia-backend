"""
Provider para Google Gemini usando o novo Google Gen AI SDK.
Implementa a interface BaseProvider do padrão Strategy.
"""
import time
from typing import Literal
from google import genai
from google.genai import types
from app.services.providers.base_provider import BaseProvider
from app.api.v1.schemas import ChatCompletionRequest, ChatCompletionResponse, ChatChoice, Message, Usage
from app.services.pricing import PricingCalculator


class GeminiProvider(BaseProvider):
    """
    Provider para modelos Gemini do Google.
    
    Suporta:
    - Gemini 2.5 Pro, Gemini 2.5 Flash (com thinking)
    - Gemini 2.0 Flash (sem thinking)
    - Controle de thinking_budget, temperature e max_output_tokens
    - 3 modos de interação (low, medium, high)
    """
    
    def __init__(self, api_key: str):
        """
        Inicializa o provider Gemini.
        
        Args:
            api_key: Chave de API do Google
        """
        super().__init__(api_key)
        self.client = genai.Client(api_key=api_key)
        
        # Modelos que suportam thinking (série 2.5)
        self.thinking_models = [
            "gemini-2-5-pro",
            "gemini-2-5-flash",
            "gemini-2-5-flash-lite"
        ]
    
    def _get_mode_params(self, mode: Literal["low", "medium", "high"], model: str) -> dict:
        """
        Retorna os parâmetros para cada modo, adaptados ao modelo.
        
        Args:
            mode: Modo de interação solicitado
            model: Nome do modelo sendo usado
            
        Returns:
            Dicionário com configurações apropriadas
        """
        # Verificar se o modelo suporta thinking
        supports_thinking = any(tm in model for tm in self.thinking_models)
        
        if supports_thinking:
            # Modelos 2.5 com thinking
            mode_mapping = {
                "low": {
                    "thinking_budget": 0,  # Desabilita thinking
                    "temperature": 0.3,
                    "max_output_tokens": 512
                },
                "medium": {
                    "thinking_budget": 2048,
                    "temperature": 0.7,
                    "max_output_tokens": 2048
                },
                "high": {
                    "thinking_budget": -1,  # Dynamic thinking
                    "temperature": 0.9,
                    "max_output_tokens": 4096
                }
            }
        else:
            # Modelos 2.0 sem thinking
            mode_mapping = {
                "low": {
                    "temperature": 0.3,
                    "max_output_tokens": 512
                },
                "medium": {
                    "temperature": 0.7,
                    "max_output_tokens": 2048
                },
                "high": {
                    "temperature": 1.0,
                    "max_output_tokens": 4096
                }
            }
        
        return mode_mapping.get(mode, mode_mapping["medium"])
    
    async def generate(
        self,
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Gera uma resposta usando a Google Gemini API.
        
        Args:
            request: Requisição de chat completion padronizada
            
        Returns:
            Resposta de chat completion padronizada
            
        Raises:
            Exception: Se houver erro na comunicação com a API do Google
        """
        try:
            # Obter parâmetros do modo
            mode_params = self._get_mode_params(request.mode, request.model)
            
            # Separar system instruction das mensagens
            system_instruction = None
            contents = []
            
            for msg in request.messages:
                if msg.role == "system":
                    system_instruction = msg.content
                else:
                    contents.append({
                        "role": msg.role,
                        "parts": [{"text": msg.content}]
                    })
            
            # Construir configuração
            config_params = {
                "temperature": mode_params["temperature"],
                "max_output_tokens": mode_params["max_output_tokens"]
            }
            
            # Adicionar thinking_config se o modelo suportar
            if "thinking_budget" in mode_params:
                config_params["thinking_config"] = types.ThinkingConfig(
                    thinking_budget=mode_params["thinking_budget"]
                )
            
            # Adicionar system_instruction se existir
            if system_instruction:
                config_params["system_instruction"] = system_instruction
            
            # Criar configuração
            config = types.GenerateContentConfig(**config_params)
            
            # Fazer chamada para a Gemini API
            response = self.client.models.generate_content(
                model=request.model,
                contents=contents,
                config=config
            )
            
            # Extrair informações de uso de tokens (Gemini pode não retornar usage)
            prompt_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
            completion_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            total_tokens = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            
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
                id=f"gemini-{int(time.time())}",
                object="chat.completion",
                created=int(time.time()),
                model=request.model,
                choices=[
                    ChatChoice(
                        index=0,
                        message=Message(
                            role="assistant",
                            content=response.text if response.text else ""
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
            raise Exception(f"Erro ao chamar Google Gemini API: {str(e)}")

