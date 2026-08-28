# AI Workflow Studio — Design & Architecture (Banking)

Architecture for a **visual agentic workflow platform** where business analysts design flows that call **internal banking APIs**, with **human-in-the-loop (HITL) approvals**, **full audit logging**, and a **hard guarantee that raw customer PII never reaches an external LLM**.

---

## 1. Design Goals and Constraints

| Goal | Design implication |
|------|-------------------|
| Visual workflow design for BAs | Low-code canvas plus governed node library |
| Agentic execution | Planner plus tool-calling runtime inside private boundary |
| Internal banking APIs | Adapter layer with strong auth, schemas, rate limits |
| Human-in-the-loop | Explicit approval nodes, task inbox, SLA and escalation |
| Full audit logging | Immutable append-only audit store plus correlation IDs |
| No raw customer data to external LLM | Private or on-prem LLM only, PII gateway, tokenization |

**Non-negotiable security principle:** Customer data stays in the **Bank Trust Zone**. The LLM only sees **redacted, tokenized, or synthetic** representations, enforced by a **Policy Gateway** — not by prompt instructions alone.

---

## 2. High-Level Logical Architecture

```mermaid
flowchart TB
    subgraph Users["Users"]
        BA["Business Analyst"]
        APP["Approver / Ops"]
        ADM["Admin / Compliance"]
    end

    subgraph Presentation["Presentation Layer"]
        STUDIO["Workflow Studio UI"]
        INBOX["Approval Inbox UI"]
        AUDIT_UI["Audit and Compliance Console"]
    end

    subgraph Control["Control Plane"]
        WFM["Workflow Manager"]
        POL["Policy Engine"]
        IAM["Identity and RBAC"]
    end

    subgraph Execution["Execution Plane - Bank Trust Zone"]
        ORCH["Workflow Orchestrator"]
        AGENT["Agent Runtime"]
        HITL["HITL Service"]
        ADAPT["Banking API Adapters"]
    end

    subgraph DataProtection["Data Protection Layer"]
        PII["PII Gateway"]
        VAULT["Token Vault"]
    end

    subgraph LLMZone["Private LLM Zone - No External Egress"]
        LLM["Private LLM"]
        LLMGW["LLM Gateway"]
    end

    subgraph Banking["Internal Banking Systems"]
        ACC["Account Service API"]
        TXN["Transaction Service API"]
        KYC["KYC Service API"]
        CORE["Core Banking / CRM"]
    end

    subgraph AuditStore["Audit and Observability"]
        AUD["Immutable Audit Log"]
        OBS["Metrics and Tracing"]
    end

    BA --> STUDIO
    APP --> INBOX
    ADM --> AUDIT_UI

    STUDIO --> WFM
    STUDIO --> IAM
    INBOX --> HITL
    AUDIT_UI --> AUD

    WFM --> ORCH
    ORCH --> AGENT
    ORCH --> HITL
    AGENT --> ADAPT
    AGENT --> LLMGW
    LLMGW --> PII
    PII --> LLM

    ADAPT --> ACC
    ADAPT --> TXN
    ADAPT --> KYC
    ADAPT --> CORE
    ADAPT --> VAULT

    ORCH --> AUD
    AGENT --> AUD
    HITL --> AUD
    ADAPT --> AUD
    PII --> AUD
    LLMGW --> AUD
    ORCH --> OBS
    AGENT --> OBS

    POL --> PII
    POL --> LLMGW
    POL --> ADAPT
    POL --> WFM
```

---

## 3. Layered Architecture

```mermaid
flowchart LR
    subgraph L1["L1 - Experience"]
        A1["Workflow Studio"]
        A2["Approval Inbox"]
        A3["Audit Console"]
    end

    subgraph L2["L2 - Application Services"]
        B1["Workflow Manager"]
        B2["Orchestrator"]
        B3["Agent Runtime"]
        B4["HITL Service"]
        B5["Audit Service"]
    end

    subgraph L3["L3 - Integration and Policy"]
        C1["Banking Adapters"]
        C2["PII Gateway"]
        C3["LLM Gateway"]
        C4["Policy Engine"]
    end

    subgraph L4["L4 - Infrastructure"]
        D1["Private LLM Cluster"]
        D2["Internal API Gateway"]
        D3["Secrets Vault"]
        D4["Immutable Audit Store"]
    end

    A1 --> B1
    A2 --> B4
    A3 --> B5
    B1 --> B2
    B2 --> B3
    B2 --> B4
    B3 --> C1
    B3 --> C3
    C3 --> C2
    C2 --> D1
    C1 --> D2
    B5 --> D4
    C4 --> C2
    C4 --> C3
    B3 --> D3
```

---

## 4. Core Components

### 4.1 Workflow Studio (for Business Analysts)

- **Visual canvas**: drag-and-drop nodes and edges with conditions
- **Governed node library**:
  - Start, End
  - Call Banking API (Account, Transaction, KYC)
  - Agent Step (reasoning plus tools)
  - Decision / Branch
  - Human Approval
  - Notification
  - Wait / Timer
  - Parallel / Join
- **Workflow lifecycle**: Draft, Validate, Simulate, Publish, Version
- **Simulation mode**: mock or synthetic data only (no production PII)
- **Schema validation**: each node bound to approved API contracts

### 4.2 Workflow Orchestrator

- Executes published workflows as **stateful DAGs**
- Recommended: **Temporal** or **Camunda 8**
- Responsibilities:
  - Step scheduling and retries
  - Correlation and workflow instance ID
  - Pause and resume at HITL nodes
  - Compensation or rollback where applicable

### 4.3 Agent Runtime

- Runs **agentic steps** inside the trust zone
- Pattern: Planner, Tool selection, Tool execution, Observation loop
- Tools are **never free-form HTTP** — only registered banking adapters
- Agent receives redacted context and structured tool outputs only

### 4.4 Banking API Adapter Layer

| Adapter | Example operations | Notes |
|---------|-------------------|-------|
| Account Adapter | get balance, profile summary, list accounts | Returns tokenized IDs outward |
| Transaction Adapter | search transactions, flag suspicious, get aggregates | Aggregates preferred over raw rows to LLM |
| KYC Adapter | get KYC status, document verification state | Status enums only to LLM |

All calls use mTLS or OAuth, idempotency keys, rate limits, and schema validation.

### 4.5 PII Gateway

**Mandatory gate on every LLM path.**

```mermaid
flowchart LR
    IN["Agent prompt context"] --> DET["PII Detector"]
    DET --> TOK["Tokenize and Redact"]
    TOK --> POLCHK["Policy Check"]
    POLCHK --> LLM["Private LLM"]
    LLM --> OUT["Response"]
    OUT --> AUD["Audit redacted"]
    OUT --> AGENT["Agent Runtime"]

    VAULT["Token Vault"] -.->|"detokenize for API calls only"| ADAPT["Banking Adapters"]
```

Rules:

- **Outbound to LLM**: redact or tokenize mandatory fields
- **Inbound from LLM**: scan for accidental PII generation
- **Detokenization**: only in adapter layer, never in LLM layer
- **Block and alert** on any policy violation

### 4.6 Human-in-the-Loop Service

- Creates **approval tasks** with redacted context package
- Assigns by role, team, risk level, amount threshold
- Supports approve, reject, request info, reassign, escalate
- SLA timers and escalation paths
- Workflow **pauses** until decision received

### 4.7 Audit and Compliance Service

- **Append-only**, tamper-evident storage
- Records:
  - Who published, ran, or approved
  - Workflow definition version hash
  - Step inputs and outputs (redacted)
  - API calls (endpoint, correlation ID — not raw payloads)
  - LLM request metadata (token counts, model version — not raw prompts with PII)
  - Policy decisions (allow, deny, redact)
- Retention aligned with banking regulations (e.g. 7 to 10 years)

---

## 5. Workflow Metamodel

```mermaid
classDiagram
    class WorkflowDefinition {
        UUID id
        string name
        int version
        string status
        JSON graph
        string owner
        datetime publishedAt
    }

    class WorkflowNode {
        UUID id
        string type
        JSON config
        JSON inputSchema
        JSON outputSchema
    }

    class WorkflowInstance {
        UUID id
        UUID definitionId
        string state
        string correlationId
        JSON context
    }

    class ApprovalTask {
        UUID id
        UUID instanceId
        string assigneeRole
        string status
        JSON redactedContext
        datetime dueAt
    }

    class AuditEvent {
        UUID id
        UUID instanceId
        string actor
        string action
        JSON redactedPayload
        datetime timestamp
        string hashChain
    }

    WorkflowDefinition "1" --> "many" WorkflowNode : contains
    WorkflowDefinition "1" --> "many" WorkflowInstance : spawns
    WorkflowInstance "1" --> "many" ApprovalTask : may create
    WorkflowInstance "1" --> "many" AuditEvent : generates
```

---

## 6. Example Workflow — KYC Exception Review

```mermaid
flowchart TD
    START(["Start - Customer case opened"]) --> KYC["Call KYC API - get_kyc_status"]
    KYC --> AGENT["Agent Step - Assess risk summary"]
    AGENT --> DEC{"Risk score above threshold?"}

    DEC -->|"No"| AUTO["Auto-resolve case"]
    DEC -->|"Yes"| HITL["Human Approval - Compliance Officer"]

    HITL -->|"Approved"| ACT["Call Transaction API - release_hold"]
    HITL -->|"Rejected"| REJ["Close case - rejected"]
    HITL -->|"Need info"| INFO["Notify ops and wait"]

    ACT --> AUD["Write Audit Event"]
    REJ --> AUD
    AUTO --> AUD
    INFO --> AUD
    AUD --> END(["End"])
```

---

## 7. Sequence Diagram — End-to-End Execution

```mermaid
sequenceDiagram
    autonumber
    actor BA as Business Analyst
    actor APP as Approver
    participant STU as Workflow Studio UI
    participant WFM as Workflow Manager
    participant ORCH as Orchestrator
    participant AGENT as Agent Runtime
    participant PII as PII Gateway
    participant LLM as Private LLM
    participant ADAPT as Banking Adapters
    participant ACC as Account API
    participant KYC as KYC API
    participant HITL as HITL Service
    participant AUD as Audit Service

    BA->>STU: Design and publish workflow v3
    STU->>WFM: validate and publish
    WFM->>AUD: log WORKFLOW_PUBLISHED

    Note over ORCH: Trigger - case ID received as token

    ORCH->>AUD: log WORKFLOW_STARTED
    ORCH->>ADAPT: get_kyc_status(CUST_TOKEN)
    ADAPT->>KYC: internal API call with real ID
    KYC-->>ADAPT: full KYC record
    ADAPT->>ADAPT: map to redacted DTO
    ADAPT-->>ORCH: status and risk flags
    ORCH->>AUD: log STEP_COMPLETED

    ORCH->>AGENT: run_agent_step with redacted context
    AGENT->>PII: sanitize prompt context
    PII->>PII: detect and tokenize PII
    PII->>LLM: redacted prompt only
    LLM-->>PII: response
    PII->>PII: scan response for PII leakage
    PII-->>AGENT: safe structured recommendation
    AGENT->>AUD: log AGENT_STEP metadata

    alt requires human approval
        ORCH->>HITL: create_approval_task
        HITL->>APP: notify inbox
        APP->>HITL: approve with comment
        HITL->>AUD: log APPROVAL_DECISION
        HITL-->>ORCH: resume workflow
    end

    ORCH->>ADAPT: execute_banking_action
    ADAPT->>ACC: internal API with detokenized ref
    ACC-->>ADAPT: result
    ADAPT-->>ORCH: redacted result
    ORCH->>AUD: log WORKFLOW_COMPLETED
```

---

## 8. PII and Data Boundary Architecture

```mermaid
flowchart TB
    subgraph ExternalZone["External Zone - Blocked"]
        EXT_LLM["External LLM"]
    end

    subgraph TrustZone["Bank Trust Zone"]
        DATA["Raw Customer Data"]
        ADAPT2["Banking Adapters"]
        PII2["PII Gateway"]
        LLM2["Private LLM"]
        AGENT2["Agent Runtime"]
    end

    EGRESS["Network Egress Deny"]

    DATA --> ADAPT2
    ADAPT2 -->|"redacted DTOs"| AGENT2
    AGENT2 --> PII2
    PII2 --> LLM2
    LLM2 --> PII2
    PII2 --> AGENT2

    EXT_LLM -.->|"blocked"| EGRESS

    style ExternalZone fill:#fee,stroke:#c00
    style TrustZone fill:#efe,stroke:#090
```

**Enforcement layers (defense in depth):**

1. **Network**: LLM subnet has no internet egress
2. **Policy Gateway**: blocks non-redacted payloads
3. **Schema contracts**: adapters return redacted DTOs only
4. **Runtime guard**: agent tools cannot bypass adapters
5. **Audit and alerts**: any policy violation triggers block and incident

---

## 9. Human-in-the-Loop State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: create_task
    Pending --> InReview: assignee_opens
    InReview --> Approved: approve
    InReview --> Rejected: reject
    InReview --> NeedInfo: request_info
    NeedInfo --> Pending: submit_info
    Pending --> Escalated: sla_breach
    Escalated --> InReview: senior_assign
    Approved --> [*]: resume_workflow
    Rejected --> [*]: terminate_or_alt_path
```

**Approval task payload (what approver sees):**

- Customer token (not raw ID)
- Workflow name and version
- Redacted summary from agent
- Risk flags and amounts (masked if needed)
- Recommended action and rationale
- Full audit trail link

---

## 10. Audit Logging Architecture

```mermaid
flowchart LR
    subgraph Producers["Event Producers"]
        P1["Workflow Manager"]
        P2["Orchestrator"]
        P3["Agent Runtime"]
        P4["PII Gateway"]
        P5["HITL Service"]
        P6["Banking Adapters"]
    end

    subgraph Pipeline["Audit Pipeline"]
        BUS["Event Bus"]
        ENR["Enrichment"]
        SCRUB["PII Scrubber"]
        HASH["Hash Chain"]
    end

    subgraph Storage["Immutable Storage"]
        WORM["WORM Object Store"]
        SIEM["SIEM Integration"]
        COMP["Compliance Reports"]
    end

    P1 --> BUS
    P2 --> BUS
    P3 --> BUS
    P4 --> BUS
    P5 --> BUS
    P6 --> BUS

    BUS --> ENR
    ENR --> SCRUB
    SCRUB --> HASH
    HASH --> WORM
    WORM --> SIEM
    WORM --> COMP
```

**Every audit event includes:**

`event_id | timestamp | actor | action | workflow_id | instance_id | step_id | definition_version | redacted_payload | prev_hash`

---

## 11. Deployment Topology

```mermaid
flowchart TB
    subgraph DMZ["DMZ"]
        LB["Load Balancer / WAF"]
    end

    subgraph AppVPC["Application VPC"]
        STU_POD["Workflow Studio"]
        ORCH_POD["Orchestrator Cluster"]
        AGENT_POD["Agent Runtime"]
        HITL_POD["HITL Service"]
        AUD_POD["Audit Ingestion"]
    end

    subgraph SecureVPC["Secure Services VPC"]
        PII_POD["PII Gateway"]
        ADAPT_POD["Banking Adapters"]
        VAULT_POD["Secrets and Token Vault"]
    end

    subgraph LLMVPC["Private LLM VPC - No Internet"]
        LLM_POD["LLM Inference"]
        LLMGW_POD["LLM Gateway"]
    end

    subgraph BankCore["Core Banking Network"]
        INTGW["Internal API Gateway"]
        ACC2["Account Service"]
        TXN2["Transaction Service"]
        KYC2["KYC Service"]
    end

    LB --> STU_POD
    STU_POD --> ORCH_POD
    ORCH_POD --> AGENT_POD
    AGENT_POD --> PII_POD
    PII_POD --> LLMGW_POD
    LLMGW_POD --> LLM_POD
    AGENT_POD --> ADAPT_POD
    ADAPT_POD --> INTGW
    INTGW --> ACC2
    INTGW --> TXN2
    INTGW --> KYC2
    ORCH_POD --> HITL_POD
    ORCH_POD --> AUD_POD
    AGENT_POD --> AUD_POD
    ADAPT_POD --> AUD_POD
    ADAPT_POD --> VAULT_POD
```

---

## 12. Technology Recommendations

| Layer | Options |
|-------|---------|
| Workflow Studio UI | React plus React Flow or Rete.js |
| Orchestrator | Temporal (recommended) or Camunda 8 |
| Agent Runtime | Python or Go service with tool registry |
| Private LLM | On-prem GPU plus vLLM, or Azure OpenAI in private VNet |
| PII Gateway | Custom plus Presidio or proprietary NER |
| Event bus | Kafka |
| Audit store | Append-only DB plus WORM S3 or immudb |
| Identity | OIDC or SAML via bank IdP |
| Secrets | HashiCorp Vault |
| API integration | Internal Kong or Apigee plus mTLS |

---

## 13. Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Availability | 99.9% or higher for execution plane |
| Workflow durability | Zero lost state on crash (orchestrator-backed) |
| Approval SLA | Configurable per workflow (e.g. 4h or 24h) |
| Audit completeness | 100% of state transitions logged |
| PII leakage | Zero raw PII to external LLM (network plus policy enforced) |
| RTO / RPO | Align with bank BCP standards |
| Multi-tenancy | Optional business unit isolation |

---

## 14. Phased Delivery Roadmap

```mermaid
gantt
    title AI Workflow Studio Delivery Phases
    dateFormat YYYY-MM
    axisFormat %b %Y

    section Phase 1 Foundation
    IAM RBAC and Audit bus           :p1a, 2026-01, 2M
    Workflow Manager and Orchestrator :p1b, 2026-02, 3M
    Banking adapters Account and KYC  :p1c, 2026-03, 2M

    section Phase 2 Studio and HITL
    Visual Workflow Studio v1         :p2a, 2026-05, 3M
    HITL inbox and approval flows     :p2b, 2026-06, 2M

    section Phase 3 Agentic and LLM
    Private LLM deployment            :p3a, 2026-07, 2M
    PII Gateway and LLM Gateway         :p3b, 2026-07, 3M
    Agent runtime and tool registry   :p3c, 2026-08, 3M

    section Phase 4 Hardening
    Pen test and compliance review    :p4a, 2026-11, 2M
    Production rollout                :p4b, 2027-01, 2M
```

---

## 15. Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM location | Private only | Regulatory and PII constraint |
| PII strategy | Tokenize and redact at gateway | Defense in depth, not prompt-only |
| Orchestration | Durable workflow engine | HITL pause and resume, retries, audit |
| BA tooling | Governed node library | Prevent unsafe API or LLM combinations |
| Audit | Immutable append-only | Banking compliance |
| Agent tools | Registered adapters only | No arbitrary API access |

---

## 16. Component Reference

| Component | Responsibility |
|-----------|----------------|
| Workflow Studio UI | Visual design, validation, simulation, publish |
| Workflow Manager | Versioning, schema checks, deployment |
| Orchestrator | Durable step execution, timers, HITL pause |
| Agent Runtime | Planner loop, tool calls, structured outputs |
| PII Gateway | Detect, tokenize, redact, block violations |
| LLM Gateway | Model routing, guardrails, request logging |
| Banking Adapters | Internal API integration, detokenization |
| HITL Service | Approval tasks, SLA, escalation |
| Audit Service | Immutable event ingestion and query |
| Policy Engine | RBAC, field allowlists, workflow governance |

---

## 17. Related Documents

- Threat model (STRIDE) — recommended next artifact
- API specification for workflow definition and execution
- Data classification and redaction policy matrix
- Compliance mapping (PCI, GDPR, local banking regulations)
