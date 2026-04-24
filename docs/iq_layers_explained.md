# The Three IQ Layers — Explained

Microsoft's IQ layers represent a shift from "AI that generates text" to **AI that is grounded in your organization's actual data, knowledge, and context**. Each layer addresses a different type of organizational intelligence.

---

## Fabric IQ — Structured Data Intelligence

**What it is**: A data intelligence layer over your structured data in Microsoft Fabric (lakehouses, warehouses, SQL databases). You store your business data in a lakehouse and the Fabric Data Agent lets agents query it with natural language via the SQL analytics endpoint.

**How it works**:
1. You upload business data (stores, products, sales, returns) to lakehouse tables.
2. The Fabric Data Agent connects to the lakehouse as a data source.
3. Agents call the Data Agent with natural-language questions.
4. The Data Agent translates to SQL (NL2SQL) and returns structured results.

**Without Fabric IQ**: The agent would need hardcoded SQL queries or rely entirely on the LLM to generate SQL — fragile, error-prone, and unable to handle complex joins.

**With Fabric IQ**: The agent says "show me return rates by product and store for March" and the Data Agent handles the SQL generation, joins, and aggregation.

**Key resource**: [Fabric IQ Overview](https://learn.microsoft.com/fabric/iq/overview)

---

## Foundry IQ — Knowledge Intelligence

**What it is**: A managed knowledge base that indexes your unstructured documents (SOPs, policies, runbooks, post-mortems) into Azure AI Search and exposes them for agentic retrieval.

**How it works**:
1. You upload documents to a blob container or connect a SharePoint site.
2. Foundry IQ indexes them into an Azure AI Search knowledge base.
3. Agents call the `knowledge_base_retrieve` MCP tool with questions.
4. The retrieval pipeline uses multi-hop reasoning — following references, combining chunks, and ranking by relevance.

**Without Foundry IQ**: The agent either hallucinates procedures or you have to manually paste relevant documents into the prompt (doesn't scale, wastes tokens).

**With Foundry IQ**: The agent asks "what's our escalation policy for quality defects?" and gets back the specific SOP section with citation.

**Key resource**: [Foundry IQ → Agent Service Connection](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect)

---

## Work IQ — Organizational Context Intelligence

**What it is**: A layer that connects agents to organizational context in Microsoft 365 — email threads, SharePoint documents/lists, and calendar events. It answers "who knows about this?" and "what's already been discussed?"

**How it works**:
1. Admin enables Work IQ MCP servers in the M365 admin center.
2. Available MCP servers: Work IQ Mail, Work IQ SharePoint, Work IQ Calendar.
3. Agents call the MCP endpoints to search for relevant organizational context.
4. Results are scoped to the user's permissions (agents only see what the user can see).

**Without Work IQ**: You ask the agent a question, get a technically correct answer, but miss that your colleague already investigated the same issue last week and documented findings in an email thread.

**With Work IQ**: The agent surfaces that Sarah Chen emailed Tom Richards about this exact issue 3 days ago, and that the weekly ops sync assigned Tom to investigate — so you know exactly who to contact and what's already in progress.

**Key resource**: [Work IQ MCP Overview](https://learn.microsoft.com/microsoft-copilot-studio/use-work-iq)

---

## How They Work Together

Each layer answers a fundamentally different question:

| Layer | Question It Answers | Data Type |
|---|---|---|
| **Fabric IQ** | *What does the data say?* | Structured (tables, metrics) |
| **Foundry IQ** | *What do we know?* | Unstructured (documents, SOPs) |
| **Work IQ** | *Who knows, and what's in motion?* | Organizational (email, SharePoint, calendar) |

A complete picture requires all three:

- Fabric IQ tells you the Vanilla Bean return rate is 36% (8/10 returns are quality-texture).
- Foundry IQ tells you the SOP says to escalate when >5 returns in 7 days, and there was a similar cold chain incident in February.
- Work IQ tells you Tom Richards is already investigating, Sarah Chen is tracking daily counts, and the weekly ops sync has it as an action item.

No single layer gives you the full picture. Together, they give an agent the same situational awareness a seasoned employee would have.

---

## The MCP Protocol — The Common Thread

All three IQ layers connect to agents via the **Model Context Protocol (MCP)**. This is significant because:

1. **Standard interface**: Agents don't need custom code for each data source — just an MCP endpoint URL.
2. **Composable**: Add a new IQ source by adding another `MCPTool` — no agent rewrite needed.
3. **Secure**: Authentication and authorization flow through existing Azure/M365 identity.
4. **Ecosystem**: Any MCP-compatible server (including custom ones) can participate.

```python
# Same pattern for all three IQ layers:
MCPTool(
    server_label="<descriptive-label>",
    server_url="<mcp-endpoint-url>",
    require_approval="never",
)
```
