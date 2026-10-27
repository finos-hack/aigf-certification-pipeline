# MI-21: Agent Decision Audit and Explainability

## Source AIGF Guidance

- **AIGF ID:** `MI-21`
- **Title:** Agent Decision Audit and Explainability
- **Type:** Detective & Procedural (Audit & Transparency)
- **Related Risks:** `AIR-DET-014` (`RI-24`: Autonomous Agent Goal Drift and Unintended Actions), `AIR-GOV-003`, `AIR-OP-004`

## Atomized Controls

| Control ID | Name | Category | Obligation | Responsible Party |
|---|---|---|---|---|
| `FINOS-AUD-021-001` | Independently Verifiable `COSE_Sign1` and IETF SCITT (`RFC 9162`) Decision Receipts | Procedural & Audit | Must | System Owners Deploying Agentic Workflows |

### `FINOS-AUD-021-001` — Independently Verifiable `COSE_Sign1` and IETF SCITT (`RFC 9162`) Decision Receipts

System owners deploying autonomous or multi-agent workflows must emit a signed, append-only cryptographic decision receipt (`COSE_Sign1` / IETF SCITT `RFC 9162` inclusion proof) for every state-mutating tool invocation, mandate evaluation, or circuit-breaker event. Each receipt must bind the `mandate-id`, `policy-digest`, `inputs-hash`, `execution-environment-attestation-digest`, `decision-verdict` (`ALLOW`, `BLOCK`, `ESCALATE`), and `monotonic-sequence-number` so internal and external auditors can verify policy conformance offline without trusting mutable application logs.

## Files

- Requirement Schema: [`requirements/FINOS-AUD-021-001.requirement.json`](./requirements/FINOS-AUD-021-001.requirement.json)
- Reference Configuration: [`configurations/FINOS-AUD-021-001.json`](./configurations/FINOS-AUD-021-001.json)
