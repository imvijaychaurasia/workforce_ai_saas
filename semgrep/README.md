# Semgrep Module for SaaS AI Platform

This module provides code and security scanning using Semgrep, containerized for multi-tenant orchestration.

## Usage
- Build the Docker image:
  ```bash
  docker build -t semgrep-module .
  ```
- Run a scan:
  ```bash
  docker run --rm semgrep-module '{"target": "/app", "rules": "auto"}'
  ```

## API Integration
- The backend will orchestrate this container per tenant and capture scan results.
- Input: JSON string with `target` (directory/file to scan) and `rules` (Semgrep config or rule set).
- Output: JSON with command, stdout, stderr, and return code.

## Example
```json
{
  "target": "./src",
  "rules": "auto"
}
```
