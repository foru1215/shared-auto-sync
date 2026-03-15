from __future__ import annotations

import datetime as dt
import pathlib

import yaml

from scripts import github_project_sync as sync


def load_seed() -> dict:
    return yaml.safe_load(pathlib.Path("data/project-seed.yaml").read_text(encoding="utf-8"))


def test_seed_field_specs_include_project1_style_fields() -> None:
    specs = sync.seed_field_specs(load_seed())
    names = {spec.name for spec in specs}
    assert "Status" in names
    assert "Deferred Until" in names
    assert "DoD Ready" in names
    assert "Start Date" in names
    assert "End Date" in names
    assert "Execution Time Block" in names
    assert "Execution Outcome" in names
    status_spec = next(spec for spec in specs if spec.name == "Status")
    assert "Deferred" in status_spec.options
    area_spec = next(spec for spec in specs if spec.name == "Area")
    assert "Security" in area_spec.options


def test_build_planned_issues_sets_extended_field_values() -> None:
    planned_issues = sync.build_planned_issues(
        load_seed(), today=dt.date(2026, 3, 14), closed_issue_seed_ids=set()
    )
    issue = next(item for item in planned_issues if item.seed_id == "ISS-025")
    assert issue.field_values["Status"] == "Deferred"
    assert issue.field_values["Task Type"] == "Exam"
    assert issue.field_values["Deferred Until"] == "2026-12-31"
    assert issue.field_values["Exam Priority Guard"] == "Exam Priority"
    assert issue.field_values["Execution Time Block"]
    assert issue.field_values["Execution Outcome"]


def test_build_planned_issues_includes_phase_cards_and_win_conditions() -> None:
    planned_issues = sync.build_planned_issues(
        load_seed(), today=dt.date(2026, 3, 14), closed_issue_seed_ids=set()
    )
    assert any(item.seed_id == "PC-phase-0" for item in planned_issues)
    assert any(item.seed_id == "WC-001" for item in planned_issues)


def test_security_track_maps_to_security_area() -> None:
    planned_issues = sync.build_planned_issues(
        load_seed(), today=dt.date(2026, 8, 1), closed_issue_seed_ids=set()
    )
    issue = next(item for item in planned_issues if item.seed_id == "ISS-043")
    assert issue.field_values["Area"] == "Security"
