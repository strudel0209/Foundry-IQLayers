"""
Enterprise Operations Advisor — Orchestrator

Entry point for the IQ-Grounded AI Agents POC. Uses persistent agents
stored in the Foundry project. Agents are created on first run and
automatically updated on subsequent runs.

  1. Data Analyst   (Fabric IQ)  — structured data via lakehouse SQL
  2. Knowledge Agent (Foundry IQ) — SOPs, policies, post-mortems
  3. People Agent    (Work IQ)    — emails, SharePoint docs/lists

The orchestrator decomposes a user question, delegates to specialists,
and synthesizes a unified response with citations and next steps.

Usage:
    python main.py "Why are Vanilla Bean returns spiking in Northeast stores?"

Or run without arguments for the default demo query.
"""

import sys
import datetime

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

import config
from agents import ensure_agent
from agents import data_analyst, knowledge_agent, people_agent

# ---------------------------------------------------------------------------
# Orchestrator agent definition
# ---------------------------------------------------------------------------

ORCHESTRATOR_NAME = "operations-advisor"
ORCHESTRATOR_INSTRUCTIONS = """\
You are the Enterprise Operations Advisor for Lakeshore Retail. You
coordinate three specialist agents to answer cross-functional business
questions by combining structured data, operational knowledge, and
organizational context.

Your specialist agents:
1. **Data Analyst** (Fabric IQ) — queries structured data: sales, returns,
   store metrics, product details via the lakehouse SQL endpoint.
2. **Knowledge Agent** (Foundry IQ) — retrieves SOPs, policies, post-mortem
   reports, and operational procedures from the knowledge base.
3. **People Agent** (Work IQ) — surfaces relevant emails, SharePoint
   documents/lists, and organizational context from Microsoft 365.

When you receive a question:
1. Decompose it into data needs, knowledge needs, and people/context needs.
2. Delegate sub-questions to the appropriate specialist agent(s).
3. Synthesize their responses into a single, actionable briefing.

Your response format:
## Data Summary (Fabric IQ)
<structured metrics and findings>

## Relevant Policies & Procedures (Foundry IQ)
<SOPs, escalation steps, past incident references>

## Organizational Context (Work IQ)
<who is involved, relevant communications, recommended contacts>

## Recommended Actions
<prioritized next steps with owners and deadlines>
"""

DEFAULT_QUERY = (
    "We're seeing a spike in returns for Vanilla Bean ice cream at our "
    "Northeast stores. What's causing it, what do our SOPs say we should "
    "do, and who has dealt with similar issues before?"
)


def _get_orchestrator_definition() -> PromptAgentDefinition:
    return PromptAgentDefinition(
        model=config.MODEL_DEPLOYMENT,
        instructions=ORCHESTRATOR_INSTRUCTIONS,
    )


def _invoke_agent(openai_client, agent_name: str, prompt: str) -> str:
    """Send a prompt to a named agent and return the text response."""
    response = openai_client.responses.create(
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "type": "agent_reference",
            }
        },
        input=prompt,
    )
    return response.output_text


def main(query: str | None = None) -> None:
    """Run the orchestrator with the given query."""
    query = query or DEFAULT_QUERY

    # --- Authenticate & create project client ---
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        endpoint=config.FOUNDRY_PROJECT_ENDPOINT,
        credential=credential,
    )
    openai = project_client.get_openai_client()

    print(f"Connected to Foundry project: {config.FOUNDRY_PROJECT_ENDPOINT}")
    print(f"Model deployment: {config.MODEL_DEPLOYMENT}\n")

    # --- Ensure persistent agents exist (creates or updates) ---
    print("Ensuring agents are provisioned...")
    da_name = data_analyst.get_or_create_agent(project_client)
    print(f"  ✓ Data Analyst    (Fabric IQ)  [{da_name}]")

    kb_name = knowledge_agent.get_or_create_agent(project_client)
    print(f"  ✓ Knowledge Agent (Foundry IQ) [{kb_name}]")

    pa_name = people_agent.get_or_create_agent(project_client)
    print(f"  ✓ People Agent    (Work IQ)    [{pa_name}]")

    orch_name = ensure_agent(
        project_client, ORCHESTRATOR_NAME, _get_orchestrator_definition()
    )
    print(f"  ✓ Orchestrator                 [{orch_name}]\n")

    # --- Run the pipeline ---
    print("=" * 60)
    print(f"QUERY: {query}")
    print("=" * 60)

    # Step 1: Delegate to Data Analyst (Fabric IQ)
    print("\n[1/3] Querying Data Analyst (Fabric IQ)...")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    data_response = _invoke_agent(
        openai, da_name,
        f"Today's date is {today}. Analyze the following from our business data: {query}",
    )
    print("  ✓ Data analysis complete")

    # Step 2: Delegate to Knowledge Agent (Foundry IQ)
    print("[2/3] Querying Knowledge Agent (Foundry IQ)...")
    kb_response = _invoke_agent(
        openai, kb_name,
        f"Find relevant SOPs, policies, and past incidents for: {query}",
    )
    print("  ✓ Knowledge retrieval complete")

    # Step 3: Delegate to People Agent (Work IQ)
    print("[3/3] Querying People Agent (Work IQ)...")
    people_response = _invoke_agent(
        openai, pa_name,
        f"Who has been involved in or knows about: {query}",
    )
    print("  ✓ Organizational context retrieved")

    # Step 4: Orchestrator synthesizes
    print("\n[Synthesis] Generating unified briefing...\n")
    final_response = _invoke_agent(
        openai, orch_name,
        f"""\
Original question: {query}

=== DATA ANALYST FINDINGS (Fabric IQ) ===
{data_response}

=== KNOWLEDGE BASE FINDINGS (Foundry IQ) ===
{kb_response}

=== ORGANIZATIONAL CONTEXT (Work IQ) ===
{people_response}

Please synthesize these findings into a unified briefing with recommended
actions. Cite the source layer (Fabric IQ / Foundry IQ / Work IQ) for
each finding.
""",
    )

    # --- Display results ---
    print("=" * 60)
    print("OPERATIONS ADVISOR BRIEFING")
    print("=" * 60)
    print(final_response)


if __name__ == "__main__":
    user_query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    main(user_query)
