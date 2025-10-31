"""
NexusAI API - Ponto de entrada da aplicação.
Microsserviço de orquestração de múltiplas IAs.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
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

def _parse_cors(origins):
    """Aceita list direta, JSON string ou CSV e normaliza."""
    if isinstance(origins, list):
        items = origins
    else:
        raw = str(origins or "").strip()
        if not raw:
            items = []
        elif raw.startswith("["):
            try:
                items = json.loads(raw)
            except Exception:
                items = []
        else:
            items = [p.strip() for p in raw.split(",") if p.strip()]

    def _norm(o: str) -> str:
        s = o.strip().strip('"\'')
        if s.startswith("http:") and not s.startswith("http://"):
            s = s.replace("http:", "http://", 1)
        if s.startswith("https:") and not s.startswith("https://"):
            s = s.replace("https:", "https://", 1)
        if not (s.startswith("http://") or s.startswith("https://")):
            s = f"http://{s}"
        return s.rstrip("/")

    return [_norm(o) for o in items]

allowed_origins = _parse_cors(getattr(settings, "CORS_ORIGINS", ["*"])) or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"]
)

if settings.DEBUG:
    try:
        print("[CORS] Allowed origins:", ", ".join(allowed_origins))
    except Exception:
        pass


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
