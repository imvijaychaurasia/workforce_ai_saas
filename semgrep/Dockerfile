# Semgrep Module Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install semgrep
COPY semgrep_scan.py .
ENTRYPOINT ["python", "semgrep_scan.py"]
