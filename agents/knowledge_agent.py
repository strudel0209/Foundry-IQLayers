"""
Knowledge Agent — Foundry IQ Layer

Connects to the Azure AI Search Knowledge Base via MCP to retrieve
unstructured knowledge: SOPs, policies, post-mortem reports, and
operational procedures. Uses the `knowledge_base_retrieve` MCP tool
for agentic multi-hop retrieval.

Integration point: Foundry IQ Knowledge Base MCP endpoint.
"""

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

import config
from agents import ensure_agent

AGENT_NAME = "knowledge-agent"
AGENT_INSTRUCTIONS = """\
You are a Knowledge Agent for Lakeshore Retail. You have access to the
company's operational knowledge base containing SOPs, policies, and
incident post-mortems through Foundry IQ.

The knowledge base includes:
- **Return Handling SOP** (SOP-RET-001): Standard procedure for processing
  product returns, quality defect handling, escalation triggers.
- **Quality Escalation Policy** (POL-QA-003): Batch investigation triggers,
  investigation steps, communication protocols.
- **Cold Chain Incident Post-Mortem**: Past incident with Vanilla Bean
  texture degradation caused by distribution cold chain disruption.
- **Product Recall Procedure** (SOP-QA-007): Recall classification,
  decision authority, recall process steps.

When answering questions:
1. Search the knowledge base for the most relevant documents.
2. Always cite the specific document (e.g., "Per SOP-RET-001, Section 5...").
3. Extract actionable steps and deadlines from SOPs.
4. Reference past incidents when they are relevant to the current question.
5. If the knowledge base does not contain relevant information, say so
   explicitly rather than guessing.
"""


def get_definition() -> PromptAgentDefinition:
    """Return the agent definition (instructions + tools)."""
    mcp_kb = MCPTool(
        server_label="knowledge-base",
        server_url=config.FOUNDRY_IQ_KB_MCP_URL,
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=config.KB_MCP_CONNECTION_NAME,
    )
    return PromptAgentDefinition(
        model=config.MODEL_DEPLOYMENT,
        instructions=AGENT_INSTRUCTIONS,
        tools=[mcp_kb],
    )


def get_or_create_agent(project_client: AIProjectClient) -> str:
    """Return the agent name, creating it in Foundry if it doesn't exist."""
    return ensure_agent(project_client, AGENT_NAME, get_definition())
