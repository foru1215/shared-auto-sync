from __future__ import annotations

from scripts import github_project_sync as sync


def test_render_issue_body_uses_japanese_action_template() -> None:
    issue = {
        "id": "ISS-999",
        "body": "過去問演習の進め方を整理する。",
        "outcome": "誤答の傾向が見える状態にする。",
        "next_action": "ノートと教材を開く。",
        "why_this_matters": "面接で語れる学習記録につなげる。",
        "career_link": "職務経歴書で語れる実績を作る",
        "ai_link": "AI を補助線として使う",
        "device": "PC / ノート",
        "inputs": ["教材", "ノート"],
        "things_to_make": ["技術メモ"],
        "work_steps": ["手順1", "手順2", "手順3"],
        "deliverables": ["成果物A"],
        "evidence_type": "Document",
        "evidence_to_keep": ["証跡A"],
        "dod": ["完了条件1", "完了条件2"],
        "completion_check": ["確認1", "確認2"],
        "daily_execution": ["朝: 誤答確認", "夜: 本体学習"],
        "active_from": "2026-03-14",
        "deferred_until": None,
        "due_date": "2026-03-31",
        "monthly_bucket": "2026-03",
        "quarter": "2026-Q1",
        "time_block": "平日 60分",
        "estimate": "3 sessions",
        "energy": "Medium",
        "focus": "再現・演習",
        "review_note": "レビュー時に更新する。",
        "task_type": "study",
    }
    body = sync.render_issue_body(
        issue,
        entity_kind="issue",
        marker={
            "seed_id": "ISS-999",
            "entity_kind": "issue",
            "fingerprint": "abc",
            "source": "data/project-seed.yaml",
        },
        phase_name="筆記試験フェーズ",
        blocked_titles=["ISS-001: blocker title"],
        linked_titles=["WC-001: sample win condition"],
    )

    assert "## 概要" in body
    assert "## 完了条件" in body
    assert "## 今回の到達目標" in body
    assert "## 最初の一手（5分で開始できる行動）" in body
    assert "## タスクリスト" in body
    assert "## 補足メモ" in body
    assert "## 記録欄" in body
    assert "- [ ] ノートと教材を開く。" in body
    assert "依存Issue: ISS-001: blocker title" in body
    assert "関連Issue: WC-001: sample win condition" in body
    assert "github-project-sync" in body


def test_render_epic_body_lists_child_issues_in_japanese() -> None:
    epic = {
        "id": "E-TEST",
        "name": "学科対策",
        "description": "学科対策の親Issueとして主要論点を束ねる。",
        "priority": "p0",
        "labels": ["area:license", "phase:written-exam"],
    }
    child_issues = [
        {"id": "ISS-001", "title": "過去問を解く", "phase": "P0", "monthly_bucket": "2026-03"},
        {"id": "ISS-002", "title": "弱点を整理する", "phase": "P0", "monthly_bucket": "2026-04"},
    ]
    body = sync.render_epic_body(
        epic,
        child_issues,
        phase_name_by_id={"P0": "筆記試験フェーズ"},
        marker={
            "seed_id": "E-TEST",
            "entity_kind": "epic",
            "fingerprint": "abc",
            "source": "data/project-seed.yaml",
        },
    )

    assert "## 概要" in body
    assert "## 完了条件" in body
    assert "## タスクリスト" in body
    assert "### 含まれるSeed Issue" in body
    assert "ISS-001: 過去問を解く" in body
    assert "ISS-002: 弱点を整理する" in body
    assert "github-project-sync" in body
