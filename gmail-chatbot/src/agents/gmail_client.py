# src/mcp/gmail_client.py
"""
Cliente MCP real para se conectar ao servidor Gmail MCP
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types

class GmailMCPClient:
    """Cliente MCP que se conecta ao servidor Gmail MCP via stdio"""
    
    def __init__(self, server_script_path: str = "src/mcp/gmail_server.py"):
        self.server_script_path = server_script_path
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.connected = False
    
    async def connect(self) -> bool:
        """Conecta ao servidor MCP Gmail"""
        try:
            # Configurar parâmetros do servidor stdio
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_script_path],
                env=None
            )
            
            # Conectar via stdio
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = stdio_transport
            
            # Criar sessão
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Inicializar conexão
            await self.session.initialize()
            
            # Listar ferramentas disponíveis
            tools_response = await self.session.list_tools()
            available_tools = [tool.name for tool in tools_response.tools]
            
            print(f"Conectado ao servidor MCP Gmail")
            print(f"Ferramentas disponíveis: {available_tools}")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Erro ao conectar no servidor MCP: {e}")
            return False
    
    async def disconnect(self):
        """Desconecta do servidor MCP"""
        if self.exit_stack:
            await self.exit_stack.aclose()
        self.connected = False
    
    async def get_recent_emails(self, count: int = 5) -> Dict[str, Any]:
        """Busca emails recentes via MCP"""
        if not self.connected or not self.session:
            raise Exception("Cliente MCP não está conectado")
        
        try:
            result = await self.session.call_tool(
                "get_recent_emails",
                arguments={"count": count}
            )
            
            # Extrair resposta do MCP
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                return json.loads(response_text)
            else:
                return {"error": "Resposta vazia do servidor MCP"}
                
        except Exception as e:
            return {"error": f"Erro ao chamar get_recent_emails: {e}"}
    
    async def get_unread_emails(self, count: int = 10) -> Dict[str, Any]:
        """Busca emails não lidos via MCP"""
        if not self.connected or not self.session:
            raise Exception("Cliente MCP não está conectado")
        
        try:
            result = await self.session.call_tool(
                "get_unread_emails",
                arguments={"count": count}
            )
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                return json.loads(response_text)
            else:
                return {"error": "Resposta vazia do servidor MCP"}
                
        except Exception as e:
            return {"error": f"Erro ao chamar get_unread_emails: {e}"}
    
    async def search_emails(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Busca emails por query via MCP"""
        if not self.connected or not self.session:
            raise Exception("Cliente MCP não está conectado")
        
        try:
            result = await self.session.call_tool(
                "search_emails",
                arguments={"query": query, "count": count}
            )
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                return json.loads(response_text)
            else:
                return {"error": "Resposta vazia do servidor MCP"}
                
        except Exception as e:
            return {"error": f"Erro ao chamar search_emails: {e}"}
    
    async def get_email_details(self, message_id: str) -> Dict[str, Any]:
        """Busca detalhes de um email específico via MCP"""
        if not self.connected or not self.session:
            raise Exception("Cliente MCP não está conectado")
        
        try:
            result = await self.session.call_tool(
                "get_email_details",
                arguments={"message_id": message_id}
            )
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                return json.loads(response_text)
            else:
                return {"error": "Resposta vazia do servidor MCP"}
                
        except Exception as e:
            return {"error": f"Erro ao chamar get_email_details: {e}"}

# Teste standalone do cliente MCP
async def test_mcp_client():
    """Testa o cliente MCP Gmail"""
    client = GmailMCPClient()
    
    try:
        print("Conectando ao servidor MCP Gmail...")
        if await client.connect():

            print("\n Verificando as tools existentes...")
            tools = await client.session.list_tools()
            for tool in tools.tools:
                print(f"Ferramenta: {tool.name}")
                print(f"Descrição: {tool.description}")

            print("\nTestando busca de emails recentes...")
            recent = await client.get_recent_emails(count=1)
            print(f"Resultado: {json.dumps(recent, indent=2, ensure_ascii=False)}")
            
            print("\nTestando busca de emails não lidos...")
            unread = await client.get_unread_emails(count=1)
            print(f"Resultado: {json.dumps(unread, indent=2, ensure_ascii=False)}")
            
        else:
            print("Falha na conexão com servidor MCP")
            
    except Exception as e:
        print(f"Erro no teste: {e}")
    
    finally:
        await client.disconnect()
        print("Desconectado do servidor MCP")

if __name__ == "__main__":
    asyncio.run(test_mcp_client())