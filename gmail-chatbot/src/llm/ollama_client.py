import requests
import json
from typing import Optional, Dict, Any
import time

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model = model
        self.context = []  # Para manter conversação
    
    def generate(self, prompt: str, stream: bool = False) -> Dict[str, Any]:
        """Gera resposta usando a API do Ollama"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "context": self.context  # Mantém contexto da conversa
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            # Atualiza contexto para próximas mensagens
            if "context" in result:
                self.context = result["context"]
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro na API Ollama: {str(e)}"}

    def chat(self, message: str) -> str:
        """Interface simplificada para chat"""
        result = self.generate(message)
        
        if "error" in result:
            return f"Erro: {result['error']}"
        
        return result.get("response", "Sem resposta")
    
    def reset_context(self):
        """Limpa o contexto da conversa"""
        self.context = []
    
    def get_stats(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai estatísticas da resposta"""
        if "error" in result:
            return {"error": True}
        
        return {
            "duration_seconds": result.get("total_duration", 0) / 1e9,
            "tokens_generated": result.get("eval_count", 0),
            "model": result.get("model", "unknown")
        }

# Teste do cliente
if __name__ == "__main__":
    client = OllamaClient()
    
    print("Testando cliente Ollama...")
    
    # Teste 1: Mensagem simples
    response = client.chat("Olá! Como você está?")
    print(f"Resposta: {response}")
    
    # Teste 2: Continuidade da conversa
    response2 = client.chat("Qual é a capital do Brasil?")
    print(f"Resposta 2: {response2}")