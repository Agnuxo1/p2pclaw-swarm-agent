FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables (to be overridden in deployment)
# Default HF tokens (should be overridden via env vars in production)
ENV AGENT_ID=p2pclaw-swarm-agent \
    AGENT_NAME="P2PCLAW Swarm Agent" \
    P2P_API_BASE=https://api-production-ff1b.up.railway.app \
    HF_MODEL=Qwen/Qwen2.5-72B-Instruct \
    HF_MODEL_FAST=meta-llama/Llama-3.3-70B-Instruct

# Run agent
CMD ["python", "agent.py"]
