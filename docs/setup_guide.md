# Setup Guide

Step-by-step instructions for provisioning Azure resources and running the POC.

---

## 1. Prerequisites

- **Python 3.11+**
- **Azure CLI** (`az`) — [Install](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **Azure subscription** with Contributor access
- **Microsoft 365 Copilot license** (for Work IQ — optional, POC works without it)

Log in to Azure:
```bash
az login
```

---

## 2. Create a Microsoft Foundry Project

The Foundry project is the central hub for agent creation and model deployments.

1. Go to [Azure AI Foundry portal](https://ai.azure.com).
2. Create a new **Project** (or use an existing one).
3. Deploy a model (e.g., `gpt-4.1-mini`) in the project's **Deployments** section.
4. Copy the **Project endpoint** from Settings > Properties.

Set in `.env`:
```
FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT=gpt-4.1-mini
```

---

## 3. Set Up Foundry IQ (Knowledge Base)

Foundry IQ uses Azure AI Search to index your operational documents.

### 3a. Create Azure AI Search Service
```bash
az search service create \
  --name <search-service-name> \
  --resource-group <rg-name> \
  --sku standard \
  --location <region>
```

### 3b. Create a Knowledge Base
1. In the Foundry portal, go to your project > **Knowledge Bases**.
2. Create a new knowledge base named `operations-kb`.
3. Upload the documents from `mock_data/foundry_iq/`:
   - `return_handling_sop.md`
   - `quality_escalation_policy.md`
   - `cold_chain_incident_postmortem.md`
   - `product_recall_procedure.md`
4. Wait for indexing to complete.

### 3c. Create a Project Connection
1. In the Foundry portal > Settings > **Connections**.
2. Add a connection to your Azure AI Search service.
3. Note the connection name (e.g., `kb-mcp-connection`).

Set in `.env`:
```
AZURE_AI_SEARCH_ENDPOINT=https://<search-service>.search.windows.net
KNOWLEDGE_BASE_NAME=operations-kb
KB_MCP_CONNECTION_NAME=kb-mcp-connection
```

---

## 4. Set Up Fabric IQ (Data Agent)

Fabric IQ connects to your structured data through a lakehouse and Data Agent.
The Data Agent uses **NL2SQL** to translate natural language questions into SQL
queries against the lakehouse's SQL analytics endpoint.

> **Why lakehouse SQL instead of ontology?** The ontology approach (GQL) is
> still in preview and has significant limitations: no `CASE WHEN`, no native
> `DATE` type support, and unreliable NL2Ontology translation. The lakehouse
> SQL endpoint is mature, supports full SQL, and works with the same Data
> Agent and Foundry connection — no code changes needed.

### 4a. Create a Fabric Workspace
1. Go to [Microsoft Fabric portal](https://app.fabric.microsoft.com).
2. Create a workspace (or use an existing one).

### 4b. Upload Data to a Lakehouse
1. Create a new **Lakehouse** in the workspace.
2. Upload the CSV files from `mock_data/fabric_iq/`:
   - `DimStore.csv` → table `dimstore`
   - `DimProducts.csv` → table `dimproducts`
   - `FactSales.csv` → table `factsales`
   - `FactReturns.csv` → table `factreturns`

### 4c. Create a Data Agent
1. In the workspace, create a **Data Agent** (preview).
2. Select **Add a data source** and choose your **Lakehouse**.
3. Select the four tables: `dimstore`, `dimproducts`, `factsales`, `factreturns`.
4. Publish the Data Agent.
5. Copy the `workspace_id` and `artifact_id` from the Data Agent URL:
   ```
   .../groups/<workspace_id>/aiskills/<artifact_id>...
   ```

### 4d. Configure Data Agent Instructions

Add instructions in the Fabric portal to help the NL2SQL engine generate
accurate queries:

1. Open your Data Agent in the Fabric portal.
2. Select **Agent instructions** from the menu ribbon.
3. Add the following text:

   ```
   ## Tone and style
   Use clear, professional, and concise language.
   Sound like an internal retail operations analyst.
   When presenting numbers, always include units (e.g., "$17.97", "3 units").
   Format dates as Month Day, Year (e.g., "March 5, 2026").

   ## General knowledge
   You are the Lakeshore Retail Data Agent. You answer questions about
   retail store performance, product sales, and product returns using the
   lakehouse SQL analytics endpoint.
   Only answer questions grounded in the available tables and their data.
   If information is missing or ambiguous, say so and suggest the user
   refine the question. Do not guess, speculate, or fabricate data.

   ## Schema overview
   The lakehouse has four tables:
   - **dimstore**: StoreId (PK), StoreName, Region, City, State, Manager, OpenDate
   - **dimproducts**: ProductId (PK), ProductName, Category, SubCategory, UnitPrice, Supplier
   - **factsales**: SaleId (PK), StoreId (FK), ProductId (FK), SaleDate, Quantity, TotalAmount, Channel
   - **factreturns**: ReturnId (PK), SaleId (FK), StoreId (FK), ProductId (FK), ReturnDate, Quantity, ReturnReason, RefundAmount

   ## Join keys
   - factsales.StoreId → dimstore.StoreId
   - factsales.ProductId → dimproducts.ProductId
   - factreturns.StoreId → dimstore.StoreId
   - factreturns.ProductId → dimproducts.ProductId
   - factreturns.SaleId → factsales.SaleId

   ## Business terminology
   - "Revenue" or "sales amount" refers to factsales.TotalAmount.
   - "Refund" refers to factreturns.RefundAmount.
   - "Return rate" means (total returned Quantity / total sold Quantity) for
     the same product and time range.
   - "Northeast stores" means stores where Region = 'Northeast' (currently:
     Downtown Flagship in New York NY, Suburban Plaza in Boston MA).
   - "Midwest" = Chicago IL. "West" = San Diego CA and Denver CO.
   - Channels are either 'In-Store' or 'Online'.
   - ReturnReason values: 'Quality-Texture', 'Customer-Preference',
     'Damaged-Packaging'.
   - Categories: 'Ice Cream', 'Sorbet', 'Italian Ice'.
     SubCategories: 'Premium', 'Standard'.

   ## Example value formats
   - StoreId: 'S001', 'S002', 'S003', 'S004', 'S005'
   - ProductId: 'P001', 'P002', ... 'P008'
   - SaleId: 'TXN001', 'TXN002', ...
   - ReturnId: 'R001', 'R002', ...
   - Dates: YYYY-MM-DD (e.g., '2026-03-01')
   - UnitPrice / TotalAmount / RefundAmount: decimal USD (e.g., 5.99, 89.85)

   ## Guardrails
   - This agent is read-only. Do not attempt to modify data.
   - If a question requires data not in the lakehouse (e.g., forecasts,
     external benchmarks), respond that it is outside the current data scope.
   ```

### 4e. Create a Foundry Project Connection
1. In the **Foundry portal**, open your project.
2. Go to **Management center** → **Connected resources**.
3. Create a connection of type **Microsoft Fabric**.
4. Enter the `workspace_id` and `artifact_id` from step 4c.
5. Save the connection and note the connection name.

Set in `.env`:
```
FABRIC_CONNECTION_NAME=fabric-data-agent
```

> **Note**: The Fabric Data Agent uses **identity passthrough (On-Behalf-Of)**.
> Service principal auth is not supported. The end user running the agent must
> have at least READ access to the Data Agent and the minimum permission on
> each underlying data source (Build on semantic models, Read on lakehouses).

---

## 5. Enable Work IQ (Optional)

Work IQ requires a Microsoft 365 Copilot license and admin configuration.
The People Agent uses Work IQ MCP servers (Mail, SharePoint) to surface
organizational context from Microsoft 365.

### 5a. Admin Enablement
1. Go to [M365 Admin Center](https://admin.microsoft.com).
2. Navigate to **Settings** > **Copilot** > **Work IQ MCP Servers**.
3. Enable the Work IQ MCP servers:
   - Work IQ Mail
   - Work IQ SharePoint
   - (optionally) Work IQ Calendar
4. Configure which users/groups can access.

### 5b. Find Your Entra Tenant ID
1. Go to [Azure Portal](https://portal.azure.com) > **Microsoft Entra ID** > **Overview**.
2. Copy the **Tenant ID** (a GUID, e.g., `babcd128-bc46-4276-b8d4-2c6bae2cd57a`).

Set in `.env`:
```
ENTRA_TENANT_ID=<your-entra-tenant-id>
```

### 5c. Configure Endpoints
The Work IQ MCP server URLs require the tenant ID in the path. The URL
pattern is:
```
https://agent365.svc.cloud.microsoft/agents/tenants/{tenantId}/servers/{serverName}
```

`config.py` constructs the URLs automatically from `ENTRA_TENANT_ID`. The
default server names are:

| Server | Name in URL |
|---|---|
| Work IQ Mail | `mcp_MailTools` |
| Work IQ SharePoint (OneDrive) | `mcp_ODSPRemoteServer` |

To override the auto-constructed URLs (e.g., for a proxy), set these
optional variables in `.env`:
```
WORK_IQ_MAIL_MCP_URL=https://agent365.svc.cloud.microsoft/agents/tenants/<tenantId>/servers/mcp_MailTools
WORK_IQ_SHAREPOINT_MCP_URL=https://agent365.svc.cloud.microsoft/agents/tenants/<tenantId>/servers/mcp_ODSPRemoteServer
```

### 5d. Add Work IQ Tools from the Foundry Catalog
The Work IQ MCP servers require OAuth authentication. The easiest way to
set this up is to add each Work IQ server from the Foundry tool catalog,
which creates the project connection automatically.

1. In the **Foundry portal**, open your project.
2. Go to **Build** → **Tools** → **Add Tool**.
3. Add **Work IQ Mail** from the catalog. The portal creates a project
   connection — note its name (e.g., `work-iq-mail`).
4. Add **Work IQ SharePoint** from the catalog. Note the connection name
   (e.g., `work-iq-sharepoint`).

Set in `.env`:
```
WORK_IQ_MAIL_CONNECTION=work-iq-mail
WORK_IQ_SHAREPOINT_CONNECTION=work-iq-sharepoint
```

> **Note**: Each Work IQ MCP server gets its own project connection because
> each has a distinct endpoint and auth scope. This matches the pattern
> used by the Knowledge Agent (`KB_MCP_CONNECTION_NAME`) and the Fabric
> Data Agent (`FABRIC_CONNECTION_NAME`).

> **Note**: If Work IQ is not available, the POC still demonstrates the
> pattern — the People Agent will simply not have access to live M365 data.
> See `mock_data/work_iq/` for example response formats.

---

## 6. Install and Run

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your values from steps 2-5

# Run with default query
python main.py

# Run with custom query
python main.py "What are the top-selling products in the West region?"
```

---

## 7. Troubleshooting

| Issue | Solution |
|---|---|
| `AuthenticationError` | Run `az login` and ensure `DefaultAzureCredential` picks up your session |
| `ResourceNotFoundError` for KB | Verify `KNOWLEDGE_BASE_NAME` matches the KB created in step 3b |
| Fabric `unauthorized` | End user lacks access to the Fabric Data Agent or its data sources — grant READ access in Fabric |
| Fabric Data Agent returns no results | Verify the lakehouse tables are selected in the Data Agent's data source config, and that column names match the CSVs |
| Work IQ `TenantIdInvalid` | The MCP URL is missing the `/tenants/{tenantId}/` segment. Ensure `ENTRA_TENANT_ID` is set in `.env` (step 5b) |
| Work IQ `Value does not match format "uri"` | The MCP URL resolved to an empty string. Unset any empty `WORK_IQ_MAIL_MCP_URL` / `WORK_IQ_SHAREPOINT_MCP_URL` env vars and let `config.py` construct them from `ENTRA_TENANT_ID` |
| Work IQ `401 Unauthorized` | The Foundry project connection for that Work IQ server is missing or misconfigured. Add the server from the tool catalog per step 5d and verify `WORK_IQ_MAIL_CONNECTION` / `WORK_IQ_SHAREPOINT_CONNECTION` match the connection names |
| Work IQ connection refused | Verify M365 Copilot license and admin enablement (step 5a) |
| Model deployment not found | Check `MODEL_DEPLOYMENT` matches the deployment name in Foundry |
