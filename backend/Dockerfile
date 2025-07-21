# Dockerfile for FastAPI Backend
# Multi-tenant aware, config via ENV

FROM python:3.11-slim
WORKDIR /app
# Only copy main.py and requirements.txt to avoid stray files
COPY main.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 9000
# Use --reload for development (remove for production)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]
