# 🚀 Guia de Deploy - NexusAI API

Este guia fornece instruções passo a passo para fazer o deploy da NexusAI API em diferentes ambientes.

---

## 📋 Pré-requisitos

Antes de fazer o deploy, certifique-se de ter:

- ✅ Python 3.11 ou superior instalado
- ✅ MongoDB instalado ou acesso ao MongoDB Atlas
- ✅ Chaves de API válidas (OpenAI, Anthropic, Google)
- ✅ (Opcional) Chave da SerpAPI para web search

---

## 🏠 Deploy Local (Desenvolvimento)

### 1. Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd nexusai_api
```

### 2. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar no Windows
.venv\Scripts\activate

# Ativar no Linux/macOS
source .venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha com suas chaves:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione suas chaves de API.

### 5. Iniciar MongoDB Local

```bash
# No Windows (se instalado como serviço)
net start MongoDB

# No Linux/macOS
sudo systemctl start mongod
```

### 6. Executar a API

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`.

---

## ☁️ Deploy em Produção

### Opção 1: Render (Recomendado para Projetos Acadêmicos)

[Render](https://render.com) oferece um plano gratuito generoso e é fácil de configurar.

#### Passos:

1. **Crie uma conta no Render**

2. **Crie um novo Web Service**
   - Conecte seu repositório GitHub
   - Selecione Python como ambiente
   - Configure o comando de build: `pip install -r requirements.txt`
   - Configure o comando de start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Configure as Variáveis de Ambiente**
   - No painel do Render, vá em "Environment"
   - Adicione todas as variáveis do `.env`:
     - `OPENAI_API_KEY`
     - `ANTHROPIC_API_KEY`
     - `GOOGLE_API_KEY`
     - `JWT_SECRET_KEY`
     - `MONGODB_URL` (use MongoDB Atlas)
     - `SERPAPI_API_KEY` (opcional)

4. **Configure o MongoDB Atlas**
   - Crie uma conta gratuita no [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Crie um cluster gratuito
   - Obtenha a connection string
   - Adicione à variável `MONGODB_URL` no Render

5. **Deploy**
   - O Render fará o deploy automaticamente
   - Sua API estará disponível em `https://seu-app.onrender.com`

---

### Opção 2: Google Cloud Run

Google Cloud Run é uma plataforma serverless que escala automaticamente.

#### Passos:

1. **Instale o Google Cloud SDK**

2. **Crie um Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

ENV PORT=8080

CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

3. **Build e Push da Imagem**

```bash
gcloud builds submit --tag gcr.io/SEU_PROJETO/nexusai-api
```

4. **Deploy no Cloud Run**

```bash
gcloud run deploy nexusai-api \
  --image gcr.io/SEU_PROJETO/nexusai-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=sk-...,ANTHROPIC_API_KEY=sk-ant-...,GOOGLE_API_KEY=AIza..."
```

---

### Opção 3: Docker + Docker Compose (Qualquer Servidor)

#### 1. Crie um `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Crie um `docker-compose.yml`

```yaml
version: '3.8'

services:
  nexusai_api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - mongodb
    restart: unless-stopped

  mongodb:
    image: mongo:latest
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    restart: unless-stopped

volumes:
  mongo_data:
```

#### 3. Deploy

```bash
# Build e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

---

## 🔒 Checklist de Segurança para Produção

Antes de fazer o deploy em produção, certifique-se de:

- [ ] Mudar `DEBUG=False` no `.env`
- [ ] Usar uma `JWT_SECRET_KEY` forte e única
- [ ] Configurar `CORS_ORIGINS` para permitir apenas o domínio do frontend
- [ ] Remover o endpoint `/v1/auth/token` (apenas para desenvolvimento)
- [ ] Usar HTTPS (certificado SSL/TLS)
- [ ] Configurar rate limiting (opcional, mas recomendado)
- [ ] Configurar logs e monitoramento
- [ ] Usar MongoDB Atlas ou outro serviço gerenciado (não container local)
- [ ] Fazer backup regular do banco de dados
- [ ] Configurar alertas de custo nas APIs de IA

---

## 📊 Monitoramento

### Logs

A API usa o sistema de logging padrão do Python. Para visualizar logs em produção:

```bash
# Docker
docker-compose logs -f nexusai_api

# Render
# Acesse o painel do Render > Logs

# Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nexusai-api"
```

### Métricas

Monitore:
- **Uso de créditos** por usuário
- **Latência** das requisições
- **Taxa de erro** das APIs externas
- **Uso de memória** e CPU

---

## 🆘 Troubleshooting

### Erro: "Connection refused" ao conectar no MongoDB

**Solução:** Verifique se o MongoDB está rodando e se a URL de conexão está correta.

```bash
# Testar conexão
mongosh "mongodb://localhost:27017"
```

### Erro: "Invalid API key" das APIs de IA

**Solução:** Verifique se as chaves estão corretas e ativas no `.env`.

### Erro: "Module not found"

**Solução:** Reinstale as dependências:

```bash
pip install -r requirements.txt
```

### API muito lenta

**Solução:** 
- Verifique a latência das APIs externas
- Use modelos mais rápidos (Mini, Flash)
- Configure cache (futuro)

---

## 📞 Suporte

Para problemas ou dúvidas:
- Consulte a [Documentação Técnica](DOCUMENTATION.md)
- Verifique o [Guia de Segurança](SECURITY.md)
- Revise o [Plano de Créditos](PRICING_PLAN.md)

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0

