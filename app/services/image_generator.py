"""
Serviço de geração de imagens usando DALL-E 3 da OpenAI.
"""
from typing import Literal
from openai import AsyncOpenAI
from pydantic import BaseModel
from app.core.config import settings


class ImageGenerationRequest(BaseModel):
    """Request para geração de imagens."""
    prompt: str
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024"
    quality: Literal["standard", "hd"] = "standard"
    n: int = 1  # DALL-E 3 suporta apenas n=1


class ImageGenerationResponse(BaseModel):
    """Response da geração de imagens."""
    created: int
    data: list[dict]


class ImageGenerator:
    """
    Gerador de imagens usando DALL-E 3.
    """
    
    def __init__(self):
        """Inicializa o gerador de imagens."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """
        Gera uma imagem usando DALL-E 3.
        
        Args:
            request: Requisição de geração de imagem
            
        Returns:
            Response com URL da imagem gerada
            
        Raises:
            Exception: Se houver erro na geração
        """
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=request.prompt,
                size=request.size,
                quality=request.quality,
                n=request.n
            )
            
            return ImageGenerationResponse(
                created=response.created,
                data=[
                    {
                        "url": image.url,
                        "revised_prompt": image.revised_prompt
                    }
                    for image in response.data
                ]
            )
        
        except Exception as e:
            raise Exception(f"Erro ao gerar imagem: {str(e)}")
    
    @staticmethod
    def calculate_cost(quality: str) -> dict:
        """
        Calcula o custo de geração de uma imagem.
        
        Args:
            quality: Qualidade da imagem (standard ou hd)
            
        Returns:
            Dicionário com custo em créditos e BRL
        """
        from app.services.pricing import AdditionalServicesPricing
        
        cost_credits = AdditionalServicesPricing.get_image_cost(quality)
        cost_brl = cost_credits * 0.01  # 1 crédito = R$ 0,01
        
        return {
            "cost_credits": cost_credits,
            "cost_brl": round(cost_brl, 2)
        }

