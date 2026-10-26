# AIGF Certification Pipeline

An open source, end-to-end certification pipeline that transforms [FINOS AI Governance Framework (AIGF)](https://www.finos.org/ai-governance) guidance into discrete, machine-configurable controls with predefined success criteria and compliance enforcement techniques.

## Problem

Organizations adopting FINOS frameworks face three key challenges:

1. **Generalized guidance** -- AIGF mitigations provide valuable direction but lack the structured, binary mandates needed for automated implementation.
2. **No defined success criteria** -- Without machine-readable control definitions, pathways for both adoption and validation remain ambiguous.
3. **No post-deployment enforcement** -- There is no open source tooling for enforcing continued compliance at runtime after systems are deployed.

## Solution

This project establishes FINOS's first certification pipeline by extending [CALM](https://github.com/finos/architecture-as-code) bidirectionally -- formalizing AIGF guidance upstream through atomization and enforcing execution-dependent controls downstream through runtime policy evaluation.

**Desired outcome:** Each FINOS policy (e.g. AIGF) has a companion playbook with universally identifiable controls, predefined success criteria, and compliance enforcement techniques.

## Pipeline Overview

The certification pipeline transforms AIGF guidance into enforceable controls through three stages:

```
                                        ┌─────────────────┐
                                   ┌───>│  Architectural  │───> CALM
                                   │    │    Controls     │
┌──────────────┐    ┌──────────┐   │    ├─────────────────┤
│     AIGF     │    │ Atomize  │   │    │    Runtime      │───> CALM ──> Cupcake
│  Mitigation  │───>│   and    │───┤───>│    Controls     │
│  Catalogue   │    │Categorize│   │    ├─────────────────┤
└──────────────┘    └──────────┘   │    │   Procedural    │───> EQTY Lab
                                   └───>│    Controls     │
                                        └─────────────────┘
```

### Step 1: Atomize Policy

Extract guidance from AIGF's 23 mitigations and convert it into individual controls with binary mandates. Each control defines:

- **Responsible party** (e.g. system owners, system owners using RAG)
- **Obligation type** (must or may)
- **Binary or near-binary mandate**

Controls are categorized by type:

| Category | ~Share | Description | Modeled In |
|---|---|---|---|
| **Architectural** | ~50% | Infrastructure/topology decisions (e.g. data segmentation, encryption standards, isolated environments) | CALM |
| **Runtime** | ~25% | Per-request enforcement (e.g. output filtering, sensitive data detection, context-aware authorization) | CALM + Cupcake |
| **Procedural** | ~25% | Periodic audits and governance processes (e.g. data filtering audits, incident feedback loops) | CALM + EQTY Lab |

### Step 2: Model as CALM-Format Controls

Populate control-specific attributes in [CALM](https://github.com/finos/architecture-as-code) format:

- Control ID, name, and description
- Required evidence and enforcement method
- Binary, control-specific requirements
- (Optional) References to related AIGF mitigation categories

**Example** -- an architectural control for encryption at rest (P14-001):

```json
{
  "control-id": "P14-001",
  "name": "Establishing Standards for Encrypting Data at Rest",
  "description": "System owners must establish clear organizational policies...",
  "approvedAlgorithms": ["AES-256", "AES-192", "AES-128-GCM"],
  "minimumKeyLength": 256,
  "modeOfOperation": "GCM",
  "keyManagementSystem": "AWS KMS",
  "keyRotationPolicy": "90-days"
}
```

### Step 3: Model as Runtime Enforcement Rules (Cupcake)

Translate execution-dependent controls into [OPA/Rego](https://www.openpolicyagent.org/) policies that evaluate inputs, outputs, or agent actions at runtime. Define decision logic (allow, block, warn) applied by the [Cupcake](https://github.com/eqtylab/cupcake) enforcement layer.

**Only runtime controls flow through both CALM and Cupcake.** Architectural controls are defined in CALM alone. Procedural controls are defined in CALM and monitored via external tooling.

## Aligned FINOS Initiatives

This project leverages and complements several existing FINOS work streams pushing towards automated, machine-readable compliance:

| Project | Role in Pipeline |
|---|---|
| [AI Governance Framework (AIGF)](https://www.finos.org/ai-governance) | Source framework -- risk catalogue with 23 mitigations |
| [CALM (Common Architecture Language Model)](https://github.com/finos/architecture-as-code) | Schema for structuring controls in a consistent, machine-configurable format |
| [AI Reference Architecture Library](https://github.com/finos-labs/ai-reference-architecture-library) | FSI-specific reference architectures with threat models -- taxonomy for specific use cases |
| [Gemara](https://github.com/finos/gemara) | GRC Engineering Model for converting written governance controls into machine-readable, automated policy rules |
| [AI Evals Framework](https://www.finos.org/ai-strategic-initiative) | Taxonomy for AI evaluations in finance -- defining evals for specific use cases |

## Open Source vs. Commercial Certification

This project focuses on the **open source configuration layer**:

**Can:**
- Validate that controls are correctly defined and modeled in CALM and Cupcake
- Monitor that a system's policy logic behaves correctly when passed through open-source enforcement engines

**Cannot:**
- Produce tamper-evident proof that enforcement occurred consistently in production
- Guarantee that runtime controls were applied on every execution without gaps

The complementary **commercial verification layer** (e.g. [EQTY Lab](https://www.eqtylab.io/) Governance Studio) can provide tamper-proof evidence, continuous monitoring, audit-ready reports, and hardware-backed attestations for organizations requiring production-grade certification.

## Roadmap

1. **Atomize AIGF mitigations** -- Extract and categorize controls from all 23 AIGF mitigations into architectural, runtime, and procedural types
2. **Model controls in CALM** -- Define CALM-format schemas with control-specific requirements and evidence definitions
3. **Implement Rego policies** -- Translate runtime controls into OPA/Rego policies for Cupcake enforcement
4. **Validate end-to-end pipeline** -- Demonstrate full certification flow from AIGF guidance through CALM definition to runtime enforcement
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
