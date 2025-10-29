"""
Repositório para operações de conversas no MongoDB.
Implementa o padrão Repository para abstrair o acesso aos dados.
"""
from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models import ConversationDocument, MessageDocument
from app.db.mongodb import get_database


class ConversationRepository:
    """
    Repositório para gerenciar conversas no MongoDB.
    Implementa operações CRUD para conversas.
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Inicializa o repositório.
        
        Args:
            database: Instância do banco de dados MongoDB
        """
        self.collection = database["conversations"]
    
    async def create(self, conversation: ConversationDocument) -> ConversationDocument:
        """
        Cria uma nova conversa.
        
        Args:
            conversation: Dados da conversa a ser criada
            
        Returns:
            Conversa criada
        """
        conversation_dict = conversation.model_dump()
        await self.collection.insert_one(conversation_dict)
        return conversation
    
    async def get_by_id(self, conversation_id: str, user_id: str) -> Optional[ConversationDocument]:
        """
        Busca uma conversa por ID.
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário (para validação de propriedade)
            
        Returns:
            Conversa encontrada ou None
        """
        doc = await self.collection.find_one({
            "conversation_id": conversation_id,
            "user_id": user_id
        })
        
        if doc:
            # Remover o _id do MongoDB antes de converter
            doc.pop("_id", None)
            return ConversationDocument(**doc)
        return None
    
    async def list_by_user(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0,
        favorites_only: bool = False
    ) -> List[ConversationDocument]:
        """
        Lista conversas de um usuário.
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de conversas a retornar
            skip: Número de conversas a pular (para paginação)
            favorites_only: Se deve retornar apenas favoritas
            
        Returns:
            Lista de conversas
        """
        query = {"user_id": user_id}
        if favorites_only:
            query["is_favorite"] = True
        
        cursor = self.collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
        conversations = []
        
        async for doc in cursor:
            doc.pop("_id", None)
            conversations.append(ConversationDocument(**doc))
        
        return conversations
    
    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        message: MessageDocument
    ) -> bool:
        """
        Adiciona uma mensagem a uma conversa existente.
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário (para validação)
            message: Mensagem a ser adicionada
            
        Returns:
            True se a mensagem foi adicionada, False caso contrário
        """
        result = await self.collection.update_one(
            {
                "conversation_id": conversation_id,
                "user_id": user_id
            },
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def update_title(
        self,
        conversation_id: str,
        user_id: str,
        title: str
    ) -> bool:
        """
        Atualiza o título de uma conversa.
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário (para validação)
            title: Novo título
            
        Returns:
            True se o título foi atualizado, False caso contrário
        """
        result = await self.collection.update_one(
            {
                "conversation_id": conversation_id,
                "user_id": user_id
            },
            {
                "$set": {
                    "title": title,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def toggle_favorite(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """
        Alterna o status de favorito de uma conversa.
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário (para validação)
            
        Returns:
            True se o status foi alterado, False caso contrário
        """
        # Primeiro buscar o status atual
        doc = await self.collection.find_one({
            "conversation_id": conversation_id,
            "user_id": user_id
        })
        
        if not doc:
            return False
        
        # Inverter o status
        new_status = not doc.get("is_favorite", False)
        
        result = await self.collection.update_one(
            {
                "conversation_id": conversation_id,
                "user_id": user_id
            },
            {
                "$set": {
                    "is_favorite": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def delete(self, conversation_id: str, user_id: str) -> bool:
        """
        Deleta uma conversa.
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário (para validação)
            
        Returns:
            True se a conversa foi deletada, False caso contrário
        """
        result = await self.collection.delete_one({
            "conversation_id": conversation_id,
            "user_id": user_id
        })
        return result.deleted_count > 0
    
    async def count_by_user(self, user_id: str) -> int:
        """
        Conta o número de conversas de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Número de conversas
        """
        return await self.collection.count_documents({"user_id": user_id})


# Função helper para obter uma instância do repositório
async def get_conversation_repository() -> ConversationRepository:
    """
    Função helper para obter uma instância do repositório de conversas.
    
    Returns:
        Instância do ConversationRepository
    """
    db = await get_database()
    return ConversationRepository(db)

