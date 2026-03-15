from __future__ import annotations

import argparse
import copy
import dataclasses
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from typing import Any

import yaml


MARKER_PREFIX = "github-project-sync"
REPORT_VERSION = 2
DATE_WINDOW_DAYS = 45

TASK_TYPE_TO_FIELD = {
    "epic": "Epic",
    "phase_card": "Phase Card",
    "win_condition": "Win Condition",
    "exam": "Exam",
    "study": "Study",
    "plc": "PLC",
    "evidence": "Evidence",
    "ai": "AI Skill Building",
    "career": "Career Prep",
    "review": "Recurring Review",
    "deliverable": "Deliverable",
    "setup": "Setup",
}

REVIEW_CYCLE_TO_FIELD = {
    "weekly": "Weekly",
    "monthly": "Monthly",
    "quarterly": "Quarterly",
}

AUDIT_SEVERITY_ORDER = {"FAIL": 0, "WARN": 1, "INFO": 2}


class SyncCommandError(RuntimeError):
    pass


@dataclasses.dataclass
class RepoTarget:
    owner: str
    repo: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclasses.dataclass
class LabelSpec:
    name: str
    color: str
    description: str


@dataclasses.dataclass
class MilestoneSpec:
    seed_id: str
    title: str
    start: str
    end: str
    goal: str

    def due_on(self) -> str:
        return f"{self.end}T00:00:00Z"

    def description(self) -> str:
        return f"Period: {self.start} to {self.end}\nGoal: {self.goal}".strip()


@dataclasses.dataclass
class ProjectFieldSpec:
    name: str
    data_type: str
    options: list[str]
    is_builtin: bool = False


@dataclasses.dataclass
class ProjectFieldRef:
    id: str
    name: str
    field_type: str
    options: dict[str, str]


@dataclasses.dataclass
class PlannedIssue:
    seed_id: str
    entity_kind: str
    title: str
    body: str
    labels: list[str]
    milestone_title: str | None
    field_values: dict[str, Any]
    fingerprint: str


@dataclasses.dataclass
class SyncOperation:
    category: str
    action: str
    target: str
    details: dict[str, Any]


@dataclasses.dataclass
class SyncContext:
    dry_run: bool
    repo: RepoTarget
    project_owner: str
    project_title: str
    today: dt.date
    seed_path: pathlib.Path
    report_dir: pathlib.Path
    operations: list[SyncOperation] = dataclasses.field(default_factory=list)
    warnings: list[str] = dataclasses.field(default_factory=list)
    errors: list[str] = dataclasses.field(default_factory=list)

    def record(self, category: str, action: str, target: str, **details: Any) -> None:
        self.operations.append(
            SyncOperation(category=category, action=action, target=target, details=details)
        )

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)


@dataclasses.dataclass
class AuditFinding:
    severity: str
    code: str
    target: str
    message: str


def run_command(
    args: list[str],
    *,
    input_obj: dict[str, Any] | list[Any] | None = None,
    cwd: pathlib.Path | None = None,
    check: bool = True,
) -> str:
    input_path: pathlib.Path | None = None
    try:
        command = list(args)
        if input_obj is not None:
            handle = tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            )
            input_path = pathlib.Path(handle.name)
            json.dump(input_obj, handle, ensure_ascii=False)
            handle.close()
            command.extend(["--input", str(input_path)])

        result = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if check and result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            raise SyncCommandError(f"{' '.join(command)} failed: {stderr}")
        return result.stdout.strip()
    finally:
        if input_path and input_path.exists():
            input_path.unlink()


def run_json(
    args: list[str],
    *,
    input_obj: dict[str, Any] | list[Any] | None = None,
    cwd: pathlib.Path | None = None,
) -> Any:
    output = run_command(args, input_obj=input_obj, cwd=cwd)
    if not output:
        return None
    return json.loads(output)


def gh_api_json(
    endpoint: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | list[Any] | None = None,
    cwd: pathlib.Path | None = None,
) -> Any:
    return run_json(["gh", "api", "--method", method, endpoint], input_obj=body, cwd=cwd)


def gh_graphql(query: str, variables: dict[str, Any], *, cwd: pathlib.Path | None = None) -> Any:
    payload = {"query": query, "variables": variables}
    return run_json(["gh", "api", "graphql", "--method", "POST"], input_obj=payload, cwd=cwd)


def gh_project_json(args: list[str], *, cwd: pathlib.Path | None = None) -> Any:
    return run_json(["gh", "project", *args], cwd=cwd)


def git_remote_url(cwd: pathlib.Path) -> str | None:
    try:
        output = run_command(["git", "remote", "get-url", "origin"], cwd=cwd)
    except SyncCommandError:
        return None
    return output.strip() or None


def parse_github_repo(remote_url: str | None) -> RepoTarget | None:
    if not remote_url:
        return None
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$", remote_url)
    if not match:
        return None
    return RepoTarget(owner=match.group("owner"), repo=match.group("repo"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_text(value: str | None) -> str:
    return (value or "").replace("\r\n", "\n").strip()


def normalize_label_name(value: str) -> str:
    return value.strip()


def marker_payload(seed_id: str, entity_kind: str, fingerprint: str) -> dict[str, str]:
    return {
        "seed_id": seed_id,
        "entity_kind": entity_kind,
        "fingerprint": fingerprint,
        "source": "data/project-seed.yaml",
    }


def marker_comment(payload: dict[str, str]) -> str:
    return f"<!-- {MARKER_PREFIX}: {json.dumps(payload, ensure_ascii=False, sort_keys=True)} -->"


def extract_marker(body: str | None) -> dict[str, Any] | None:
    if not body:
        return None
    match = re.search(
        rf"<!--\s*{re.escape(MARKER_PREFIX)}:\s*(\{{.*?\}})\s*-->",
        body,
        flags=re.DOTALL,
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def iso_today() -> dt.date:
    return dt.date.today()


def parse_iso_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    return dt.date.fromisoformat(value)


def is_valid_iso_date(value: str | None) -> bool:
    if value in (None, ""):
        return True
    try:
        parse_iso_date(value)
    except ValueError:
        return False
    return True


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def active_window_text(issue: dict[str, Any]) -> str | None:
    active_from = issue.get("active_from")
    due_date = issue.get("due_date")
    if active_from and due_date:
        return f"{active_from} -> {due_date}"
    if active_from:
        return f"From {active_from}"
    return None


def markdown_checklist(items: list[str]) -> str:
    if not items:
        return "- [ ] None"
    return "\n".join(f"- [ ] {item}" for item in items)


def markdown_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def completion_check_text(items: list[str]) -> str | None:
    cleaned = [normalize_text(item) for item in items if normalize_text(item)]
    return " / ".join(cleaned) or None


def entity_collections(seed: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    return [
        ("phase_card", list(seed.get("phase_cards", []))),
        ("win_condition", list(seed.get("win_conditions", []))),
        ("issue", list(seed.get("issues", []))),
    ]


def iter_seed_work_items(seed: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    items: list[tuple[str, dict[str, Any]]] = []
    for entity_kind, collection in entity_collections(seed):
        for item in collection:
            items.append((entity_kind, item))
    return items


def render_epic_body(
    base_body: str,
    metadata_lines: list[str],
    marker: dict[str, str],
) -> str:
    parts = [normalize_text(base_body)]
    if metadata_lines:
        parts.append("\n".join(["## Sync Metadata", *metadata_lines]))
    parts.append(marker_comment(marker))
    return "\n\n".join(part for part in parts if part).strip() + "\n"


def render_issue_body(
    issue: dict[str, Any],
    *,
    marker: dict[str, str],
    phase_name: str | None,
    blocked_titles: list[str],
    linked_titles: list[str],
) -> str:
    summary = normalize_text(issue.get("body")) or "No summary."
    outcome = normalize_text(issue.get("outcome")) or "No outcome defined."
    next_action = normalize_text(issue.get("next_action")) or "No next action defined."
    why_lines = []
    if issue.get("why_this_matters"):
        why_lines.append(f"- {issue['why_this_matters']}")
    if phase_name:
        why_lines.append(f"- Phase: {phase_name}")
    if issue.get("career_link"):
        why_lines.append(f"- Career: {issue['career_link']}")
    if issue.get("ai_link"):
        why_lines.append(f"- AI: {issue['ai_link']}")
    if not why_lines:
        why_lines.append("- No linked context.")

    dependency_lines = blocked_titles or ["None"]
    timing_lines = [
        f"- Start date: {issue.get('active_from') or 'None'}",
        f"- End date: {issue.get('due_date') or 'None'}",
        f"- Active from: {issue.get('active_from') or 'None'}",
        f"- Deferred until: {issue.get('deferred_until') or 'None'}",
        f"- Phase: {phase_name or 'None'}",
        f"- Monthly bucket: {issue.get('monthly_bucket') or 'None'}",
        f"- Quarter: {issue.get('quarter') or 'None'}",
        f"- Time block: {issue.get('time_block') or 'None'}",
        f"- Estimate: {issue.get('estimate') or 'None'}",
        f"- Energy: {issue.get('energy') or 'None'}",
        f"- Focus: {issue.get('focus') or 'None'}",
    ]
    parts = [
        "## Summary",
        "",
        summary,
        "",
        "---",
        "",
        "## Outcome",
        "",
        outcome,
        "",
        "---",
        "",
        "## Next Action",
        "",
        f"- [ ] {next_action}",
        "",
        "---",
        "",
        "## Why this matters",
        "",
        "\n".join(why_lines),
        "",
        "---",
        "",
        "## Device",
        "",
        normalize_text(issue.get("device")) or "None",
        "",
        "---",
        "",
        "## Inputs",
        "",
        markdown_list(list(issue.get("inputs", []))),
        "",
        "---",
        "",
        "## Things to make",
        "",
        markdown_list(list(issue.get("things_to_make", []))),
        "",
        "---",
        "",
        "## Work checklist",
        "",
        markdown_checklist(list(issue.get("work_steps", []))),
        "",
        "---",
        "",
        "## Deliverables",
        "",
        markdown_list(list(issue.get("deliverables", []))),
        "",
        "---",
        "",
        "## Evidence to keep",
        "",
        f"Evidence type: **{issue.get('evidence_type') or 'None'}**",
        "",
        markdown_list(list(issue.get("evidence_to_keep", []))),
        "",
        "---",
        "",
        "## Definition of Done",
        "",
        markdown_checklist(list(issue.get("dod", []))),
        "",
        "---",
        "",
        "## Completion check",
        "",
        markdown_checklist(list(issue.get("completion_check", []))),
        "",
        "---",
        "",
        "## Evidence to keep",
        "",
        f"Evidence type: **{issue.get('evidence_type') or 'None'}**",
        "",
        markdown_list(list(issue.get("evidence_to_keep", []))),
        "",
        "---",
        "",
        "## Blockers / dependencies",
        "",
        markdown_list(dependency_lines),
        "",
        "---",
        "",
        "## Linked work items",
        "",
        markdown_list(linked_titles),
        "",
        "---",
        "",
        "## Daily execution",
        "",
        markdown_list(list(issue.get("daily_execution", []))),
        "",
        "---",
        "",
        "## Timing",
        "",
        "\n".join(timing_lines),
        "",
        "---",
        "",
        "## Review note",
        "",
        issue.get("review_note") or "None.",
        "",
        "---",
        "",
        marker_comment(marker),
    ]
    return "\n".join(parts).strip() + "\n"


def option_color(field_name: str, option_name: str, index: int) -> str:
    status_map = {
        "Backlog": "GRAY",
        "Todo": "BLUE",
        "In Progress": "YELLOW",
        "Done": "GREEN",
        "Blocked": "RED",
        "Deferred": "ORANGE",
    }
    priority_map = {"P0": "RED", "P1": "ORANGE", "P2": "GREEN"}
    task_type_map = {
        "Epic": "PURPLE",
        "Phase Card": "BLUE",
        "Win Condition": "GREEN",
        "Exam": "RED",
        "Study": "BLUE",
        "PLC": "YELLOW",
        "Evidence": "ORANGE",
        "AI Skill Building": "PURPLE",
        "Career Prep": "GREEN",
        "Recurring Review": "PINK",
        "Deliverable": "PINK",
        "Setup": "GRAY",
    }
    review_map = {"Weekly": "BLUE", "Monthly": "GREEN", "Quarterly": "ORANGE", "None": "GRAY"}
    ready_map = {"Ready": "GREEN", "Missing": "RED", "N/A": "GRAY"}
    deferred_flag_map = {"Active": "BLUE", "Deferred": "ORANGE", "N/A": "GRAY"}
    exam_guard_map = {"Exam Priority": "RED", "Normal": "GRAY", "N/A": "GRAY"}
    lookup = {}
    if field_name == "Status":
        lookup = status_map
    elif field_name == "Priority":
        lookup = priority_map
    elif field_name == "Task Type":
        lookup = task_type_map
    elif field_name == "Review Cycle":
        lookup = review_map
    elif field_name in {"DoD Ready", "Evidence Ready"}:
        lookup = ready_map
    elif field_name == "Deferred Flag":
        lookup = deferred_flag_map
    elif field_name == "Exam Priority Guard":
        lookup = exam_guard_map
    if option_name in lookup:
        return lookup[option_name]
    cycle = ["GRAY", "BLUE", "GREEN", "YELLOW", "ORANGE", "RED", "PINK", "PURPLE"]
    return cycle[index % len(cycle)]


def build_project_readme(seed: dict[str, Any]) -> str:
    lines = [
        "# Career Transition 24-Month Plan",
        "",
        f"- Source of truth: `{pathlib.Path('data/project-seed.yaml').as_posix()}`",
        f"- Period: {seed['meta']['start_date']} to {seed['meta']['end_date']}",
        "- Sync policy: labels, milestones, issues, project items, and custom fields are managed from seed data.",
        "- Exam priority: written exam first until 2026-04-27, then practical exam until 2026-07-04.",
        "",
        "## Phases",
    ]
    for phase in seed.get("phases", []):
        lines.append(f"- {phase['name']}: {phase['start']} to {phase['end']}")
    lines.extend(
        [
            "",
            "## Review Rules",
            "- Weekly review: 30 minutes",
            "- Monthly review: end-of-month summary and plan adjustment",
            "- Quarterly review: milestone audit and next-quarter alignment",
            "",
            "## Notes",
            "- This project is synced by `scripts/github_project_sync.py`.",
            "- Managed issues include a machine-readable marker for idempotent re-sync.",
        ]
    )
    return "\n".join(lines).strip()


def seed_field_specs(seed: dict[str, Any]) -> list[ProjectFieldSpec]:
    return [
        ProjectFieldSpec(
            name=field["name"],
            data_type=str(field["type"]).lower(),
            options=list(field.get("options", [])),
            is_builtin=field["name"] == "Status",
        )
        for field in seed.get("project_fields", [])
    ]


def label_specs_from_seed(seed: dict[str, Any]) -> list[LabelSpec]:
    labels: list[LabelSpec] = []
    for group_entries in seed.get("labels", {}).values():
        for item in group_entries:
            labels.append(
                LabelSpec(
                    name=normalize_label_name(item["name"]),
                    color=str(item["color"]).lower(),
                    description=str(item.get("description", "")),
                )
            )
    return labels


def milestone_specs_from_seed(seed: dict[str, Any]) -> list[MilestoneSpec]:
    return [
        MilestoneSpec(
            seed_id=item["id"],
            title=item["title"],
            start=item["start"],
            end=item["end"],
            goal=item.get("goal", ""),
        )
        for item in seed.get("milestones", [])
    ]


def area_from_labels(labels: list[str]) -> str | None:
    mapping = {
        "area:license": "License",
        "area:control": "Control",
        "area:plc": "PLC",
        "area:drawings": "Drawings",
        "area:practice": "Practice",
        "area:evidence": "Evidence",
        "area:security": "Security",
        "area:ai": "AI",
        "area:career": "Career",
    }
    for label in labels:
        if label in mapping:
            return mapping[label]
    return None


def phase_from_labels(labels: list[str]) -> str | None:
    mapping = {
        "phase:written-exam": "Written Exam",
        "phase:practical-exam": "Practical Exam",
        "phase:control-foundation": "Control Foundation",
        "phase:plc-growth": "PLC Growth",
        "phase:denken-ramp": "Denken Ramp",
        "phase:ai-specialist": "AI Specialist",
        "phase:career-finish": "Career Finish",
    }
    for label in labels:
        if label in mapping:
            return mapping[label]
    return None


def priority_to_field(priority: str | None) -> str | None:
    if not priority:
        return None
    return priority.upper()


def task_type_to_field(task_type: str | None) -> str | None:
    if not task_type:
        return None
    return TASK_TYPE_TO_FIELD.get(task_type, task_type)


def infer_task_type(issue: dict[str, Any], *, entity_kind: str) -> str:
    if entity_kind == "epic":
        return "Epic"
    return task_type_to_field(str(issue.get("task_type", "")).lower()) or "Study"


def infer_review_cycle(issue: dict[str, Any]) -> str | None:
    recurring = issue.get("recurring")
    if not recurring:
        return "None"
    return REVIEW_CYCLE_TO_FIELD.get(str(recurring).lower(), "None")


def is_exam_priority_period(today: dt.date) -> bool:
    exam_windows = [
        (dt.date(2026, 3, 14), dt.date(2026, 4, 27)),
        (dt.date(2026, 4, 28), dt.date(2026, 7, 4)),
        (dt.date(2027, 7, 1), dt.date(2027, 8, 31)),
    ]
    return any(start <= today <= end for start, end in exam_windows)


def compute_status(
    today: dt.date,
    deferred_until: str | None,
    active_from: str | None,
    blocked_by: list[str],
    closed_issue_seed_ids: set[str],
    exam_priority_guard: bool,
    current_phase_is_exam: bool,
    due_date: str | None,
    date_window_days: int = DATE_WINDOW_DAYS,
) -> str:
    deferred_date = parse_iso_date(deferred_until)
    if deferred_date and today <= deferred_date:
        return "Deferred"
    active_date = parse_iso_date(active_from)
    if active_date and today < active_date:
        return "Backlog"
    if blocked_by and any(seed_id not in closed_issue_seed_ids for seed_id in blocked_by):
        return "Blocked"
    if current_phase_is_exam and not exam_priority_guard:
        return "Backlog"
    due = parse_iso_date(due_date)
    if due and due <= today + dt.timedelta(days=date_window_days):
        return "Todo"
    return "Backlog"


def infer_status(
    issue: dict[str, Any],
    *,
    entity_kind: str,
    today: dt.date,
    closed_issue_seed_ids: set[str],
) -> str:
    if entity_kind == "epic":
        return "Backlog"
    return compute_status(
        today=today,
        deferred_until=issue.get("deferred_until"),
        active_from=issue.get("active_from"),
        blocked_by=list(issue.get("blocked_by", [])),
        closed_issue_seed_ids=closed_issue_seed_ids,
        exam_priority_guard=normalize_bool(issue.get("exam_priority_guard")),
        current_phase_is_exam=is_exam_priority_period(today),
        due_date=issue.get("due_date"),
    )


def validate_seed(seed: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    required_sections = [
        "meta",
        "phases",
        "epics",
        "milestones",
        "labels",
        "project_fields",
        "phase_cards",
        "win_conditions",
        "issues",
    ]
    for section in required_sections:
        if section not in seed:
            errors.append(f"Missing top-level section: {section}")
    required_fields = {
        "Status",
        "Priority",
        "Area",
        "Phase",
        "Due Date",
        "Evidence Type",
        "Monthly Bucket",
        "Quarter",
        "Career Link",
        "AI Link",
        "Task Type",
        "Review Cycle",
        "Active Window",
        "Deferred Until",
        "Deferred Flag",
        "Blocked By",
        "DoD Ready",
        "Evidence Ready",
        "Exam Priority Guard",
        "Start Date",
        "End Date",
        "Execution Time Block",
        "Execution Estimate",
        "Execution Energy",
        "Execution Focus",
        "Execution Next Action",
        "Execution Outcome",
        "Execution Check",
    }
    project_field_names = {field["name"] for field in seed.get("project_fields", [])}
    missing_project_fields = sorted(required_fields - project_field_names)
    for field_name in missing_project_fields:
        errors.append(f"Missing project field: {field_name}")
    phase_ids = {item["id"] for item in seed.get("phases", [])}
    epic_ids = {item["id"] for item in seed.get("epics", [])}
    milestone_ids = {item["id"] for item in seed.get("milestones", [])}
    allowed_task_types = set(TASK_TYPE_TO_FIELD) - {"epic"}
    entity_ids: set[str] = set()
    for entity_kind, items in entity_collections(seed):
        for item in items:
            item_id = item.get("id")
            label = entity_kind.replace("_", " ").title()
            if item_id in entity_ids:
                errors.append(f"Duplicate seed entity id: {item_id}")
            entity_ids.add(item_id)
            if item.get("phase") and item["phase"] not in phase_ids:
                errors.append(f"{label} {item_id} references unknown phase: {item['phase']}")
            if item.get("epic") and item["epic"] not in epic_ids:
                errors.append(f"{label} {item_id} references unknown epic: {item['epic']}")
            if item.get("milestone") and item["milestone"] not in milestone_ids:
                errors.append(f"{label} {item_id} references unknown milestone: {item['milestone']}")
            task_type = item.get("task_type")
            if task_type not in allowed_task_types:
                errors.append(f"{label} {item_id} has invalid task_type: {task_type}")
            for list_key in (
                "work_steps",
                "deliverables",
                "evidence_to_keep",
                "dod",
                "blocked_by",
                "dependencies",
                "inputs",
                "things_to_make",
                "completion_check",
                "daily_execution",
            ):
                value = item.get(list_key)
                if not isinstance(value, list):
                    errors.append(f"{label} {item_id} has non-list {list_key}")
            if item.get("linked_issue_ids") is not None and not isinstance(item.get("linked_issue_ids"), list):
                errors.append(f"{label} {item_id} has non-list linked_issue_ids")
            for required_text in ("outcome", "next_action", "why_this_matters", "device", "time_block", "estimate", "energy", "focus"):
                if not normalize_text(str(item.get(required_text, ""))):
                    errors.append(f"{label} {item_id} is missing {required_text}")
            if not item.get("work_steps"):
                errors.append(f"{label} {item_id} is missing work_steps")
            if not item.get("dod"):
                errors.append(f"{label} {item_id} is missing dod")
            if not item.get("completion_check"):
                errors.append(f"{label} {item_id} is missing completion_check")
            if not item.get("daily_execution"):
                errors.append(f"{label} {item_id} is missing daily_execution")
            if not item.get("active_from"):
                errors.append(f"{label} {item_id} is missing active_from")
            if not is_valid_iso_date(item.get("active_from")):
                errors.append(f"{label} {item_id} has invalid active_from: {item.get('active_from')}")
            if not is_valid_iso_date(item.get("deferred_until")):
                errors.append(f"{label} {item_id} has invalid deferred_until: {item.get('deferred_until')}")
            if not is_valid_iso_date(item.get("due_date")):
                errors.append(f"{label} {item_id} has invalid due_date: {item.get('due_date')}")
            if item.get("evidence_type") and not item.get("evidence_to_keep"):
                warnings.append(f"{label} {item_id} has evidence_type but no evidence_to_keep")
            if item.get("due_date") and item.get("active_from"):
                due_date = parse_iso_date(item["due_date"])
                active_date = parse_iso_date(item["active_from"])
                if due_date and active_date and due_date < active_date:
                    warnings.append(f"{label} {item_id} due_date is earlier than active_from")
            if entity_kind in {"phase_card", "win_condition"} and not item.get("linked_issue_ids"):
                errors.append(f"{label} {item_id} is missing linked_issue_ids")
    for entity_kind, items in entity_collections(seed):
        label = entity_kind.replace("_", " ").title()
        for item in items:
            item_id = item["id"]
            for dependency in item.get("dependencies", []):
                if dependency not in entity_ids:
                    errors.append(f"{label} {item_id} references unknown dependency: {dependency}")
            for blocker in item.get("blocked_by", []):
                if blocker not in entity_ids:
                    errors.append(f"{label} {item_id} references unknown blocked_by: {blocker}")
            for linked_id in item.get("linked_issue_ids", []):
                if linked_id not in entity_ids:
                    errors.append(f"{label} {item_id} references unknown linked_issue_id: {linked_id}")
            if sorted(item.get("blocked_by", [])) != sorted(item.get("dependencies", [])):
                warnings.append(f"{label} {item_id} blocked_by does not match dependencies")
    return errors, warnings


def build_epic_issue(epic: dict[str, Any], child_issues: list[dict[str, Any]]) -> PlannedIssue:
    base_lines = [epic.get("description", "").strip()]
    if child_issues:
        base_lines.extend(
            [
                "",
                "## Included Seed Issues",
                *[f"- {issue['id']}: {issue['title']}" for issue in child_issues],
            ]
        )
    base_body = "\n".join(line for line in base_lines if line is not None).strip()
    metadata_lines = [
        f"- Seed ID: {epic['id']}",
        f"- Default Priority: {priority_to_field(epic.get('priority')) or ''}",
        f"- Child Issue Count: {len(child_issues)}",
    ]
    fingerprint_source = {
        "seed_id": epic["id"],
        "entity_kind": "epic",
        "title": f"[Epic] {epic['name']}",
        "body": base_body,
        "labels": sorted(epic.get("labels", []) + [f"priority:{epic['priority']}"]),
        "field_values": {
            "Status": "Backlog",
            "Priority": priority_to_field(epic.get("priority")),
            "Area": area_from_labels(epic.get("labels", [])),
            "Task Type": "Epic",
        },
    }
    fingerprint = sha256_text(json.dumps(fingerprint_source, ensure_ascii=False, sort_keys=True))
    marker = marker_payload(epic["id"], "epic", fingerprint)
    body = render_epic_body(base_body, metadata_lines, marker)
    return PlannedIssue(
        seed_id=epic["id"],
        entity_kind="epic",
        title=f"[Epic] {epic['name']}",
        body=body,
        labels=sorted(epic.get("labels", []) + [f"priority:{epic['priority']}"]),
        milestone_title=None,
        field_values={
            "Status": "Backlog",
            "Priority": priority_to_field(epic.get("priority")),
            "Area": area_from_labels(epic.get("labels", [])),
            "Phase": None,
            "Due Date": None,
            "Evidence Type": None,
            "Monthly Bucket": None,
            "Quarter": None,
            "Career Link": None,
            "AI Link": None,
            "Task Type": "Epic",
            "Review Cycle": "None",
            "Active Window": None,
            "Deferred Until": None,
            "Deferred Flag": "N/A",
            "Blocked By": None,
            "DoD Ready": "N/A",
            "Evidence Ready": "N/A",
            "Exam Priority Guard": "N/A",
        },
        fingerprint=fingerprint,
    )


def build_seed_issue(
    issue: dict[str, Any],
    *,
    entity_kind: str,
    phase_name_by_id: dict[str, str],
    issue_title_by_id: dict[str, str],
    today: dt.date,
    closed_issue_seed_ids: set[str],
) -> PlannedIssue:
    blocked_titles = [
        f"{seed_id}: {issue_title_by_id.get(seed_id, '(unknown issue)')}"
        for seed_id in issue.get("blocked_by", [])
    ]
    linked_titles = [
        f"{seed_id}: {issue_title_by_id.get(seed_id, '(unknown issue)')}"
        for seed_id in issue.get("linked_issue_ids", [])
    ]
    field_values = {
        "Status": infer_status(
            issue,
            entity_kind=entity_kind,
            today=today,
            closed_issue_seed_ids=closed_issue_seed_ids,
        ),
        "Priority": priority_to_field(issue.get("priority")),
        "Area": area_from_labels(issue.get("labels", [])),
        "Phase": phase_from_labels(issue.get("labels", [])),
        "Due Date": issue.get("due_date") or None,
        "Evidence Type": issue.get("evidence_type") or None,
        "Monthly Bucket": issue.get("monthly_bucket") or None,
        "Quarter": issue.get("quarter") or None,
        "Career Link": issue.get("career_link") or None,
        "AI Link": issue.get("ai_link") or None,
        "Task Type": infer_task_type(issue, entity_kind="issue"),
        "Review Cycle": infer_review_cycle(issue),
        "Active Window": active_window_text(issue),
        "Deferred Until": issue.get("deferred_until") or None,
        "Deferred Flag": (
            "Deferred"
            if issue.get("deferred_until") and today <= parse_iso_date(issue["deferred_until"])
            else "Active"
        ),
        "Blocked By": ", ".join(issue.get("blocked_by", [])) or None,
        "DoD Ready": "Ready" if issue.get("dod") else "Missing",
        "Evidence Ready": (
            "Ready"
            if issue.get("evidence_to_keep")
            else ("Missing" if issue.get("evidence_type") else "N/A")
        ),
        "Exam Priority Guard": (
            "Exam Priority" if normalize_bool(issue.get("exam_priority_guard")) else "Normal"
        ),
        "Start Date": issue.get("active_from") or None,
        "End Date": issue.get("due_date") or None,
        "Execution Time Block": issue.get("time_block") or None,
        "Execution Estimate": issue.get("estimate") or None,
        "Execution Energy": issue.get("energy") or None,
        "Execution Focus": issue.get("focus") or None,
        "Execution Next Action": issue.get("next_action") or None,
        "Execution Outcome": issue.get("outcome") or None,
        "Execution Check": completion_check_text(list(issue.get("completion_check", []))),
    }
    fingerprint_source = {
        "seed_id": issue["id"],
        "entity_kind": entity_kind,
        "title": issue["title"],
        "body": normalize_text(issue.get("body")),
        "labels": sorted(issue.get("labels", [])),
        "milestone": issue.get("milestone"),
        "field_values": field_values,
    }
    fingerprint = sha256_text(json.dumps(fingerprint_source, ensure_ascii=False, sort_keys=True))
    marker = marker_payload(issue["id"], entity_kind, fingerprint)
    body = render_issue_body(
        issue,
        marker=marker,
        phase_name=phase_name_by_id.get(issue.get("phase", "")),
        blocked_titles=blocked_titles,
        linked_titles=linked_titles,
    )
    return PlannedIssue(
        seed_id=issue["id"],
        entity_kind=entity_kind,
        title=issue["title"],
        body=body,
        labels=sorted(issue.get("labels", [])),
        milestone_title=issue.get("milestone_title") or issue.get("milestone"),
        field_values=field_values,
        fingerprint=fingerprint,
    )


def build_planned_issues(
    seed: dict[str, Any],
    *,
    today: dt.date,
    closed_issue_seed_ids: set[str] | None = None,
) -> list[PlannedIssue]:
    milestone_title_by_id = {item["id"]: item["title"] for item in seed.get("milestones", [])}
    phase_name_by_id = {item["id"]: item["name"] for item in seed.get("phases", [])}
    seed_issues = copy.deepcopy(seed.get("issues", []))
    phase_cards = copy.deepcopy(seed.get("phase_cards", []))
    win_conditions = copy.deepcopy(seed.get("win_conditions", []))
    all_seed_items = phase_cards + win_conditions + seed_issues
    issue_title_by_id = {item["id"]: item["title"] for item in all_seed_items}
    closed_issue_seed_ids = closed_issue_seed_ids or set()
    for issue in all_seed_items:
        issue["milestone_title"] = milestone_title_by_id.get(issue.get("milestone"))

    child_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in seed_issues:
        if issue.get("epic"):
            child_map[issue["epic"]].append(issue)

    planned: list[PlannedIssue] = []
    for epic in seed.get("epics", []):
        planned.append(build_epic_issue(epic, child_map.get(epic["id"], [])))
    for entity_kind, collection in (("phase_card", phase_cards), ("win_condition", win_conditions), ("issue", seed_issues)):
        for issue in collection:
            planned.append(
                build_seed_issue(
                    issue,
                    entity_kind=entity_kind,
                    phase_name_by_id=phase_name_by_id,
                    issue_title_by_id=issue_title_by_id,
                    today=today,
                    closed_issue_seed_ids=closed_issue_seed_ids,
                )
            )
    return planned


def closed_issue_seed_ids(existing_issues: list[dict[str, Any]]) -> set[str]:
    closed_ids: set[str] = set()
    for issue in existing_issues:
        if issue.get("state") != "closed":
            continue
        marker = extract_marker(issue.get("body"))
        if marker and marker.get("seed_id"):
            closed_ids.add(str(marker["seed_id"]))
    return closed_ids


def build_audit_findings(seed: dict[str, Any], *, today: dt.date) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    validation_errors, validation_warnings = validate_seed(seed)
    for message in validation_errors:
        findings.append(AuditFinding("FAIL", "seed-validation", "seed", message))
    for message in validation_warnings:
        findings.append(AuditFinding("WARN", "seed-validation", "seed", message))

    for entity_kind, issue in iter_seed_work_items(seed):
        issue_id = issue["id"]
        status = compute_status(
            today=today,
            deferred_until=issue.get("deferred_until"),
            active_from=issue.get("active_from"),
            blocked_by=list(issue.get("blocked_by", [])),
            closed_issue_seed_ids=set(),
            exam_priority_guard=normalize_bool(issue.get("exam_priority_guard")),
            current_phase_is_exam=is_exam_priority_period(today),
            due_date=issue.get("due_date"),
        )
        if not issue.get("recurring") and not issue.get("due_date"):
            findings.append(
                AuditFinding("WARN", "missing-due-date", issue_id, "Non-recurring item has no due_date.")
            )
        if not issue.get("recurring") and not issue.get("milestone"):
            findings.append(
                AuditFinding("WARN", "missing-milestone", issue_id, "Non-recurring item has no milestone.")
            )
        if not issue.get("phase") and issue.get("task_type") not in {"review", "evidence"}:
            findings.append(
                AuditFinding("WARN", "missing-phase", issue_id, "Item has no phase assignment.")
            )
        if not issue.get("dod"):
            findings.append(AuditFinding("FAIL", "missing-dod", issue_id, "Item has no Definition of Done."))
        if not issue.get("outcome"):
            findings.append(AuditFinding("FAIL", "missing-outcome", issue_id, "Item has no Outcome."))
        if not issue.get("next_action"):
            findings.append(AuditFinding("FAIL", "missing-next-action", issue_id, "Item has no Next Action."))
        if not issue.get("completion_check"):
            findings.append(
                AuditFinding("FAIL", "missing-completion-check", issue_id, "Item has no completion_check.")
            )
        if not issue.get("daily_execution"):
            findings.append(
                AuditFinding("FAIL", "missing-daily-execution", issue_id, "Item has no daily_execution.")
            )
        if issue.get("evidence_type") and not issue.get("evidence_to_keep"):
            findings.append(
                AuditFinding("FAIL", "missing-evidence", issue_id, "Item has evidence_type but no evidence_to_keep.")
            )
        if issue.get("due_date") and issue.get("active_from"):
            due_date = parse_iso_date(issue["due_date"])
            active_date = parse_iso_date(issue["active_from"])
            if due_date and active_date and due_date < active_date:
                findings.append(
                    AuditFinding(
                        "WARN",
                        "invalid-window",
                        issue_id,
                        "Item due_date is earlier than active_from.",
                    )
                )
        if status == "Blocked":
            findings.append(AuditFinding("INFO", "blocked", issue_id, "Item is blocked by open dependencies."))
        if entity_kind in {"phase_card", "win_condition"} and not issue.get("linked_issue_ids"):
            findings.append(
                AuditFinding("FAIL", "missing-linked-items", issue_id, "Layered item has no linked_issue_ids.")
            )
        if is_exam_priority_period(today) and not normalize_bool(issue.get("exam_priority_guard")):
            if status not in {"Backlog", "Deferred"}:
                findings.append(
                    AuditFinding(
                        "FAIL",
                        "exam-priority-violation",
                        issue_id,
                        "Non-guarded issue is active during an exam priority period.",
                    )
                )

    findings.sort(key=lambda item: (AUDIT_SEVERITY_ORDER[item.severity], item.code, item.target))
    return findings


def summarize_audit(findings: list[AuditFinding]) -> dict[str, int]:
    counter = Counter(item.severity for item in findings)
    for severity in AUDIT_SEVERITY_ORDER:
        counter.setdefault(severity, 0)
    return dict(counter)


def write_audit_report(
    *,
    seed: dict[str, Any],
    findings: list[AuditFinding],
    report_dir: pathlib.Path,
    seed_path: pathlib.Path,
    today: dt.date,
) -> dict[str, str]:
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "report_version": REPORT_VERSION,
        "mode": "audit",
        "generated_at": timestamp,
        "seed_path": str(seed_path),
        "today": today.isoformat(),
        "summary": summarize_audit(findings),
        "findings": [dataclasses.asdict(item) for item in findings],
        "seed_counts": {
            "phases": len(seed.get("phases", [])),
            "epics": len(seed.get("epics", [])),
            "milestones": len(seed.get("milestones", [])),
            "issues": len(seed.get("issues", [])),
        },
    }
    json_path = report_dir / f"{timestamp}_audit.json"
    latest_json = report_dir / "latest_audit.json"
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")

    summary = summarize_audit(findings)
    md_lines = [
        "# Sync Audit Report",
        "",
        f"- Generated at: {timestamp}",
        f"- Seed: `{seed_path.as_posix()}`",
        f"- Today: `{today.isoformat()}`",
        "",
        "## Summary",
        f"- FAIL: {summary['FAIL']}",
        f"- WARN: {summary['WARN']}",
        f"- INFO: {summary['INFO']}",
        "",
        "## Findings",
    ]
    if not findings:
        md_lines.append("- No findings.")
    else:
        for finding in findings:
            md_lines.append(
                f"- [{finding.severity}] {finding.target} ({finding.code}): {finding.message}"
            )
    md_path = report_dir / f"{timestamp}_audit.md"
    latest_md = report_dir / "latest_audit.md"
    md_text = "\n".join(md_lines)
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path)}


def list_repo_labels(repo: RepoTarget) -> dict[str, dict[str, Any]]:
    labels = run_json(
        [
            "gh",
            "label",
            "list",
            "--repo",
            repo.full_name,
            "--limit",
            "200",
            "--json",
            "name,color,description",
        ]
    )
    return {item["name"]: item for item in labels}


def list_repo_milestones(repo: RepoTarget) -> dict[str, dict[str, Any]]:
    milestones = gh_api_json(f"repos/{repo.full_name}/milestones?state=all&per_page=100")
    return {item["title"]: item for item in milestones}


def list_repo_issues(repo: RepoTarget) -> list[dict[str, Any]]:
    return run_json(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo.full_name,
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "number,title,body,url,labels,milestone,state",
        ]
    )


def find_existing_issue(
    planned_issue: PlannedIssue,
    existing_issues: list[dict[str, Any]],
) -> dict[str, Any] | None:
    marker_match = None
    title_matches: list[dict[str, Any]] = []
    for existing in existing_issues:
        marker = extract_marker(existing.get("body"))
        if marker and marker.get("seed_id") == planned_issue.seed_id:
            marker_match = existing
            break
        if existing.get("title") == planned_issue.title:
            title_matches.append(existing)
    if marker_match:
        return marker_match
    if len(title_matches) == 1:
        return title_matches[0]
    return None


def compare_issue_state(
    planned_issue: PlannedIssue,
    existing_issue: dict[str, Any] | None,
    milestone_numbers: dict[str, int],
) -> dict[str, Any]:
    desired = {
        "title": planned_issue.title,
        "body": planned_issue.body,
        "labels": planned_issue.labels,
        "milestone_number": milestone_numbers.get(planned_issue.milestone_title or ""),
    }
    if not existing_issue:
        return {"action": "create", "desired": desired}
    current_labels = sorted(label["name"] for label in existing_issue.get("labels", []))
    current_body = normalize_text(existing_issue.get("body"))
    current_title = existing_issue.get("title")
    current_milestone_number = (
        existing_issue["milestone"]["number"] if existing_issue.get("milestone") else None
    )
    changes: dict[str, Any] = {}
    if current_title != desired["title"]:
        changes["title"] = {"current": current_title, "desired": desired["title"]}
    if current_body != normalize_text(desired["body"]):
        changes["body"] = {
            "current_hash": sha256_text(current_body),
            "desired_hash": sha256_text(desired["body"]),
        }
    if current_labels != sorted(desired["labels"]):
        changes["labels"] = {"current": current_labels, "desired": sorted(desired["labels"])}
    if current_milestone_number != desired["milestone_number"]:
        changes["milestone_number"] = {
            "current": current_milestone_number,
            "desired": desired["milestone_number"],
        }
    return {"action": "update" if changes else "noop", "changes": changes, "desired": desired}


def existing_project(owner: str, title: str) -> dict[str, Any] | None:
    user_query = """
    query($login:String!) {
      user(login:$login) {
        projectsV2(first:100) {
          nodes {
            id
            number
            title
            closed
            public
            shortDescription
            readme
            url
          }
        }
      }
    }
    """
    org_query = """
    query($login:String!) {
      organization(login:$login) {
        projectsV2(first:100) {
          nodes {
            id
            number
            title
            closed
            public
            shortDescription
            readme
            url
          }
        }
      }
    }
    """
    data = gh_graphql(user_query, {"login": owner})
    projects = (((data or {}).get("data") or {}).get("user") or {}).get("projectsV2", {}).get("nodes", [])
    if not projects:
        data = gh_graphql(org_query, {"login": owner})
        projects = (((data or {}).get("data") or {}).get("organization") or {}).get("projectsV2", {}).get("nodes", [])
    for project in projects:
        if project["title"] == title:
            return project
    return None


def project_fields(project_number: int, owner: str) -> dict[str, ProjectFieldRef]:
    query = """
    query($owner: String!, $number: Int!, $after: String) {
      repositoryOwner(login: $owner) {
        ... on User {
          projectV2(number: $number) {
            fields(first: 100, after: $after) {
              nodes {
                __typename
                ... on ProjectV2FieldCommon {
                  id
                  name
                  dataType
                }
                ... on ProjectV2SingleSelectField {
                  options {
                    id
                    name
                  }
                }
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
        ... on Organization {
          projectV2(number: $number) {
            fields(first: 100, after: $after) {
              nodes {
                __typename
                ... on ProjectV2FieldCommon {
                  id
                  name
                  dataType
                }
                ... on ProjectV2SingleSelectField {
                  options {
                    id
                    name
                  }
                }
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
      }
    }
    """
    cursor: str | None = None
    result: dict[str, ProjectFieldRef] = {}
    while True:
        payload = gh_graphql(query, {"owner": owner, "number": project_number, "after": cursor})
        project = ((payload.get("data") or {}).get("repositoryOwner") or {}).get("projectV2")
        if not project:
            break
        fields = project["fields"]
        for field in fields.get("nodes", []):
            options = {option["name"]: option["id"] for option in field.get("options", [])}
            result[field["name"]] = ProjectFieldRef(
                id=field["id"],
                name=field["name"],
                field_type=field["__typename"],
                options=options,
            )
        page_info = fields.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
    return result


def project_items(project_number: int, owner: str) -> dict[str, dict[str, Any]]:
    payload = gh_project_json(
        [
            "item-list",
            str(project_number),
            "--owner",
            owner,
            "--limit",
            "500",
            "--format",
            "json",
        ]
    )
    items = {}
    for item in payload.get("items", []):
        content = item.get("content") or {}
        url = content.get("url")
        if url:
            items[url] = item
    return items


def ensure_labels(ctx: SyncContext, desired_labels: list[LabelSpec]) -> None:
    existing = list_repo_labels(ctx.repo)
    for label in desired_labels:
        current = existing.get(label.name)
        if not current:
            ctx.record("label", "create", label.name, color=label.color, description=label.description)
            if not ctx.dry_run:
                run_command(
                    [
                        "gh",
                        "label",
                        "create",
                        label.name,
                        "--repo",
                        ctx.repo.full_name,
                        "--color",
                        label.color,
                        "--description",
                        label.description,
                    ]
                )
            continue
        if current["color"].lower() != label.color.lower() or normalize_text(current.get("description")) != normalize_text(label.description):
            ctx.record(
                "label",
                "update",
                label.name,
                current=current,
                desired=dataclasses.asdict(label),
            )
            if not ctx.dry_run:
                run_command(
                    [
                        "gh",
                        "label",
                        "create",
                        label.name,
                        "--repo",
                        ctx.repo.full_name,
                        "--color",
                        label.color,
                        "--description",
                        label.description,
                        "--force",
                    ]
                )
        else:
            ctx.record("label", "noop", label.name)


def ensure_milestones(ctx: SyncContext, desired_milestones: list[MilestoneSpec]) -> dict[str, int]:
    existing = list_repo_milestones(ctx.repo)
    title_to_number: dict[str, int] = {}
    for milestone in desired_milestones:
        current = existing.get(milestone.title)
        desired = {
            "title": milestone.title,
            "description": milestone.description(),
            "due_on": milestone.due_on(),
            "state": "open",
        }
        if not current:
            ctx.record("milestone", "create", milestone.title, desired=desired)
            if not ctx.dry_run:
                created = gh_api_json(
                    f"repos/{ctx.repo.full_name}/milestones",
                    method="POST",
                    body=desired,
                )
                title_to_number[milestone.title] = created["number"]
            continue
        title_to_number[milestone.title] = current["number"]
        current_desc = normalize_text(current.get("description"))
        changes = {}
        if current_desc != normalize_text(desired["description"]):
            changes["description"] = {"current": current_desc, "desired": desired["description"]}
        if current.get("due_on") != desired["due_on"]:
            changes["due_on"] = {"current": current.get("due_on"), "desired": desired["due_on"]}
        if current.get("state") != desired["state"]:
            changes["state"] = {"current": current.get("state"), "desired": desired["state"]}
        if changes:
            ctx.record("milestone", "update", milestone.title, changes=changes)
            if not ctx.dry_run:
                gh_api_json(
                    f"repos/{ctx.repo.full_name}/milestones/{current['number']}",
                    method="PATCH",
                    body=desired,
                )
        else:
            ctx.record("milestone", "noop", milestone.title)
    if ctx.dry_run:
        for milestone in desired_milestones:
            current = existing.get(milestone.title)
            if current:
                title_to_number[milestone.title] = current["number"]
    return title_to_number


def ensure_project(ctx: SyncContext, seed: dict[str, Any]) -> dict[str, Any] | None:
    project = existing_project(ctx.project_owner, ctx.project_title)
    desired_readme = build_project_readme(seed)
    desired_description = "24-month exam, control, AI, evidence, and career execution board."
    if not project:
        ctx.record("project", "create", ctx.project_title, owner=ctx.project_owner)
        if ctx.dry_run:
            return None
        created = gh_project_json(
            [
                "create",
                "--owner",
                ctx.project_owner,
                "--title",
                ctx.project_title,
                "--format",
                "json",
            ]
        )
        project = {
            "id": created["id"],
            "number": created["number"],
            "title": created["title"],
            "closed": created.get("closed", False),
            "public": created.get("public", False),
            "shortDescription": created.get("shortDescription", ""),
            "readme": created.get("readme", ""),
            "url": created.get("url"),
        }
    if project.get("closed"):
        ctx.warn(
            f"Project '{ctx.project_title}' exists but is closed (number {project['number']}); sync will continue against it."
        )
    changes = {}
    if normalize_text(project.get("shortDescription")) != normalize_text(desired_description):
        changes["description"] = desired_description
    if normalize_text(project.get("readme")) != normalize_text(desired_readme):
        changes["readme"] = desired_readme
    if project.get("public"):
        changes["visibility"] = "PRIVATE"
    if changes:
        ctx.record("project", "update", ctx.project_title, changes=changes)
        if not ctx.dry_run:
            edit_args = [
                "edit",
                str(project["number"]),
                "--owner",
                ctx.project_owner,
                "--description",
                desired_description,
                "--readme",
                desired_readme,
                "--visibility",
                "PRIVATE",
            ]
            gh_project_json(edit_args)
    else:
        ctx.record("project", "noop", ctx.project_title)
    if not ctx.dry_run:
        try:
            run_command(
                [
                    "gh",
                    "project",
                    "link",
                    str(project["number"]),
                    "--owner",
                    ctx.project_owner,
                    "--repo",
                    ctx.repo.full_name,
                ]
            )
            ctx.record("project", "link", ctx.project_title, repo=ctx.repo.full_name)
        except SyncCommandError as exc:
            if "already linked" in str(exc).lower():
                ctx.record("project", "noop", f"{ctx.project_title}:link", repo=ctx.repo.full_name)
            else:
                raise
    else:
        ctx.record("project", "link", ctx.project_title, repo=ctx.repo.full_name)
    return project


def update_single_select_field_options(
    field: ProjectFieldRef,
    spec: ProjectFieldSpec,
) -> None:
    options = [
        {
            "name": option_name,
            "color": option_color(spec.name, option_name, index),
            "description": option_name,
        }
        for index, option_name in enumerate(spec.options)
    ]
    mutation = """
    mutation($input: UpdateProjectV2FieldInput!) {
      updateProjectV2Field(input: $input) {
        projectV2Field {
          __typename
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
    """
    gh_graphql(
        mutation,
        {
            "input": {
                "fieldId": field.id,
                "singleSelectOptions": options,
            }
        },
    )


def ensure_project_fields(
    ctx: SyncContext,
    project: dict[str, Any] | None,
    desired_fields: list[ProjectFieldSpec],
) -> dict[str, ProjectFieldRef]:
    if ctx.dry_run and not project:
        for spec in desired_fields:
            ctx.record("project_field", "create", spec.name, type=spec.data_type, options=spec.options)
        return {}

    if not project:
        return {}

    existing = project_fields(project["number"], ctx.project_owner)
    for spec in desired_fields:
        current = existing.get(spec.name)
        if not current:
            ctx.record("project_field", "create", spec.name, type=spec.data_type, options=spec.options)
            if not ctx.dry_run:
                create_args = [
                    "field-create",
                    str(project["number"]),
                    "--owner",
                    ctx.project_owner,
                    "--name",
                    spec.name,
                    "--data-type",
                    spec.data_type.upper(),
                    "--format",
                    "json",
                ]
                if spec.data_type == "single_select":
                    create_args.extend(["--single-select-options", ",".join(spec.options)])
                gh_project_json(create_args)
            continue
        if spec.data_type == "single_select":
            current_options = list(current.options.keys())
            if current_options != spec.options:
                ctx.record(
                    "project_field",
                    "update",
                    spec.name,
                    current=current_options,
                    desired=spec.options,
                )
                if not ctx.dry_run:
                    update_single_select_field_options(current, spec)
            else:
                ctx.record("project_field", "noop", spec.name)
        else:
            ctx.record("project_field", "noop", spec.name)
    if not ctx.dry_run:
        return project_fields(project["number"], ctx.project_owner)
    synthetic = dict(existing)
    for spec in desired_fields:
        if spec.name in synthetic:
            continue
        field_type = "ProjectV2SingleSelectField" if spec.data_type == "single_select" else "ProjectV2Field"
        synthetic[spec.name] = ProjectFieldRef(
            id=f"dry-run-{spec.name}",
            name=spec.name,
            field_type=field_type,
            options={option: option for option in spec.options},
        )
    return synthetic


def ensure_repo_issues(
    ctx: SyncContext,
    planned_issues: list[PlannedIssue],
    milestone_numbers: dict[str, int],
) -> dict[str, dict[str, Any]]:
    existing = list_repo_issues(ctx.repo)
    planned_by_seed_id: dict[str, dict[str, Any]] = {}
    for planned_issue in planned_issues:
        current = find_existing_issue(planned_issue, existing)
        diff = compare_issue_state(planned_issue, current, milestone_numbers)
        target = f"{planned_issue.seed_id} {planned_issue.title}"
        if diff["action"] == "create":
            ctx.record(
                "issue",
                "create",
                target,
                labels=planned_issue.labels,
                milestone=planned_issue.milestone_title,
            )
            if not ctx.dry_run:
                body = {
                    "title": planned_issue.title,
                    "body": planned_issue.body,
                    "labels": planned_issue.labels,
                }
                milestone_number = diff["desired"].get("milestone_number")
                if milestone_number:
                    body["milestone"] = milestone_number
                created = gh_api_json(
                    f"repos/{ctx.repo.full_name}/issues",
                    method="POST",
                    body=body,
                )
                planned_by_seed_id[planned_issue.seed_id] = created
            continue
        if diff["action"] == "update":
            ctx.record("issue", "update", target, changes=diff["changes"])
            if not ctx.dry_run:
                body = {
                    "title": planned_issue.title,
                    "body": planned_issue.body,
                    "labels": planned_issue.labels,
                    "milestone": diff["desired"]["milestone_number"],
                }
                updated = gh_api_json(
                    f"repos/{ctx.repo.full_name}/issues/{current['number']}",
                    method="PATCH",
                    body=body,
                )
                planned_by_seed_id[planned_issue.seed_id] = updated
            continue
        ctx.record("issue", "noop", target)
        if current:
            planned_by_seed_id[planned_issue.seed_id] = current
    refreshed = existing if ctx.dry_run else list_repo_issues(ctx.repo)
    for planned_issue in planned_issues:
        current = find_existing_issue(planned_issue, refreshed)
        if current:
            planned_by_seed_id[planned_issue.seed_id] = current
    return planned_by_seed_id


def ensure_project_items(
    ctx: SyncContext,
    project: dict[str, Any] | None,
    planned_issues: list[PlannedIssue],
    repo_issue_map: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    if ctx.dry_run and not project:
        for planned_issue in planned_issues:
            ctx.record("project_item", "add", planned_issue.title)
        return {}
    if not project:
        return {}
    existing = project_items(project["number"], ctx.project_owner)
    for planned_issue in planned_issues:
        issue = repo_issue_map.get(planned_issue.seed_id)
        if not issue:
            if ctx.dry_run:
                ctx.record("project_item", "add", planned_issue.title)
            else:
                ctx.error(f"Managed issue missing after sync: {planned_issue.seed_id}")
            continue
        issue_url = issue["url"]
        if issue_url in existing:
            ctx.record("project_item", "noop", planned_issue.title, url=issue_url)
            continue
        ctx.record("project_item", "add", planned_issue.title, url=issue_url)
        if not ctx.dry_run:
            gh_project_json(
                [
                    "item-add",
                    str(project["number"]),
                    "--owner",
                    ctx.project_owner,
                    "--url",
                    issue_url,
                    "--format",
                    "json",
                ]
            )
    return project_items(project["number"], ctx.project_owner) if not ctx.dry_run else existing


def current_item_value(current_item: dict[str, Any], field_name: str) -> Any:
    if field_name in current_item:
        return current_item[field_name]
    for key, value in current_item.items():
        if isinstance(key, str) and key.lower() == field_name.lower():
            return value
    return None


def compare_field_value(current_item: dict[str, Any], field_name: str, desired_value: Any) -> bool:
    current_value = current_item_value(current_item, field_name)
    if isinstance(current_value, list):
        current_value = sorted(str(item) for item in current_value)
        desired_value = sorted(str(item) for item in (desired_value or []))
        return current_value == desired_value
    if isinstance(current_value, str):
        current_value = normalize_text(current_value)
    if isinstance(desired_value, str):
        desired_value = normalize_text(desired_value)
    if current_value in ("", None):
        current_value = None
    if desired_value in ("", None):
        desired_value = None
    return current_value == desired_value


def field_set_args(
    project_id: str,
    item_id: str,
    field: ProjectFieldRef,
    value: Any,
) -> list[str]:
    base = [
        "item-edit",
        "--project-id",
        project_id,
        "--id",
        item_id,
        "--field-id",
        field.id,
    ]
    if value in ("", None):
        return base + ["--clear"]
    if field.field_type == "ProjectV2SingleSelectField":
        option_id = field.options[value]
        return base + ["--single-select-option-id", option_id]
    if field.field_type == "ProjectV2Field":
        if isinstance(value, (int, float)):
            return base + ["--number", str(value)]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)):
            return base + ["--date", str(value)]
        return base + ["--text", str(value)]
    if field.field_type == "ProjectV2IterationField":
        raise SyncCommandError(f"Iteration fields are not supported for field {field.name}")
    return base + ["--text", str(value)]


def ensure_project_item_fields(
    ctx: SyncContext,
    project: dict[str, Any] | None,
    planned_issues: list[PlannedIssue],
    repo_issue_map: dict[str, dict[str, Any]],
    fields: dict[str, ProjectFieldRef],
) -> None:
    if ctx.dry_run and not project:
        for planned_issue in planned_issues:
            for field_name, value in planned_issue.field_values.items():
                if value in ("", None):
                    continue
                ctx.record("project_field_value", "set", f"{planned_issue.title}:{field_name}", value=value)
        return
    if not project:
        return
    items = project_items(project["number"], ctx.project_owner)
    for planned_issue in planned_issues:
        issue = repo_issue_map.get(planned_issue.seed_id)
        if not issue:
            if ctx.dry_run:
                for field_name, desired_value in planned_issue.field_values.items():
                    if desired_value in ("", None):
                        continue
                    ctx.record(
                        "project_field_value",
                        "set",
                        f"{planned_issue.title}:{field_name}",
                        value=desired_value,
                    )
            continue
        item = items.get(issue["url"])
        if not item:
            if ctx.dry_run:
                for field_name, desired_value in planned_issue.field_values.items():
                    if desired_value in ("", None):
                        continue
                    ctx.record(
                        "project_field_value",
                        "set",
                        f"{planned_issue.title}:{field_name}",
                        value=desired_value,
                    )
            else:
                ctx.error(f"Project item missing for issue {planned_issue.seed_id}")
            continue
        for field_name, desired_value in planned_issue.field_values.items():
            field = fields.get(field_name)
            if not field:
                ctx.warn(f"Project field not found: {field_name}")
                continue
            if compare_field_value(item, field_name, desired_value):
                ctx.record("project_field_value", "noop", f"{planned_issue.title}:{field_name}")
                continue
            ctx.record(
                "project_field_value",
                "set",
                f"{planned_issue.title}:{field_name}",
                value=desired_value,
            )
            if not ctx.dry_run:
                args = field_set_args(project["id"], item["id"], field, desired_value)
                gh_project_json(args + ["--format", "json"])


def summarize_operations(operations: list[SyncOperation]) -> dict[str, dict[str, int]]:
    summary: dict[str, Counter[str]] = defaultdict(Counter)
    for operation in operations:
        summary[operation.category][operation.action] += 1
    return {category: dict(counter) for category, counter in summary.items()}


def write_report(
    ctx: SyncContext,
    *,
    seed: dict[str, Any],
    project: dict[str, Any] | None,
    planned_issues: list[PlannedIssue],
) -> dict[str, str]:
    ctx.report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    mode = "dry-run" if ctx.dry_run else "apply"
    status_counts = Counter(
        planned_issue.field_values.get("Status")
        for planned_issue in planned_issues
        if planned_issue.entity_kind == "issue"
    )
    task_type_counts = Counter(
        planned_issue.field_values.get("Task Type")
        for planned_issue in planned_issues
        if planned_issue.entity_kind == "issue"
    )
    payload = {
        "report_version": REPORT_VERSION,
        "mode": mode,
        "generated_at": timestamp,
        "today": ctx.today.isoformat(),
        "seed_path": str(ctx.seed_path),
        "target_repo": ctx.repo.full_name,
        "project_owner": ctx.project_owner,
        "project_title": ctx.project_title,
        "project_number": project.get("number") if project else None,
        "warnings": ctx.warnings,
        "errors": ctx.errors,
        "summary": summarize_operations(ctx.operations),
        "operations": [dataclasses.asdict(operation) for operation in ctx.operations],
        "seed_counts": {
            "phases": len(seed.get("phases", [])),
            "epics": len(seed.get("epics", [])),
            "milestones": len(seed.get("milestones", [])),
            "issues": len(seed.get("issues", [])),
        },
        "planned_status_counts": dict(status_counts),
        "planned_task_type_counts": dict(task_type_counts),
    }
    json_path = ctx.report_dir / f"{timestamp}_{mode}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_json = ctx.report_dir / f"latest_{mode}.json"
    latest_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        f"# Sync Report ({mode})",
        "",
        f"- Generated at: {timestamp}",
        f"- Today: `{ctx.today.isoformat()}`",
        f"- Seed: `{ctx.seed_path.as_posix()}`",
        f"- Target repo: `{ctx.repo.full_name}`",
        f"- Project owner: `{ctx.project_owner}`",
        f"- Project title: `{ctx.project_title}`",
        f"- Project number: `{project.get('number') if project else 'n/a'}`",
        "",
        "## Summary",
    ]
    for category, counts in summarize_operations(ctx.operations).items():
        count_text = ", ".join(f"{action}={count}" for action, count in sorted(counts.items()))
        md_lines.append(f"- {category}: {count_text}")
    if ctx.warnings:
        md_lines.extend(["", "## Warnings", *[f"- {warning}" for warning in ctx.warnings]])
    if ctx.errors:
        md_lines.extend(["", "## Errors", *[f"- {error}" for error in ctx.errors]])
    md_lines.extend(["", "## Planned Breakdown"])
    for status_name, count in sorted(status_counts.items()):
        md_lines.append(f"- Status {status_name}: {count}")
    for task_type, count in sorted(task_type_counts.items()):
        md_lines.append(f"- Task Type {task_type}: {count}")
    md_lines.extend(["", "## Operations"])
    for operation in ctx.operations:
        md_lines.append(f"- [{operation.category}] {operation.action} {operation.target}")
    md_path = ctx.report_dir / f"{timestamp}_{mode}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    latest_md = ctx.report_dir / f"latest_{mode}.md"
    latest_md.write_text("\n".join(md_lines), encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync data/project-seed.yaml into GitHub Projects.")
    parser.add_argument("--seed-path", default="data/project-seed.yaml")
    parser.add_argument("--owner", help="Override repository owner.")
    parser.add_argument("--repo", help="Override repository name.")
    parser.add_argument("--project-owner", help="Override project owner; defaults to repository owner.")
    parser.add_argument("--project-title", help="Override project title; defaults to seed meta project_name.")
    parser.add_argument("--today", help="Override the date used for status and audit calculations (YYYY-MM-DD).")
    parser.add_argument("--validate", action="store_true", help="Validate seed structure without GitHub access.")
    parser.add_argument("--audit", action="store_true", help="Run plan quality audit without syncing to GitHub.")
    parser.add_argument("--apply", action="store_true", help="Apply changes instead of running dry-run.")
    parser.add_argument(
        "--allow-repo-mismatch",
        action="store_true",
        help="Allow apply even if git remote and seed meta owner/repo differ.",
    )
    parser.add_argument(
        "--strict-target",
        action="store_true",
        help="Fail when git remote and seed meta owner/repo differ.",
    )
    parser.add_argument("--report-dir", default="data/sync-reports")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = pathlib.Path.cwd()
    seed_path = pathlib.Path(args.seed_path)
    if not seed_path.exists():
        print(f"Seed file not found: {seed_path}", file=sys.stderr)
        return 1

    seed = yaml.safe_load(seed_path.read_text(encoding="utf-8"))
    today = parse_iso_date(args.today) if args.today else iso_today()
    validation_errors, validation_warnings = validate_seed(seed)

    if args.validate:
        for error in validation_errors:
            print(f"[FAIL] {error}")
        for warning in validation_warnings:
            print(f"[WARN] {warning}")
        print(f"FAIL: {len(validation_errors)}")
        print(f"WARN: {len(validation_warnings)}")
        return 1 if validation_errors else 0

    if validation_errors:
        for error in validation_errors:
            print(error, file=sys.stderr)
        return 1

    if args.audit:
        findings = build_audit_findings(seed, today=today)
        report_paths = write_audit_report(
            seed=seed,
            findings=findings,
            report_dir=pathlib.Path(args.report_dir),
            seed_path=seed_path,
            today=today,
        )
        summary = summarize_audit(findings)
        print("Mode: audit")
        print(f"Today: {today.isoformat()}")
        print(f"FAIL: {summary['FAIL']}")
        print(f"WARN: {summary['WARN']}")
        print(f"INFO: {summary['INFO']}")
        print(f"JSON report: {report_paths['json']}")
        print(f"Markdown report: {report_paths['md']}")
        return 1 if summary["FAIL"] else 0

    remote_target = parse_github_repo(git_remote_url(cwd))
    seed_target = None
    if seed.get("meta", {}).get("owner") and seed.get("meta", {}).get("repo"):
        seed_target = RepoTarget(owner=seed["meta"]["owner"], repo=seed["meta"]["repo"])

    if not remote_target and not seed_target and (not args.owner or not args.repo):
        print("Could not infer target GitHub repository.", file=sys.stderr)
        return 1

    repo_target = RepoTarget(
        owner=args.owner or (remote_target.owner if remote_target else seed_target.owner),
        repo=args.repo or (remote_target.repo if remote_target else seed_target.repo),
    )
    project_owner = args.project_owner or repo_target.owner
    project_title = args.project_title or seed["meta"]["project_name"]

    ctx = SyncContext(
        dry_run=not args.apply,
        repo=repo_target,
        project_owner=project_owner,
        project_title=project_title,
        today=today,
        seed_path=seed_path,
        report_dir=pathlib.Path(args.report_dir),
    )

    if remote_target and seed_target and remote_target.full_name != seed_target.full_name:
        mismatch_message = (
            "Seed meta owner/repo does not match the Git remote. "
            f"Using git remote target '{remote_target.full_name}' and reporting the mismatch."
        )
        if args.strict_target:
            print(mismatch_message, file=sys.stderr)
            return 1
        if args.apply and not args.allow_repo_mismatch and not (args.owner and args.repo):
            print(
                mismatch_message
                + " Refusing apply without explicit --owner/--repo or --allow-repo-mismatch.",
                file=sys.stderr,
            )
            return 1
        ctx.warn(mismatch_message)

    existing_issues = list_repo_issues(ctx.repo)
    managed_closed_seed_ids = closed_issue_seed_ids(existing_issues)
    planned_issues = build_planned_issues(
        seed,
        today=today,
        closed_issue_seed_ids=managed_closed_seed_ids,
    )
    label_specs = label_specs_from_seed(seed)
    milestone_specs = milestone_specs_from_seed(seed)
    field_specs = seed_field_specs(seed)

    project: dict[str, Any] | None = None
    try:
        ensure_labels(ctx, label_specs)
        milestone_numbers = ensure_milestones(ctx, milestone_specs)
        project = ensure_project(ctx, seed)
        fields = ensure_project_fields(ctx, project, field_specs)
        repo_issue_map = ensure_repo_issues(ctx, planned_issues, milestone_numbers)
        ensure_project_items(ctx, project, planned_issues, repo_issue_map)
        ensure_project_item_fields(ctx, project, planned_issues, repo_issue_map, fields)
    except SyncCommandError as exc:
        ctx.error(str(exc))

    report_paths = write_report(ctx, seed=seed, project=project, planned_issues=planned_issues)
    summary = summarize_operations(ctx.operations)
    print(f"Mode: {'dry-run' if ctx.dry_run else 'apply'}")
    print(f"Today: {ctx.today.isoformat()}")
    print(f"Target repo: {ctx.repo.full_name}")
    print(f"Project: {ctx.project_title}")
    for category, counts in sorted(summary.items()):
        rendered = ", ".join(f"{action}={count}" for action, count in sorted(counts.items()))
        print(f"- {category}: {rendered}")
    if ctx.warnings:
        print("Warnings:")
        for warning in ctx.warnings:
            print(f"- {warning}")
    if ctx.errors:
        print("Errors:")
        for error in ctx.errors:
            print(f"- {error}")
    print(f"JSON report: {report_paths['json']}")
    print(f"Markdown report: {report_paths['md']}")
    return 1 if ctx.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
