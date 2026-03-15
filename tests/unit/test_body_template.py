from __future__ import annotations

from scripts import github_project_sync as sync


def test_render_issue_body_contains_project1_sections() -> None:
    issue = {
        "id": "ISS-999",
        "body": "サンプルの概要です。",
        "outcome": "完了条件が明確になっている。",
        "next_action": "ノートと教材を開く。",
        "why_this_matters": "面接で語れる成果へつなげる。",
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
    }
    body = sync.render_issue_body(
        issue,
        marker={
            "seed_id": "ISS-999",
            "entity_kind": "issue",
            "fingerprint": "abc",
            "source": "data/project-seed.yaml",
        },
        phase_name="Written Exam",
        blocked_titles=["ISS-001: blocker title"],
        linked_titles=["WC-001: sample win condition"],
    )
    assert "## Outcome" in body
    assert "## Next Action" in body
    assert "## Device" in body
    assert "## Inputs" in body
    assert "## Things to make" in body
    assert "## Work checklist" in body
    assert "## Completion check" in body
    assert "## Daily execution" in body
    assert "ISS-001: blocker title" in body
    assert "WC-001: sample win condition" in body
    assert "github-project-sync" in body
