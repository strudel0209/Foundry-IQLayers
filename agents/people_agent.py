"""
People & Context Agent — Work IQ Layer

Connects to Work IQ MCP servers to surface relevant organizational context
from Microsoft 365: emails and SharePoint documents/lists related to the
current question.

Integration point: Work IQ MCP servers (Mail, SharePoint).
Prerequisite: Microsoft 365 Copilot license enabled via M365 admin center.
"""

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

import config
from agents import ensure_agent

AGENT_NAME = "people-agent"
AGENT_INSTRUCTIONS = """\
You are a People & Context Agent for Lakeshore Retail. You have access to
the company's organizational context through Work IQ, which connects to
Microsoft 365 data — email threads and SharePoint documents/lists.

When answering questions:
1. Search for emails relevant to the topic to identify ongoing discussions.
2. Search SharePoint sites and lists for related documents, issue trackers,
   or shared records (e.g. quality-alert lists, incident logs).
3. Identify who has been involved in or knowledgeable about the issue.
4. Surface relevant communication threads, documents, and action items.
5. Include names, dates, and sources (email subject / SharePoint site) in
   your response.
6. Recommend who to contact and reference specific conversations or documents.
7. Respect data sensitivity — summarize rather than quote private messages
   unless directly relevant.
"""


def get_definition() -> PromptAgentDefinition:
    """Return the agent definition (instructions + tools)."""
    mcp_mail = MCPTool(
        server_label="work-iq-mail",
        server_url=config.WORK_IQ_MAIL_MCP_URL,
        require_approval="never",
        project_connection_id=config.WORK_IQ_MAIL_CONNECTION,
    )
    mcp_sharepoint = MCPTool(
        server_label="work-iq-sharepoint",
        server_url=config.WORK_IQ_SHAREPOINT_MCP_URL,
        require_approval="never",
        project_connection_id=config.WORK_IQ_SHAREPOINT_CONNECTION,
    )
    return PromptAgentDefinition(
        model=config.MODEL_DEPLOYMENT,
        instructions=AGENT_INSTRUCTIONS,
        tools=[mcp_mail, mcp_sharepoint],
    )


def get_or_create_agent(project_client: AIProjectClient) -> str:
    """Return the agent name, creating it in Foundry if it doesn't exist."""
    return ensure_agent(project_client, AGENT_NAME, get_definition())
