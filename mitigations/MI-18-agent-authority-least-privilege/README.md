# MI-18: Agent Authority Least Privilege Framework

Source AIGF Mitigation: [MI-18: Agent Authority Least Privilege Framework](https://air-governance-framework.finos.org/mitigations/mi-18_agent-authority-least-privilege-framework.html)

## Atomized Controls

| Control ID | Responsible Party | Obligation Type | Binary Mandate | Category |
| :--- | :--- | :--- | :--- | :--- |
| **`FINOS-PREV-018-001`** | System owners deploying autonomous or bounded-autonomy agents | `must` | System owners must verify the resolved action against the active mandate's scope, value ceiling, and non-revoked freshness at the point of commitment before executing any state-mutating tool or transaction. | **Runtime** (CALM defines the required commitment-gate architecture and mandatory input claims; runtime evaluation occurs at the pre-execution gate). |
| **`FINOS-PREV-018-002`** | System owners operating multi-agent or cross-institution delegated workflows | `must` | System owners must enforce atomic shared-limit reservations across concurrent agents and attenuate delegated authority monotonically across agent hops so no sub-agent exceeds its parent mandate's scope or remaining budget. | **Architectural & Runtime** (CALM specifies the atomic reservation boundary and delegation attenuation contract). |

## Why Host-Memory Policy Checks Alone Are Insufficient

As highlighted in AIGF discussions on stale authority and cross-institution delegation (`#407`, `#421`), checking a static credential when a task is queued does not prevent time-of-check to time-of-use (`TOCTOU`) authority drift or concurrent multi-agent budget exhaustion. `FINOS-PREV-018-001` and `FINOS-PREV-018-002` require commitment-time mandate freshness verification and atomic shared-limit reservation (`two-phase-reserve-commit`) so uncertain or in-flight commitments remain counted until deterministically settled or released.

## Artefacts

- Requirement Schemas:
  - [`requirements/FINOS-PREV-018-001.requirement.json`](./requirements/FINOS-PREV-018-001.requirement.json)
  - [`requirements/FINOS-PREV-018-002.requirement.json`](./requirements/FINOS-PREV-018-002.requirement.json)
- Reference Configurations:
  - [`configurations/FINOS-PREV-018-001.json`](./configurations/FINOS-PREV-018-001.json)
  - [`configurations/FINOS-PREV-018-002.json`](./configurations/FINOS-PREV-018-002.json)
