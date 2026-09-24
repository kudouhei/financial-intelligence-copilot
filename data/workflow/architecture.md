
# Azure architecture overview

```
┌─────────────────────────────────────────────────────┐
│ 1. Client                                            │
│ React browser UI                                     │
└───────────────────────┬─────────────────────────────┘
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────┐
│ 2. Application Runtime                              │
│ Azure Container Apps                                │
│ FastAPI + React static build + LangGraph            │
└───────┬───────────┬──────────────┬──────────────────┘
        │           │              │
        ▼           ▼              ▼
┌──────────────┐ ┌────────────┐ ┌─────────────────────┐
│ PostgreSQL   │ │ AI Search  │ │ Azure OpenAI        │
│ Structured   │ │ Documents  │ │ Planning/Synthesis  │
│ financial DB │ │ + vectors  │ │ Embeddings          │
└──────────────┘ └────────────┘ └─────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ 3. Identity & Security                              │
│ Managed Identity + RBAC + Key Vault                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 4. Software Delivery                                │
│ Docker → Azure Container Registry → Container Apps  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 5. Observability                                    │
│ Log Analytics + Azure Monitor + LangSmith           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 6. Governance                                       │
│ Resource Group + Subscription + Region + Tags       │
└─────────────────────────────────────────────────────┘
```
