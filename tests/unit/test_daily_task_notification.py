from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import yaml

from scripts import github_project_sync as sync
from scripts import daily_task_notification as notify


TODAY = dt.date(2026, 3, 26)


def load_seed() -> dict:
    return yaml.safe_load(Path("data/project-seed.yaml").read_text(encoding="utf-8"))


def managed_issue(seed_id: str, title: str, *, number: int, state: str = "OPEN") -> dict:
    marker = {
        "seed_id": seed_id,
        "entity_kind": "issue",
        "fingerprint": "test",
        "source": "data/project-seed.yaml",
    }
    if seed_id.startswith("PC-"):
        marker["entity_kind"] = "phase_card"
    elif seed_id.startswith("WC-"):
        marker["entity_kind"] = "win_condition"
    body = f"<!-- {sync.MARKER_PREFIX}: {json.dumps(marker, ensure_ascii=False)} -->"
    return {
        "number": number,
        "title": title,
        "body": body,
        "state": state,
        "labels": [],
    }


def existing_issue_snapshot() -> list[dict]:
    return [
        managed_issue("ISS-001", "[資格] 2026-03: 第一種電気工事士 過去問入手・1年分着手", number=19),
        managed_issue("ISS-002", "[AI] 2026-03: GitHub Projects 初期セットアップ", number=20),
        managed_issue("ISS-003", "[AI] 2026-03: Codex / Claude Code 環境構築", number=21),
        managed_issue("ISS-004", "[証跡] 2026-03: 仕様書1件を技術視点で読み直す", number=22),
        managed_issue("ISS-005", "[資格] 2026-04: 学科試験 過去問5年分×2周", number=23),
        managed_issue("ISS-006", "[資格] 2026-04-27: 第一種電気工事士 学科試験 受験", number=24),
        managed_issue("PC-phase-0", "[26/03/14-04/27] [PHASE] 直前対策期", number=65),
        managed_issue("WC-001", "[26/03/14-04/27] [WIN] 学科の過去問ループを立ち上げる", number=72),
        managed_issue("WC-002", "[26/03/14-04/27] [WIN] GitHub Projects と AI 運用基盤を整える", number=73),
    ]


def test_build_plan_picks_single_focus_task_for_today() -> None:
    plan = notify.build_plan(load_seed(), existing_issue_snapshot(), today=TODAY)

    assert plan.focus is not None
    assert plan.focus.seed_id == "ISS-001"
    assert plan.focus.issue_number == 19
    assert plan.focus.title.startswith("[資格]")
    assert plan.focus.first_execution.startswith("朝 (60分)")
    assert all(item.seed_id != "PC-phase-0" for item in plan.blocked + plan.deferred)
    assert any(item.seed_id == "ISS-005" and "ISS-001" in item.reason for item in plan.blocked)
    assert any(item.seed_id == "ISS-002" and "試験優先期間" in item.reason for item in plan.deferred)


def test_build_plan_accepts_uppercase_issue_states_from_gh_cli() -> None:
    snapshot = existing_issue_snapshot()
    snapshot[0]["state"] = "OPEN"
    snapshot[4]["state"] = "OPEN"

    plan = notify.build_plan(load_seed(), snapshot, today=TODAY)

    assert plan.focus is not None
    assert plan.focus.seed_id == "ISS-001"


def test_closed_dependency_is_recognized_when_gh_cli_uses_uppercase_closed() -> None:
    snapshot = existing_issue_snapshot()
    snapshot[0]["state"] = "CLOSED"

    plan = notify.build_plan(load_seed(), snapshot, today=TODAY)

    assert all(item.seed_id != "ISS-005" for item in plan.blocked)


def test_render_issue_body_shows_one_focus_and_not_all_parallel_tasks() -> None:
    body = notify.render_issue_body(
        notify.build_plan(load_seed(), existing_issue_snapshot(), today=TODAY),
        today=TODAY,
        recipient="foru1215",
    )

    assert "@foru1215 今日の主タスク通知です。" in body
    assert "今日は **1件** に絞ります。" in body
    assert "#19 [資格] 2026-03: 第一種電気工事士 過去問入手・1年分着手" in body
    assert "[26/03/14-04/27] [PHASE] 直前対策期" not in body
    assert "GitHub Projects 初期セットアップ" in body
    assert "必要なツール、設定、権限を洗い出す" not in body
