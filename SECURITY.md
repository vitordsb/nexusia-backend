# Segurança da NexusAI API

## 🔒 Visão Geral

A NexusAI API implementa múltiplas camadas de segurança para proteger dados sensíveis e garantir que apenas usuários autorizados possam acessar os recursos.

## 🛡️ Camadas de Segurança

### 1. Autenticação JWT

Todos os endpoints da API (exceto o endpoint de saúde) requerem autenticação via **JSON Web Token (JWT)**.

#### Como Funciona

1. O usuário faz login no sistema principal da plataforma
2. O sistema principal gera um token JWT contendo o `user_id`
3. O frontend envia este token no cabeçalho `Authorization` de cada requisição
4. A API valida o token e extrai o `user_id`
5. Se o token for válido, a requisição é processada
6. Se o token for inválido ou expirado, a API retorna erro 401

#### Formato do Token

```
Authorization: Bearer <token_jwt>
```

#### Exemplo de Uso

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5",
    "mode": "medium",
    "messages": [
      {"role": "user", "content": "Olá!"}
    ]
  }'
```

### 2. Proteção de Chaves de API

As chaves de API dos provedores de IA (OpenAI, Anthropic, Google) são armazenadas de forma segura:

#### ✅ Boas Práticas Implementadas

- **Variáveis de Ambiente**: Chaves armazenadas em arquivo `.env` (nunca no código)
- **Gitignore**: Arquivo `.env` está no `.gitignore` (nunca versionado)
- **Server-Side Only**: Chaves ficam apenas no servidor backend
- **Sem Exposição ao Cliente**: Frontend nunca tem acesso às chaves
- **Validação de Propriedade**: Usuários só acessam suas próprias conversas

#### ❌ O Que NÃO Fazer

- ❌ Nunca commitar o arquivo `.env` no Git
- ❌ Nunca expor chaves de API no frontend
- ❌ Nunca incluir chaves em logs ou mensagens de erro
- ❌ Nunca compartilhar chaves publicamente

### 3. Isolamento de Dados por Usuário

Cada operação no banco de dados valida que o usuário só pode acessar seus próprios dados:

```python
# Exemplo: Buscar conversa
conversation = await repo.get_by_id(
    conversation_id=conversation_id,
    user_id=current_user["user_id"]  # ✅ Validação de propriedade
)
```

### 4. CORS (Cross-Origin Resource Sharing)

A API implementa CORS para controlar quais origens podem fazer requisições:

```python
# Em produção, configure apenas as origens permitidas
CORS_ORIGINS=["https://nexusai.com", "https://app.nexusai.com"]
```

## 🔑 Gerenciamento de Chaves de API

### Obtendo as Chaves

1. **OpenAI**: https://platform.openai.com/api-keys
2. **Anthropic**: https://console.anthropic.com/settings/keys
3. **Google**: https://aistudio.google.com/app/apikey

### Configurando as Chaves

1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` e adicione suas chaves:
   ```env
   OPENAI_API_KEY=sk-proj-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=AIza...
   ```

3. **NUNCA** commite o arquivo `.env` no Git

### Rotação de Chaves

Para maior segurança, recomenda-se rotacionar as chaves periodicamente:

1. Gere uma nova chave no console do provedor
2. Atualize o arquivo `.env` com a nova chave
3. Reinicie a aplicação
4. Revogue a chave antiga no console do provedor

## 🚨 Endpoint de Teste (Desenvolvimento)

### ⚠️ ATENÇÃO

O endpoint `POST /v1/auth/token` é **apenas para desenvolvimento/teste**. Ele permite gerar tokens JWT sem autenticação.

**Em produção:**
- ❌ Remova este endpoint
- ✅ Use o sistema de autenticação principal da plataforma

### Como Usar (Desenvolvimento)

```bash
# 1. Gerar um token de teste
curl -X POST "http://localhost:8000/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123"}'

# Resposta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# 2. Usar o token nas requisições
curl -X GET "http://localhost:8000/v1/models" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🔐 Configurações de Segurança

### JWT Secret Key

A chave secreta usada para assinar os tokens JWT deve ser:

- ✅ Aleatória e complexa (mínimo 32 caracteres)
- ✅ Diferente em cada ambiente (dev, staging, prod)
- ✅ Armazenada de forma segura (variável de ambiente)
- ❌ Nunca versionada no Git

```env
# Exemplo de chave forte
JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Tempo de Expiração do Token

Configure o tempo de expiração adequado para seu caso de uso:

```env
# 30 minutos (padrão)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 1 hora
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 24 horas
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 📋 Checklist de Segurança

Antes de fazer deploy em produção:

- [ ] Arquivo `.env` está no `.gitignore`
- [ ] Chaves de API estão configuradas como variáveis de ambiente
- [ ] JWT_SECRET_KEY é forte e única
- [ ] Endpoint de teste (`/auth/token`) foi removido
- [ ] CORS está configurado apenas para origens confiáveis
- [ ] MongoDB está protegido com autenticação
- [ ] Conexão com MongoDB usa TLS/SSL
- [ ] Logs não expõem informações sensíveis
- [ ] Rate limiting está configurado (se aplicável)

## 🆘 Em Caso de Comprometimento

Se você suspeitar que uma chave foi comprometida:

1. **Imediatamente**:
   - Revogue a chave comprometida no console do provedor
   - Gere uma nova chave
   - Atualize o arquivo `.env`
   - Reinicie a aplicação

2. **Investigue**:
   - Verifique logs de acesso
   - Identifique possíveis acessos não autorizados
   - Avalie o impacto

3. **Previna**:
   - Revise permissões de acesso
   - Implemente alertas de uso anômalo
   - Considere implementar rate limiting

## 📚 Recursos Adicionais

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

