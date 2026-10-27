# MI-19: Tool Chain Validation and Sanitization

Source AIGF Mitigation: [MI-19: Tool Chain Validation and Sanitization](https://air-governance-framework.finos.org/mitigations/mi-19_tool-chain-validation-and-sanitization.html)

## Atomized Controls

| Control ID | Responsible Party | Obligation Type | Binary Mandate | Category |
| :--- | :--- | :--- | :--- | :--- |
| **`FINOS-PREV-019-001`** | System owners deploying tool-using agents | `must` | System owners must ensure selected tools don't exceed the agent's or user's authorization level for the current transaction. | **Runtime** (CALM specifies the required authorization architecture and input bindings; pre-execution enforcement occurs at the runtime policy / enclave gate). |

## Artefacts

- Requirement Schema: [`requirements/FINOS-PREV-019-001.requirement.json`](./requirements/FINOS-PREV-019-001.requirement.json)
- Reference Configuration: [`configurations/FINOS-PREV-019-001.json`](./configurations/FINOS-PREV-019-001.json)
