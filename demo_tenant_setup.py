#!/usr/bin/env python3
"""
Demo Tenant Setup Script
Creates a demo tenant with all modules enabled and sample data
"""

import os
import json
import requests
import uuid
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json

# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://keycloak:keycloak@localhost:5432/keycloak")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "saas-platform")

# Demo tenant configuration
DEMO_TENANT_ID = "demo-tenant"
DEMO_USER_EMAIL = "testuser"
DEMO_USER_PASSWORD = "testpass"

def setup_database_data():
    """Set up demo data directly in the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔧 Setting up demo modules in registry...")
        
        # Register demo modules
        demo_modules = [
            {
                "name": "document-processor",
                "image": "employee-ai/document-processor:latest",
                "description": "AI-powered document processing and analysis",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "max_file_size": {"type": "integer", "default": 10485760},
                        "supported_formats": {"type": "array", "default": ["pdf", "docx", "txt"]},
                        "ai_model": {"type": "string", "default": "gpt-3.5-turbo"}
                    }
                }
            },
            {
                "name": "data-analyzer",
                "image": "employee-ai/data-analyzer:latest",
                "description": "Advanced data analysis and visualization",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "chart_types": {"type": "array", "default": ["bar", "line", "pie"]},
                        "max_rows": {"type": "integer", "default": 100000}
                    }
                }
            },
            {
                "name": "workflow-automation",
                "image": "employee-ai/workflow-automation:latest",
                "description": "Intelligent workflow automation and orchestration",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "max_concurrent_workflows": {"type": "integer", "default": 10},
                        "timeout_minutes": {"type": "integer", "default": 60}
                    }
                }
            },
            {
                "name": "ai-assistant",
                "image": "employee-ai/ai-assistant:latest",
                "description": "Conversational AI assistant for business tasks",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "personality": {"type": "string", "default": "professional"},
                        "knowledge_base": {"type": "string", "default": "general"}
                    }
                }
            },
            {
                "name": "security-scanner",
                "image": "employee-ai/security-scanner:latest",
                "description": "Automated security scanning and vulnerability assessment",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "scan_depth": {"type": "string", "default": "standard"},
                        "report_format": {"type": "string", "default": "json"}
                    }
                }
            },
            {
                "name": "email-processor",
                "image": "employee-ai/email-processor:latest",
                "description": "Intelligent email processing and categorization",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "auto_reply": {"type": "boolean", "default": False},
                        "categories": {"type": "array", "default": ["urgent", "normal", "low"]}
                    }
                }
            },
            {
                "name": "report-generator",
                "image": "employee-ai/report-generator:latest",
                "description": "Automated report generation and formatting",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "template_style": {"type": "string", "default": "corporate"},
                        "output_formats": {"type": "array", "default": ["pdf", "docx"]}
                    }
                }
            },
            {
                "name": "task-scheduler",
                "image": "employee-ai/task-scheduler:latest",
                "description": "Intelligent task scheduling and resource management",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "max_concurrent_tasks": {"type": "integer", "default": 20},
                        "priority_levels": {"type": "integer", "default": 5}
                    }
                }
            }
        ]
        
        # Insert modules into registry
        for module in demo_modules:
            cur.execute("""
                INSERT INTO modules_registry (name, image, description, config_schema)
                VALUES (%(name)s, %(image)s, %(description)s, %(config_schema)s)
                ON CONFLICT (name) DO UPDATE SET
                    image = EXCLUDED.image,
                    description = EXCLUDED.description,
                    config_schema = EXCLUDED.config_schema
            """, {
                "name": module["name"],
                "image": module["image"],
                "description": module["description"],
                "config_schema": Json(module["config_schema"])
            })
        
        print("✅ Demo modules registered successfully")
        
        # Activate all modules for demo tenant
        print("🚀 Activating modules for demo tenant...")
        for module in demo_modules:
            cur.execute("""
                INSERT INTO tenant_modules (tenant_id, module_name, config)
                VALUES (%(tenant_id)s, %(module_name)s, %(config)s)
                ON CONFLICT (tenant_id, module_name) DO UPDATE SET
                    config = EXCLUDED.config
            """, {
                "tenant_id": DEMO_TENANT_ID,
                "module_name": module["name"],
                "config": Json(module["config_schema"].get("properties", {}))
            })
        
        print("✅ All modules activated for demo tenant")
        
        # Create demo providers
        print("🔗 Setting up demo providers...")
        demo_providers = [
            {
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT_ID,
                "name": "OpenAI",
                "config": Json({
                    "api_key": "demo-openai-key",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 2000
                })
            },
            {
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT_ID,
                "name": "Anthropic",
                "config": Json({
                    "api_key": "demo-anthropic-key",
                    "model": "claude-3-sonnet",
                    "max_tokens": 4000
                })
            },
            {
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT_ID,
                "name": "Google AI",
                "config": Json({
                    "api_key": "demo-google-key",
                    "model": "gemini-pro",
                    "temperature": 0.7
                })
            }
        ]
        
        for provider in demo_providers:
            cur.execute("""
                INSERT INTO providers (id, tenant_id, name, config)
                VALUES (%(id)s, %(tenant_id)s, %(name)s, %(config)s)
                ON CONFLICT (id) DO NOTHING
            """, provider)
        
        print("✅ Demo providers configured")
        
        # Create sample orchestrations
        print("🔄 Creating demo orchestrations...")
        demo_orchestrations = [
            {
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT_ID,
                "name": "Document Processing Pipeline",
                "pipeline": [
                    {"module": "document-processor", "config": {"ai_model": "gpt-3.5-turbo"}},
                    {"module": "data-analyzer", "config": {"chart_types": ["bar", "pie"]}},
                    {"module": "report-generator", "config": {"template_style": "corporate"}}
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT_ID,
                "name": "Security Assessment Workflow",
                "pipeline": [
                    {"module": "security-scanner", "config": {"scan_depth": "deep"}},
                    {"module": "report-generator", "config": {"output_formats": ["pdf"]}},
                    {"module": "email-processor", "config": {"auto_reply": True}}
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT_ID,
                "name": "AI Assistant Integration",
                "pipeline": [
                    {"module": "ai-assistant", "config": {"personality": "helpful"}},
                    {"module": "task-scheduler", "config": {"priority_levels": 3}},
                    {"module": "workflow-automation", "config": {"timeout_minutes": 30}}
                ]
            }
        ]
        
        for orchestration in demo_orchestrations:
            cur.execute("""
                INSERT INTO module_orchestrations (id, tenant_id, name, pipeline)
                VALUES (%(id)s, %(tenant_id)s, %(name)s, %(pipeline)s)
                ON CONFLICT (id) DO NOTHING
            """, {
                "id": orchestration["id"],
                "tenant_id": orchestration["tenant_id"],
                "name": orchestration["name"],
                "pipeline": Json(orchestration["pipeline"])
            })
        
        print("✅ Demo orchestrations created")
        
        # Add sample usage metrics
        print("📊 Generating sample usage metrics...")
        sample_metrics = [
            {"metric_name": "api_requests", "value": {"count": 1250, "period": "last_30_days"}},
            {"metric_name": "documents_processed", "value": {"count": 89, "period": "last_30_days"}},
            {"metric_name": "workflows_executed", "value": {"count": 156, "period": "last_30_days"}},
            {"metric_name": "ai_queries", "value": {"count": 342, "period": "last_30_days"}},
            {"metric_name": "storage_used", "value": {"bytes": 2147483648, "unit": "bytes"}},
            {"metric_name": "active_users", "value": {"count": 24, "period": "last_7_days"}}
        ]
        
        for metric in sample_metrics:
            cur.execute("""
                INSERT INTO usage_metrics (id, tenant_id, metric_name, value, timestamp)
                VALUES (%(id)s, %(tenant_id)s, %(metric_name)s, %(value)s, %(timestamp)s)
            """, {
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT_ID,
                "metric_name": metric["metric_name"],
                "value": Json(metric["value"]),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        print("✅ Sample usage metrics added")
        
        # Add audit log entries
        print("📝 Creating sample audit log entries...")
        sample_audit_events = [
            {"action": "module_activated", "details": {"module": "document-processor"}},
            {"action": "provider_configured", "details": {"provider": "OpenAI"}},
            {"action": "orchestration_created", "details": {"name": "Document Processing Pipeline"}},
            {"action": "user_login", "details": {"user": "testuser"}},
            {"action": "workflow_executed", "details": {"workflow": "Security Assessment Workflow"}},
        ]
        
        for event in sample_audit_events:
            cur.execute("""
                INSERT INTO audit_log (id, tenant_id, user_id, action, details, timestamp)
                VALUES (%(id)s, %(tenant_id)s, %(user_id)s, %(action)s, %(details)s, %(timestamp)s)
            """, {
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT_ID,
                "user_id": "testuser",
                "action": event["action"],
                "details": Json(event["details"]),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        print("✅ Sample audit log entries created")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("🎉 Demo tenant setup completed successfully!")
        print(f"📧 Demo tenant ID: {DEMO_TENANT_ID}")
        print(f"👤 Demo user: {DEMO_USER_EMAIL}")
        print("🔐 All modules are now active and ready to use")
        
    except Exception as e:
        print(f"❌ Error setting up demo tenant: {e}")
        raise

def print_setup_summary():
    """Print a summary of what was set up"""
    print("\n" + "="*60)
    print("🎯 DEMO TENANT SETUP SUMMARY")
    print("="*60)
    print(f"Tenant ID: {DEMO_TENANT_ID}")
    print(f"User Email: {DEMO_USER_EMAIL}")
    print("\n📦 ACTIVATED MODULES:")
    modules = [
        "• Document Processor - AI-powered document analysis",
        "• Data Analyzer - Advanced data visualization", 
        "• Workflow Automation - Intelligent process automation",
        "• AI Assistant - Conversational business AI",
        "• Security Scanner - Vulnerability assessment",
        "• Email Processor - Smart email categorization",
        "• Report Generator - Automated report creation",
        "• Task Scheduler - Intelligent task management"
    ]
    for module in modules:
        print(module)
    
    print("\n🔗 CONFIGURED PROVIDERS:")
    providers = [
        "• OpenAI (GPT-3.5 Turbo)",
        "• Anthropic (Claude-3 Sonnet)", 
        "• Google AI (Gemini Pro)"
    ]
    for provider in providers:
        print(provider)
    
    print("\n🔄 SAMPLE ORCHESTRATIONS:")
    orchestrations = [
        "• Document Processing Pipeline",
        "• Security Assessment Workflow",
        "• AI Assistant Integration"
    ]
    for orchestration in orchestrations:
        print(orchestration)
    
    print("\n📊 SAMPLE DATA:")
    data = [
        "• Usage metrics and analytics",
        "• Audit log entries",
        "• Performance indicators",
        "• Activity history"
    ]
    for item in data:
        print(item)
    
    print("\n🚀 Ready to explore the Employee.AI platform!")
    print("="*60)

if __name__ == "__main__":
    print("🚀 Starting Demo Tenant Setup...")
    print("="*50)
    
    try:
        setup_database_data()
        print_setup_summary()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        exit(1)