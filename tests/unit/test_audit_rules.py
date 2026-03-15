from __future__ import annotations

import copy
import datetime as dt
import pathlib

import yaml

from scripts import github_project_sync as sync


def load_seed() -> dict:
    return yaml.safe_load(pathlib.Path("data/project-seed.yaml").read_text(encoding="utf-8"))


def test_real_seed_audit_has_no_fail_or_warn_findings() -> None:
    findings = sync.build_audit_findings(load_seed(), today=dt.date(2026, 3, 14))
    summary = sync.summarize_audit(findings)
    assert summary["FAIL"] == 0
    assert summary["WARN"] == 0


def test_audit_detects_missing_dod() -> None:
    seed = copy.deepcopy(load_seed())
    seed["issues"][0]["dod"] = []
    findings = sync.build_audit_findings(seed, today=dt.date(2026, 3, 14))
    assert any(item.code == "missing-dod" and item.severity == "FAIL" for item in findings)


def test_audit_detects_missing_next_action() -> None:
    seed = copy.deepcopy(load_seed())
    seed["issues"][0]["next_action"] = ""
    findings = sync.build_audit_findings(seed, today=dt.date(2026, 3, 14))
    assert any(item.code == "missing-next-action" and item.severity == "FAIL" for item in findings)
