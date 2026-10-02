# Ticket Analysis System 🚀

Sistema de análise automatizada de tickets de suporte usando o modelo Laya (similar ao Jev LSM) via Ollama.

## 📖 O que é?

Este projeto é uma API de classificação de tickets que automatiza o roteamento de atendimento ao cliente, analisando o conteúdo de cada ticket para determinar:

- **Qual departamento deve atender** (billing, technical, account, sales, general)
- **Se o ticket é urgente** (score de 0.0 a 1.0)
- **Qual canal de suporte enviar**

## 🧠 Como funciona?

O sistema utiliza o **Laya**, um modelo de decisão System One que não gera texto, mas sim classifica tickets em campos pré-definidos com uma única passagem (forward pass). Isso equivale a uma estrutura de `if/else` probabilística.

### Fluxo de Classificação

1. **Departamento** (Choice): O ticket é classificado em uma das 5 categorias
2. **Urgência** (Noul): Retorna probabilidade de urgência (0.0 a 1.0)
3. **Roteamento**: Calcula qual equipe deve atender

## 🛠️ Tecnologias

- **Python 3.10+** - API REST com FastAPI
- **Laya** - Modelo de decisão (Apache 2.0)
- **Ollama** - Execução local do modelo
- **Docker Compose** - Containerização
- **Uvicorn** - Servidor ASGI

## 🚀 Como executar

### Opção 1: Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/ticket-analysis.git
cd ticket-analysis

# 2. Suba os containers
docker-compose up --build -d

# 3. Aguarde o Ollama baixar o modelo (~1-2 minutos)
docker logs -f ollama-server

# 4. Teste a API
curl http://localhost:8000/health | jq
```

### Opção 2: Local (Desenvolvimento)

```bash
# 1. Instalar dependências
pip install fastapi uvicorn httpx pydantic laya

# 2. Iniciar servidor
uvicorn src.main:app --reload

# 3. Acessar: http://localhost:8000
# Docs Swagger: http://localhost:8000/docs
```

### Opção 3: Demo rápida (sem dependências)

```bash
python3 demo.py
```

## 📡 API Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-------------|
| `/analyze` | POST | Analisa um único ticket |
| `/analyze-batch` | POST | Analisa múltiplos tickets |
| `/health` | GET | Verificação de saúde |
| `/tickets/example` | GET | Exemplo de ticket para teste |

## 📝 Exemplos

### Ticket de Cobrança Dupla

**Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TKT-001",
    "description": "I was charged twice for my subscription this month. Please refund one of the charges. I need this resolved today.",
    "user_id": "USR-12345",
    "timestamp": "2024-01-15T14:30:00Z"
  }'
```

**Response:**
```json
{
  "ticket_id": "TKT-001",
  "department": "billing",
  "confidence": 0.95,
  "urgency_score": 0.82,
  "is_urgent": true,
  "reasoning": "Department: billing (confidence: 0.95). Urgency: 0.82. Routing to: Billing & Payments Team"
}
```

### Ticket Técnico

**Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TKT-002",
    "description": "My app crashed during checkout and I cannot complete my purchase.",
    "user_id": "USR-67890",
    "timestamp": "2024-01-15T15:00:00Z"
  }'
```

**Response:**
```json
{
  "ticket_id": "TKT-002",
  "department": "technical",
  "confidence": 0.92,
  "urgency_score": 0.95,
  "is_urgent": true,
  "reasoning": "Department: technical (confidence: 0.92). Urgency: 0.95. Routing to: Technical Support Team"
}
```

## 📂 Estrutura do Projeto

```
ticket-analysis/
├── docker-compose.yml      # Orquestração dos containers
├── Dockerfile              # Build da API
├── requirements.txt        # Dependências Python
├── docker-entrypoint.sh    # Script de inicialização automática
├── test_api.sh             # Script de testes automatizados
├── demo.py                 # Demo rápida (sem Ollama)
├── local_setup.py          # Setup local alternativo
├── README.md               # Esta documentação
└── src/
    └── main.py            # Aplicação FastAPI
```

## 🔑 Regras de Classificação

### Departamentos

1. **Billing** - Cobranças duplicadas, refunds, disputas de pagamento, chargebacks
2. **Technical** - Bugs, crashes, problemas de login, conectividade, erros
3. **Account** - Reset de senha, dados pessoais, alterações de perfil
4. **Sales** - Dúvidas sobre produtos, preços, upgrades, features
5. **General** - Questões não classificadas

### Critérios de Urgência

Palavras-chave que indicam urgência:
- Alta prioridade: "today", "urgent", "asap", "immediately", "emergency", "critical"
- Blocker: "down", "outage", "blocked", "cannot", "can't"
- Tempo: "24 hours", "today"

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | URL do servidor Ollama |

### Portas

| Serviço | Porta | Descrição |
|---------|-------|-------------|
| Ollama | 11434 | API do modelo Laya |
| Ticket API | 8000 | API REST |

## 🧪 Testes

```bash
# Executar testes de classificação
python3 local_setup.py test

# Executar demo
python3 demo.py
```

## 🔒 Segurança

- Todos os dados permanecem locais (offline-first)
- Nenhuma chamada a APIs externas em produção
- Modelos e pesos armazenados localmente

## 📄 Licença

Apache 2.0 - Livre para uso comercial e modificação.

---

## 🎯 Próximos Passos

- [ ] Adicionar suporte a anexos
- [ ] Integração com n8n para automação
- [ ] Cache de tickets processados
- [ ] Métricas de performance