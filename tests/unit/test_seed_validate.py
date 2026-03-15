from __future__ import annotations

import copy
import pathlib

import yaml

from scripts import github_project_sync as sync


def load_seed() -> dict:
    path = pathlib.Path("data/project-seed.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_real_seed_has_no_validation_failures_or_warnings() -> None:
    errors, warnings = sync.validate_seed(load_seed())
    assert errors == []
    assert warnings == []


def test_validate_seed_fails_when_task_type_is_missing() -> None:
    seed = load_seed()
    broken = copy.deepcopy(seed)
    broken["issues"][0].pop("task_type")
    errors, warnings = sync.validate_seed(broken)
    assert any("invalid task_type" in error for error in errors)
    assert warnings == []


def test_validate_seed_fails_when_phase_cards_are_missing() -> None:
    seed = load_seed()
    broken = copy.deepcopy(seed)
    broken.pop("phase_cards")
    errors, _warnings = sync.validate_seed(broken)
    assert "Missing top-level section: phase_cards" in errors
