# MI-20: Real-Time Monitoring and Circuit Breakers

## Source AIGF Guidance

- **AIGF ID:** `MI-20`
- **Title:** Real-Time Monitoring and Circuit Breakers
- **Type:** Detective & Preventive (Runtime)
- **Related Risks:** `AIR-DET-014` (`RI-24`: Autonomous Agent Goal Drift and Unintended Actions), `AIR-SEC-010`, `AIR-OP-004`

## Atomized Controls

| Control ID | Name | Category | Obligation | Responsible Party |
|---|---|---|---|---|
| `FINOS-DET-020-001` | Deterministic Runtime and Collective-Exposure Circuit Breakers (`ST-01..ST-05`) | Runtime | Must | System Owners Deploying Agentic Workflows |

### `FINOS-DET-020-001` — Deterministic Runtime and Collective-Exposure Circuit Breakers (`ST-01..ST-05`)

System owners deploying autonomous or multi-agent financial workflows must enforce deterministic, fail-closed runtime circuit breakers across five mandatory state triggers (`ST-01` through `ST-05`), including aggregate collective-exposure caps across concurrent agent instances to prevent correlated high-velocity liquidity drains or cascading counterparty exposure:

- **`ST-01` (`velocity-and-rate-anomaly`)**: Trips when single-agent or aggregate call velocity or notional outflow rate exceeds configured window bounds.
- **`ST-02` (`scope-and-authority-violation`)**: Trips on repeated out-of-scope tool invocation attempts or revoked/expired mandate references.
- **`ST-03` (`loop-and-recursion-exhaustion`)**: Trips when cyclical tool-call graphs or delegation depth exceed configured bounds.
- **`ST-04` (`data-boundary-and-egress-violation`)**: Trips when restricted classification labels or unapproved external endpoints are detected.
- **`ST-05` (`collective-systemic-exposure-breach`)**: Trips when aggregate uncommitted reservations or net counterparty exposure across a fleet of concurrent agents exceed the institution-wide or desk-wide systemic risk ceiling, even when individual agent actions remain within their local per-agent limits.

## Files

- Requirement Schema: [`requirements/FINOS-DET-020-001.requirement.json`](./requirements/FINOS-DET-020-001.requirement.json)
- Reference Configuration: [`configurations/FINOS-DET-020-001.json`](./configurations/FINOS-DET-020-001.json)
