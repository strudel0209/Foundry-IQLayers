# IQ-Grounded AI Agents — Enterprise Operations Advisor

A Python proof-of-concept demonstrating how **Fabric IQ**, **Foundry IQ**, and **Work IQ** form a unified intelligence layer that grounds AI agents in business data, operational knowledge, and organizational context.

Built on **Microsoft Agent Framework** and **Foundry Agent Service** (2026 GA), using the **MCP protocol** to connect agents to each IQ layer.

---

## What This Demonstrates

An **Operations Advisor** agent answers cross-functional questions by coordinating three specialist agents, each powered by a different IQ layer:

| Agent | IQ Layer | Data Source | Protocol |
|---|---|---|---|
| **Data Analyst** | Fabric IQ | Lakehouse SQL — sales, returns, stores, products | Fabric Data Agent (OBO auth) |
| **Knowledge Agent** | Foundry IQ | SOPs, policies, post-mortem reports | AI Search Knowledge Base MCP |
| **People Agent** | Work IQ | Emails, SharePoint documents/lists | Work IQ MCP Server |

### Example Query

> "We're seeing a spike in returns for Vanilla Bean ice cream at our Northeast stores. What's causing it, what do our SOPs say, and who has dealt with similar issues before?"

The orchestrator:
1. **Fabric IQ** → Queries the lakehouse to find that Vanilla Bean (P001) has 8 of 10 returns with “Quality-Texture” reason, concentrated in stores S001 and S003.
2. **Foundry IQ** → Retrieves SOP-RET-001 (escalation triggers: >5 quality returns in 7 days), the quality escalation policy, and the February cold chain post-mortem.
3. **Work IQ** → Surfaces email threads between Sarah Chen and Tom Richards about the issue, a SharePoint quality-alerts list item, and action items from the weekly ops sync.

Result: A unified briefing with data-backed findings, specific SOP steps, past incident parallels, recommended contacts, and prioritized next steps.

---

## Repository Structure

```
iqs/
├── main.py                    # Orchestrator entry point
├── config.py                  # Environment configuration
├── agents/
│   ├── data_analyst.py        # Fabric IQ — Data Agent (project connection)
│   ├── knowledge_agent.py     # Foundry IQ — Knowledge Base MCP
│   └── people_agent.py        # Work IQ — Work IQ MCP Server
├── mock_data/
│   ├── fabric_iq/             # Structured business data (CSVs + schema)
│   ├── foundry_iq/            # SOPs, policies, post-mortem reports
│   └── work_iq/               # Sample organizational context
├── industry_mappings/         # How to adapt to other industries
└── docs/                      # Architecture, IQ explainer, setup guide
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Azure subscription with:
  - [Microsoft Foundry project](https://learn.microsoft.com/azure/foundry/create-project)
  - [Azure AI Search](https://learn.microsoft.com/azure/search/search-create-service-portal) with knowledge base
  - [Microsoft Fabric workspace](https://learn.microsoft.com/fabric/get-started/create-workspaces) with Data Agent
- Microsoft 365 Copilot license (for Work IQ)

### Option A: Dev Container (Recommended)

This repo includes a dev container configuration with Python 3.12, Azure CLI, and all dependencies pre-installed.

1. Install [Docker](https://www.docker.com/products/docker-desktop) and the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) VS Code extension.
2. Open this repo in VS Code and select **Reopen in Container** when prompted (or run `Dev Containers: Reopen in Container` from the Command Palette).
3. Copy and configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure resource endpoints
   ```
4. Run:
   ```bash
   python main.py
   # Or with a custom query:
   python main.py "Vanilla Bean Classic returns are spiking again at our Northeast stores this March. How bad is it compared to the February incident, what does our escalation policy say we should do right now, and is anyone already on it?"
   ```

> Agents are created in Foundry on first run and automatically updated on subsequent runs.

### Option B: Local Setup

```bash
# Clone and install
git clone <repo-url> && cd iqs
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure resource endpoints

# Run
python main.py
# Or with a custom query:
python main.py "What are our top-selling products in the West region?"
```

See [docs/setup_guide.md](docs/setup_guide.md) for detailed Azure resource provisioning steps.

### Loading Mock Data into Each IQ Layer

The `mock_data/` folder contains sample data for all three IQ layers. Here's how to inject it into each service.

#### Fabric IQ — Load CSVs into a Lakehouse

Source files: `mock_data/fabric_iq/` — `DimStore.csv`, `DimProducts.csv`, `FactSales.csv`, `FactReturns.csv`, `lakehouse_schema.json`

1. In the [Fabric portal](https://app.fabric.microsoft.com), create a **Lakehouse** in your workspace.
2. Select **Get data > Upload files** and upload all four CSVs.
3. For each file, select **… > Load to Tables > New table** to convert to Delta tables. Default table names (lowercase file names) are: `dimstore`, `dimproducts`, `factsales`, `factreturns`.
4. Create a **Data Agent**, add the lakehouse as a data source, select the four tables, and add the agent instructions from `docs/setup_guide.md` step 4d.

**Programmatic alternative** — use the [Fabric Lakehouse REST API](https://learn.microsoft.com/fabric/data-engineering/lakehouse-api#load-a-file-into-a-delta-table):
```http
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/lakehouses/{lakehouseId}/tables/dimstore/load
{ "relativePath": "Files/DimStore.csv", "pathType": "File", "mode": "Overwrite",
  "formatOptions": { "format": "Csv", "header": true, "delimiter": "," } }
```

See the official [Fabric Data Agent docs](https://learn.microsoft.com/fabric/data-science/concept-data-agent) for the full walkthrough.

#### Foundry IQ — Index Documents into a Knowledge Base

Source files: `mock_data/foundry_iq/` — `return_handling_sop.md`, `quality_escalation_policy.md`, `cold_chain_incident_postmortem.md`, `product_recall_procedure.md`

**Via Foundry portal:**
1. In [Microsoft Foundry](https://ai.azure.com), open your project → **Build** → **Knowledge** tab.
2. Create or connect to an Azure AI Search service.
3. Create a **Knowledge Base** and add a knowledge source pointing to these documents.
4. Upload the four `.md` files — AI Search indexes them automatically (Markdown is a [supported format](https://learn.microsoft.com/azure/search/search-how-to-index-azure-blob-markdown)).

**Programmatically** — use the [Azure AI Search knowledge base APIs](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-knowledge-base) or upload via the [Foundry file search tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/file-search):
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())
# Upload each doc, create a vector store, then attach to your agent's knowledge
```

The Knowledge Agent in `agents/knowledge_agent.py` accesses these documents via the `knowledge_base_retrieve` MCP tool.

#### Work IQ — No Upload Needed (Live M365 Data)

Source file: `mock_data/work_iq/work_context_samples.json`

Work IQ queries **live Microsoft 365 data** (emails, SharePoint documents/lists). The `work_context_samples.json` file is a **reference sample** showing what Work IQ responses look like for this POC scenario (email threads between Sarah Chen and Tom Richards about Vanilla Bean returns, SharePoint quality-alert list items, and meeting notes stored in a SharePoint document library).

To produce similar live data for testing:
- **Email**: Send emails in your M365 tenant that match the sample subjects/content.
- **SharePoint**: Create a SharePoint site (e.g. "Quality Alerts") with a list of active alert items, and a document library with meeting notes. The SharePoint MCP server can search sites, lists, list items, and files (≤5 MB).

### Creating the Work IQ MCP Servers
#### Prerequisites

- [Microsoft 365 Copilot license](https://learn.microsoft.com/copilot/microsoft-365/microsoft-365-copilot-licensing)
- [Microsoft Entra](https://learn.microsoft.com/entra/fundamentals/what-is-entra) user account with permission to register applications (or tenant admin assistance)

#### Path A: Register an Enterprise Application in Entra (Pro-Code / Coding Agents)

This is the path for programmatic access from agents, GitHub Copilot CLI, or Claude Code. You register a **public client application** in Entra that has the proper API permissions to call the Work IQ MCP servers.

1. Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com/) (or [Azure portal](https://ms.portal.azure.com/) → Microsoft Entra ID).
2. Select your [tenant](https://learn.microsoft.com/entra/fundamentals/create-new-tenant).
3. Go to **App registrations** → **New registration**.
4. Name it (e.g., `WorkIQ-PublicMCPClient`), select **Accounts in this organizational directory only**, and register.
5. On the **Overview** page, note the **Application (client) ID** and **Directory (tenant) ID**.
6. Go to **API permissions** → **Add a permission**. Add the permissions for each Work IQ server you need:
   - `WorkIQ-MailServer` — for Work IQ Mail
   - `WorkIQ-SharePointRemoteServer` — for Work IQ SharePoint
   - `WorkIQ-CalendarServer` — for Work IQ Calendar
   - (and others as needed from the [Agent 365 tools catalog](https://learn.microsoft.com/microsoft-agent-365/tooling-servers-overview#agent-365-tools-catalog))
7. **Grant admin consent** for the permissions.
8. Go to **Authentication** → **Add a platform** → **Mobile and desktop applications** → set redirect URI to `http://localhost:8080/callback`.
9. Done. Users in your org can now use this client app to authenticate against the Work IQ MCP servers.

The MCP server URLs for the `.env` file follow this pattern:
```
https://agent365.svc.cloud.microsoft/agents/tenants/{tenantId}/servers/mcp_MailTools
https://agent365.svc.cloud.microsoft/agents/tenants/{tenantId}/servers/mcp_SharePointRemoteServer
```

Alternatively, you can use the PowerShell approach — see [Manage apps with Entra PowerShell](https://learn.microsoft.com/powershell/entra-powershell/manage-apps).

#### Path B: Enable via Microsoft 365 Admin Center (IT Admin Governance)

IT admins control which Work IQ MCP servers are available tenant-wide:

1. Sign in to the [Microsoft 365 admin center](https://admin.microsoft.com/).
2. Go to **Agents and Tools** → **Tools** page.
3. View all available MCP servers (Work IQ Mail, Work IQ Calendar, Work IQ SharePoint, etc.).
4. Set each server's status to **Available** or **Blocked** per organizational policy.
5. Grant scoped permissions so agents only access what they need.

See [Manage Tools for Agent 365](https://learn.microsoft.com/microsoft-365/admin/manage/manage-tools-for-agent) for details.

> **Note:** This feature is currently available for Frontier tenants only and may not be rolled out in all regions yet.

#### Path C: Create Custom MCP Servers via the MCP Management Server

If you need **custom** MCP servers (not the built-in Work IQ ones), Agent 365 provides the **MCP Management Server** — an API-first build surface for creating scenario-focused servers:

1. In VS Code, open Command Palette → **MCP: Add Server** → select **http**.
2. Enter: `https://agent365.svc.cloud.microsoft/mcp/environments/{environment ID}/servers/MCPManagement`
3. Use built-in tools like **CreateMCPServer**, **CreateToolWithConnector**, and **PublishMCPServer** to define custom servers backed by 1,500+ connectors, Microsoft Graph APIs, Dataverse, or any REST endpoint.

See [Extend your agents with custom MCP servers](https://learn.microsoft.com/microsoft-agent-365/tooling-servers-overview#extend-your-agents-with-available-or-custom-mcp-servers) for the full guide.

#### How This Codebase Uses Work IQ

The `WORK_IQ_MAIL_MCP_URL` and `WORK_IQ_SHAREPOINT_MCP_URL` env vars are loaded in [config.py](config.py) and passed as `server_url` to `MCPTool` instances in [agents/people_agent.py](agents/people_agent.py):

```python
def get_definition() -> PromptAgentDefinition:
    mcp_mail = MCPTool(
        server_label="work-iq-mail",
        server_url=config.WORK_IQ_MAIL_MCP_URL,
        require_approval="never",
    )
    mcp_sharepoint = MCPTool(
        server_label="work-iq-sharepoint",
        server_url=config.WORK_IQ_SHAREPOINT_MCP_URL,
        require_approval="never",
    )
    return PromptAgentDefinition(
        model=config.MODEL_DEPLOYMENT,
        instructions=AGENT_INSTRUCTIONS,
        tools=[mcp_mail, mcp_sharepoint],
    )
```

---

## The Three IQ Layers

### Fabric IQ — Structured Data Intelligence
Connects agents to your organization’s structured data through a Fabric lakehouse and the SQL analytics endpoint. The Fabric Data Agent translates natural language into SQL queries (NL2SQL) against lakehouse tables (dimstore, dimproducts, factsales, factreturns). Authentication uses identity passthrough (On-Behalf-Of) through a Foundry project connection of type “Microsoft Fabric”.

### Foundry IQ — Knowledge Intelligence
Indexes your unstructured knowledge (documents, SOPs, runbooks) into an Azure AI Search knowledge base. Agents retrieve relevant content through the `knowledge_base_retrieve` MCP tool with agentic multi-hop retrieval — going beyond simple keyword search to understand context and follow references.

### Work IQ — Organizational Context Intelligence
Surfaces relevant context from Microsoft 365 — emails, SharePoint documents/lists, and calendar events. Agents discover who has institutional knowledge, what conversations have occurred, and what documents or list items are relevant. Connects via Work IQ MCP servers (Mail, SharePoint, Calendar).

See [docs/iq_layers_explained.md](docs/iq_layers_explained.md) for the full explainer.

---

## Cross-Industry Applicability

This pattern adapts to any industry. The three IQ layers map to universal business needs:

| Industry | Fabric IQ | Foundry IQ | Work IQ |
|---|---|---|---|
| **Retail** (this POC) | Sales, returns, inventory | SOPs, quality policies | Who handled last issue |
| **Manufacturing** | Machines, defects, work orders | Maintenance manuals, safety SOPs | Which engineer fixed it |
| **Healthcare** | Patients, appointments, claims | Clinical guidelines, compliance | Which coordinator knows |
| **Financial Services** | Transactions, risk scores | Regulatory policies, audit reports | Which analyst reviewed |
| **Energy** | Assets, meters, outages | Safety procedures, regulations | Which field engineer |

See [industry_mappings/mappings.md](industry_mappings/mappings.md) for detailed adaptation guidance.

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full architecture diagram and explanation.

---

## References

- [Foundry IQ → Agent Service (Python)](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect)
- [Fabric IQ Overview](https://learn.microsoft.com/fabric/iq/overview)
- [Fabric Data Agent as MCP Server](https://learn.microsoft.com/fabric/data-science/data-agent-mcp-server)
- [Work IQ MCP Overview](https://learn.microsoft.com/microsoft-copilot-studio/use-work-iq)
- [Agent 365 Tools Catalog & MCP Server Setup](https://learn.microsoft.com/microsoft-agent-365/tooling-servers-overview)
- [Manage Tools for Agent 365 (M365 Admin Center)](https://learn.microsoft.com/microsoft-365/admin/manage/manage-tools-for-agent)
- [Work IQ CLI (`@microsoft/workiq`)](https://learn.microsoft.com/microsoft-365/copilot/extensibility/workiq-overview)
- [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)
- [Foundry Agent Service GA (March 2026)](https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-mar-2026/)
