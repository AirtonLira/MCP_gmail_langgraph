# Gmail Chatbot

Chatbot inteligente que integra Gmail com modelos de linguagem através do protocolo MCP (Model Context Protocol) e LangGraph.

## O que faz

- Interface de chat em Streamlit para conversar com seus emails do Gmail
- Integração com Ollama usando modelo Llama 3.1 8B
- Acesso seguro aos emails através da API do Google Gmail
- Protocolo MCP para comunicação entre o modelo e os serviços
- LangGraph para orquestração de agentes inteligentes

## Requisitos

- Python 3.11 ou superior
- Docker e Docker Compose
- Conta Google com API Gmail habilitada
- Ollama instalado (ou usar o container)

## Instalação

1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd gmail-chatbot
```

2. Configure as credenciais do Google
   - Acesse o Google Cloud Console
   - Crie um projeto e habilite a Gmail API
   - Baixe o arquivo de credenciais JSON
   - Salve como `credentials/credentials.json`

3. Execute com Docker
```bash
docker-compose up -d
```

## Como usar

1. Acesse http://localhost:8501 no navegador
2. Na primeira vez, você será direcionado para autenticar com o Google
3. Após a autenticação, comece a conversar sobre seus emails

## Estrutura do projeto

```
gmail-chatbot/
├── docker-compose.yml          # Orquestração dos containers
├── Dockerfile                  # Container da aplicação
├── requirements.txt            # Dependências Python
├── credentials/                # Credenciais do Google (não versionado)
├── src/
│   ├── app.py                 # Interface Streamlit principal
│   ├── agents/                # Agentes LangGraph
│   ├── mcp/                   # Configuração MCP para Gmail
│   ├── llm/                   # Cliente Ollama
│   └── utils/                 # Utilitários e configurações
└── docker/
    └── ollama/                # Docker personalizado do Ollama
```

## Principais tecnologias

- **Streamlit**: Interface web
- **LangGraph**: Orquestração de agentes
- **MCP (Model Context Protocol)**: Comunicação com serviços
- **Ollama + Llama 3.1**: Modelo de linguagem local
- **Google Gmail API**: Acesso aos emails
- **Docker**: Containerização

## Comandos úteis

Parar os serviços:
```bash
docker-compose down
```

Ver logs:
```bash
docker-compose logs -f
```

Rebuild da aplicação:
```bash
docker-compose build
```

## Configuração avançada

O projeto usa as seguintes portas:
- 8501: Interface Streamlit
- 11434: Ollama API

Para modificar configurações, edite o arquivo `docker-compose.yml`.