"""
Endpoints relacionados a autenticação (apenas para desenvolvimento/teste).

ATENÇÃO: Em produção, a autenticação será feita pelo sistema principal.
Este endpoint é apenas para facilitar testes durante o desenvolvimento.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.security import create_access_token


router = APIRouter()


class TokenRequest(BaseModel):
    """Schema para solicitar um token de teste."""
    user_id: str


class TokenResponse(BaseModel):
    """Schema de resposta com o token."""
    access_token: str
    token_type: str = "bearer"


@router.post("/auth/token", response_model=TokenResponse)
async def generate_test_token(request: TokenRequest):
    """
    Gera um token JWT para testes.
    
    ⚠️ ATENÇÃO: Este endpoint é apenas para desenvolvimento/teste.
    Em produção, remova este endpoint e use o sistema de autenticação principal.
    
    Args:
        request: ID do usuário para gerar o token
        
    Returns:
        Token JWT de acesso
    """
    access_token = create_access_token(data={"sub": request.user_id})
    return TokenResponse(access_token=access_token)

