# Project 1 Reference Notes

## Source
- Reference project: [foru1215 Project 1](https://github.com/users/foru1215/projects/1)
- Read with:
  - `gh project view 1 --owner foru1215 --format json`
  - `gh project field-list 1 --owner foru1215 --format json`
  - `gh project item-list 1 --owner foru1215 --limit 200 --format json`

## Principles confirmed in Project 1
- Mainline is always one thing at a time.
- Each phase has at most three win conditions.
- Progress is measured by outcomes and evidence, not by "I touched it".
- Structure is `Phase -> Win Condition -> Concrete Work`.
- Card title prefixes include a bounded date window.
- Exam days are represented as single-day issues.

Project readme on 2026-03-14 explicitly said:
- `主役は常に1つだけ`
- `Phaseごとの勝ち条件は3つ以内`
- `進捗は成果物で測る`
- `構造は Phase epic -> 勝ち条件 -> 具体作業`

## Fields observed in Project 1

Built-in and custom fields visible from `gh project field-list`:
- `Status`
- `開始日`
- `終了日`
- `作業時間(h)`
- `実績時間(h)`
- `Time Block`
- `DayType`
- `Domain`
- `Phase`
- `Estimate`
- `Energy`
- `Focus`
- `Next Action`
- `Outcome`
- `Due`
- Built-ins such as `Parent issue` and `Sub-issues progress`

## Card body pattern observed in Project 1

The issue bodies were not generic notes. They were execution-oriented. Common sections were:
- `Outcome（完了条件）`
- `Next Action（5分で開始できる最初の一手）`
- `Device`
- `進め方（推奨順）`
- `タスクリスト`
- `成果の証跡（Doneにするとき記入）`
- `日次実行`

This is the key difference from the current repo. Current synced issues already have `Summary / Work steps / Definition of Done`, but Project 1 goes one step deeper:
- You can open a card and begin immediately.
- You can tell what "done" looks like without interpretation.
- You can tell what to do today, not just this month.

## What should be imported into this repo

The current 24-month board should adopt the same granularity pattern:

1. `Phase card`
- Represents the major operating window.
- Has at most three win conditions.
- Explains what becomes the mainline during that phase.

2. `Win condition card`
- Mid-level outcome under a phase.
- Defines what must become true.
- Owns 2-5 concrete work issues.

3. `Concrete work issue`
- Small enough to finish in 1 to 3 study sessions or within one week.
- Must include `Outcome`, `Next Action`, `Completion Check`, and `Evidence`.
- Must be understandable without opening the plan docs.

4. `Daily execution`
- Lives in the body of the concrete work issue.
- Gives day-by-day or session-by-session execution instructions.
- Makes it obvious what to do today and what to defer.

## Translation rules for this repo

Use the following rules when refining `data/project-seed.yaml`:
- If one issue covers multiple knowledge clusters, split it.
- If one issue would need more than three work steps, split it.
- If one issue would remain active longer than one week, split it unless it is a phase or win condition card.
- If "done" cannot be judged with a visible artifact, rewrite the issue.
- If the first action cannot be started in five minutes, rewrite the issue.

## Required body sections for refined cards

Every concrete work issue should be able to render the following sections:
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

## Fields worth importing directly

These should be considered first-class project fields in this repo:
- `Start Date`
- `End Date`
- `Time Block`
- `Estimate`
- `Energy`
- `Focus`
- `Next Action`
- `Outcome`

They do not replace the existing fields such as `Priority`, `Area`, `Phase`, `Deferred Flag`, and `Blocked By`. They add the execution layer that is currently missing.

## Recommended title granularity

Titles should signal bounded work. Examples:
- `[26/03/14-03/20] [電工] 学科: 高圧受電設備の白紙再現`
- `[26/03/14-03/20] [電工] 学科: 保護継電器の役割説明`
- `[26/04/12] [Exam] 第一種電気工事士 学科本番`

## Most important takeaway

Do not stop at "richer metadata". Project 1 works because the board is executable:
- what to do
- what not to do
- what counts as done
- what evidence to keep
- what to do today

That execution quality is what this repo now needs.
