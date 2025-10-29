# 🚀 NexusAI API

**Microsserviço de Orquestração de Inteligência Artificial**

A NexusAI API é um microsserviço robusto e escalável que unifica o acesso a múltiplos provedores de IA (OpenAI, Anthropic, Google) em uma única interface padronizada. Desenvolvido como projeto acadêmico com foco em qualidade production-ready.

---

## ✨ Recursos Principais

- 🤖 **8 Modelos de IA** de 3 provedores diferentes (OpenAI GPT, Anthropic Claude, Google Gemini)
- 💬 **Gerenciamento de Conversas** com histórico persistente no MongoDB
- 🔐 **Autenticação JWT** em todos os endpoints
- 💰 **Sistema de Créditos** com cálculo automático de custos
- 🎨 **Geração de Imagens** com DALL-E 3
- 🔍 **Web Search** com Google Search via SerpAPI
- 📚 **Documentação Automática** com Swagger UI e Redoc
- 🏗️ **Padrão Strategy** para extensibilidade e manutenibilidade

---

## 📖 Documentação Completa

- **Documentação Técnica:** [DOCUMENTATION.md](DOCUMENTATION.md)
- **Guia de Deploy:** [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)
- **Plano de Créditos:** [PRICING_PLAN.md](PRICING_PLAN.md)
- **Segurança:** [SECURITY.md](SECURITY.md)
- **Swagger UI:** http://127.0.0.1:8000/docs
- **Redoc:** http://127.0.0.1:8000/redoc

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0.0

---

## 🖥️ Frontend Web

O diretório `frontend/` contém uma aplicação React (Vite + TypeScript) para interagir com esta API:

- Login com geração de token (`POST /v1/auth/token`)
- Dashboard de conversas (`GET /v1/conversations`)
- Histórico completo e chat em tempo real (`GET /v1/conversations/{conversation_id}` e `POST /v1/chat/completions`)

Para executar:

```bash
cd frontend
npm install
npm run dev
```

A aplicação assume o backend disponível em `http://127.0.0.1:8000`.
