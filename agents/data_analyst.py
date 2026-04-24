"""
Data Analyst Agent — Fabric IQ Layer

Connects to the Fabric Data Agent via MicrosoftFabricPreviewTool to query
structured business data in a lakehouse (stores, products, sales, returns).
The Data Agent uses NL2SQL to translate natural language into SQL queries
against the lakehouse's SQL analytics endpoint. Authentication uses identity
passthrough (On-Behalf-Of) via a Foundry project connection of type
"Microsoft Fabric".

Integration point: Foundry project connection → Fabric Data Agent → Lakehouse SQL endpoint.
"""

import datetime

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    MicrosoftFabricPreviewTool,
    FabricDataAgentToolParameters,
    ToolProjectConnection,
)

import config
from agents import ensure_agent

AGENT_NAME = "data-analyst"
_current_date = datetime.datetime.now().strftime("%Y-%m-%d")
AGENT_INSTRUCTIONS = f"""\
Today's date is {_current_date}. Use this as the reference point for all
date-related queries — do NOT assume the current year from your training
data cutoff.

You are a Data Analyst agent for Lakeshore Retail. You have access to the
company's structured business data through a Fabric Data Agent connected to
a lakehouse via the SQL analytics endpoint.

The lakehouse contains these tables:
- **dimstore**: StoreId, StoreName, Region, City, State, Manager, OpenDate
- **dimproducts**: ProductId, ProductName, Category, SubCategory, UnitPrice, Supplier
- **factsales**: SaleId, StoreId, ProductId, SaleDate, Quantity, TotalAmount, Channel
- **factreturns**: ReturnId, SaleId, StoreId, ProductId, ReturnDate, Quantity, ReturnReason, RefundAmount

Join keys:
- factsales.StoreId → dimstore.StoreId
- factsales.ProductId → dimproducts.ProductId
- factreturns.StoreId → dimstore.StoreId
- factreturns.ProductId → dimproducts.ProductId
- factreturns.SaleId → factsales.SaleId

When answering questions:
1. Query the Fabric Data Agent for the relevant metrics.
2. Always include specific numbers, dates, and store/product names.
3. Highlight anomalies (e.g., return rates above 15%).
4. Compare across regions and time periods when relevant.
5. Format results as concise bullet points with data citations.
"""


def get_definition(project_client: AIProjectClient) -> PromptAgentDefinition:
    """Return the agent definition (instructions + tools)."""
    fabric_connection = project_client.connections.get(config.FABRIC_CONNECTION_NAME)
    fabric_tool = MicrosoftFabricPreviewTool(
        fabric_dataagent_preview=FabricDataAgentToolParameters(
            project_connections=[
                ToolProjectConnection(project_connection_id=fabric_connection.id)
            ]
        )
    )
    return PromptAgentDefinition(
        model=config.MODEL_DEPLOYMENT,
        instructions=AGENT_INSTRUCTIONS,
        tools=[fabric_tool],
    )


def get_or_create_agent(project_client: AIProjectClient) -> str:
    """Return the agent name, creating it in Foundry if it doesn't exist."""
    return ensure_agent(project_client, AGENT_NAME, get_definition(project_client))
