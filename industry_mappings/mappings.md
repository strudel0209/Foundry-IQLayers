# Cross-Industry Mappings

This POC uses a **Lakeshore Retail** scenario, but the three-IQ-layer pattern applies to any industry. Below are mappings showing how to adapt each layer.

---

## Retail (This POC)

| Layer | Entities / Sources | Example Query |
|---|---|---|
| **Fabric IQ** | Store, Product, SaleEvent, ReturnEvent | "Return rate for Vanilla Bean in Northeast stores" |
| **Foundry IQ** | Return SOPs, quality policies, incident post-mortems | "What's our escalation policy for >5 quality returns?" |
| **Work IQ** | Store manager emails, SharePoint quality-alerts list | "Who investigated the last texture complaint?" |

---

## Manufacturing

| Layer | Entities / Sources | Example Query |
|---|---|---|
| **Fabric IQ** | Machine, Part, WorkOrder, DefectRate, Supplier, ProductionLine | "Defect rate on Line 3 for the past 30 days" |
| **Foundry IQ** | Maintenance manuals, safety SOPs, quality protocols, failure analysis reports | "What's the maintenance procedure for hydraulic press HYD-04?" |
| **Work IQ** | Maintenance engineer emails, shift handoff notes, SharePoint plant-ops list | "Which engineer resolved the HYD-04 bearing failure last month?" |

**Adaptation**: Replace CSV data with machine telemetry tables. Replace SOPs with maintenance runbooks. Lakehouse tables shift from retail (dimstore, dimproducts) to manufacturing (machines, parts, workorders).

---

## Healthcare

| Layer | Entities / Sources | Example Query |
|---|---|---|
| **Fabric IQ** | Patient, Provider, Appointment, Claim, Diagnosis, Procedure | "Readmission rates for cardiac patients at Metro Hospital Q1" |
| **Foundry IQ** | Clinical guidelines, insurance policies, compliance procedures, care protocols | "What's our protocol for managing post-surgical wound infections?" |
| **Work IQ** | Care coordinator emails, case review meeting notes, SharePoint clinical-alerts list | "Which coordinator handled the last complex wound care case?" |

**Adaptation**: Lakehouse tables map to clinical data (FHIR-aligned if needed). Knowledge base indexes clinical SOPs and guidelines. Work IQ surfaces care team communications. Note: healthcare data requires additional access controls and HIPAA compliance.

---

## Financial Services

| Layer | Entities / Sources | Example Query |
|---|---|---|
| **Fabric IQ** | Account, Transaction, RiskScore, Portfolio, Client, Alert | "Unusual transaction patterns for accounts flagged this week" |
| **Foundry IQ** | Regulatory policies, compliance procedures, audit reports, KYC guidelines | "What's our SAR filing procedure for transactions over $10K?" |
| **Work IQ** | Compliance analyst emails, risk committee meeting notes, #fraud-alerts | "Who reviewed the last batch of flagged transactions?" |

**Adaptation**: Lakehouse tables map to financial entities. Knowledge base indexes regulatory and compliance documents. Work IQ helps identify which analysts have investigated similar patterns.

---

## Energy & Utilities

| Layer | Entities / Sources | Example Query |
|---|---|---|
| **Fabric IQ** | Asset, Meter, WorkOrder, OutageEvent, Region, Grid | "Outage frequency in the Northeast grid sector this quarter" |
| **Foundry IQ** | Safety procedures, maintenance manuals, regulatory filings, incident reports | "What's the lockout/tagout procedure for transformer T-450?" |
| **Work IQ** | Field engineer dispatches, safety team emails, SharePoint grid-ops list | "Which field engineer resolved the last transformer fault in Sector 7?" |

**Adaptation**: Lakehouse tables map to asset management and grid infrastructure. Knowledge base indexes safety and regulatory documents. Work IQ surfaces field operations communications.

---

## How to Adapt This POC

1. **Replace mock data CSVs** in `mock_data/fabric_iq/` with your domain's entity tables.
2. **Update `lakehouse_schema.json`** to reflect your domain's tables, columns, and join keys.
3. **Replace documents** in `mock_data/foundry_iq/` with your domain's SOPs, policies, and reports.
4. **Update agent instructions** in `agents/*.py` to reference your domain's terminology.
5. **Update the orchestrator prompt** in `main.py` to reflect your domain's question patterns.

The MCP integration code (`MCPTool` configuration) stays the same — only the endpoint URLs and agent instructions change.
