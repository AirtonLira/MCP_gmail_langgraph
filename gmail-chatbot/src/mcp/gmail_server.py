# src/mcp/gmail_server.py
"""
Servidor MCP real para Gmail usando o SDK oficial do Model Context Protocol
"""
import asyncio
import json
import os
import pickle
from typing import Any, Dict, List
import base64

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server

# Configurações do Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailMCPServer:
    def __init__(self):
        self.service = None
        self.server = Server("gmail-mcp-server")
        self._setup_tools()
    
    def _setup_tools(self):
        """Registra as ferramentas MCP disponíveis"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """Lista todas as ferramentas disponíveis no servidor MCP"""
            return [
                types.Tool(
                    name="get_recent_emails",
                    description="Busca emails recentes da caixa de entrada",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "integer",
                                "description": "Número de emails para buscar (padrão: 5)",
                                "default": 5
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_unread_emails", 
                    description="Busca emails não lidos",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "integer", 
                                "description": "Número máximo de emails não lidos (padrão: 10)",
                                "default": 10
                            }
                        }
                    }
                ),
                types.Tool(
                    name="search_emails",
                    description="Busca emails usando query do Gmail",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Query de busca do Gmail (ex: 'from:pessoa@email.com', 'subject:reunião')"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Número máximo de emails para retornar (padrão: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_email_details",
                    description="Busca detalhes completos de um email específico",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {
                                "type": "string",
                                "description": "ID da mensagem no Gmail"
                            }
                        },
                        "required": ["message_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent]:
            """Executa uma ferramenta específica"""
            
            if not arguments:
                arguments = {}
            
            # Inicializa Gmail se necessário
            if not self.service:
                await self._initialize_gmail()
            
            try:
                if name == "get_recent_emails":
                    count = arguments.get("count", 5)
                    result = await self._get_recent_emails(count)
                    
                elif name == "get_unread_emails":
                    count = arguments.get("count", 10)
                    result = await self._get_unread_emails(count)
                    
                elif name == "search_emails":
                    query = arguments.get("query", "")
                    count = arguments.get("count", 10)
                    result = await self._search_emails(query, count)
                    
                elif name == "get_email_details":
                    message_id = arguments.get("message_id", "")
                    result = await self._get_email_details(message_id)
                    
                else:
                    result = {"error": f"Ferramenta desconhecida: {name}"}
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
                
            except Exception as e:
                error_result = {"error": f"Erro ao executar {name}: {str(e)}"}
                return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    async def _initialize_gmail(self):
        """Inicializa conexão com Gmail via OAuth"""
        try:
            creds = None
            token_path = "credentials/token.pickle"
            credentials_path = "credentials/credentials.json"
            
            # Carrega token salvo se existir
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # Se não há credenciais válidas, faz autenticação
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        raise FileNotFoundError(
                            f"Credenciais não encontradas em {credentials_path}"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Salva credenciais
                os.makedirs(os.path.dirname(token_path), exist_ok=True)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('gmail', 'v1', credentials=creds)
            
        except Exception as e:
            raise Exception(f"Erro ao inicializar Gmail: {e}")
    
    async def _get_recent_emails(self, count: int) -> Dict[str, Any]:
        """Implementação MCP: busca emails recentes"""
        try:
            result = self.service.users().messages().list(
                userId='me', maxResults=count
            ).execute()
            
            messages = result.get('messages', [])
            emails = []
            
            for message in messages[:count]:
                email_data = await self._get_email_details(message['id'])
                if email_data and 'error' not in email_data:
                    emails.append(email_data)
            
            return {
                "tool": "get_recent_emails",
                "success": True,
                "count": len(emails),
                "emails": emails
            }
            
        except Exception as e:
            return {"error": f"Erro ao buscar emails recentes: {e}"}
    
    async def _get_unread_emails(self, count: int) -> Dict[str, Any]:
        """Implementação MCP: busca emails não lidos"""
        try:
            result = self.service.users().messages().list(
                userId='me', q='is:unread', maxResults=count
            ).execute()
            
            messages = result.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = await self._get_email_details(message['id'])
                if email_data and 'error' not in email_data:
                    emails.append(email_data)
            
            return {
                "tool": "get_unread_emails", 
                "success": True,
                "count": len(emails),
                "emails": emails
            }
            
        except Exception as e:
            return {"error": f"Erro ao buscar emails não lidos: {e}"}
    
    async def _search_emails(self, query: str, count: int) -> Dict[str, Any]:
        """Implementação MCP: busca emails por query"""
        try:
            result = self.service.users().messages().list(
                userId='me', q=query, maxResults=count
            ).execute()
            
            messages = result.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = await self._get_email_details(message['id'])
                if email_data and 'error' not in email_data:
                    emails.append(email_data)
            
            return {
                "tool": "search_emails",
                "query": query,
                "success": True,
                "count": len(emails),
                "emails": emails
            }
            
        except Exception as e:
            return {"error": f"Erro na busca '{query}': {e}"}
    
    async def _get_email_details(self, message_id: str) -> Dict[str, Any]:
        """Implementação MCP: busca detalhes de um email específico"""
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id
            ).execute()
            
            # Extrair headers
            headers = {}
            for header in message['payload'].get('headers', []):
                name = header['name'].lower()
                if name in ['from', 'to', 'subject', 'date']:
                    headers[name] = header['value']
            
            # Extrair corpo
            body = self._extract_body(message['payload'])
            
            return {
                "id": message_id,
                "thread_id": message['threadId'],
                "from": headers.get('from', ''),
                "to": headers.get('to', ''),
                "subject": headers.get('subject', ''),
                "date": headers.get('date', ''),
                "body": body,
                "snippet": message.get('snippet', ''),
                "labels": message.get('labelIds', [])
            }
            
        except Exception as e:
            return {"error": f"Erro ao buscar email {message_id}: {e}"}
    
    def _extract_body(self, payload) -> str:
        """Extrai corpo do email recursivamente"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                elif 'parts' in part:
                    body = self._extract_body(part)
                    if body:
                        break
        else:
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(
                        payload['body']['data']
                    ).decode('utf-8')
        
        return body.strip()

async def main():
    """Função principal que inicia o servidor MCP"""
    gmail_server = GmailMCPServer()
    
    # Executa o servidor MCP via stdio (versão corrigida)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await gmail_server.server.run(
            read_stream,
            write_stream,
            gmail_server.server.create_initialization_options()
        )

if __name__ == "__main__":
    print("Iniciando servidor MCP Gmail...")
    asyncio.run(main())