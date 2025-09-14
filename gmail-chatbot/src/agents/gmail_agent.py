from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import json

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "Lista de mensagens da conversa"]
    user_query: str  # Pergunta original do usuário
    intent: str  # Que tipo de ação no Gmail (buscar, contar, etc)
    gmail_data: dict  # Dados retornados do Gmail via MCP
    formatted_response: str  # Resposta final formatada


def analyze_intent(state: AgentState) -> AgentState:
    """Analisa a intenção do usuário - que tipo de busca no Gmail fazer"""
    query = state["user_query"].lower()
    
    # Lógica simples para determinar intenção
    if "últimos" in query or "recentes" in query:
        intent = "recent_emails"
    elif "não lidos" in query or "unread" in query:
        intent = "unread_emails"
    elif "de:" in query or "from:" in query:
        intent = "search_by_sender"
    elif "assunto" in query or "subject:" in query:
        intent = "search_by_subject"
    else:
        intent = "general_search"
    
    state["intent"] = intent
    return state

def search_gmail(state: AgentState) -> AgentState:
    """Busca dados no Gmail usando MCP (placeholder por enquanto)"""
    intent = state["intent"]
    
    # Por enquanto vamos simular dados do Gmail
    mock_gmail_data = {
        "recent_emails": {
            "count": 5,
            "emails": [
                {"from": "joão@example.com", "subject": "Reunião amanhã", "date": "2025-09-13"},
                {"from": "maria@example.com", "subject": "Relatório mensal", "date": "2025-09-12"}
            ]
        },
        "unread_emails": {
            "count": 3,
            "emails": [
                {"from": "sistema@bank.com", "subject": "Extrato disponível", "date": "2025-09-13"}
            ]
        }
    }
    
    # Simula busca baseada na intenção
    if intent in mock_gmail_data:
        state["gmail_data"] = mock_gmail_data[intent]
    else:
        state["gmail_data"] = {"count": 0, "emails": [], "message": "Nenhum email encontrado"}
    
    return state

def format_response(state: AgentState) -> AgentState:
    """Formata a resposta de forma legível para o usuário"""
    gmail_data = state["gmail_data"]
    
    if gmail_data["count"] == 0:
        response = "Não encontrei emails com esses critérios."
    else:
        response = f"Encontrei {gmail_data['count']} email(s):\n\n"
        
        for email in gmail_data["emails"]:
            response += f"• **De:** {email['from']}\n"
            response += f"  **Assunto:** {email['subject']}\n"
            response += f"  **Data:** {email['date']}\n\n"
    
    state["formatted_response"] = response
    return state

class GmailAgent:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Constrói o grafo do agente com LangGraph"""
        
        # Criar o grafo
        workflow = StateGraph(AgentState)
        
        # Adicionar nós (estados)
        workflow.add_node("analyze", analyze_intent)
        workflow.add_node("search", search_gmail)
        workflow.add_node("format", format_response)
        
        # Definir o fluxo (edges)
        workflow.set_entry_point("analyze")  # Começa aqui
        workflow.add_edge("analyze", "search")  # analyze → search
        workflow.add_edge("search", "format")   # search → format
        workflow.add_edge("format", END)        # format → FIM
        
        return workflow.compile()
    
    def process_query(self, user_query: str) -> str:
        """Processa uma pergunta do usuário sobre Gmail"""
        
        # Estado inicial
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "intent": "",
            "gmail_data": {},
            "formatted_response": ""
        }
        
        # Executar o grafo
        result = self.graph.invoke(initial_state)
        
        return result["formatted_response"]

if __name__ == "__main__":
    # Importa nosso cliente Ollama
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'llm'))
    from ollama_client import OllamaClient
    
    # Criar agente
    ollama = OllamaClient()
    agent = GmailAgent(ollama)
    
    # Testar diferentes tipos de pergunta
    test_queries = [
        "Quais são meus últimos emails?",
        "Quantos emails não lidos eu tenho?",
        "Me mostre emails recentes"
    ]
    
    for query in test_queries:
        print(f"\n Pergunta: {query}")
        response = agent.process_query(query)
        print(f"Resposta: {response}")