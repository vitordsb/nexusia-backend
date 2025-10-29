"""
Script de exemplo para testar a NexusAI API.

Este script demonstra como:
1. Gerar um token de autenticação
2. Listar modelos disponíveis
3. Criar uma conversa
4. Enviar mensagens para diferentes modelos
5. Consultar preços
6. Gerar imagens
7. Fazer busca na web
"""
import requests
import json
from typing import Optional


class NexusAIClient:
    """Cliente Python para a NexusAI API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Inicializa o cliente.
        
        Args:
            base_url: URL base da API
        """
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def generate_token(self, user_id: str) -> str:
        """
        Gera um token de autenticação para testes.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Token JWT
        """
        response = requests.post(
            f"{self.base_url}/v1/auth/token",
            json={"user_id": user_id}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        print(f"✅ Token gerado com sucesso!")
        return self.token
    
    def _get_headers(self) -> dict:
        """Retorna os headers com o token de autenticação."""
        if not self.token:
            raise ValueError("Token não configurado. Execute generate_token() primeiro.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def list_models(self):
        """Lista todos os modelos disponíveis."""
        response = requests.get(
            f"{self.base_url}/v1/models",
            headers=self._get_headers()
        )
        response.raise_for_status()
        models = response.json()["data"]
        
        print(f"\n📋 {len(models)} modelos disponíveis:\n")
        for model in models:
            print(f"  • {model['id']} ({model['provider']}) - {model['name']}")
        
        return models
    
    def create_conversation(self, title: str = "Nova Conversa") -> str:
        """
        Cria uma nova conversa.
        
        Args:
            title: Título da conversa
            
        Returns:
            ID da conversa criada
        """
        response = requests.post(
            f"{self.base_url}/v1/conversations",
            headers=self._get_headers(),
            json={"title": title}
        )
        response.raise_for_status()
        conversation_id = response.json()["_id"]
        print(f"✅ Conversa criada: {conversation_id}")
        return conversation_id
    
    def chat(
        self,
        model: str,
        message: str,
        conversation_id: Optional[str] = None,
        mode: str = "medium"
    ) -> dict:
        """
        Envia uma mensagem para um modelo de IA.
        
        Args:
            model: ID do modelo
            message: Mensagem do usuário
            conversation_id: ID da conversa (opcional)
            mode: Modo de interação (low, medium, high)
            
        Returns:
            Resposta completa da API
        """
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "mode": mode
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_pricing(self):
        """Consulta a tabela de preços."""
        response = requests.get(
            f"{self.base_url}/v1/pricing",
            headers=self._get_headers()
        )
        response.raise_for_status()
        pricing = response.json()
        
        print(f"\n💰 Tabela de Preços:\n")
        for model_pricing in pricing:
            print(f"  • {model_pricing['model']}")
            print(f"    Input: {model_pricing['credits_per_1k_tokens']['input']} créditos/1K tokens")
            print(f"    Output: {model_pricing['credits_per_1k_tokens']['output']} créditos/1K tokens\n")
        
        return pricing
    
    def generate_image(self, prompt: str, quality: str = "standard") -> dict:
        """
        Gera uma imagem com DALL-E 3.
        
        Args:
            prompt: Descrição da imagem
            quality: Qualidade (standard ou hd)
            
        Returns:
            Resposta com URL da imagem
        """
        response = requests.post(
            f"{self.base_url}/v1/images/generate",
            headers=self._get_headers(),
            json={"prompt": prompt, "quality": quality}
        )
        response.raise_for_status()
        return response.json()
    
    def search_web(self, query: str, num_results: int = 5) -> dict:
        """
        Faz uma busca na web.
        
        Args:
            query: Termo de busca
            num_results: Número de resultados
            
        Returns:
            Resultados da busca
        """
        response = requests.post(
            f"{self.base_url}/v1/search",
            headers=self._get_headers(),
            json={"query": query, "num_results": num_results}
        )
        response.raise_for_status()
        return response.json()


def main():
    """Função principal com exemplos de uso."""
    
    # Inicializar cliente
    client = NexusAIClient()
    
    print("🚀 NexusAI API - Script de Teste\n")
    print("=" * 50)
    
    # 1. Gerar token
    print("\n1️⃣ Gerando token de autenticação...")
    client.generate_token("user_test_123")
    
    # 2. Listar modelos
    print("\n2️⃣ Listando modelos disponíveis...")
    models = client.list_models()
    
    # 3. Criar conversa
    print("\n3️⃣ Criando uma nova conversa...")
    conversation_id = client.create_conversation("Teste de API")
    
    # 4. Testar chat com GPT-5 Mini (mais barato)
    print("\n4️⃣ Testando chat com GPT-5 Mini...")
    response = client.chat(
        model="gpt-5-mini",
        message="Olá! Você pode me dizer quanto é 2+2?",
        conversation_id=conversation_id,
        mode="low"
    )
    
    assistant_message = response["choices"][0]["message"]["content"]
    usage = response["usage"]
    
    print(f"\n💬 Resposta: {assistant_message}")
    print(f"📊 Uso: {usage['total_tokens']} tokens | {usage['cost_credits']} créditos")
    
    # 5. Consultar preços
    print("\n5️⃣ Consultando tabela de preços...")
    client.get_pricing()
    
    # 6. Testar geração de imagens (opcional - requer créditos OpenAI)
    print("\n6️⃣ Testando geração de imagens...")
    try:
        image_response = client.generate_image(
            prompt="A beautiful sunset over the ocean",
            quality="standard"
        )
        print(f"🖼️ Imagem gerada: {image_response['data'][0]['url']}")
        print(f"📊 Custo: {image_response['usage']['cost_credits']} créditos")
    except Exception as e:
        print(f"⚠️ Erro ao gerar imagem: {e}")
    
    # 7. Testar web search (opcional - requer SerpAPI key)
    print("\n7️⃣ Testando busca na web...")
    try:
        search_response = client.search_web("Python programming", num_results=3)
        print(f"\n🔍 Resultados da busca:")
        for result in search_response['results']:
            print(f"  • {result['title']}")
            print(f"    {result['link']}\n")
    except Exception as e:
        print(f"⚠️ Erro na busca: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")


if __name__ == "__main__":
    main()

