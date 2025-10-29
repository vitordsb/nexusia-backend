"""
Módulo de precificação e cálculo de créditos.
Gerencia custos de tokens e conversão para créditos da plataforma.

Estratégia de Precificação:
- 1 crédito = R$ 0,01 (1 centavo)
- Margem de lucro mínima de 200% sobre o custo da API
- Valores arredondados para facilitar o entendimento
"""
from typing import Literal


class PricingCalculator:
    """
    Calculadora de custos e créditos baseada no uso de tokens.
    
    Sistema de créditos simplificado:
    - Custo calculado por 100 tokens (input e output separados)
    - 1 crédito = R$ 0,01
    - Margem de lucro embutida nos preços
    """
    
    # Custos em CRÉDITOS por 100 tokens (já com margem de lucro)
    # Baseado nos custos reais das APIs + margem de 200-300%
    PRICING_TABLE = {
        # OpenAI GPT - Custos por 100 tokens
        "gpt-5-pro": {"input": 1, "output": 5},      # Modelo premium
        "gpt-5": {"input": 1, "output": 5},          # Modelo premium
        "gpt-5-mini": {"input": 1, "output": 2},     # Modelo econômico
        
        # Anthropic Claude - Custos por 100 tokens
        "claude-opus-4-1": {"input": 10, "output": 50},    # Ultra premium
        "claude-sonnet-4-5": {"input": 2, "output": 10},   # Premium
        "claude-haiku-4-5": {"input": 1, "output": 3},     # Balanceado
        
        # Google Gemini - Custos por 100 tokens
        "gemini-2-5-pro": {"input": 1, "output": 5},       # Premium
        "gemini-2-5-flash": {"input": 1, "output": 1},     # Econômico
    }
    
    @classmethod
    def calculate_credits(
        cls,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> int:
        """
        Calcula o custo em créditos NexusAI.
        
        Args:
            model: Nome do modelo usado
            prompt_tokens: Número de tokens do prompt
            completion_tokens: Número de tokens da resposta
            
        Returns:
            Custo em créditos (inteiro)
            
        Raises:
            ValueError: Se o modelo não for encontrado
        """
        if model not in cls.PRICING_TABLE:
            raise ValueError(f"Modelo '{model}' não encontrado na tabela de preços")
        
        pricing = cls.PRICING_TABLE[model]
        
        # Calcular custo por 100 tokens
        input_cost = (prompt_tokens / 100) * pricing["input"]
        output_cost = (completion_tokens / 100) * pricing["output"]
        
        total_credits = input_cost + output_cost
        
        # Arredondar para cima e garantir mínimo de 1 crédito
        return max(1, int(total_credits + 0.5))
    
    @classmethod
    def calculate_cost_brl(
        cls,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calcula o custo em Reais (BRL).
        
        Args:
            model: Nome do modelo usado
            prompt_tokens: Número de tokens do prompt
            completion_tokens: Número de tokens da resposta
            
        Returns:
            Custo em BRL
        """
        credits = cls.calculate_credits(model, prompt_tokens, completion_tokens)
        # 1 crédito = R$ 0,01
        return credits * 0.01
    
    @classmethod
    def get_model_pricing(cls, model: str) -> dict:
        """
        Retorna informações de preço de um modelo.
        
        Args:
            model: Nome do modelo
            
        Returns:
            Dicionário com informações de preço
        """
        if model not in cls.PRICING_TABLE:
            raise ValueError(f"Modelo '{model}' não encontrado")
        
        pricing = cls.PRICING_TABLE[model]
        
        return {
            "model": model,
            "credits_per_100_tokens": {
                "input": pricing["input"],
                "output": pricing["output"]
            },
            "brl_per_100_tokens": {
                "input": pricing["input"] * 0.01,
                "output": pricing["output"] * 0.01
            }
        }
    
    @classmethod
    def get_all_pricing(cls) -> list:
        """
        Retorna informações de preço de todos os modelos.
        
        Returns:
            Lista com informações de preço de todos os modelos
        """
        return [cls.get_model_pricing(model) for model in cls.PRICING_TABLE.keys()]
    
    @classmethod
    def estimate_cost(
        cls,
        model: str,
        estimated_tokens: int,
        token_type: Literal["input", "output"] = "output"
    ) -> int:
        """
        Estima o custo em créditos para um número de tokens.
        
        Args:
            model: Nome do modelo
            estimated_tokens: Número estimado de tokens
            token_type: Tipo de token (input ou output)
            
        Returns:
            Custo estimado em créditos
        """
        if token_type == "input":
            return cls.calculate_credits(model, estimated_tokens, 0)
        else:
            return cls.calculate_credits(model, 0, estimated_tokens)


# Custos fixos para serviços adicionais
class AdditionalServicesPricing:
    """Precificação de serviços adicionais (imagens, busca)."""
    
    # Geração de imagens (DALL-E 3)
    IMAGE_GENERATION = {
        "standard": 10,  # 10 créditos = R$ 0,10
        "hd": 20         # 20 créditos = R$ 0,20
    }
    
    # Busca na web (SerpAPI)
    WEB_SEARCH = 2  # 2 créditos = R$ 0,02 por busca
    
    @classmethod
    def get_image_cost(cls, quality: str = "standard") -> int:
        """Retorna o custo em créditos para geração de imagem."""
        return cls.IMAGE_GENERATION.get(quality, cls.IMAGE_GENERATION["standard"])
    
    @classmethod
    def get_search_cost(cls) -> int:
        """Retorna o custo em créditos para busca na web."""
        return cls.WEB_SEARCH

