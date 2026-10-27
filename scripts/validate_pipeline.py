#!/usr/bin/env python3
"""
AIGF Certification Pipeline — Deterministic CALM Control & Schema Validator
Copyright (c) Contributors to the AIGF Certification Pipeline project.
SPDX-License-Identifier: Apache-2.0

Validates all atomized AIGF mitigations under `mitigations/`:
  1. Directory hygiene: README.md, requirements/*.requirement.json, configurations/*.json
  2. Schema invariants: JSON Schema 2020-12, canonical $id matching repo path,
     HTTPS CALM meta-schema $ref, additionalProperties: false, and uniqueItems: true
  3. Instance conformance: Recursive validation of every configuration JSON against
     its corresponding CALM control requirement schema.
  4. Adversarial self-test (`--self-test`): Executes 12 negative mutation tests to
     prove fail-closed detection of schema drift, duplicate array bypasses, insecure
     $ref URIs, stale mandates, and collective circuit-breaker omissions.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_ID_PREFIX = "https://finos-labs.github.io/aigf-certification-pipeline/mitigations"
CALM_META_REF = "https://calm.finos.org/controls/2025-03/meta/control-requirement.json"
JSON_SCHEMA_2020_12 = "https://json-schema.org/draft/2020-12/schema"


def is_valid_https_uri(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.netloc)
    except Exception:
        return False


def validate_json_value(instance: object, schema: dict, path: str = "$") -> list[str]:
    """Deterministic zero-dependency JSON Schema 2020-12 subset validator for CALM controls."""
    errors: list[str] = []

    if "allOf" in schema:
        for idx, subschema in enumerate(schema["allOf"]):
            if "$ref" in subschema:
                continue
            errors.extend(validate_json_value(instance, subschema, f"{path}.allOf[{idx}]"))

    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object, got {type(instance).__name__}"]
        required = schema.get("required", [])
        for req_key in required:
            if req_key not in instance:
                errors.append(f"{path}: missing required property '{req_key}'")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and props:
            for key in instance:
                if key == "$schema":
                    continue
                if key not in props:
                    errors.append(f"{path}: unexpected additional property '{key}'")
        for key, val in instance.items():
            if key == "$schema":
                continue
            if key in props:
                errors.extend(validate_json_value(val, props[key], f"{path}.{key}"))

    elif expected_type == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array, got {type(instance).__name__}"]
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: array length {len(instance)} is less than minItems {min_items}")
        if schema.get("uniqueItems") is True:
            serialized = [json.dumps(item, sort_keys=True) for item in instance]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: array contains duplicate items (violates uniqueItems: true)")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(instance):
                errors.extend(validate_json_value(item, item_schema, f"{path}[{idx}]"))

    elif expected_type == "string":
        if not isinstance(instance, str):
            return [f"{path}: expected string, got {type(instance).__name__}"]
        if schema.get("format") == "uri" and not is_valid_https_uri(instance):
            errors.append(f"{path}: value '{instance}' is not a valid HTTPS URI")

    elif expected_type == "integer":
        if isinstance(instance, bool) or not isinstance(instance, int):
            return [f"{path}: expected integer, got {type(instance).__name__}"]
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: integer {instance} is less than minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: integer {instance} exceeds maximum {schema['maximum']}")

    elif expected_type == "boolean":
        if not isinstance(instance, bool):
            return [f"{path}: expected boolean, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum {schema['enum']}")

    return errors


def validate_requirement_schema_structure(
    schema: dict, mitigation_dir_name: str, req_filename: str
) -> list[str]:
    """Enforces structural invariants on a CALM .requirement.json file."""
    errors: list[str] = []
    if schema.get("$schema") != JSON_SCHEMA_2020_12:
        errors.append(
            f"{req_filename}: $schema must be '{JSON_SCHEMA_2020_12}', got {schema.get('$schema')!r}"
        )

    expected_id = f"{CANONICAL_ID_PREFIX}/{mitigation_dir_name}/requirements/{req_filename}"
    if schema.get("$id") != expected_id:
        errors.append(
            f"{req_filename}: $id mismatch. Expected '{expected_id}', got {schema.get('$id')!r}"
        )

    all_of = schema.get("allOf")
    if not isinstance(all_of, list) or len(all_of) < 1:
        errors.append(f"{req_filename}: must contain an 'allOf' list referencing CALM meta-schema")
        return errors

    ref = all_of[0].get("$ref")
    if ref != CALM_META_REF:
        errors.append(
            f"{req_filename}: allOf[0].$ref must be '{CALM_META_REF}' (HTTPS required), got {ref!r}"
        )

    if schema.get("additionalProperties") is not False:
        errors.append(f"{req_filename}: top-level schema must set 'additionalProperties': false")

    props = schema.get("properties", {})
    for req_field in ("control-id", "name", "description"):
        if req_field not in props or "const" not in props[req_field]:
            errors.append(
                f"{req_filename}: properties.{req_field} must be pinned via 'const'"
            )

    def check_arrays(node: dict, node_path: str) -> None:
        if node.get("type") == "array":
            items = node.get("items", {})
            if node.get("minItems", 0) > 1 and "enum" in items:
                if node.get("uniqueItems") is not True:
                    errors.append(
                        f"{req_filename}: {node_path} has minItems > 1 over an enum and must set 'uniqueItems': true"
                    )
        for k, v in node.get("properties", {}).items():
            if isinstance(v, dict):
                check_arrays(v, f"{node_path}.{k}")

    check_arrays(schema, "schema")
    return errors


def validate_repository(root: Path = REPO_ROOT) -> tuple[bool, list[str], int]:
    mitigations_root = root / "mitigations"
    if not mitigations_root.is_dir():
        return False, ["Missing mitigations/ directory"], 0

    all_errors: list[str] = []
    controls_checked = 0

    mitigation_dirs = sorted(
        [d for d in mitigations_root.iterdir() if d.is_dir() and d.name.startswith("MI-")]
    )
    if not mitigation_dirs:
        return False, ["No MI-* directories found under mitigations/"], 0

    for mdir in mitigation_dirs:
        readme_path = mdir / "README.md"
        if not readme_path.is_file():
            all_errors.append(f"{mdir.name}: missing README.md")
            readme_text = ""
        else:
            readme_text = readme_path.read_text(encoding="utf-8")

        req_dir = mdir / "requirements"
        cfg_dir = mdir / "configurations"
        if not req_dir.is_dir():
            all_errors.append(f"{mdir.name}: missing requirements/ directory")
            continue
        if not cfg_dir.is_dir():
            all_errors.append(f"{mdir.name}: missing configurations/ directory")
            continue

        req_files = sorted(req_dir.glob("*.requirement.json"))
        if not req_files:
            all_errors.append(f"{mdir.name}: no *.requirement.json files found in requirements/")

        for req_file in req_files:
            control_id = req_file.name.replace(".requirement.json", "")
            controls_checked += 1

            if readme_text and control_id not in readme_text:
                all_errors.append(
                    f"{mdir.name}/README.md: does not document control ID '{control_id}'"
                )

            try:
                req_schema = json.loads(req_file.read_text(encoding="utf-8"))
            except Exception as exc:
                all_errors.append(f"{req_file}: invalid JSON ({exc})")
                continue

            all_errors.extend(
                validate_requirement_schema_structure(req_schema, mdir.name, req_file.name)
            )

            cfg_file = cfg_dir / f"{control_id}.json"
            if not cfg_file.is_file():
                all_errors.append(
                    f"{mdir.name}: missing matching configuration file configurations/{control_id}.json"
                )
                continue

            try:
                cfg_instance = json.loads(cfg_file.read_text(encoding="utf-8"))
            except Exception as exc:
                all_errors.append(f"{cfg_file}: invalid JSON ({exc})")
                continue

            expected_schema_uri = req_schema.get("$id")
            if cfg_instance.get("$schema") != expected_schema_uri:
                all_errors.append(
                    f"{cfg_file.name}: $schema '{cfg_instance.get('$schema')}' does not match requirement $id '{expected_schema_uri}'"
                )

            instance_errors = validate_json_value(cfg_instance, req_schema, cfg_file.name)
            all_errors.extend(instance_errors)

    return len(all_errors) == 0, all_errors, controls_checked


def run_self_tests() -> bool:
    """Runs 12 adversarial red-team mutation tests against the validator."""
    print("Running 12 adversarial red-team self-test scenarios...")
    passed = 0
    total = 12

    base_req_path = (
        REPO_ROOT
        / "mitigations/MI-19-tool-chain-validation-and-sanitization"
        / "requirements/FINOS-PREV-019-001.requirement.json"
    )
    base_cfg_path = (
        REPO_ROOT
        / "mitigations/MI-19-tool-chain-validation-and-sanitization"
        / "configurations/FINOS-PREV-019-001.json"
    )
    mi18_1_req_path = (
        REPO_ROOT
        / "mitigations/MI-18-agent-authority-least-privilege"
        / "requirements/FINOS-PREV-018-001.requirement.json"
    )
    mi18_1_cfg_path = (
        REPO_ROOT
        / "mitigations/MI-18-agent-authority-least-privilege"
        / "configurations/FINOS-PREV-018-001.json"
    )
    mi18_2_req_path = (
        REPO_ROOT
        / "mitigations/MI-18-agent-authority-least-privilege"
        / "requirements/FINOS-PREV-018-002.requirement.json"
    )
    mi18_2_cfg_path = (
        REPO_ROOT
        / "mitigations/MI-18-agent-authority-least-privilege"
        / "configurations/FINOS-PREV-018-002.json"
    )
    mi20_req_path = (
        REPO_ROOT
        / "mitigations/MI-20-real-time-monitoring-and-circuit-breakers"
        / "requirements/FINOS-DET-020-001.requirement.json"
    )
    mi20_cfg_path = (
        REPO_ROOT
        / "mitigations/MI-20-real-time-monitoring-and-circuit-breakers"
        / "configurations/FINOS-DET-020-001.json"
    )
    mi21_req_path = (
        REPO_ROOT
        / "mitigations/MI-21-agent-decision-audit-and-explainability"
        / "requirements/FINOS-AUD-021-001.requirement.json"
    )
    mi21_cfg_path = (
        REPO_ROOT
        / "mitigations/MI-21-agent-decision-audit-and-explainability"
        / "configurations/FINOS-AUD-021-001.json"
    )

    base_req = json.loads(base_req_path.read_text(encoding="utf-8"))
    base_cfg = json.loads(base_cfg_path.read_text(encoding="utf-8"))
    mi18_1_req = json.loads(mi18_1_req_path.read_text(encoding="utf-8"))
    mi18_1_cfg = json.loads(mi18_1_cfg_path.read_text(encoding="utf-8"))
    mi18_2_req = json.loads(mi18_2_req_path.read_text(encoding="utf-8"))
    mi18_2_cfg = json.loads(mi18_2_cfg_path.read_text(encoding="utf-8"))
    mi20_req = json.loads(mi20_req_path.read_text(encoding="utf-8"))
    mi20_cfg = json.loads(mi20_cfg_path.read_text(encoding="utf-8"))
    mi21_req = json.loads(mi21_req_path.read_text(encoding="utf-8"))
    mi21_cfg = json.loads(mi21_cfg_path.read_text(encoding="utf-8"))

    scenarios = []

    # 1. Broken $id path (/MI-19/ instead of /MI-19-tool-chain-validation-and-sanitization/ and .json instead of .requirement.json)
    s1 = copy.deepcopy(base_req)
    s1["$id"] = (
        "https://finos-labs.github.io/aigf-certification-pipeline/mitigations/MI-19/requirements/FINOS-PREV-019-001.json"
    )
    scenarios.append(
        (
            "1. Detect broken $id directory/filename path in requirement schema",
            validate_requirement_schema_structure(
                s1,
                "MI-19-tool-chain-validation-and-sanitization",
                "FINOS-PREV-019-001.requirement.json",
            ),
        )
    )

    # 2. Insecure http:// CALM meta-schema $ref
    s2 = copy.deepcopy(base_req)
    s2["allOf"][0]["$ref"] = "http://calm.finos.org/controls/2025-03/meta/control-requirement.json"
    scenarios.append(
        (
            "2. Reject insecure http:// CALM meta-schema $ref",
            validate_requirement_schema_structure(
                s2,
                "MI-19-tool-chain-validation-and-sanitization",
                "FINOS-PREV-019-001.requirement.json",
            ),
        )
    )

    # 3. Missing uniqueItems: true on enum array with minItems > 1
    s3 = copy.deepcopy(base_req)
    del s3["properties"]["required-decision-inputs"]["uniqueItems"]
    scenarios.append(
        (
            "3. Detect missing uniqueItems: true on required-decision-inputs schema",
            validate_requirement_schema_structure(
                s3,
                "MI-19-tool-chain-validation-and-sanitization",
                "FINOS-PREV-019-001.requirement.json",
            ),
        )
    )

    # 4. Missing additionalProperties: false on requirement schema
    s4 = copy.deepcopy(base_req)
    del s4["additionalProperties"]
    scenarios.append(
        (
            "4. Detect missing additionalProperties: false on requirement schema",
            validate_requirement_schema_structure(
                s4,
                "MI-19-tool-chain-validation-and-sanitization",
                "FINOS-PREV-019-001.requirement.json",
            ),
        )
    )

    # 5. Duplicate items in required-decision-inputs configuration instance
    s5 = copy.deepcopy(base_cfg)
    s5["required-decision-inputs"] = ["user-id", "user-id", "user-id"]
    scenarios.append(
        (
            "5. Reject duplicate items in required-decision-inputs instance",
            validate_json_value(s5, base_req),
        )
    )

    # 6. Undeclared additional property injection in config
    s6 = copy.deepcopy(base_cfg)
    s6["bypass-policy"] = True
    scenarios.append(
        (
            "6. Reject undeclared additional property injection (additionalProperties: false)",
            validate_json_value(s6, base_req),
        )
    )

    # 7. MI-18 (001): Stale mandate window exceeding 300s bound
    s7 = copy.deepcopy(mi18_1_cfg)
    s7["max-mandate-staleness-seconds"] = 3600
    scenarios.append(
        (
            "7. Reject MI-18-001 stale mandate window (> 300 seconds)",
            validate_json_value(s7, mi18_1_req),
        )
    )

    # 8. MI-18 (002): Excessive delegation hop depth (> 5)
    s8 = copy.deepcopy(mi18_2_cfg)
    s8["max-delegation-depth"] = 12
    scenarios.append(
        (
            "8. Reject MI-18-002 delegation hop depth exceeding maximum bound",
            validate_json_value(s8, mi18_2_req),
        )
    )

    # 9. MI-20: Missing ST-05 collective systemic exposure trigger
    s9 = copy.deepcopy(mi20_cfg)
    s9["mandatory-state-triggers"] = [
        "ST-01-velocity-and-rate-anomaly",
        "ST-02-scope-and-authority-violation",
        "ST-03-loop-and-recursion-exhaustion",
        "ST-04-data-boundary-and-egress-violation",
    ]
    scenarios.append(
        (
            "9. Reject MI-20 circuit breaker omitting ST-05 collective systemic exposure trigger",
            validate_json_value(s9, mi20_req),
        )
    )

    # 10. MI-20: Unattended auto-reset enabled after circuit breaker trip
    s10 = copy.deepcopy(mi20_cfg)
    s10["auto-reset-permitted"] = True
    scenarios.append(
        (
            "10. Reject MI-20 circuit breaker enabling unattended auto-reset",
            validate_json_value(s10, mi20_req),
        )
    )

    # 11. MI-21: Missing execution-environment-attestation-digest claim in SCITT receipt
    s11 = copy.deepcopy(mi21_cfg)
    s11["required-receipt-claims"] = [
        "mandate-id",
        "policy-digest",
        "inputs-hash",
        "decision-verdict",
        "monotonic-sequence-number",
    ]
    scenarios.append(
        (
            "11. Reject MI-21 audit receipt omitting execution-environment-attestation-digest",
            validate_json_value(s11, mi21_req),
        )
    )

    # 12. MI-21: Sub-regulatory audit retention period (< 2555 days / 7 years)
    s12 = copy.deepcopy(mi21_cfg)
    s12["minimum-retention-days"] = 30
    scenarios.append(
        (
            "12. Reject MI-21 audit retention period below 7-year (2555-day) regulatory floor",
            validate_json_value(s12, mi21_req),
        )
    )

    for label, errs in scenarios:
        if errs:
            print(f"  [PASS] {label} -> caught ({errs[0]})")
            passed += 1
        else:
            print(f"  [FAIL] {label} -> mutation was NOT caught!")

    print(f"\nAdversarial Self-Test Summary: {passed}/{total} scenarios passed.")
    return passed == total


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate AIGF Certification Pipeline CALM schemas and configurations."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run 12 adversarial negative mutation tests against the validator.",
    )
    args = parser.parse_args()

    ok, errors, count = validate_repository(REPO_ROOT)
    if not ok:
        print(f"[FAIL] Repository validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(
        f"[PASS] Validated {count} atomized CALM controls across all MI-* directories with 0 errors."
    )

    if args.self_test:
        if not run_self_tests():
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
