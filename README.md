# 🐄 BoviCare API - Backend Service

Backend API do BoviCare desenvolvido com Flask, Python, Docker e PostgreSQL. Este serviço atua como API Gateway, orquestrando a comunicação entre o frontend React e os serviços RAG (FastAPI).

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Git
- Conta OpenAI (para API key)
- (Opcional) Conta Milvus Cloud (para vector database)

## 🚀 Deployment

Este repositório está configurado com **GitHub Actions** para deploy automático na AWS (EC2).

### Fluxo de Deploy
1.  Qualquer push na branch `main` dispara o workflow de deploy.
2.  A imagem Docker é construída e enviada para o Amazon ECR.
3.  O serviço na instância EC2 é atualizado via AWS Systems Manager (SSM).

### Configuração Necessária
Certifique-se de que as seguintes Secrets estão configuradas no repositório:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`

## 🚀 Setup Completo do Projeto (Local)

O BoviCare é uma aplicação de microserviços composta por 3 repositórios separados. Para executar a aplicação completa, você precisa clonar todos os repositórios.

### 1. Clone Todos os Repositórios

Crie uma pasta para o projeto e clone os 3 repositórios:

```bash
# Criar pasta do projeto
mkdir BoviCare
cd BoviCare

# Clonar os repositórios
git clone <URL_DO_REPOSITORIO_RAG> RAG
git clone <URL_DO_REPOSITORIO_BACKEND> bovicare-api
git clone <URL_DO_REPOSITORIO_FRONTEND> bovicare-web
```

**Estrutura esperada:**
```
BoviCare/
├── RAG/                    # Serviço RAG (FastAPI)
├── bovicare-api/           # Backend API (Flask) - ESTE REPOSITÓRIO
│   ├── docker-compose.yml  # ← Docker Compose está aqui!
│   ├── app/
│   ├── Dockerfile
│   └── ...
└── bovicare-web/           # Frontend (React)
```

### 2. Configure o Arquivo `.env`

Crie um arquivo `.env` na raiz do diretório `bovicare-api` (mesmo nível do `docker-compose.yml`):

```bash
cd bovicare-api
touch .env
```

Adicione as seguintes variáveis ao arquivo `.env`:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Milvus Vector Database (cloud)
MILVUS_URI=https://your-instance.milvus.io
MILVUS_TOKEN=your_milvus_token_here

# Optional: Email Configuration
EMAIL_USER=your_email@example.com
EMAIL_PASSWORD=your_email_password_here
```

**Nota:** Se `MILVUS_URI` e `MILVUS_TOKEN` não forem fornecidos, o sistema usará uma instância local do Milvus.

### 3. Execute com Docker Compose

A partir do diretório `bovicare-api`, execute:

```bash
# Construir e iniciar todos os serviços
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar todos os serviços
docker-compose down

# Reconstruir após mudanças no código
docker-compose up -d --build
```

### 4. Acesse a Aplicação

Após iniciar os serviços, você pode acessar:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5003
- **RAG Service**: http://localhost:8000
- **RAG API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

## 📁 Estrutura do Projeto

```
bovicare-api/
├── app/                    # Código da aplicação Flask
│   ├── __init__.py        # Inicialização da app
│   ├── routes.py          # Rotas da API
│   ├── models.py          # Modelos do banco de dados
│   ├── rag_client.py      # Cliente HTTP para RAG service
│   └── ...
├── instance/              # Banco de dados SQLite (desenvolvimento)
├── config.py             # Configurações
├── requirements.txt      # Dependências Python
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestração de todos os serviços
└── README.md            # Este arquivo
```

## 🔧 Desenvolvimento Local (Sem Docker)

Se preferir executar sem Docker:

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export FLASK_APP=app
export FLASK_ENV=development

# Executar
python run.py
```

**Nota:** Para desenvolvimento local, você precisará ter o RAG service rodando separadamente. Veja o README do repositório RAG para instruções.

## 🔑 Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `OPENAI_API_KEY` | Chave da API OpenAI | Sim |
| `MILVUS_URI` | URI do Milvus (cloud) | Não |
| `MILVUS_TOKEN` | Token do Milvus | Não |
| `EMAIL_USER` | Email para notificações | Não |
| `EMAIL_PASSWORD` | Senha do email | Não |

## 🐳 Docker Compose

O arquivo `docker-compose.yml` neste repositório orquestra todos os serviços:

- **rag-service**: Serviço RAG (FastAPI) na porta 8000
- **backend**: API Flask na porta 5003
- **frontend**: Aplicação React na porta 3000
- **db**: Banco de dados PostgreSQL na porta 5432

## 📝 Notas Importantes

1. **Localização do docker-compose.yml**: O arquivo `docker-compose.yml` está no repositório `bovicare-api` e deve ser executado a partir deste diretório.

2. **Estrutura de Diretórios**: Os caminhos no `docker-compose.yml` assumem que os 3 repositórios (`RAG`, `bovicare-api`, `bovicare-web`) estão no mesmo diretório pai.

3. **Arquivo .env**: O arquivo `.env` deve estar no diretório `bovicare-api` (mesmo nível do `docker-compose.yml`).

## 🐛 Troubleshooting

### Erro: "Cannot connect to database"
- Verifique se o serviço `db` está rodando: `docker-compose ps`
- Verifique os logs: `docker-compose logs db`

### Erro: "RAG service unavailable"
- Verifique se o serviço `rag-service` está rodando: `docker-compose ps`
- Verifique os logs: `docker-compose logs rag-service`
- Verifique se `OPENAI_API_KEY` está configurada no `.env`

### Erro: "Cannot find module"
- Reconstrua os containers: `docker-compose up -d --build`

## 📄 Licença

Este projeto está licenciado sob a licença MIT.
