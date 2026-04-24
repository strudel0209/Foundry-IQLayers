"""
Centralized configuration loader for the IQ-Grounded AI Agents POC.

Loads settings from a .env file (for local development) or environment
variables (for production/CI). See .env.example for the full list.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# --- Microsoft Foundry ---
FOUNDRY_PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ.get("MODEL_DEPLOYMENT", "gpt-4.1-mini")

# --- Foundry IQ (Azure AI Search Knowledge Base) ---
AZURE_AI_SEARCH_ENDPOINT = os.environ["AZURE_AI_SEARCH_ENDPOINT"]
KNOWLEDGE_BASE_NAME = os.environ.get("KNOWLEDGE_BASE_NAME", "operations-kb")
KB_MCP_CONNECTION_NAME = os.environ.get("KB_MCP_CONNECTION_NAME", "kb-mcp-connection")

# --- Fabric IQ (Data Agent) ---
FABRIC_CONNECTION_NAME = os.environ.get("FABRIC_CONNECTION_NAME", "fabric-data-agent")

# --- Work IQ (M365 MCP) ---
# Tenant ID is required; all M365 MCP URLs include it.
ENTRA_TENANT_ID = os.environ["ENTRA_TENANT_ID"]
_AGENT365_BASE = f"https://agent365.svc.cloud.microsoft/agents/tenants/{ENTRA_TENANT_ID}/servers"

WORK_IQ_MAIL_MCP_URL = (
    os.environ.get("WORK_IQ_MAIL_MCP_URL")
    or f"{_AGENT365_BASE}/mcp_MailTools"
)
WORK_IQ_SHAREPOINT_MCP_URL = (
    os.environ.get("WORK_IQ_SHAREPOINT_MCP_URL")
    or f"{_AGENT365_BASE}/mcp_ODSPRemoteServer"
)

# Per-server Foundry project connections (created when adding Work IQ tools from the catalog)
WORK_IQ_MAIL_CONNECTION = os.environ.get("WORK_IQ_MAIL_CONNECTION", "work-iq-mail")
WORK_IQ_SHAREPOINT_CONNECTION = os.environ.get("WORK_IQ_SHAREPOINT_CONNECTION", "work-iq-sharepoint")

# --- Derived MCP endpoint for Foundry IQ Knowledge Base ---
FOUNDRY_IQ_KB_MCP_URL = (
    f"{AZURE_AI_SEARCH_ENDPOINT}/knowledgebases/"
    f"{KNOWLEDGE_BASE_NAME}/mcp?api-version=2025-11-01-preview"
)
