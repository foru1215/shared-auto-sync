from __future__ import annotations

import datetime as dt

from scripts import github_project_sync as sync


TODAY = dt.date(2026, 3, 14)


def test_deferred_until_future_returns_deferred() -> None:
    status = sync.compute_status(
        today=TODAY,
        deferred_until="2026-12-31",
        active_from="2026-03-14",
        blocked_by=[],
        closed_issue_seed_ids=set(),
        exam_priority_guard=False,
        current_phase_is_exam=False,
        due_date="2027-01-31",
    )
    assert status == "Deferred"


def test_active_from_future_returns_backlog() -> None:
    status = sync.compute_status(
        today=TODAY,
        deferred_until=None,
        active_from="2026-07-05",
        blocked_by=[],
        closed_issue_seed_ids=set(),
        exam_priority_guard=False,
        current_phase_is_exam=False,
        due_date="2026-07-31",
    )
    assert status == "Backlog"


def test_blocked_by_open_issue_returns_blocked() -> None:
    status = sync.compute_status(
        today=TODAY,
        deferred_until=None,
        active_from="2026-03-14",
        blocked_by=["ISS-001"],
        closed_issue_seed_ids=set(),
        exam_priority_guard=True,
        current_phase_is_exam=True,
        due_date="2026-03-31",
    )
    assert status == "Blocked"


def test_exam_period_without_guard_returns_backlog() -> None:
    status = sync.compute_status(
        today=TODAY,
        deferred_until=None,
        active_from="2026-03-14",
        blocked_by=[],
        closed_issue_seed_ids=set(),
        exam_priority_guard=False,
        current_phase_is_exam=True,
        due_date="2026-03-31",
    )
    assert status == "Backlog"


def test_due_within_window_returns_todo() -> None:
    status = sync.compute_status(
        today=TODAY,
        deferred_until=None,
        active_from="2026-03-14",
        blocked_by=[],
        closed_issue_seed_ids=set(),
        exam_priority_guard=True,
        current_phase_is_exam=True,
        due_date="2026-03-31",
    )
    assert status == "Todo"


def test_outside_window_returns_backlog() -> None:
    status = sync.compute_status(
        today=TODAY,
        deferred_until=None,
        active_from="2026-03-14",
        blocked_by=[],
        closed_issue_seed_ids=set(),
        exam_priority_guard=True,
        current_phase_is_exam=True,
        due_date="2026-12-31",
    )
    assert status == "Backlog"
