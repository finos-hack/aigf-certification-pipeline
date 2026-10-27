# AIGF Certification Pipeline

An open source, end-to-end certification pipeline that transforms [FINOS AI Governance Framework (AIGF)](https://www.finos.org/ai-governance) guidance into discrete, machine-configurable controls with predefined success criteria and compliance enforcement techniques.

## Problem

Organizations adopting FINOS frameworks face three key challenges:

1. **Generalized guidance** -- AIGF mitigations provide valuable direction but lack the structured, binary mandates needed for automated implementation.
2. **No defined success criteria** -- Without machine-readable control definitions, pathways for both adoption and validation remain ambiguous.
3. **No post-deployment enforcement** -- Without continuous runtime validation, atomic mandate reservation, and cryptographic audit evidence, unverified software policies remain vulnerable to stale authority, multi-agent collective exposure, and automated systemic attacks.

## Solution

This project establishes FINOS's first certification pipeline by extending [CALM](https://github.com/finos/architecture-as-code) bidirectionally -- formalizing AIGF guidance upstream through atomization and enforcing execution-dependent controls downstream through runtime policy evaluation and verifiable cryptographic evidence.

**Desired outcome:** Each FINOS policy (e.g. AIGF) has a companion playbook with universally identifiable controls, predefined success criteria, and deterministic compliance enforcement techniques.

## Pipeline Overview

The certification pipeline transforms AIGF guidance into enforceable controls through three stages:

```
                                        ┌─────────────────┐
                                   ┌───>│  Architectural  │───> CALM
                                   │    │    Controls     │
┌──────────────┐    ┌──────────┐   │    ├─────────────────┤
│     AIGF     │    │ Atomize  │   │    │    Runtime      │───> CALM ──> Policy / Enclave Gate
│  Mitigation  │───>│   and    │───┤───>│    Controls     │
│  Catalogue   │───>│Categorize│   │    ├─────────────────┤
└──────────────┘    └──────────┘   │    │   Procedural &  │───> CALM ──> IETF SCITT (RFC 9162)
                                   └───>│ Audit Controls  │
                                        └─────────────────┘
```

### Step 1: Atomize Policy

Extract guidance from AIGF's mitigations and convert it into individual controls with binary mandates. Each control defines:

- **Responsible party** (e.g. system owners, system owners deploying agentic workflows)
- **Obligation type** (must or may)
- **Binary or near-binary mandate**

Controls are categorized by type:

| Category | ~Share | Description | Modeled In |
|---|---|---|---|
| **Architectural** | ~50% | Infrastructure/topology decisions (e.g. data segmentation, encryption standards, isolated execution environments) | CALM |
| **Runtime** | ~25% | Per-request pre-execution enforcement (e.g. atomic mandate checks, collective-exposure circuit breakers, tool-scope verification) | CALM + Runtime Policy / Enclave Gate |
| **Procedural & Audit** | ~25% | Verifiable execution receipts, periodic audits, and governance evidence (e.g. IETF SCITT `RFC 9162` / `COSE_Sign1` receipts, incident feedback loops) | CALM + Verifiable Transparency Log |

### Step 2: Model as CALM-Format Controls

Populate control-specific attributes in [CALM](https://github.com/finos/architecture-as-code) format:

- Control ID, name, and description (`const` pinned in the requirement schema)
- Required evidence and enforcement method
- Binary, control-specific requirements (`additionalProperties: false`, `uniqueItems: true` on input sets)
- References to related AIGF mitigation categories

**Modeled Mitigations in This Repository:**

| AIGF Mitigation | Directory | Atomized Controls | Category |
|---|---|---|---|
| **MI-18: Agent Authority Least Privilege Framework** | [`mitigations/MI-18-agent-authority-least-privilege/`](./mitigations/MI-18-agent-authority-least-privilege/) | `FINOS-PREV-018-001` (Pre-Commit Mandate Scope & Freshness)<br>`FINOS-PREV-018-002` (Atomic Shared-Limit Reservation & Cross-Institution Delegation) | Runtime & Architectural |
| **MI-19: Tool Chain Validation and Sanitization** | [`mitigations/MI-19-tool-chain-validation-and-sanitization/`](./mitigations/MI-19-tool-chain-validation-and-sanitization/) | `FINOS-PREV-019-001` (Ensuring Appropriate Authorization Level) | Runtime |
| **MI-20: Real-Time Monitoring and Circuit Breakers** | [`mitigations/MI-20-real-time-monitoring-and-circuit-breakers/`](./mitigations/MI-20-real-time-monitoring-and-circuit-breakers/) | `FINOS-DET-020-001` (Deterministic Runtime & Collective-Exposure Circuit Breakers `ST-01..ST-05`) | Runtime |
| **MI-21: Agent Decision Audit and Explainability** | [`mitigations/MI-21-agent-decision-audit-and-explainability/`](./mitigations/MI-21-agent-decision-audit-and-explainability/) | `FINOS-AUD-021-001` (Independently Verifiable `COSE_Sign1` / IETF SCITT `RFC 9162` Decision Receipts) | Procedural & Audit |

### Step 3: Validate & Enforce Conformance

Run the repository's zero-dependency conformance validator to verify every atomized CALM requirement schema (`JSON Schema 2020-12`), configuration instance, and documentation manifest:

```bash
python3 scripts/validate_pipeline.py
python3 scripts/validate_pipeline.py --self-test
```

## Aligned FINOS Initiatives

This project leverages and complements several existing FINOS work streams pushing towards automated, machine-readable compliance:

| Project | Role in Pipeline |
|---|---|
| [AI Governance Framework (AIGF)](https://www.finos.org/ai-governance) | Source framework -- risk and mitigation catalogue |
| [CALM (Common Architecture Language Model)](https://github.com/finos/architecture-as-code) | Schema for structuring controls in a consistent, machine-configurable format |
| [AI Reference Architecture Library](https://github.com/finos/ai-reference-architecture-library) | FSI-specific reference architectures with threat models -- taxonomy for specific use cases |
| [Gemara](https://github.com/finos/gemara) | GRC Engineering Model for converting written governance controls into machine-readable, automated policy rules |
| [AI Evals Framework](https://github.com/finos-labs/ai-evals-framework) | Taxonomy for AI evaluations in finance -- defining evals for specific use cases |

## Open Source Configuration vs. Institutional Hardware-Attested Verification

This project focuses on the **open source configuration and schema validation layer**:

**Can:**
- Validate that controls are correctly defined and modeled in CALM JSON Schema 2020-12 (`scripts/validate_pipeline.py`)
- Verify that a system's declared policy configuration satisfies required structural and boundary invariants in CI/CD

**Cannot (via unattested host-memory policy engines alone):**
- Produce hardware-rooted, tamper-evident proof that pre-execution checks occurred inside an isolated execution environment
- Prevent concurrent multi-agent limit exhaustion or TOCTOU (time-of-check to time-of-use) authority drift without atomic state reservation

For regulated financial institutions and Digital Financial Market Infrastructures (`D-FMI`) requiring production-grade assurance against stale authority, collective multi-agent exposure, and automated systemic attacks, this open specification pairs with **IETF SCITT (`RFC 9162`) transparency logs** and **Hardware-Attested Execution & Non-Custodial Clearing Verification layers** (such as **[Ashlar Blue](https://ashlar.blue)** by Corrente Labs, Inc., or commercial governance studios such as [EQTY Lab](https://www.eqtylab.io/)) to bind CALM control evaluations directly to hardware-attested execution environments and non-repudiable cryptographic audit receipts.

## Roadmap

1. **Atomize AIGF mitigations** -- Extract and categorize controls from AIGF mitigations into architectural, runtime, and procedural/audit types (`MI-18`, `MI-19`, `MI-20`, `MI-21` modeled)
2. **Model controls in CALM** -- Define CALM-format schemas with control-specific requirements and evidence definitions
3. **Automate conformance validation** -- Enforce schema and configuration invariants in CI via `scripts/validate_pipeline.py`
4. **Validate end-to-end pipeline** -- Demonstrate full certification flow from AIGF guidance through CALM definition to runtime enforcement and verifiable receipt generation
5. **Expand to additional FINOS frameworks** -- Generalize the pipeline to support certification against other FINOS policies beyond AIGF

## License

Copyright (c) Contributors to the AIGF Certification Pipeline project.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
