FROM ollama/ollama:latest

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application files
COPY . .

# Pull models in advance
RUN ollama pull llama3.1

# Expose ports for Ollama and Streamlit
EXPOSE 11434 8501

# Start both Ollama and Streamlit
CMD ["sh", "-c", "ollama serve & python3 -m streamlit run app.py"]
