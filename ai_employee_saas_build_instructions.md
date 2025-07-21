# AI Build Instructions for SaaS AI Platform (Phase-wise)

---

## 1. AI Assistant Instructions

**Read this entire document first before generating any code.**\
**Always work in the current phase, step-by-step.**\
**Summarize each phase plan before building.**\
**After each step, wait for user confirmation before proceeding.**\
**When prompted for code, generate only for the current step/phase.**\
**Each service must be dockerized.**\
**Use open-source stacks as specified.**\
**All APIs, models, and logic must be multi-tenant aware.**\
**Keep all config, secrets, and tokens out of source code (use ENV or secrets manager).**\
**Document all endpoints, schema, and Docker configs in comments.**

---

## 2. Project Overview (AI summary purpose)

- **Goal:** Build a multi-tenant, modular SaaS AI platform that automates business operations.
- **Principles:** Open-source, dockerized, API-first, document-driven AI, tenant-isolation, pluggable integrations.
- **Scope:** Foundation first (Phase 1), then modules and integrations, then advanced AI, then scale.

---

## 3. Phase-wise Build Roadmap

### **Phase 1: Core Platform Foundation**

**Goal:** Deploy all core infrastructure in Docker. Build the authentication, tenant, user, module, and inventory services. Implement basic API Gateway (FastAPI) and frontend (React).

#### **Phase 1 Steps:**

1. Set up Docker Compose with:
   - Keycloak (Auth), PostgreSQL (structured), MongoDB (unstructured), ChromaDB (vector), Redis (cache), Ollama (LLM), FastAPI backend, React frontend.
2. Scaffold backend (FastAPI):
   - Auth (OIDC/JWT, Keycloak)
   - CRUD for tenants, users, modules, inventory (multi-tenant)
   - Serve API docs (OpenAPI)
3. Scaffold frontend (React):
   - Login/Signup (OIDC)
   - Dashboard (tasks, activity)
   - Module marketplace (list/activate)
   - Inventory CRUD
   - Minimal AI chat UI (connect to backend, not direct to LLM)
4. Add N8N as workflow engine (as a Docker service).
5. Add basic logging (ELK stack), metrics (Prometheus/Grafana).
6. Validate multi-tenancy: all APIs and UI must scope by tenant.
7. Confirm all services can run/stop independently via Docker Compose.

**Stop and request review before moving to Phase 2.**

---

### **Phase 2: Functional Modules & Integrations**

**Goal:** Add real modules and integrations for business automation.

#### **Phase 2 Steps:**

1. Implement module loader:
   - Allow module containers to be registered/activated per tenant.
2. Integrate Nmap (network scan) as a service/module.
3. Integrate Semgrep (code/CSPM security scan) as a service/module.
4. Integrate Google Workspace, AWS, GitHub, etc., via MCP-Server or N8N connectors.
5. Build per-tenant workflow builder (use N8N, expose via API).
6. Implement per-tenant logging, auditing, and module access control.
7. Extend frontend for:
   - Module configuration/activation
   - Provider integration UI

**Pause for user review before Phase 3.**

---

### **Phase 3: Advanced AI & Extensibility**

**Goal:** Add advanced AI, file ingestion, Q&A, agents, and cloud AI fallback.

#### **Phase 3 Steps:**

1. Add document upload API and UI per module.
2. Implement vector storage (ChromaDB) and RAG workflow for document Q&A.
3. Expose `/ai/ask` and `/ai/upload` endpoints (tenant- and module-scoped).
4. Add AI agents (LangChain Agents, CrewAI, etc.) for task execution.
5. Add integration for cloud AI services (OpenAI, Gemini, Grok, DeepSeek) via MCP-Server plugins.
6. Add logic for AI fallback (local LLM to cloud AI).
7. Ensure all secrets and API keys are stored securely, per tenant.

**Pause for review before Phase 4.**

---

### **Phase 4: Scale, Security, Observability**

**Goal:** Ready for production and growth.

#### **Phase 4 Steps:**

1. Refactor Docker Compose to Kubernetes manifests (if scaling needed).
2. Integrate Vault for secrets management.
3. Harden RBAC and API rate limiting.
4. Meter usage per tenant (analytics).
5. Build out a module/provider marketplace UI.
6. Ensure centralized logging, monitoring, and auditing.

---

## 4. General AI Coding Guidelines

- All source code should be well-commented.
- Each API/service/module must include a README.
- All environment variables and config must be documented.
- When generating database migrations/schemas, prefer SQLAlchemy for Python.
- Use OpenAPI (Swagger) for all REST APIs.
- All endpoints must check tenant-scoping before processing data.
- All modules must log actions with timestamp, tenant, user, and module info.
- Provide example API requests and responses in comments.

---

## 5. Initial Directory Structure

```
/ (repo root)
|-- /backend           # FastAPI code, schemas, Dockerfile
|-- /frontend          # React app, Dockerfile
|-- /n8n               # N8N workflows, config
|-- /ollama            # Ollama LLM setup
|-- /mcp-server        # Integration server, plugins
|-- /docker            # Docker Compose, env, configs
|-- /docs              # Architecture, API docs
|-- README.md
```

---

## 6. On Each Phase

- Summarize what will be built and the relevant APIs.
- Generate code, config, or documentation only for the current phase/step.
- Wait for user review/approval before the next phase.

---

**End of Instructions — AI must read this whole document before building.**


---

## 7. Platform Endpoints, Services, and Credentials

This section provides a comprehensive overview of the SaaS AI platform's services, API endpoints, and default credentials.

### 7.1. Services and Default Credentials

| Service         | URL                       | Default User | Default Password | Notes                               |
|-----------------|---------------------------|--------------|------------------|-------------------------------------|
| Keycloak        | `http://localhost:8080`   | `admin`      | `admin`          | Identity and Access Management      |
| PostgreSQL      | `localhost:5432`          | `keycloak`   | `keycloak`       | Database: `keycloak`                |
| MongoDB         | `mongodb://localhost:27017` | N/A          | N/A              | Unstructured data store             |
| ChromaDB        | `http://localhost:8000`   | N/A          | N/A              | Vector database for AI              |
| Redis           | `redis://localhost:6379`  | N/A          | N/A              | In-memory cache                     |
| Ollama          | `http://localhost:11434`  | N/A          | N/A              | Local LLM service                   |
| Backend API     | `http://localhost:9000`   | N/A          | N/A              | Main FastAPI application            |
| Frontend        | `http://localhost:3000`   | N/A          | N/A              | React-based user interface          |
| n8n             | `http://localhost:5678`   | `admin`      | `admin`          | Workflow automation engine          |
| Elasticsearch   | `http://localhost:9200`   | N/A          | N/A              | Search and analytics engine         |
| Kibana          | `http://localhost:5601`   | N/A          | N/A              | Visualization for Elasticsearch     |
| Prometheus      | `http://localhost:9090`   | N/A          | N/A              | Monitoring and alerting             |
| Grafana         | `http://localhost:3001`   | `admin`      | `admin`          | Analytics and monitoring dashboard  |
| Vault           | `http://localhost:8200`   | N/A          | `root` (token)   | Secrets management                  |

### 7.2. Backend API Endpoints

All endpoints are accessed through the base URL: `http://localhost:9000`

#### Auth
- `GET /protected`: A protected test endpoint to verify authentication.

#### Tenants
- `POST /tenants`: Create a new tenant.

#### Users
- `GET /users`: List users for the current tenant.
- `POST /users`: Create a new user for the current tenant.

#### Inventory
- `GET /inventory`: List inventory items for the current tenant.
- `POST /inventory`: Create a new inventory item.

#### Modules
- `GET /modules`: List all available modules in the registry.
- `GET /modules/active`: List active modules for the current tenant.
- `POST /modules/activate`: Activate a module for the current tenant.
- `POST /modules/deactivate`: Deactivate a module for the current tenant.
- `POST /modules/register`: Register a new module in the system.

#### Nmap Module
- `POST /modules/nmap/scan`: Trigger an Nmap scan.
- `GET /modules/nmap/results`: List Nmap scan results for the tenant.
- `GET /modules/nmap/results/{scan_id}`: Get a specific Nmap scan result.

#### Semgrep Module
- `POST /modules/semgrep/scan`: Trigger a Semgrep scan.
- `GET /modules/semgrep/results`: List Semgrep scan results for the tenant.
- `GET /modules/semgrep/results/{scan_id}`: Get a specific Semgrep scan result.

#### Workflows (n8n)
- `GET /workflows`: List N8N workflows for the tenant.
- `POST /workflows`: Create a new N8N workflow.
- `POST /workflows/{workflow_id}/trigger`: Trigger an N8N workflow.

#### Orchestrations
- `POST /orchestrations`: Create a module orchestration.
- `GET /orchestrations`: List module orchestrations for the tenant.
- `GET /orchestrations/{orchestration_id}`: Get a specific module orchestration.
- `PUT /orchestrations/{orchestration_id}`: Update a module orchestration.
- `DELETE /orchestrations/{orchestration_id}`: Delete a module orchestration.
- `POST /orchestrations/{orchestration_id}/trigger`: Trigger a module orchestration.

#### Providers
- `POST /providers`: Create a provider integration.
- `GET /providers`: List provider integrations for the tenant.
- `GET /providers/{provider_id}`: Get a specific provider integration.
- `PUT /providers/{provider_id}`: Update a provider integration.
- `DELETE /providers/{provider_id}`: Delete a provider integration.

#### Audit Log
- `GET /audit-log`: Get the audit log for the tenant.

#### Documents
- `POST /documents/upload`: Upload a document.
- `GET /documents`: List documents for a module.

#### AI
- `POST /ai/ask`: Ask a question to the AI.
- `POST /ai/agent/execute`: Execute a task with an AI agent.
- `POST /ai/cloud/ask`: Ask a question to a cloud AI service.

#### Usage Metrics
- `GET /usage-metrics`: Get usage metrics for the tenant.
