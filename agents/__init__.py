"""
Agent lifecycle helpers for persistent Foundry agents.

Agents are stored as named, versioned assets in Microsoft Foundry.
create_version() is idempotent — it creates the agent on first run
and updates it with a new version on subsequent runs.
"""

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition


def ensure_agent(
    project_client: AIProjectClient,
    agent_name: str,
    definition: PromptAgentDefinition,
) -> str:
    """Create or update a named agent in Foundry.

    Returns the agent name (used as the identifier in the responses API).
    """
    agent = project_client.agents.create_version(
        agent_name=agent_name,
        definition=definition,
    )
    return agent.name