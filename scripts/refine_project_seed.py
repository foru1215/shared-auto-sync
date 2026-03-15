from __future__ import annotations

import datetime as dt
import pathlib

import yaml


PHASE_LABEL_BY_ID = {
    "phase-0": "phase:written-exam",
    "phase-1": "phase:practical-exam",
    "phase-2": "phase:control-foundation",
    "phase-3": "phase:plc-growth",
    "phase-4": "phase:denken-ramp",
    "phase-5": "phase:ai-specialist",
    "phase-6": "phase:career-finish",
}

PHASE_MAINLINE = {
    "phase-0": "第一種電気工事士 学科",
    "phase-1": "第一種電気工事士 実技",
    "phase-2": "制御基礎と図面読解",
    "phase-3": "PLC / シーケンス制御",
    "phase-4": "電験三種 段階導入",
    "phase-5": "AI 成果物 + 転職準備",
    "phase-6": "応募・面接・内定獲得",
}

PHASE_DEFERRED_SCOPE = {
    "phase-0": ["電験三種の本格着手", "転職書類の本格作成"],
    "phase-1": ["電験三種の本格着手", "AI の深掘り学習"],
    "phase-2": ["転職活動の本格開始"],
    "phase-3": ["電験三種の前面化", "転職活動の本格開始"],
    "phase-4": ["AI 成果物の主役化"],
    "phase-5": ["新しい資格の追加着手"],
    "phase-6": ["新しい学習テーマの追加"],
}

TASK_PROFILES = {
    "exam": {
        "device": "iPad / ノート",
        "time_block": "平日 60-90分 + 休日 120分",
        "estimate": "3-5 sessions",
        "energy": "High",
        "focus": "再現・演習・誤答修正",
        "inputs": ["過去問", "参考書または学習アプリ", "誤答メモ"],
        "daily_execution": [
            "朝: 前回の誤答または要点を3つだけ再確認する",
            "主作業: 過去問・複線図・直前対策の本体を1セット進める",
            "終了前: 間違い理由と次回の再テスト対象を記録する",
        ],
    },
    "study": {
        "device": "ノート / iPad",
        "time_block": "平日 60分",
        "estimate": "2-3 sessions",
        "energy": "Medium",
        "focus": "理解・整理・ノート化",
        "inputs": ["教材", "ノート", "図や例題"],
        "daily_execution": [
            "セッション1: 範囲確認と要点の下書きを作る",
            "セッション2: 自分の言葉で説明できる形へ整える",
            "セッション3: 弱点だけを見直して次の範囲へつなぐ",
        ],
    },
    "plc": {
        "device": "PC / シミュレータ / ノート",
        "time_block": "平日 60分 + 休日 120分",
        "estimate": "3-4 sessions",
        "energy": "High",
        "focus": "実装・動作確認・説明可能化",
        "inputs": ["シミュレータ", "ラダー図", "課題仕様"],
        "daily_execution": [
            "セッション1: 仕様と入出力を整理する",
            "セッション2: ラダーを組んで動作を確認する",
            "セッション3: 修正点と学びを技術メモへ残す",
        ],
    },
    "evidence": {
        "device": "PC / ノート",
        "time_block": "週末 60-90分",
        "estimate": "2 sessions",
        "energy": "Medium",
        "focus": "整理・言語化・証跡化",
        "inputs": ["仕様書", "現場メモ", "改善案"],
        "daily_execution": [
            "セッション1: 材料を集めて技術観点を整理する",
            "セッション2: 面接で語れる形の技術メモにまとめる",
        ],
    },
    "ai": {
        "device": "PC",
        "time_block": "週末 120-180分",
        "estimate": "3-4 sessions",
        "energy": "High",
        "focus": "試作・検証・文章化",
        "inputs": ["Claude Code / Codex", "仕様メモ", "評価観点"],
        "daily_execution": [
            "セッション1: 作るものと評価観点を1枚に整理する",
            "セッション2: 小さく試作して動作を確認する",
            "セッション3: 実務・面接に接続する説明を残す",
        ],
    },
    "career": {
        "device": "PC",
        "time_block": "週末 60-90分",
        "estimate": "2-3 sessions",
        "energy": "Medium",
        "focus": "書類・面接・応募導線",
        "inputs": ["実績メモ", "職務経歴書ドラフト", "求人要件"],
        "daily_execution": [
            "セッション1: 伝える実績を3件に絞る",
            "セッション2: 書類または面接回答を更新する",
            "セッション3: 次回改善点をメモして再利用可能化する",
        ],
    },
    "review": {
        "device": "GitHub Projects / ノート",
        "time_block": "30-60分",
        "estimate": "1 session",
        "energy": "Low",
        "focus": "棚卸し・優先順位・軌道修正",
        "inputs": ["GitHub Projects", "実績メモ", "前回レビュー"],
        "daily_execution": [
            "今の In Progress を確認し、主役を1つに絞る",
            "未完・Blocker・Deferred を棚卸しする",
            "次回までの最優先タスクを1つだけ決める",
        ],
    },
    "deliverable": {
        "device": "PC",
        "time_block": "週末 120-180分",
        "estimate": "4 sessions",
        "energy": "High",
        "focus": "仕上げ・公開・説明準備",
        "inputs": ["既存成果物", "スクリーンショット", "説明文"],
        "daily_execution": [
            "セッション1: 仕上げに必要な差分を洗い出す",
            "セッション2: 成果物を更新して確認する",
            "セッション3: 公開用の説明と証跡を整える",
        ],
    },
    "setup": {
        "device": "PC",
        "time_block": "60-90分",
        "estimate": "1-2 sessions",
        "energy": "Medium",
        "focus": "設定・検証・運用開始",
        "inputs": ["設定値", "CLI", "確認用チェックリスト"],
        "daily_execution": [
            "セッション1: 現状確認と設定反映を行う",
            "セッション2: 動作確認して運用ルールを記録する",
        ],
    },
}

WIN_CONDITION_SPECS = [
    ("WC-001", "phase-0", "学科の過去問ループを立ち上げる", ["ISS-001", "ISS-005", "ISS-006"], ["area:license"]),
    ("WC-002", "phase-0", "GitHub Projects と AI 運用基盤を整える", ["ISS-002", "ISS-003"], ["area:ai"]),
    ("WC-003", "phase-0", "実務証跡の記録を止めない", ["ISS-004", "ISS-R01", "ISS-R02", "ISS-R04"], ["area:evidence"]),
    ("WC-004", "phase-1", "実技13問を複線図まで反復できるようにする", ["ISS-007", "ISS-008", "ISS-009"], ["area:license"]),
    ("WC-005", "phase-1", "AI 学習を補助線として維持する", ["ISS-010", "ISS-R01", "ISS-R02"], ["area:ai"]),
    ("WC-006", "phase-2", "制御基礎ノートを5章まで完成させる", ["ISS-011", "ISS-012", "ISS-013", "ISS-014"], ["area:control"]),
    ("WC-007", "phase-2", "図面読解と仕様書読解を接続する", ["ISS-015", "ISS-016", "ISS-017", "ISS-018"], ["area:drawings", "area:evidence"]),
    ("WC-008", "phase-2", "AI 中級と記録運用を継続する", ["ISS-019", "ISS-R01", "ISS-R02", "ISS-R04"], ["area:ai"]),
    ("WC-009", "phase-3", "PLC 基礎から課題5件まで到達する", ["ISS-020", "ISS-021", "ISS-022", "ISS-023", "ISS-024"], ["area:plc"]),
    ("WC-010", "phase-3", "図面読解を完成して PLC 読解へつなぐ", ["ISS-024", "ISS-026"], ["area:drawings", "area:plc"]),
    ("WC-011", "phase-3", "電験三種の deferred 管理を準備する", ["ISS-025", "ISS-R03"], ["area:license"]),
    ("WC-012", "phase-4", "電験三種の主科目を段階的に積み上げる", ["ISS-027", "ISS-028", "ISS-029", "ISS-030", "ISS-031"], ["area:license"]),
    ("WC-013", "phase-4", "PLC 応用と社内改善を成果物へつなぐ", ["ISS-032", "ISS-033"], ["area:plc", "area:evidence"]),
    ("WC-014", "phase-4", "受験期でもレビューと記録を維持する", ["ISS-R01", "ISS-R02", "ISS-R03", "ISS-R04"], ["area:evidence"]),
    ("WC-015", "phase-5", "AI と制御の成果物をポートフォリオへ統合する", ["ISS-034", "ISS-035", "ISS-036", "ISS-039"], ["area:ai"]),
    ("WC-016", "phase-5", "転職書類と面接ストーリーを整える", ["ISS-037", "ISS-038"], ["area:career"]),
    ("WC-017", "phase-5", "レビューと証跡の運用を維持する", ["ISS-R01", "ISS-R02", "ISS-R03", "ISS-R04"], ["area:evidence"]),
    ("WC-018", "phase-6", "応募導線を稼働させる", ["ISS-040"], ["area:career"]),
    ("WC-019", "phase-6", "面接通過率を上げる", ["ISS-041"], ["area:career"]),
    ("WC-020", "phase-6", "オファー獲得と計画完了記録を締める", ["ISS-042", "ISS-R02", "ISS-R03"], ["area:career"]),
]


def parse_date(text: str) -> dt.date:
    return dt.date.fromisoformat(text)


def quarter_id(date_str: str) -> str:
    parsed = parse_date(date_str)
    quarter = (parsed.month - 1) // 3 + 1
    return f"{parsed.year}-Q{quarter}"


def milestone_id(date_str: str) -> str:
    return f"M-{quarter_id(date_str)}"


def range_label(start: str, end: str) -> str:
    start_date = parse_date(start)
    end_date = parse_date(end)
    return f"[{start_date.strftime('%y/%m/%d')}-{end_date.strftime('%m/%d')}]"


def month_bucket(start: str, end: str) -> str:
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date.year == end_date.year and start_date.month == end_date.month:
        return start_date.strftime("%Y-%m")
    return f"{start_date.strftime('%Y-%m')}..{end_date.strftime('%Y-%m')}"


def phase_priority_guard(phase_id: str) -> bool:
    return phase_id in {"phase-0", "phase-1", "phase-4"}


def build_completion_check(item: dict) -> list[str]:
    checks = list(item.get("dod") or [])
    if item.get("deliverables"):
        checks.append("成果物が issue 本文またはコメントから辿れる")
    if item.get("evidence_to_keep"):
        checks.append("証跡が残り、次の面接・レビューで再利用できる")
    return checks[:4]


def build_issue_outcome(item: dict) -> str:
    if item["task_type"] == "review":
        return "レビュー後に主役・保留・次アクションが更新され、次の期間の迷いが減っている。"
    return f"{item['title']} を完了し、必要な成果物と証跡を残して次のタスクへ接続できる状態にする。"


def build_issue_next_action(item: dict) -> str:
    first_step = (item.get("work_steps") or ["最初の作業を1つ決める"])[0]
    return f"{first_step}ために、必要な資料と作業環境を開く。"


def build_why_this_matters(item: dict) -> str:
    links = [value for value in [item.get("career_link"), item.get("ai_link")] if value]
    if links:
        return " / ".join(links)
    return item.get("body") or item["title"]


def issue_title_lookup(seed: dict) -> dict[str, str]:
    titles: dict[str, str] = {}
    for issue in seed.get("issues", []):
        titles[issue["id"]] = issue["title"]
    return titles


def enrich_issue(issue: dict) -> None:
    profile = TASK_PROFILES[issue["task_type"]]
    issue["outcome"] = build_issue_outcome(issue)
    issue["next_action"] = build_issue_next_action(issue)
    issue["why_this_matters"] = build_why_this_matters(issue)
    issue["device"] = profile["device"]
    issue["inputs"] = list(profile["inputs"])
    issue["things_to_make"] = list(issue.get("deliverables") or [])
    issue["completion_check"] = build_completion_check(issue)
    issue["daily_execution"] = list(profile["daily_execution"])
    issue["time_block"] = profile["time_block"]
    issue["estimate"] = profile["estimate"]
    issue["energy"] = profile["energy"]
    issue["focus"] = profile["focus"]


def update_project_fields(seed: dict) -> None:
    legacy_names = {
        "Time Block",
        "Estimate",
        "Energy",
        "Focus",
        "Next Action",
        "Outcome",
        "Completion Check",
    }
    fields = [field for field in seed["project_fields"] if field["name"] not in legacy_names]
    seed["project_fields"] = fields
    field_by_name = {field["name"]: field for field in fields}
    field_by_name["Task Type"]["options"] = [
        "Epic",
        "Phase Card",
        "Win Condition",
        "Exam",
        "Study",
        "PLC",
        "Evidence",
        "AI Skill Building",
        "Career Prep",
        "Recurring Review",
        "Deliverable",
        "Setup",
    ]
    additional_fields = [
        {"name": "Start Date", "type": "date"},
        {"name": "End Date", "type": "date"},
        {"name": "Execution Time Block", "type": "text"},
        {"name": "Execution Estimate", "type": "text"},
        {"name": "Execution Energy", "type": "text"},
        {"name": "Execution Focus", "type": "text"},
        {"name": "Execution Next Action", "type": "text"},
        {"name": "Execution Outcome", "type": "text"},
        {"name": "Execution Check", "type": "text"},
    ]
    for field in additional_fields:
        if field["name"] not in field_by_name:
            fields.append(field)


def build_phase_cards(seed: dict) -> list[dict]:
    phase_to_wc_ids = {
        phase_id: [wc_id for wc_id, target_phase, *_rest in WIN_CONDITION_SPECS if target_phase == phase_id]
        for phase_id in PHASE_LABEL_BY_ID
    }
    phase_cards: list[dict] = []
    for phase in seed["phases"]:
        phase_id = phase["id"]
        phase_cards.append(
            {
                "id": f"PC-{phase_id}",
                "title": f"{range_label(phase['start'], phase['end'])} [PHASE] {phase['name']}",
                "body": f"{phase['name']} の運用カード。主役を固定し、勝ち条件を3つ以内で回す。",
                "epic": "",
                "phase": phase_id,
                "labels": [PHASE_LABEL_BY_ID[phase_id], f"priority:{phase['priority']}"],
                "priority": phase["priority"],
                "milestone": milestone_id(phase["end"]),
                "due_date": phase["end"],
                "recurring": False,
                "dependencies": [],
                "blocked_by": [],
                "linked_issue_ids": phase_to_wc_ids[phase_id],
                "evidence_type": "Document",
                "monthly_bucket": month_bucket(phase["start"], phase["end"]),
                "quarter": quarter_id(phase["end"]),
                "career_link": "主役と非主役を明確にし、転職価値につながる蓄積を崩さない",
                "ai_link": "AI は主役でない時期も再開コストを下げる補助線として扱う",
                "task_type": "phase_card",
                "outcome": f"{phase['name']} の主役と保留対象が明確になり、Phase の終点まで迷わず運用できる。",
                "next_action": "この Phase で主役にするカードを1つだけ確認し、勝ち条件を上から順に見直す。",
                "why_this_matters": "Project 1 と同じく、主役は常に1つだけに保ち、進捗は成果物で測る。",
                "device": "GitHub Projects / ノート",
                "inputs": list(phase.get("focus", [])),
                "things_to_make": ["phase運用メモ", "優先順位メモ"],
                "work_steps": [
                    f"主役を `{PHASE_MAINLINE[phase_id]}` に固定する",
                    "勝ち条件を3つ以内に絞って順番を決める",
                    "週次レビューで脱線を戻す",
                ],
                "deliverables": ["phase運用メモ", "レビュー更新"],
                "evidence_to_keep": ["週次レビュー記録", "priority 更新ログ"],
                "dod": [
                    "主役と保留対象が本文で明文化されている",
                    "勝ち条件が3つ以内に整理されている",
                ],
                "completion_check": [
                    "主役が1つに固定されている",
                    "勝ち条件3つ以内で回せている",
                    "保留対象が明文化されている",
                ],
                "daily_execution": [
                    "今週の主役カードだけを In Progress にする",
                    "保留対象に手を出したらレビューで戻す",
                    "週末に勝ち条件の進捗と証跡を更新する",
                ],
                "active_from": phase["start"],
                "deferred_until": None,
                "exam_priority_guard": phase_priority_guard(phase_id),
                "review_note": f"主役: {PHASE_MAINLINE[phase_id]} / 保留: {'、'.join(PHASE_DEFERRED_SCOPE[phase_id])}",
                "time_block": "週次レビュー 30-60分",
                "estimate": "Phase span",
                "energy": "Medium",
                "focus": PHASE_MAINLINE[phase_id],
            }
        )
    return phase_cards


def build_win_conditions(seed: dict) -> list[dict]:
    title_by_id = issue_title_lookup(seed)
    phase_by_id = {phase["id"]: phase for phase in seed["phases"]}
    win_conditions: list[dict] = []
    for win_id, phase_id, title, linked_ids, area_labels in WIN_CONDITION_SPECS:
        phase = phase_by_id[phase_id]
        linked_titles = [title_by_id.get(item_id, item_id) for item_id in linked_ids]
        win_conditions.append(
            {
                "id": win_id,
                "title": f"{range_label(phase['start'], phase['end'])} [WIN] {title}",
                "body": f"{phase['name']} で達成すべき中間成果。関連する具体作業を束ねる。",
                "epic": "",
                "phase": phase_id,
                "labels": area_labels + [PHASE_LABEL_BY_ID[phase_id], f"priority:{phase['priority']}"],
                "priority": phase["priority"],
                "milestone": milestone_id(phase["end"]),
                "due_date": phase["end"],
                "recurring": False,
                "dependencies": [],
                "blocked_by": [],
                "linked_issue_ids": linked_ids,
                "evidence_type": "Document",
                "monthly_bucket": month_bucket(phase["start"], phase["end"]),
                "quarter": quarter_id(phase["end"]),
                "career_link": "中間成果が見えることで、学習と転職価値の接続が説明しやすくなる",
                "ai_link": "必要な時だけ AI を補助線として使い、主役を崩さない",
                "task_type": "win_condition",
                "outcome": f"{title} が達成され、関連タスクの成果物と証跡で進捗を説明できる。",
                "next_action": f"関連カードのうち最初に着手する 1 件を選び、 `{linked_titles[0]}` を確認する。",
                "why_this_matters": "Phase の勝ち条件を満たすことで、ただ学ぶだけでなく成果として積み上がる。",
                "device": "GitHub Projects / ノート",
                "inputs": linked_titles,
                "things_to_make": ["中間成果メモ", "関連成果物へのリンク"],
                "work_steps": [
                    "関連カードの順番を決める",
                    "完了条件を満たす成果物を揃える",
                    "レビューで勝ち条件の達成度を確認する",
                ],
                "deliverables": ["勝ち条件の達成メモ"],
                "evidence_to_keep": ["関連 Issue のリンク", "達成度メモ"],
                "dod": [
                    "関連カードが完了または説明可能な状態になっている",
                    "証跡から達成度を説明できる",
                ],
                "completion_check": [
                    "関連カードの完了状況が確認できる",
                    "証跡が1か所に集約されている",
                    "次の勝ち条件へ移る準備ができている",
                ],
                "daily_execution": [
                    "今週着手する関連カードを1つだけ選ぶ",
                    "関連カードの証跡を更新する",
                    "週次レビューで未達理由を言語化する",
                ],
                "active_from": phase["start"],
                "deferred_until": None,
                "exam_priority_guard": phase_priority_guard(phase_id),
                "review_note": "関連タスクの進み具合と証跡の質で達成判定する",
                "time_block": "週次レビュー 30分 + 実作業",
                "estimate": "Phase sub-goal",
                "energy": "Medium",
                "focus": title,
            }
        )
    return win_conditions


def main() -> int:
    seed_path = pathlib.Path("data/project-seed.yaml")
    seed = yaml.safe_load(seed_path.read_text(encoding="utf-8"))

    seed["meta"]["owner"] = "foru1215"
    seed["meta"]["repo"] = "shared-auto-sync"

    update_project_fields(seed)
    for issue in seed["issues"]:
        enrich_issue(issue)
    seed["phase_cards"] = build_phase_cards(seed)
    seed["win_conditions"] = build_win_conditions(seed)

    rendered = yaml.safe_dump(seed, allow_unicode=True, sort_keys=False, width=120)
    seed_path.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
