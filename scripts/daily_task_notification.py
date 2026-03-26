from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import yaml

if __package__ in {None, ""}:
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from scripts import github_project_sync as sync


PRIORITY_ORDER = {"p0": 0, "p1": 1, "p2": 2, "p3": 3}


@dataclasses.dataclass
class NotificationItem:
    seed_id: str
    issue_number: int
    title: str
    reason: str
    next_action: str
    first_execution: str
    time_block: str | None


@dataclasses.dataclass
class DailyTaskPlan:
    focus: NotificationItem | None
    blocked: list[NotificationItem]
    deferred: list[NotificationItem]


def issue_state(issue: dict[str, Any]) -> str:
    return str(issue.get("state") or "").strip().lower()


def closed_issue_seed_ids(existing_issues: list[dict[str, Any]]) -> set[str]:
    closed_ids: set[str] = set()
    for issue in existing_issues:
        if issue_state(issue) != "closed":
            continue
        marker = sync.extract_marker(issue.get("body"))
        if marker and marker.get("seed_id"):
            closed_ids.add(str(marker["seed_id"]))
    return closed_ids


def parse_marker_issue_map(existing_issues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    issue_map: dict[str, dict[str, Any]] = {}
    for issue in existing_issues:
        marker = sync.extract_marker(issue.get("body"))
        if not marker or marker.get("entity_kind") not in {"issue", "phase_card", "win_condition"}:
            continue
        issue_map[str(marker["seed_id"])] = issue
    return issue_map


def first_execution(issue: dict[str, Any]) -> str:
    executions = sync.clean_text_list(list(issue.get("daily_execution", [])))
    return executions[0] if executions else normalize_text(issue.get("next_action")) or "最初の一手から始める"


def normalize_text(value: Any) -> str:
    return sync.normalize_text(value)


def status_reason(issue: dict[str, Any], *, today: dt.date, closed_issue_seed_ids: set[str]) -> tuple[str, str]:
    deferred_date = sync.parse_iso_date(issue.get("deferred_until"))
    if deferred_date and today <= deferred_date:
        return "延期", f"{issue['deferred_until']} まで保留"

    active_date = sync.parse_iso_date(issue.get("active_from"))
    if active_date and today < active_date:
        return "バックログ", f"{issue['active_from']} から着手"

    blocked_by = [seed_id for seed_id in issue.get("blocked_by", []) if seed_id not in closed_issue_seed_ids]
    if blocked_by:
        return "ブロック中", f"{blocked_by[0]} 完了待ち"

    if sync.is_exam_priority_period(today) and not sync.normalize_bool(issue.get("exam_priority_guard")):
        return "バックログ", "試験優先期間のため後回し"

    due_date = sync.parse_iso_date(issue.get("due_date"))
    if due_date and due_date <= today + dt.timedelta(days=sync.DATE_WINDOW_DAYS):
        return "未着手", "今日の主役候補"

    return "バックログ", "期限まで余裕があるため後回し"


def notification_item(issue: dict[str, Any], existing_issue: dict[str, Any], reason: str) -> NotificationItem:
    return NotificationItem(
        seed_id=issue["id"],
        issue_number=int(existing_issue["number"]),
        title=issue["title"],
        reason=reason,
        next_action=normalize_text(issue.get("next_action")),
        first_execution=first_execution(issue),
        time_block=normalize_text(issue.get("time_block")) or None,
    )


def concrete_seed_issues(seed: dict[str, Any]) -> list[dict[str, Any]]:
    return [issue for issue in seed.get("issues", [])]


def sort_key(issue: dict[str, Any]) -> tuple[int, dt.date, dt.date]:
    priority = PRIORITY_ORDER.get(str(issue.get("priority", "")).lower(), 9)
    due_date = sync.parse_iso_date(issue.get("due_date")) or dt.date.max
    active_from = sync.parse_iso_date(issue.get("active_from")) or dt.date.max
    return (priority, due_date, active_from)


def build_plan(seed: dict[str, Any], existing_issues: list[dict[str, Any]], *, today: dt.date) -> DailyTaskPlan:
    issue_map = parse_marker_issue_map(existing_issues)
    closed_ids = closed_issue_seed_ids(existing_issues)

    ready_candidates: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    blocked: list[NotificationItem] = []
    deferred: list[NotificationItem] = []

    for issue in concrete_seed_issues(seed):
        existing_issue = issue_map.get(issue["id"])
        if not existing_issue or issue_state(existing_issue) != "open":
            continue

        status, reason = status_reason(issue, today=today, closed_issue_seed_ids=closed_ids)
        if status == "未着手":
            ready_candidates.append((issue, existing_issue, reason))
        elif status == "ブロック中":
            blocked.append(notification_item(issue, existing_issue, reason))
        elif status in {"バックログ", "延期"}:
            deferred.append(notification_item(issue, existing_issue, reason))

    ready_candidates.sort(key=lambda item: sort_key(item[0]))
    focus = None
    if ready_candidates:
        selected_issue, selected_existing, reason = ready_candidates[0]
        focus = notification_item(selected_issue, selected_existing, reason)

    blocked.sort(key=lambda item: item.issue_number)
    deferred.sort(key=lambda item: item.issue_number)
    return DailyTaskPlan(focus=focus, blocked=blocked[:3], deferred=deferred[:3])


def render_issue_body(plan: DailyTaskPlan, *, today: dt.date, recipient: str) -> str:
    day_name = ["月", "火", "水", "木", "金", "土", "日"][today.weekday()]
    lines = [
        f"## ☀️ {today.year}/{today.month:02d}/{today.day:02d}（{day_name}）の主タスク",
        "",
        f"@{recipient} 今日の主タスク通知です。",
        "",
        "今日は **1件** に絞ります。",
        "",
    ]

    if plan.focus is None:
        lines.extend(["### 今日やること", "", "> 候補なし", ""])
    else:
        lines.extend(
            [
                "### 今日やること",
                "",
                f"### #{plan.focus.issue_number} {plan.focus.title}",
                "",
                f"> 最初の1セッション: {plan.focus.first_execution}",
                f"> 5分で始める: {plan.focus.next_action}",
            ]
        )
        if plan.focus.time_block:
            lines.append(f"> 時間の目安: {plan.focus.time_block}")
        lines.append("")

    if plan.blocked:
        lines.extend(["### まだ着手しない（依存待ち）", ""])
        for item in plan.blocked:
            lines.append(f"- #{item.issue_number} {item.title} ({item.reason})")
        lines.append("")

    if plan.deferred:
        lines.extend(["### 今は後回し", ""])
        for item in plan.deferred:
            lines.append(f"- #{item.issue_number} {item.title} ({item.reason})")
        lines.append("")

    lines.extend(
        [
            "---",
            "💡 主役以外は進めない前提で、完了か詰まりだけを記録してください。",
            "",
        ]
    )
    return "\n".join(lines)


def issue_title(today: dt.date) -> str:
    day_name = ["月", "火", "水", "木", "金", "土", "日"][today.weekday()]
    return f"[今日の主タスク] {today.year}/{today.month:02d}/{today.day:02d}（{day_name}）"


def fetch_existing_issues(repo: str, *, limit: int = 500) -> list[dict[str, Any]]:
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            str(limit),
            "--json",
            "number,title,body,state,labels",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def build_payload(seed_path: pathlib.Path, *, repo: str, today: dt.date, recipient: str) -> dict[str, str]:
    seed = yaml.safe_load(seed_path.read_text(encoding="utf-8"))
    plan = build_plan(seed, fetch_existing_issues(repo), today=today)
    return {
        "title": issue_title(today),
        "body": render_issue_body(plan, today=today, recipient=recipient),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the daily focus task issue body.")
    parser.add_argument("--repo", required=True, help="GitHub repository in owner/name form.")
    parser.add_argument("--recipient", required=True, help="GitHub username to mention and assign.")
    parser.add_argument("--seed-path", default="data/project-seed.yaml")
    parser.add_argument("--today", help="Override the date used for planning (YYYY-MM-DD).")
    parser.add_argument("--title-path", required=True)
    parser.add_argument("--body-path", required=True)
    args = parser.parse_args()

    today = sync.parse_iso_date(args.today) if args.today else sync.iso_today()
    payload = build_payload(pathlib.Path(args.seed_path), repo=args.repo, today=today, recipient=args.recipient)
    pathlib.Path(args.title_path).write_text(payload["title"], encoding="utf-8")
    pathlib.Path(args.body_path).write_text(payload["body"], encoding="utf-8")


if __name__ == "__main__":
    main()
