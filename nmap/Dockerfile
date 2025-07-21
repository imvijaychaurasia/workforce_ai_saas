# Nmap Dockerfile for SaaS AI Platform
FROM alpine:latest
LABEL maintainer="SaaS AI Platform"

RUN apk add --no-cache nmap python3 py3-pip

WORKDIR /scan

COPY nmap_scan.py ./

ENTRYPOINT ["python3", "nmap_scan.py"]
