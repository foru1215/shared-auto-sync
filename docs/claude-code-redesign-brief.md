# Claude Code Redesign Brief

## Purpose

This document briefs Claude Code on how to redesign the current GitHub Projects operating model so it becomes more detailed, easier to execute, and closer to the quality of [Project 1](https://github.com/users/foru1215/projects/1).

This is not a blank-sheet redesign. A working sync engine already exists. The redesign must build on that implementation without throwing away the safety guarantees.

## Read order

Read these in order:
1. `data/project-seed.yaml`
2. `docs/project1-reference-notes.md`
3. `docs/project-plan-summary.md`
4. `docs/project-plan.md`
5. `scripts/github_project_sync.py`
6. `docs/github-project-sync.md`
7. `README.md`
8. `data/sync-reports/latest_dry-run.md`
9. `data/sync-reports/latest_apply.md`

## What already exists

As of 2026-03-14, the repo already has:
- `gh` CLI based sync to GitHub Projects
- `dry-run`
- `apply`
- idempotent issue/project sync with machine-readable markers
- label sync
- milestone sync
- epic issue sync
- seed issue sync
- project item sync
- project field sync
- `--validate`
- `--audit`
- unit tests
- sync reports

Current live target:
- repo: `foru1215/shared-auto-sync`
- project: `Career Transition 24-Month Plan`
- project URL: [Project 4](https://github.com/users/foru1215/projects/4)

## Current implementation is useful but not detailed enough

The present implementation is structurally sound, but execution quality is still weak.

Main gaps:
1. Issues are still too coarse.
- They describe areas of work, but not always bounded work units.
- Some cards are still "topic buckets" rather than cards a person can finish.

2. Completion quality is under-specified.
- `dod` exists, but "how do I know I am done today" is still weak.
- Evidence and completion checks are not strict enough across all issue types.

3. Daily execution is weak.
- The board can answer "what phase am I in?"
- It is less reliable at answering "what exactly do I do in the next 30 minutes?"

4. Dependency and deferred behavior are present, but operationally thin.
- Current rules can set `Blocked`, `Deferred`, and `Backlog`.
- The design still needs a better human-readable model for when work activates, why it is blocked, and when it should stay deliberately inactive.

5. Review and recurring work are not yet as concrete as Project 1.
- Recurring work exists conceptually.
- It is not yet rendered with the same operational sharpness as daily/weekly review cards in Project 1.

## Project 1 patterns that must be imported

Project 1 should be treated as the reference for execution quality.

Patterns to import:
- `Phase -> Win Condition -> Concrete Work -> Daily Execution`
- at most three win conditions per phase
- outcome-first card design
- explicit `Next Action`
- evidence-based completion
- bounded date windows in titles
- exam days as single-day issues
- fewer simultaneous active cards

## Required target structure

The redesigned board must express all four layers below.

### 1. Phase card
- Represents the operating phase.
- Declares the mainline.
- Lists up to three win conditions.
- Explains what is intentionally de-emphasized.

### 2. Win condition card
- Represents a measurable mid-level outcome.
- Sits between phase and concrete work.
- Owns 2-5 concrete work cards.
- Has explicit completion evidence.

### 3. Concrete work card
- Small enough to finish in one week or 1-3 focused sessions.
- Describes exactly what to make, verify, and keep.
- Must be executable without opening the long plan docs.

### 4. Daily execution
- Lives in the issue body.
- Defines what to do today or in the next study block.
- Makes "do now", "do later", and "do not do yet" obvious.

## Required issue body design

For concrete work cards, require these sections:
- `Outcome`
- `Next Action`
- `Why this matters`
- `Device`
- `Inputs`
- `Things to make`
- `Work checklist`
- `Definition of Done`
- `Completion check`
- `Evidence to keep`
- `Blockers / dependencies`
- `Daily execution`
- machine-readable marker

For phase cards and win condition cards, use a lighter version, but still include:
- `Outcome`
- `Mainline`
- `What stays deferred`
- `Evidence`
- `Exit condition`

## Required field design

Keep current fields that are already useful:
- `Status`
- `Priority`
- `Area`
- `Phase`
- `Due Date`
- `Evidence Type`
- `Monthly Bucket`
- `Quarter`
- `Career Link`
- `AI Link`
- `Task Type`
- `Review Cycle`
- `Active Window`
- `Deferred Until`
- `Deferred Flag`
- `Blocked By`
- `DoD Ready`
- `Evidence Ready`
- `Exam Priority Guard`

Add or strongly consider adding these Project 1 style execution fields:
- `Start Date`
- `End Date`
- `Time Block`
- `Estimate`
- `Energy`
- `Focus`
- `Next Action`
- `Outcome`
- `Completion Check`

## Required seed redesign direction

Do not only enrich the existing 46 issue entries.

The redesign should:
- add `phase_cards`
- add `win_conditions`
- reclassify existing 46 issues as concrete work where appropriate
- split any issue that is still too large
- add `daily_execution` or equivalent execution slots for concrete work cards

Split rules:
- split if one issue spans multiple skills or knowledge clusters
- split if one issue would need more than three work steps
- split if one issue exceeds one week of realistic focus
- split if the first action cannot be started in five minutes
- split if completion cannot be checked by evidence

## Status and deferred behavior

The current `compute_status()` rule set is a good base, but redesign must explain the human-operational meaning of:
- `Blocked`
- `Deferred`
- `Backlog`
- `Todo`
- `In Progress`
- `Done`

It must also clarify:
- when exam-priority windows suppress non-mainline work
- how Denken cards stay intentionally inactive without disappearing
- how AI work stays supportive and does not steal the mainline
- how career prep activates only in the intended windows

## Non-negotiable constraints

- `data/project-seed.yaml` remains the only source of truth.
- `dry-run` must happen before `apply`.
- idempotency must be preserved.
- re-running must not create duplicates.
- sync logs and diff reports must remain.
- silent failure is not allowed.
- unrelated existing issues/items must not be touched.
- First-class exam priority must remain:
  - until 2026-04-27: 第一種電気工事士 学科 mainline
  - 2026-04-28 to 2026-07-04: 第一種電気工事士 実技 mainline
- Denken must remain manageable as backlog/deferred.
- AI learning must remain supportive, not dominant.

## Known environment facts

- Seed meta currently points to `forui/my-app`.
- Actual Git remote and live sync target are `foru1215/shared-auto-sync`.
- Existing managed project is [Project 4](https://github.com/users/foru1215/projects/4).
- Existing managed issues/items already exist and must be migrated, not blindly recreated.

## What Claude Code should output

Claude Code should produce a concrete redesign proposal with:
1. investigation summary
2. evaluation of current implementation
3. prioritized problems
4. proposed target information model
5. phase/win-condition/work-item hierarchy design
6. issue body templates
7. project field design
8. completion criteria and completion check design
9. dependency / deferred / recurring rules
10. migration strategy from current Project 4
11. validation and audit plan
12. testing plan
13. implementation steps
14. known constraints and tradeoffs

## Most important instruction

Do not answer with "add more metadata" only.

The redesign succeeds only if opening a card makes these obvious:
- what to do now
- what not to do yet
- what counts as done
- what evidence to keep
- what to do today if time is limited
