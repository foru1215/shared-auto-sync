from __future__ import annotations

import pathlib
from typing import Any

import yaml


TASK_PROFILES: dict[str, dict[str, Any]] = {
    "study": {
        "device": "ノート / PC",
        "time_block": "週末 60-90分",
        "estimate": "2-3 sessions",
        "energy": "Medium",
        "focus": "理解・整理・ノート化",
        "inputs": ["公式ドキュメント", "ノート", "比較メモ"],
        "daily_execution": [
            "セッション1: 読む範囲と観点を決める",
            "セッション2: 重要点を抜き出して整理する",
            "セッション3: 実務や面接に接続する要点を書く",
        ],
    },
    "evidence": {
        "device": "PC / ノート",
        "time_block": "週末 60-90分",
        "estimate": "2 sessions",
        "energy": "Medium",
        "focus": "整理・言語化・証跡化",
        "inputs": ["既存ノート", "仕様書メモ", "改善観点"],
        "daily_execution": [
            "セッション1: 既存の PLC / 図面 / 制御メモから観点を拾う",
            "セッション2: 面接や実務で使える形のチェックリストへまとめる",
        ],
    },
    "deliverable": {
        "device": "PC",
        "time_block": "週末 120-180分",
        "estimate": "3-4 sessions",
        "energy": "High",
        "focus": "統合・説明可能化・公開準備",
        "inputs": ["既存成果物", "ポートフォリオ原稿", "説明観点"],
        "daily_execution": [
            "セッション1: 元の成果物と説明観点を並べる",
            "セッション2: OT セキュリティ視点を補足して統合する",
            "セッション3: 面接で話せる要点を 3 つ以上残す",
        ],
    },
}


def completion_check(item: dict[str, Any]) -> list[str]:
    checks = list(item["dod"])
    checks.append("成果物が issue 本文またはコメントから辿れる")
    checks.append("証跡が残り、次の面接・レビューで再利用できる")
    return checks[:4]


def why_this_matters(item: dict[str, Any]) -> str:
    links = [value for value in [item.get("career_link"), item.get("ai_link")] if value]
    return " / ".join(links) if links else item["body"]


def enrich_issue(item: dict[str, Any]) -> dict[str, Any]:
    profile = TASK_PROFILES[item["task_type"]]
    first_step = item["work_steps"][0]
    item["outcome"] = (
        f"{item['title']} を完了し、必要な成果物と証跡を残して次のタスクへ接続できる状態にする。"
    )
    item["next_action"] = f"{first_step}ために、必要な資料と作業環境を開く。"
    item["why_this_matters"] = why_this_matters(item)
    item["device"] = profile["device"]
    item["inputs"] = list(profile["inputs"])
    item["things_to_make"] = list(item["deliverables"])
    item["completion_check"] = completion_check(item)
    item["daily_execution"] = list(profile["daily_execution"])
    item["time_block"] = profile["time_block"]
    item["estimate"] = profile["estimate"]
    item["energy"] = profile["energy"]
    item["focus"] = profile["focus"]
    return item


def update_win_condition(
    item: dict[str, Any],
    *,
    title: str,
    labels: list[str],
    linked_issue_ids: list[str],
    inputs: list[str],
    focus: str,
    next_action: str,
) -> None:
    item["title"] = title
    item["labels"] = labels
    item["linked_issue_ids"] = linked_issue_ids
    item["inputs"] = inputs
    item["focus"] = focus
    item["outcome"] = f"{title.split('[WIN] ', 1)[1]} が達成され、関連タスクの成果物と証跡で進捗を説明できる。"
    item["next_action"] = next_action
    item["review_note"] = "関連タスクの進み具合と証跡の質で達成判定する。security は side track として無理なく接続する。"


def ensure_area_label(seed: dict[str, Any]) -> None:
    area_labels = seed["labels"]["area"]
    if not any(item["name"] == "area:security" for item in area_labels):
        area_labels.append(
            {
                "name": "area:security",
                "color": "0052cc",
                "description": "OT / ICS セキュリティ",
            }
        )


def ensure_area_field(seed: dict[str, Any]) -> None:
    area_field = next(field for field in seed["project_fields"] if field["name"] == "Area")
    if "Security" not in area_field["options"]:
        area_field["options"].append("Security")


def ensure_security_epic(seed: dict[str, Any]) -> None:
    if any(item["id"] == "E-SEC" for item in seed["epics"]):
        return
    new_epic = {
        "id": "E-SEC",
        "name": "OT / ICS Security",
        "description": "OT / ICS セキュリティを最小トラックで学び、制御・PLC・AI の成果物へ接続する",
        "labels": ["area:security"],
        "priority": "p2",
    }
    insert_at = next(
        (index for index, item in enumerate(seed["epics"]) if item["id"] == "E-CAR"),
        len(seed["epics"]),
    )
    seed["epics"].insert(insert_at, new_epic)


def security_issues() -> list[dict[str, Any]]:
    return [
        enrich_issue(
            {
                "id": "ISS-043",
                "title": "[E-SEC] 2026-08: NIST SP 800-82 で OT / ICS セキュリティの全体像を掴む",
                "body": "NIST SP 800-82 Rev.3 の要点を読み、IT と OT の違い・安全性・可用性・制御システム固有の観点を1枚にまとめる。",
                "epic": "E-SEC",
                "phase": "phase-2",
                "labels": ["area:security", "area:control", "phase:control-foundation", "priority:p2"],
                "priority": "p2",
                "milestone": "M-2026-Q3",
                "due_date": "2026-08-31",
                "recurring": False,
                "dependencies": [],
                "evidence_type": "Document",
                "monthly_bucket": "2026-08",
                "quarter": "2026-Q3",
                "career_link": "制御理解にセキュリティ観点を重ねて語れる基礎を作る",
                "ai_link": "",
                "task_type": "study",
                "work_steps": [
                    "NIST SP 800-82 Rev.3 の読む章を決める。",
                    "IT と OT の違い、安全性・可用性・制御系固有の注意点を抜き出す。",
                    "面接やレビューで使える1ページの要点メモにまとめる。",
                ],
                "deliverables": ["OT / ICS セキュリティ要点メモ"],
                "evidence_to_keep": [
                    "読んだ章と日付の記録",
                    "1ページ要点メモの保存先リンク",
                ],
                "dod": [
                    "OT と IT の違いを自分の言葉で説明できる。",
                    "安全性・可用性・制御系の観点を含む要点メモが残っている。",
                ],
                "active_from": "2026-07-05",
                "deferred_until": None,
                "blocked_by": [],
                "exam_priority_guard": False,
                "review_note": "レビュー時に、制御基礎学習とどう接続したか、今後の実務で使えそうな視点を更新する。",
            }
        ),
        enrich_issue(
            {
                "id": "ISS-044",
                "title": "[E-SEC] 2026-09: CISA ICS 101 ベースで IT / OT 差分と基本対策を整理する",
                "body": "CISA ICS 101 相当の内容を基に、ICS アーキテクチャ、IT / OT 差分、代表的リスクと基本対策を整理する。",
                "epic": "E-SEC",
                "phase": "phase-2",
                "labels": ["area:security", "area:control", "phase:control-foundation", "priority:p2"],
                "priority": "p2",
                "milestone": "M-2026-Q3",
                "due_date": "2026-09-30",
                "recurring": False,
                "dependencies": ["ISS-043"],
                "evidence_type": "Document",
                "monthly_bucket": "2026-09",
                "quarter": "2026-Q3",
                "career_link": "設備・制御の運用リスクをセキュリティ視点で説明できるようにする",
                "ai_link": "",
                "task_type": "study",
                "work_steps": [
                    "CISA ICS 101 の学習範囲を決める。",
                    "ICS アーキテクチャ、IT / OT 差分、基本対策を表形式で整理する。",
                    "現職の設備理解とつながる観点を3つ書き出す。",
                ],
                "deliverables": ["ICS 101 学習メモ", "IT / OT 差分表"],
                "evidence_to_keep": [
                    "学習ログ",
                    "差分表またはメモの保存先リンク",
                ],
                "dod": [
                    "ICS アーキテクチャと IT / OT 差分を説明できる。",
                    "代表的リスクと基本対策が表や箇条書きで残っている。",
                ],
                "active_from": "2026-07-05",
                "deferred_until": None,
                "blocked_by": ["ISS-043"],
                "exam_priority_guard": False,
                "review_note": "レビュー時に、制御基礎ノートや図面読解に取り込めるポイントを追記する。",
            }
        ),
        enrich_issue(
            {
                "id": "ISS-045",
                "title": "[E-SEC] 2026-12: PLC / 制御盤向け セキュリティ観点チェックリストを作る",
                "body": "PLC・制御盤・図面読解の学習内容をもとに、OT / ICS セキュリティ観点のチェックリストを作成する。",
                "epic": "E-SEC",
                "phase": "phase-3",
                "labels": ["area:security", "area:plc", "area:drawings", "phase:plc-growth", "priority:p2"],
                "priority": "p2",
                "milestone": "M-2026-Q4",
                "due_date": "2026-12-31",
                "recurring": False,
                "dependencies": ["ISS-044", "ISS-020"],
                "evidence_type": "Document",
                "monthly_bucket": "2026-12",
                "quarter": "2026-Q4",
                "career_link": "PLC と制御盤を安全性・可用性の観点でも見られる証拠にする",
                "ai_link": "",
                "task_type": "evidence",
                "work_steps": [
                    "既存の PLC / 図面 / 制御メモから重要観点を洗い出す。",
                    "ネットワーク分離、変更管理、アカウント、ログ、保守時の注意点を整理する。",
                    "A4 1-2枚のチェックリストとして保存する。",
                ],
                "deliverables": ["PLC / 制御盤セキュリティ観点チェックリスト"],
                "evidence_to_keep": [
                    "チェックリスト本体",
                    "元にした学習ノートや仕様書メモへのリンク",
                ],
                "dod": [
                    "PLC / 制御盤向けの観点がチェックリストとして残っている。",
                    "既存の制御・図面学習との接続が本文かコメントに明記されている。",
                ],
                "active_from": "2026-11-01",
                "deferred_until": None,
                "blocked_by": ["ISS-044", "ISS-020"],
                "exam_priority_guard": False,
                "review_note": "レビュー時に、面接で語れるポイントと現職で使えそうな観点を分けて追記する。",
            }
        ),
        enrich_issue(
            {
                "id": "ISS-046",
                "title": "[E-SEC] 2027-11: 制御 × AI 成果物に OT セキュリティ視点を加える",
                "body": "制御 × AI の成果物に対し、OT / ICS セキュリティ観点の補足メモを作成し、ポートフォリオ説明へ統合する。",
                "epic": "E-SEC",
                "phase": "phase-5",
                "labels": ["area:security", "area:ai", "area:control", "phase:ai-specialist", "priority:p2"],
                "priority": "p2",
                "milestone": "M-2027-Q4",
                "due_date": "2027-11-30",
                "recurring": False,
                "dependencies": ["ISS-035"],
                "evidence_type": "Portfolio",
                "monthly_bucket": "2027-11",
                "quarter": "2027-Q4",
                "career_link": "制御 × AI に加えて OT セキュリティ視点も持つ人材として語れる",
                "ai_link": "制御 × AI 成果物に安全性・可用性・運用リスク視点を追加する",
                "task_type": "deliverable",
                "work_steps": [
                    "既存の制御 × AI 成果物を1件選ぶ。",
                    "安全性、可用性、誤操作、権限、変更管理の観点で補足を書く。",
                    "ポートフォリオの説明文へ統合する。",
                ],
                "deliverables": ["OT セキュリティ補足メモ", "ポートフォリオ説明更新"],
                "evidence_to_keep": [
                    "更新したポートフォリオリンク",
                    "セキュリティ観点メモ",
                ],
                "dod": [
                    "制御 × AI 成果物に OT セキュリティ視点が追加されている。",
                    "面接で説明できる要点が3つ以上残っている。",
                ],
                "active_from": "2027-10-01",
                "deferred_until": "2027-09-30",
                "blocked_by": ["ISS-035"],
                "exam_priority_guard": False,
                "review_note": "レビュー時に、差別化ポイントと面接での話し方を更新する。",
            }
        ),
    ]


def upsert_security_issues(seed: dict[str, Any]) -> None:
    issues_by_id = {item["id"]: item for item in seed["issues"]}
    for issue in security_issues():
        issues_by_id[issue["id"]] = issue
    regular = []
    recurring = []
    for issue_id, issue in issues_by_id.items():
        if issue_id.startswith("ISS-R"):
            recurring.append(issue)
        else:
            regular.append(issue)
    regular.sort(key=lambda item: int(item["id"].split("-")[1]))
    recurring.sort(key=lambda item: item["id"])
    seed["issues"] = regular + recurring


def update_win_conditions(seed: dict[str, Any]) -> None:
    issue_title_by_id = {item["id"]: item["title"] for item in seed["issues"]}
    win_conditions = {item["id"]: item for item in seed["win_conditions"]}

    update_win_condition(
        win_conditions["WC-007"],
        title="[26/07/05-10/31] [WIN] 図面・仕様書・OT セキュリティの読解を接続する",
        labels=["area:security", "area:drawings", "area:evidence", "phase:control-foundation", "priority:p1"],
        linked_issue_ids=["ISS-015", "ISS-016", "ISS-017", "ISS-018", "ISS-043", "ISS-044"],
        inputs=[
            issue_title_by_id["ISS-015"],
            issue_title_by_id["ISS-016"],
            issue_title_by_id["ISS-017"],
            issue_title_by_id["ISS-018"],
            issue_title_by_id["ISS-043"],
            issue_title_by_id["ISS-044"],
        ],
        focus="図面・仕様書・OT セキュリティの読解を接続する",
        next_action=f"関連カードのうち最初に着手する 1 件を選び、 `{issue_title_by_id['ISS-043']}` を確認する。",
    )

    update_win_condition(
        win_conditions["WC-010"],
        title="[26/11/01-03/31] [WIN] 図面読解を完成し PLC とセキュリティ観点へつなぐ",
        labels=["area:security", "area:drawings", "area:plc", "phase:plc-growth", "priority:p1"],
        linked_issue_ids=["ISS-024", "ISS-026", "ISS-045"],
        inputs=[
            issue_title_by_id["ISS-024"],
            issue_title_by_id["ISS-026"],
            issue_title_by_id["ISS-045"],
        ],
        focus="図面読解を完成し PLC とセキュリティ観点へつなぐ",
        next_action=f"関連カードのうち最初に着手する 1 件を選び、 `{issue_title_by_id['ISS-045']}` を確認する。",
    )

    update_win_condition(
        win_conditions["WC-015"],
        title="[27/10/01-01/31] [WIN] AI・制御・OT セキュリティの成果物を統合する",
        labels=["area:security", "area:ai", "phase:ai-specialist", "priority:p1"],
        linked_issue_ids=["ISS-034", "ISS-035", "ISS-036", "ISS-039", "ISS-046"],
        inputs=[
            issue_title_by_id["ISS-034"],
            issue_title_by_id["ISS-035"],
            issue_title_by_id["ISS-036"],
            issue_title_by_id["ISS-039"],
            issue_title_by_id["ISS-046"],
        ],
        focus="AI・制御・OT セキュリティの成果物を統合する",
        next_action=f"関連カードのうち最初に着手する 1 件を選び、 `{issue_title_by_id['ISS-046']}` を確認する。",
    )


def main() -> int:
    path = pathlib.Path("data/project-seed.yaml")
    seed = yaml.safe_load(path.read_text(encoding="utf-8"))
    ensure_area_label(seed)
    ensure_area_field(seed)
    ensure_security_epic(seed)
    upsert_security_issues(seed)
    update_win_conditions(seed)
    path.write_text(yaml.safe_dump(seed, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
