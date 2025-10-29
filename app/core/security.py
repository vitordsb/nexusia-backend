"""
Módulo de segurança e autenticação JWT.
Responsável por validar tokens JWT e extrair informações do usuário.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings


security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um novo token JWT.
    
    Args:
        data: Dados a serem codificados no token (ex: {"sub": user_id})
        expires_delta: Tempo de expiração do token
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verifica e decodifica um token JWT.
    
    Args:
        credentials: Credenciais HTTP do cabeçalho Authorization
        
    Returns:
        user_id extraído do token
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Token inválido: usuário não encontrado"
            )
        
        return user_id
    
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Obtém o usuário atual a partir do token JWT.
    
    Esta função é usada como dependência nos endpoints para garantir
    que apenas usuários autenticados possam acessar os recursos.
    
    Args:
        credentials: Credenciais HTTP do cabeçalho Authorization
        
    Returns:
        Dicionário com informações do usuário (user_id, etc.)
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    user_id = verify_token(credentials)
    return {"user_id": user_id}

