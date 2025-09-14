FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY src/ ./src/
COPY . .

# Expor porta do Streamlit
EXPOSE 8501

# Comando para executar
CMD ["streamlit", "run", "src/app.py", "--server.address", "0.0.0.0"]