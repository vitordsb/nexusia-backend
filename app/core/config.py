"""
Configurações centralizadas do projeto NexusAI API.
Gerencia todas as variáveis de ambiente e configurações globais.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""
    
    # Configurações da API
    APP_NAME: str = "NexusAI API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/v1"
    
    # Configurações de Segurança
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações do MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "nexusai"
    
    # Chaves de API dos Provedores de IA
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    GOOGLE_API_KEY: str
    
    # Chave de API para Web Search (Opcional)
    SERPAPI_API_KEY: str | None = None
    
    # Configurações Opcionais
    DEBUG: bool = False
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global de configurações
settings = Settings()

