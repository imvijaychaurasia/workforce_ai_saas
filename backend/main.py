

import os
import logging
import http.client as http_client
import json
import subprocess
import uuid
from datetime import datetime
from typing import Optional

import docker
import requests
from fastapi import FastAPI, Depends, Request, HTTPException, status, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenID
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, JSON, Table, MetaData
from sqlalchemy.orm import sessionmaker, Session
import chromadb
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from crewai import Agent, Task, Crew, Process
from cryptography.fernet import Fernet
import hvac
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- FastAPI App Initialization ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="SaaS AI Platform API",
    description="Multi-tenant, modular SaaS AI backend.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")
# http_client.HTTPConnection.debuglevel = 1  # Uncomment for detailed HTTP requests debugging

# --- Environment Variables & Configuration ---
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://keycloak:keycloak@postgres:5432/keycloak")
KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://keycloak:8080/")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "saas-platform")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "saas-frontend")
N8N_URL = os.environ.get("N8N_URL", "http://n8n:5678")
CHROMA_URL = os.environ.get("CHROMA_URL", "http://chromadb:8000")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp-server:3002")
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())
VAULT_URL = os.environ.get("VAULT_URL", "http://vault:8200")
VAULT_TOKEN = os.environ.get("VAULT_TOKEN", "root")

# --- Vault Client ---
vault_client = hvac.Client(url=VAULT_URL, token=VAULT_TOKEN)

# --- ChromaDB Client ---
chroma_client = chromadb.HttpClient(host=CHROMA_URL, port=8000)
embeddings = OllamaEmbeddings(base_url=OLLAMA_URL)
llm = Ollama(base_url=OLLAMA_URL)

# --- Database Setup ---
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# --- Database Tables ---
modules_table = Table(
    "modules_registry", metadata,
    Column("name", String, primary_key=True),
    Column("image", String, nullable=False),
    Column("description", Text),
    Column("config_schema", JSON)
)

tenant_modules_table = Table(
    "tenant_modules", metadata,
    Column("tenant_id", String, primary_key=True),
    Column("module_name", String, primary_key=True),
    Column("config", JSON)
)

nmap_results_table = Table(
    "nmap_scan_results", metadata,
    Column("scan_id", String, primary_key=True),
    Column("tenant_id", String, index=True),
    Column("targets", JSON),
    Column("options", String),
    Column("result", JSON),
    Column("timestamp", String)
)

semgrep_results_table = Table(
    "semgrep_scan_results", metadata,
    Column("scan_id", String, primary_key=True),
    Column("tenant_id", String, index=True),
    Column("target", String),
    Column("rules", String),
    Column("result", JSON),
    Column("timestamp", String)
)

module_orchestrations_table = Table(
    "module_orchestrations", metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, index=True),
    Column("name", String),
    Column("pipeline", JSON)
)

providers_table = Table(
    "providers", metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, index=True),
    Column("name", String),
    Column("encrypted_config", Text)
)

audit_log_table = Table(
    "audit_log", metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, index=True),
    Column("user_id", String),
    Column("action", String),
    Column("details", JSON),
    Column("timestamp", String)
)

documents_table = Table(
    "documents", metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, index=True),
    Column("module_id", String, index=True),
    Column("name", String),
    Column("path", String),
    Column("timestamp", String)
)

usage_metrics_table = Table(
    "usage_metrics", metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, index=True),
    Column("metric_name", String),
    Column("value", JSON),
    Column("timestamp", String)
)

migration_model_table = Table(
    "migration_model", metadata,
    Column("id", String, primary_key=True),
    Column("name", String),
    Column("applied_on", String)
)

metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Dependency for Database Session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Audit Log Helper ---
def log_audit_event(db: Session, tenant_id: str, user_id: str, action: str, details: dict):
    """Logs an audit event to the database."""
    db.execute(audit_log_table.insert().values(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        details=details,
        timestamp=datetime.utcnow().isoformat()
    ))
    db.commit()

# --- Encryption/Decryption Helpers ---
def encrypt_data(data: dict) -> str:
    return cipher_suite.encrypt(json.dumps(data).encode()).decode()

def decrypt_data(encrypted_data: str) -> dict:
    return json.loads(cipher_suite.decrypt(encrypted_data.encode()).decode())

# --- Usage Metrics Helper ---
def record_usage(db: Session, tenant_id: str, metric_name: str, value: dict):
    """Records a usage metric to the database."""
    db.execute(usage_metrics_table.insert().values(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        metric_name=metric_name,
        value=value,
        timestamp=datetime.utcnow().isoformat()
    ))
    db.commit()

# --- Authentication Setup ---
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates token and returns user info."""
    try:
        public_key = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
        return keycloak_openid.decode_token(token, key=public_key, options={"verify_signature": True, "verify_aud": False, "exp": True})
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_tenant(request: Request) -> str:
    """Extracts tenant ID from request headers, defaults to 'default'."""
    return request.headers.get("X-Tenant-ID", "default")

# --- Pydantic Models (Request/Response Schemas) ---
class ModuleActivateRequest(BaseModel):
    module_name: str
    config: Optional[dict] = None

class ModuleRegisterRequest(BaseModel):
    name: str
    image: str
    description: Optional[str] = None
    config_schema: Optional[dict] = None

class NmapScanRequest(BaseModel):
    targets: list
    options: Optional[str] = "-sV"

class SemgrepScanRequest(BaseModel):
    target: str
    rules: Optional[str] = "auto"

class WorkflowCreateRequest(BaseModel):
    name: str
    definition: dict

class OrchestrationCreateRequest(BaseModel):
    name: str
    pipeline: list[dict]

class ProviderCreateRequest(BaseModel):
    name: str
    config: dict

class DocumentUploadRequest(BaseModel):
    module_id: str
    name: str

# --- API Endpoints ---

# --- Protected Test Endpoint ---
@app.get("/protected", summary="Protected endpoint", tags=["Auth"])
@limiter.limit("5/minute")
def protected(request: Request, user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {user.get('preferred_username', 'user')}!"}

# --- Tenant Management Endpoints ---
@app.post("/tenants", summary="Create tenant", tags=["Tenants"])
def create_tenant(data: dict, tenant: str = Depends(get_tenant), user: dict = Depends(get_current_user)):
    return {"id": "new_tenant", "status": "created"}

# --- User Management Endpoints ---
@app.get("/users", summary="List users", tags=["Users"])
def list_users(tenant: str = Depends(get_tenant), user: dict = Depends(get_current_user)):
    return [{"id": f"user1_{tenant}"}]

@app.post("/users", summary="Create user", tags=["Users"])
def create_user(data: dict, tenant: str = Depends(get_tenant), user: dict = Depends(get_current_user)):
    return {"id": "new_user", "status": "created"}

# --- Inventory Management Endpoints ---
@app.get("/inventory", summary="List inventory", tags=["Inventory"])
def list_inventory(tenant: str = Depends(get_tenant), user: dict = Depends(get_current_user)):
    return [{"id": f"item1_{tenant}"}]

@app.post("/inventory", summary="Create inventory item", tags=["Inventory"])
def create_inventory(data: dict, tenant: str = Depends(get_tenant), user: dict = Depends(get_current_user)):
    return {"id": "new_item", "status": "created"}

# --- Module Management Endpoints ---
@app.get("/modules", summary="List available modules", tags=["Modules"])
def list_available_modules(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Lists all modules in the registry."""
    modules = db.execute(modules_table.select()).fetchall()
    return [dict(m) for m in modules]

@app.get("/modules/active", summary="List active modules for tenant", tags=["Modules"])
def list_active_modules(tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Lists active modules for the current tenant."""
    rows = db.execute(tenant_modules_table.select().where(tenant_modules_table.c.tenant_id == tenant)).fetchall()
    return [r.module_name for r in rows]

@app.post("/modules/activate", summary="Activate module for tenant", tags=["Modules"])
def activate_module(req: ModuleActivateRequest, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Activates a module for the current tenant by launching a Docker container."""
    module_row = db.execute(modules_table.select().where(modules_table.c.name == req.module_name)).fetchone()
    if not module_row:
        raise HTTPException(status_code=404, detail="Module not found")

    db.execute(tenant_modules_table.insert().values(tenant_id=tenant, module_name=req.module_name, config=req.config))
    db.commit()

    try:
        client = docker.from_env()
        container_name = f"{tenant}-{req.module_name}"
        env_vars = {"TENANT_ID": tenant, "MODULE_CONFIG": json.dumps(req.config)}
        client.containers.run(
            module_row.image,
            name=container_name,
            environment=env_vars,
            detach=True,
            network="default",
            restart_policy={"Name": "unless-stopped"}
        )
        log_audit_event(db, tenant, user.get("sub"), "activate_module", {"module_name": req.module_name})
        return {"status": "activated", "module": req.module_name, "tenant": tenant}
    except docker.errors.APIError as e:
        logger.error(f"Docker error activating module {req.module_name} for tenant {tenant}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to activate module: {e}")

@app.post("/modules/deactivate", summary="Deactivate module for tenant", tags=["Modules"])
def deactivate_module(req: ModuleActivateRequest, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Deactivates a module for the current tenant by stopping and removing its container."""
    db.execute(tenant_modules_table.delete().where(
        (tenant_modules_table.c.tenant_id == tenant) & (tenant_modules_table.c.module_name == req.module_name)
    ))
    db.commit()

    try:
        client = docker.from_env()
        container_name = f"{tenant}-{req.module_name}"
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
        log_audit_event(db, tenant, user.get("sub"), "deactivate_module", {"module_name": req.module_name})
        return {"status": "deactivated", "module": req.module_name, "tenant": tenant}
    except docker.errors.NotFound:
        logger.warning(f"Container {container_name} not found for deactivation.")
        return {"status": "deactivated", "module": req.module_name, "tenant": tenant, "info": "Container not found, removed from DB."}
    except docker.errors.APIError as e:
        logger.error(f"Docker error deactivating module {req.module_name} for tenant {tenant}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to deactivate module: {e}")

@app.post("/modules/register", summary="Register a new module", tags=["Modules"])
def register_module(req: ModuleRegisterRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Registers a new module in the system."""
    db.execute(modules_table.insert().values(
        name=req.name,
        image=req.image,
        description=req.description,
        config_schema=req.config_schema
    ))
    db.commit()
    return {"status": "registered", "module": req.name}

# --- Nmap Module Endpoints ---
@app.post("/modules/nmap/scan", summary="Trigger Nmap scan", tags=["Nmap"])
def trigger_nmap_scan(req: NmapScanRequest, request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Triggers an Nmap scan via a Docker container."""
    tenant = get_tenant(request)
    scan_id = str(uuid.uuid4())
    scan_input = json.dumps({"targets": req.targets, "options": req.options})

    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "nmap-module", scan_input],
            capture_output=True, text=True, timeout=180, check=True
        )
        output = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Nmap scan failed for tenant {tenant}: {e}")
        output = {"error": str(e)}

    db.execute(nmap_results_table.insert().values(
        scan_id=scan_id, tenant_id=tenant, targets=req.targets,
        options=req.options, result=output, timestamp=datetime.utcnow().isoformat()
    ))
    db.commit()
    return {"scan_id": scan_id, "result": output}

@app.get("/modules/nmap/results", summary="List Nmap scan results", tags=["Nmap"])
def list_nmap_results(request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    tenant = get_tenant(request)
    rows = db.execute(nmap_results_table.select().where(nmap_results_table.c.tenant_id == tenant)).fetchall()
    return [dict(r) for r in rows]

@app.get("/modules/nmap/results/{scan_id}", summary="Get Nmap scan result", tags=["Nmap"])
def get_nmap_result(scan_id: str, request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    tenant = get_tenant(request)
    row = db.execute(nmap_results_table.select().where(
        (nmap_results_table.c.scan_id == scan_id) & (nmap_results_table.c.tenant_id == tenant)
    )).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Nmap scan result not found")
    return dict(row)

# --- Semgrep Module Endpoints ---
@app.post("/modules/semgrep/scan", summary="Trigger Semgrep scan", tags=["Semgrep"])
def trigger_semgrep_scan(req: SemgrepScanRequest, request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Triggers a Semgrep scan via a Docker container."""
    tenant = get_tenant(request)
    scan_id = str(uuid.uuid4())
    scan_input = json.dumps({"target": req.target, "rules": req.rules})

    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "semgrep-module", scan_input],
            capture_output=True, text=True, timeout=180, check=True
        )
        output = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Semgrep scan failed for tenant {tenant}: {e}")
        output = {"error": str(e)}

    db.execute(semgrep_results_table.insert().values(
        scan_id=scan_id, tenant_id=tenant, target=req.target,
        rules=req.rules, result=output, timestamp=datetime.utcnow().isoformat()
    ))
    db.commit()
    return {"scan_id": scan_id, "result": output}

@app.get("/modules/semgrep/results", summary="List Semgrep scan results", tags=["Semgrep"])
def list_semgrep_results(request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    tenant = get_tenant(request)
    rows = db.execute(semgrep_results_table.select().where(semgrep_results_table.c.tenant_id == tenant)).fetchall()
    return [dict(r) for r in rows]

@app.get("/modules/semgrep/results/{scan_id}", summary="Get Semgrep scan result", tags=["Semgrep"])
def get_semgrep_result(scan_id: str, request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    tenant = get_tenant(request)
    row = db.execute(semgrep_results_table.select().where(
        (semgrep_results_table.c.scan_id == scan_id) & (semgrep_results_table.c.tenant_id == tenant)
    )).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Semgrep scan result not found")
    return dict(row)

# --- N8N Workflow Endpoints ---
@app.get("/workflows", summary="List N8N workflows", tags=["Workflows"])
def list_workflows(request: Request, user: dict = Depends(get_current_user)):
    """Lists all N8N workflows, scoped by tenant."""
    tenant = get_tenant(request)
    try:
        # N8N does not support tenant-scoping out-of-the-box via API, so we prepend tenant to workflow names.
        response = requests.get(f"{N8N_URL}/api/v1/workflows", timeout=10)
        response.raise_for_status()
        workflows = [w for w in response.json() if w.get('name', '').startswith(f"{tenant}_")]
        return workflows
    except requests.RequestException as e:
        logger.error(f"Could not fetch N8N workflows for tenant {tenant}: {e}")
        raise HTTPException(status_code=502, detail="Could not connect to workflow service.")

@app.post("/workflows", summary="Create N8N workflow", tags=["Workflows"])
def create_workflow(req: WorkflowCreateRequest, request: Request, user: dict = Depends(get_current_user)):
    """Creates a new N8N workflow, scoped by tenant."""
    tenant = get_tenant(request)
    workflow_data = {
        "name": f"{tenant}_{req.name}",
        "nodes": req.definition.get("nodes", []),
        "connections": req.definition.get("connections", {}),
        "active": False
    }
    try:
        response = requests.post(f"{N8N_URL}/api/v1/workflows", json=workflow_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Could not create N8N workflow for tenant {tenant}: {e}")
        raise HTTPException(status_code=502, detail="Could not connect to workflow service.")

@app.post("/workflows/{workflow_id}/trigger", summary="Trigger N8N workflow", tags=["Workflows"])
def trigger_workflow(workflow_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Triggers an N8N workflow execution."""
    tenant = get_tenant(request)
    # Note: Add logic here to ensure the user's tenant owns the workflow_id
    try:
        response = requests.post(f"{N8N_URL}/api/v1/workflows/{workflow_id}/activate", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Could not trigger N8N workflow {workflow_id} for tenant {tenant}: {e}")
        raise HTTPException(status_code=502, detail="Could not connect to workflow service.")

# --- Module Orchestration Endpoints ---
@app.post("/orchestrations", summary="Create a module orchestration", tags=["Orchestrations"])
def create_orchestration(req: OrchestrationCreateRequest, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    orchestration_id = str(uuid.uuid4())
    db.execute(module_orchestrations_table.insert().values(
        id=orchestration_id,
        tenant_id=tenant,
        name=req.name,
        pipeline=req.pipeline
    ))
    db.commit()
    return {"id": orchestration_id, "name": req.name, "pipeline": req.pipeline}

@app.get("/orchestrations", summary="List module orchestrations", tags=["Orchestrations"])
def list_orchestrations(tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rows = db.execute(module_orchestrations_table.select().where(module_orchestrations_table.c.tenant_id == tenant)).fetchall()
    return [dict(r) for r in rows]

@app.get("/orchestrations/{orchestration_id}", summary="Get a module orchestration", tags=["Orchestrations"])
def get_orchestration(orchestration_id: str, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    row = db.execute(module_orchestrations_table.select().where(
        (module_orchestrations_table.c.id == orchestration_id) & (module_orchestrations_table.c.tenant_id == tenant)
    )).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Orchestration not found")
    return dict(row)

@app.put("/orchestrations/{orchestration_id}", summary="Update a module orchestration", tags=["Orchestrations"])
def update_orchestration(orchestration_id: str, req: OrchestrationCreateRequest, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db.execute(module_orchestrations_table.update().where(
        (module_orchestrations_table.c.id == orchestration_id) & (module_orchestrations_table.c.tenant_id == tenant)
    ).values(name=req.name, pipeline=req.pipeline))
    db.commit()
    return {"id": orchestration_id, "status": "updated"}

@app.delete("/orchestrations/{orchestration_id}", summary="Delete a module orchestration", tags=["Orchestrations"])
def delete_orchestration(orchestration_id: str, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db.execute(module_orchestrations_table.delete().where(
        (module_orchestrations_table.c.id == orchestration_id) & (module_orchestrations_table.c.tenant_id == tenant)
    ))
    db.commit()
    return {"id": orchestration_id, "status": "deleted"}

@app.post("/orchestrations/{orchestration_id}/trigger", summary="Trigger a module orchestration", tags=["Orchestrations"])
async def trigger_orchestration(orchestration_id: str, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    row = db.execute(module_orchestrations_table.select().where(
        (module_orchestrations_table.c.id == orchestration_id) & (module_orchestrations_table.c.tenant_id == tenant)
    )).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Orchestration not found")

    pipeline = row.pipeline
    results = []
    for step in pipeline:
        module_name = step.get("module")
        config = step.get("config", {})
        # This is a simplified trigger, a real implementation would be more robust
        # and handle different module types and configs.
        logger.info(f"Triggering module {module_name} with config {config} for tenant {tenant}")
        # Placeholder for actual module execution logic
        results.append({"module": module_name, "status": "triggered", "result": "placeholder"})

    return {"orchestration_id": orchestration_id, "status": "triggered", "results": results}

# --- Provider Integration Endpoints ---
@app.post("/providers", summary="Create a provider integration", tags=["Providers"])
def create_provider(req: ProviderCreateRequest, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    provider_id = str(uuid.uuid4())
    vault_path = f"secret/data/{tenant}/providers/{req.name}"
    vault_client.secrets.kv.v2.create_or_update_secret(path=vault_path, secret=req.config)
    db.execute(providers_table.insert().values(
        id=provider_id,
        tenant_id=tenant,
        name=req.name
    ))
    db.commit()
    return {"id": provider_id, "name": req.name}

@app.get("/providers", summary="List provider integrations", tags=["Providers"])
def list_providers(tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rows = db.execute(providers_table.select().where(providers_table.c.tenant_id == tenant)).fetchall()
    return [dict(r) for r in rows]

@app.get("/providers/{provider_id}", summary="Get a provider integration", tags=["Providers"])
def get_provider(provider_id: str, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    row = db.execute(providers_table.select().where(
        (providers_table.c.id == provider_id) & (providers_table.c.tenant_id == tenant)
    )).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Provider not found")
    vault_path = f"secret/data/{tenant}/providers/{row.name}"
    try:
        secret = vault_client.secrets.kv.v2.read_secret_version(path=vault_path)
        config = secret['data']['data']
    except hvac.exceptions.InvalidPath:
        config = {}
    return {"id": row.id, "name": row.name, "config": config}

@app.put("/providers/{provider_id}", summary="Update a provider integration", tags=["Providers"])
def update_provider(provider_id: str, req: ProviderCreateRequest, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    vault_path = f"secret/data/{tenant}/providers/{req.name}"
    vault_client.secrets.kv.v2.create_or_update_secret(path=vault_path, secret=req.config)
    db.execute(providers_table.update().where(
        (providers_table.c.id == provider_id) & (providers_table.c.tenant_id == tenant)
    ).values(name=req.name))
    db.commit()
    return {"id": provider_id, "status": "updated"}

@app.delete("/providers/{provider_id}", summary="Delete a provider integration", tags=["Providers"])
def delete_provider(provider_id: str, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db.execute(providers_table.delete().where(
        (providers_table.c.id == provider_id) & (providers_table.c.tenant_id == tenant)
    ))
    db.commit()
    log_audit_event(db, tenant, user.get("sub"), "delete_provider", {"provider_id": provider_id})
    return {"id": provider_id, "status": "deleted"}

# --- Audit Log Endpoints ---
@app.get("/audit-log", summary="Get audit log for tenant", tags=["Audit Log"])
def get_audit_log(tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rows = db.execute(audit_log_table.select().where(audit_log_table.c.tenant_id == tenant).order_by(audit_log_table.c.timestamp.desc())).fetchall()
    return [dict(r) for r in rows]

# --- Document Management Endpoints ---
@app.post("/documents/upload", summary="Upload a document", tags=["Documents"])
async def upload_document(file: UploadFile, module_id: str = Form(...), tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    document_id = str(uuid.uuid4())
    file_path = f"/app/uploads/{tenant}/{module_id}/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db.execute(documents_table.insert().values(
        id=document_id,
        tenant_id=tenant,
        module_id=module_id,
        name=file.filename,
        path=file_path,
        timestamp=datetime.utcnow().isoformat()
    ))
    db.commit()
    log_audit_event(db, tenant, user.get("sub"), "upload_document", {"document_id": document_id, "filename": file.filename})
    return {"id": document_id, "filename": file.filename}

@app.get("/documents", summary="List documents", tags=["Documents"])
def list_documents(module_id: str, tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rows = db.execute(documents_table.select().where(
        (documents_table.c.tenant_id == tenant) & (documents_table.c.module_id == module_id)
    )).fetchall()
    # Process and store the document in ChromaDB
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    with open(file_path, "r") as f:
        text = f.read()
    texts = text_splitter.split_text(text)
    collection_name = f"{tenant}_{module_id}"
    Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        collection_name=collection_name,
        client=chroma_client
    )
    return [dict(r) for r in rows]

# --- AI Endpoints ---
@app.post("/ai/ask", summary="Ask a question to the AI", tags=["AI"])
async def ask_ai(question: str, module_id: str, tenant: str = Depends(get_tenant), user: dict = Depends(get_current_user)):
    collection_name = f"{tenant}_{module_id}"
    vectorstore = Chroma(client=chroma_client, collection_name=collection_name, embedding_function=embeddings)
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    try:
        # Try local LLM first
        response = llm.invoke(prompt)
        record_usage(db, tenant, "local_llm_request", {"question": question})
        return {"answer": response, "context": context, "source": "local"}
    except Exception as e:
        logger.warning(f"Local LLM failed: {e}. Falling back to cloud AI.")
        try:
            # Fallback to cloud AI
            response = requests.post(f"{MCP_SERVER_URL}/openai", json={"prompt": prompt})
            response.raise_for_status()
            record_usage(db, tenant, "cloud_llm_request", {"question": question})
            return {"answer": response.json()["choices"][0]["text"], "context": context, "source": "cloud"}
        except requests.RequestException as e:
            logger.error(f"Cloud AI fallback failed: {e}")
            raise HTTPException(status_code=503, detail="All AI services are currently unavailable.")

# --- Usage Metrics Endpoints ---
@app.get("/usage-metrics", summary="Get usage metrics for tenant", tags=["Usage Metrics"])
def get_usage_metrics(tenant: str = Depends(get_tenant), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rows = db.execute(usage_metrics_table.select().where(usage_metrics_table.c.tenant_id == tenant).order_by(usage_metrics_table.c.timestamp.desc())).fetchall()
    return [dict(r) for r in rows]

@app.post("/ai/agent/execute", summary="Execute a task with an AI agent", tags=["AI"])
async def execute_agent_task(task_description: str, tenant: str = Depends(get_tenant), user: dict = Depends(get_current_user)):
    # Define a simple researcher agent
    researcher = Agent(
        role='Researcher',
        goal='Research new AI trends',
        backstory='You are an AI research assistant.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Define a simple research task
    task = Task(
        description=task_description,
        agent=researcher
    )

    # Create and run the crew
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        process=Process.sequential
    )

    result = crew.kickoff()
    return {"result": result}

@app.post("/ai/cloud/ask", summary="Ask a question to a cloud AI service", tags=["AI"])
async def ask_cloud_ai(prompt: str, tenant: str = Depends(get_tenant), user: dict = Depends(get_current_user)):
    try:
        response = requests.post(f"{MCP_SERVER_URL}/openai", json={"prompt": prompt})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Could not connect to MCP-Server: {e}")
        raise HTTPException(status_code=502, detail="Could not connect to AI service.")