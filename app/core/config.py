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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240
    
    # Configurações do MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "nexusai"
    
    # Chaves de API dos Provedores de IA
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    GOOGLE_API_KEY: str
    PORT: int
    
    # Chave de API para Web Search (Opcional)
    SERPAPI_API_KEY: str | None = None
    
    # Configurações Opcionais
    DEBUG: bool = False
    CORS_ORIGINS: list = ["*"]
    ENABLE_CREDIT_SIMULATION: bool = False
    LLM_REQUEST_TIMEOUT_SECONDS: int = 0
    LLM_ENABLE_FALLBACK: bool = True
    LLM_FALLBACK_MODEL: Optional[str] = "gemini-2-5-flash"
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_BACKOFF_SECONDS: float = 1.5
    LLM_MAX_CONCURRENT_REQUESTS_PER_MODEL: int = 3

    # Integração com backendAuth
    BACKEND_AUTH_BASE_URL: str = "http://localhost:4000"
    FRONTEND_BASE_URL: Optional[str] = None
    INTERNAL_SERVICE_TOKEN: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global de configurações
settings = Settings()
