"""
NexusAI API - Ponto de entrada da aplicação.
Microsserviço de orquestração de múltiplas IAs.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from dotenv import load_dotenv
import uvicorn
import os

load = load_dotenv()
# Criar instância do FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de orquestração de múltiplas inteligências artificiais",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "Bem-vindo à NexusAI API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


# Eventos de ciclo de vida
@app.on_event("startup")
async def startup_event():
    """Evento executado ao iniciar a aplicação."""
    from app.db.mongodb import MongoDB
    await MongoDB.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado ao encerrar a aplicação."""
    from app.db.mongodb import MongoDB
    await MongoDB.disconnect()


# Importar e incluir routers
from app.api.v1.endpoints import chat, models, conversations, auth, pricing, images, search

app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Auth (Dev Only)"])
app.include_router(chat.router, prefix=settings.API_V1_PREFIX, tags=["Chat"])
app.include_router(models.router, prefix=settings.API_V1_PREFIX, tags=["Models"])
app.include_router(conversations.router, prefix=settings.API_V1_PREFIX, tags=["Conversations"])
app.include_router(pricing.router, prefix=settings.API_V1_PREFIX, tags=["Pricing"])
app.include_router(images.router, prefix=settings.API_V1_PREFIX, tags=["Images"])
app.include_router(search.router, prefix=settings.API_V1_PREFIX, tags=["Search"])


if __name__ == "__main__":
    port_env = os.getenv("PORT")
    try:
        port = int(port_env) if port_env else settings.PORT
    except (TypeError, ValueError):
        port = settings.PORT
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )
