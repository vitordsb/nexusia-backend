"""
Módulo de conexão com MongoDB usando Motor (driver assíncrono).
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings


class MongoDB:
    """
    Gerenciador de conexão com MongoDB.
    Implementa o padrão Singleton para garantir uma única instância.
    """
    
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None
    
    @classmethod
    async def connect(cls):
        """Conecta ao MongoDB."""
        if cls.client is None:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.database = cls.client[settings.MONGODB_DB_NAME]
            print(f"✅ Conectado ao MongoDB: {settings.MONGODB_DB_NAME}")
    
    @classmethod
    async def disconnect(cls):
        """Desconecta do MongoDB."""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.database = None
            print("❌ Desconectado do MongoDB")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """
        Retorna a instância do banco de dados.
        
        Returns:
            Instância do banco de dados MongoDB
            
        Raises:
            RuntimeError: Se não estiver conectado
        """
        if cls.database is None:
            raise RuntimeError("Banco de dados não conectado. Chame MongoDB.connect() primeiro.")
        return cls.database


# Função helper para obter o banco de dados
async def get_database() -> AsyncIOMotorDatabase:
    """
    Função helper para obter o banco de dados MongoDB.
    
    Returns:
        Instância do banco de dados MongoDB
    """
    return MongoDB.get_database()

