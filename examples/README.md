# 📚 Exemplos de Uso da NexusAI API

Esta pasta contém scripts de exemplo que demonstram como interagir com a NexusAI API.

## 🚀 Como Usar

### 1. Certifique-se de que a API está rodando

```bash
# No diretório raiz do projeto
uvicorn app.main:app --reload
```

### 2. Execute o script de teste

```bash
# No diretório raiz do projeto
python examples/test_api.py
```

## 📝 O que o script faz

O script `test_api.py` demonstra:

1. **Autenticação:** Gera um token JWT para testes
2. **Listar Modelos:** Obtém a lista de todos os modelos disponíveis
3. **Criar Conversa:** Cria uma nova conversa no banco de dados
4. **Chat Completion:** Envia uma mensagem para o GPT-5 Mini
5. **Consultar Preços:** Obtém a tabela de preços completa
6. **Gerar Imagem:** Testa a geração de imagens com DALL-E 3 (se configurado)
7. **Busca na Web:** Testa a busca no Google (se configurado)

## 🔧 Personalizando

Você pode modificar o script para testar diferentes cenários:

```python
# Testar com outro modelo
response = client.chat(
    model="claude-sonnet-4-5",
    message="Explique a teoria da relatividade em termos simples",
    mode="high"  # Modo de máxima qualidade
)

# Testar geração de imagem HD
image = client.generate_image(
    prompt="A futuristic city with flying cars",
    quality="hd"
)
```

## 📊 Saída Esperada

```
🚀 NexusAI API - Script de Teste

==================================================

1️⃣ Gerando token de autenticação...
✅ Token gerado com sucesso!

2️⃣ Listando modelos disponíveis...

📋 8 modelos disponíveis:

  • gpt-5-pro (openai) - GPT-5 Pro
  • gpt-5 (openai) - GPT-5
  • gpt-5-mini (openai) - GPT-5 Mini
  • claude-opus-4-1 (anthropic) - Claude Opus 4.1
  • claude-sonnet-4-5 (anthropic) - Claude Sonnet 4.5
  • claude-haiku-4-5 (anthropic) - Claude Haiku 4.5
  • gemini-2-5-pro (google) - Gemini 2.5 Pro
  • gemini-2-5-flash (google) - Gemini 2.5 Flash

3️⃣ Criando uma nova conversa...
✅ Conversa criada: 507f1f77bcf86cd799439011

4️⃣ Testando chat com GPT-5 Mini...

💬 Resposta: 2 + 2 é igual a 4.
📊 Uso: 25 tokens | 2 créditos

5️⃣ Consultando tabela de preços...

💰 Tabela de Preços:

  • gpt-5-pro
    Input: 0.16 créditos/1K tokens
    Output: 1.3 créditos/1K tokens

  ...

==================================================
✅ Testes concluídos!
```

## ⚠️ Notas Importantes

- **Token de Teste:** O endpoint `/v1/auth/token` é apenas para desenvolvimento e deve ser removido em produção.
- **Custos:** Cada requisição consome créditos. Use modelos econômicos (Mini, Flash) para testes.
- **SerpAPI:** A busca na web requer uma chave da SerpAPI configurada no `.env`.

