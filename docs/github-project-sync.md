# GitHub Project Sync Spec

## Source priority

1. `data/project-seed.yaml`
2. `docs/project-plan-summary.md`
3. `docs/project-plan.md`

The sync engine treats the YAML as authoritative. The markdown documents are only for human reference when seed data is incomplete or needs interpretation.

## Managed resources

- Repository labels
- Repository milestones
- Managed GitHub issues
- Managed phase cards
- Managed win-condition cards
- GitHub Project v2
- Project items linked to managed issues
- Project custom field values
- Validation report (`--validate`)
- Audit report (`--audit`)

## Idempotency strategy

Managed issues include an HTML comment marker:

```html
<!-- github-project-sync: {...} -->
```

The marker stores:

- `seed_id`
- `entity_kind`
- `fingerprint`
- `source`

Sync matching order:

1. Existing marker with the same `seed_id`
2. Exact title match fallback

This prevents duplicate creation on rerun and makes planned updates deterministic.

## Entity mapping

### Labels

All labels in `labels.*` are synced by exact name.

### Milestones

Each YAML milestone is synced to a repository milestone with:

- title
- description
- due date

### Epics

Each YAML epic is turned into a managed GitHub issue:

- title: `[Epic] <name>`
- task type: `Epic`

### Issues

Each YAML item becomes a managed GitHub issue with:

- summary
- outcome
- next action
- why-this-matters
- device / inputs / things-to-make
- work checklist
- deliverables / evidence
- DoD / completion check
- blockers / linked work items
- daily execution
- timing / review-note
- machine-readable marker

### Phase cards

Each `phase_cards` entry is synced as a `[PHASE] ...` issue.

### Win conditions

Each `win_conditions` entry is synced as a `[WIN] ...` issue.

### Project fields

Seed-defined fields are authoritative and synced as-is from `data/project-seed.yaml`.

## Default field mapping

| Field | Mapping |
|------|---------|
| Status | `compute_status()` six-rule evaluation |
| Priority | `p0/p1/p2` -> `P0/P1/P2` |
| Area | derived from `area:*` label |
| Phase | derived from `phase:*` label |
| Due Date | `due_date` |
| Evidence Type | `evidence_type` |
| Monthly Bucket | `monthly_bucket` |
| Quarter | `quarter` |
| Career Link | `career_link` |
| AI Link | `ai_link` |
| Task Type | `task_type` -> display mapping |
| Review Cycle | `weekly/monthly/quarterly` recurring value, otherwise `None` |
| Active Window | `active_from` and `due_date` summary |
| Deferred Until | `deferred_until` |
| Deferred Flag | current deferred state |
| Blocked By | `blocked_by` joined text |
| DoD Ready | whether `dod` exists |
| Evidence Ready | whether `evidence_to_keep` exists |
| Exam Priority Guard | whether the issue is allowed during exam-priority windows |
| Start Date | `active_from` |
| End Date | `due_date` |
| Execution Time Block | `time_block` |
| Execution Estimate | `estimate` |
| Execution Energy | `energy` |
| Execution Focus | `focus` |
| Execution Next Action | `next_action` |
| Execution Outcome | `outcome` |
| Execution Check | `completion_check` summary text |

## Status rules

`Status` is derived in this exact order:

1. `deferred_until >= today` -> `Deferred`
2. `active_from > today` -> `Backlog`
3. unresolved `blocked_by` -> `Blocked`
4. exam-priority period + `exam_priority_guard == false` -> `Backlog`
5. `due_date <= today + DATE_WINDOW_DAYS` -> `Todo`
6. otherwise -> `Backlog`

Use `--today YYYY-MM-DD` to simulate a specific planning date.

## Validate

```powershell
python scripts/github_project_sync.py --validate
```

This checks:

- required top-level sections
- required layered sections (`phase_cards`, `win_conditions`, `issues`)
- required project fields
- `task_type`, `outcome`, `next_action`, `work_steps`, `dod`, `completion_check`, `daily_execution`
- `active_from`, `deferred_until`, `time_block`, `estimate`, `energy`, `focus`
- dependency and blocked-by references
- linked work-item references
- milestone / epic / phase references

`FAIL` returns exit code `1`. `WARN` is reported but keeps exit code `0`.

## Audit

```powershell
python scripts/github_project_sync.py --audit --today 2026-03-14
```

Audit flags:

- missing due date or milestone on non-recurring tasks
- missing outcome / next action / completion check / daily execution
- missing DoD or evidence requirements
- invalid active window
- blocked items
- exam-priority violations

Reports are written to:

- `data/sync-reports/latest_audit.json`
- `data/sync-reports/latest_audit.md`

## Reports

Each run writes JSON and Markdown reports into `data/sync-reports/`.

These reports include:

- target repo
- simulated `today`
- project identity
- warnings
- errors
- action counts
- per-operation details
- planned status breakdown
- planned task-type breakdown

## Re-sync rules

- Update `data/project-seed.yaml`
- Run `python scripts/github_project_sync.py --validate`
- Run `pytest -q`
- Run `python scripts/github_project_sync.py --audit --today 2026-03-14`
- Run dry-run
- Review `data/sync-reports/latest_dry-run.md`
- Run apply

No manual cleanup should be necessary for managed resources unless the target repository or project changes.

## Target safety

Current target:

- seed meta: `foru1215/shared-auto-sync`
- git remote: `foru1215/shared-auto-sync`

Safety behavior:

- dry-run continues and records a warning when a mismatch appears
- `--apply` refuses to continue unless you pass explicit target overrides or `--allow-repo-mismatch`
- `--strict-target` fails immediately on mismatch
