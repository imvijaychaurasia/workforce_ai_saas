# Nmap Module for SaaS AI Platform

This module provides network scanning and monitoring using Nmap, containerized for multi-tenant orchestration.

## Usage
- Build the Docker image:
  ```bash
  docker build -t nmap-module .
  ```
- Run a scan:
  ```bash
  docker run --rm nmap-module '{"targets": ["192.168.1.1"], "options": "-sV"}'
  ```

## API Integration
- The backend will orchestrate this container per tenant and capture scan results.
- Input: JSON string with `targets` (list of IPs/hosts) and `options` (Nmap CLI options).
- Output: JSON with command, stdout, stderr, and return code.

## Example
```json
{
  "targets": ["scanme.nmap.org"],
  "options": "-A"
}
```
