"""
Endpoints relacionados a geração de imagens.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from app.services.image_generator import ImageGenerator, ImageGenerationRequest, ImageGenerationResponse
from app.core.security import get_current_user


router = APIRouter()


class ImageRequest(BaseModel):
    """Schema de requisição para geração de imagem."""
    prompt: str
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024"
    quality: Literal["standard", "hd"] = "standard"


class ImageResponseData(BaseModel):
    """Schema de dados da imagem gerada."""
    url: str
    revised_prompt: str


class ImageResponse(BaseModel):
    """Schema de resposta de geração de imagem."""
    created: int
    data: list[ImageResponseData]
    usage: dict


@router.post("/images/generate", response_model=ImageResponse)
async def generate_image(
    request: ImageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera uma imagem usando DALL-E 3.
    
    Args:
        request: Requisição de geração de imagem
        current_user: Usuário autenticado
        
    Returns:
        URL da imagem gerada e informações de custo
        
    Raises:
        HTTPException: Se houver erro na geração
    """
    try:
        generator = ImageGenerator()
        
        # Gerar imagem
        gen_request = ImageGenerationRequest(
            prompt=request.prompt,
            size=request.size,
            quality=request.quality
        )
        
        response = await generator.generate(gen_request)
        
        # Calcular custo
        cost_info = ImageGenerator.calculate_cost(request.quality)
        
        return ImageResponse(
            created=response.created,
            data=[
                ImageResponseData(
                    url=item["url"],
                    revised_prompt=item["revised_prompt"]
                )
                for item in response.data
            ],
            usage={
                "cost_usd": cost_info["cost_usd"],
                "cost_credits": cost_info["cost_credits"]
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/pricing")
async def get_image_pricing(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações de preço para geração de imagens.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        Informações de preço
    """
    return {
        "model": "dall-e-3",
        "pricing": {
            "standard": ImageGenerator.calculate_cost("standard"),
            "hd": ImageGenerator.calculate_cost("hd")
        }
    }

