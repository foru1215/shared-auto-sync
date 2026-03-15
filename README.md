# shared-auto-sync

このリポジトリは 2 つの用途を兼ねています。

1. **SKK 案件管理** — 制御盤 / 設備案件の見積・提案・受注管理
2. **GitHub Project Sync** — 24 か月転職計画の進捗管理 ([Project #4](https://github.com/users/foru1215/projects/4))

---

## SKK — 案件管理

### 運用ルール

#### 1. Googleカレンダー ＝ タスクのみ
- **時間枠・リマインド・予定だけ**を管理する
- 金額・反応・提出証跡は**書かない**（GitHubに集約）
- イベントタイトル規約：`<案件ID> | <種別> | <短い内容>`

| 種別例 | イベントタイトル例 |
|--------|-------------------|
| 見積作成 | `Q12345 \| 見積作成 \| 60m` |
| 見積提出 | `Q12345 \| 見積提出 \| v2送付` |
| 先方回答確認 | `Q12345 \| 先方回答確認 \| 15m` |
| 現地立会 | `Q12345 \| 現地立会 \| I/O確認` |
| 社内確認 | `Q12345 \| 社内確認 \| 部長承認` |
| 手配 | `J67890 \| 手配 \| 盤発注` |

#### 2. GitHub ＝ 案件台帳の正
- **案件1件 ＝ Issue 1枚**
- 状態・履歴・金額・先方反応はすべてIssueに集約する
- Issueタイトル規約：`<案件ID> <顧客略号> <案件名>`（例：`Q12345 A社 盤改造見積`）

#### 3. Statusの正は Project（SKK）
- **Project の Status フィールドが唯一の正**
- Issue本文にステータスを重複管理しない（参照のみ）
- Status値：Backlog → Estimating → Submitted → Re-submitting → Waiting Reply → On-site → Won / Lost / On Hold

#### 4. 更新は最低限「3点だけ」
案件に動きがあったら：

1. **Issue本文にログ追記**（提出 / 回答 / 立会）
2. **ProjectのStatus更新**
3. **Due & Last Action 更新**（必要なら Amount Latest / Submitted At / Quote Ver / Reply Summary も更新）

#### 5. ラベル運用
| ラベル | 用途 |
|--------|------|
| `type:quote` | 見積案件 |
| `type:onsite` | 現地立会あり |
| `type:customer-reply` | 先方回答待ち / 回答あり |
| `type:internal` | 社内タスク |
| `priority:high` | 高優先 |
| `priority:mid` | 中優先 |
| `priority:low` | 低優先 |

**テンプレート:** Issues → New Issue → 「案件台帳」テンプレートを選択して作成する。

---

## GitHub Project Sync

`data/project-seed.yaml` is the source of truth for the 24-month career plan sync.

### What it does

- Reads labels, milestones, epics, issues, and project fields from `data/project-seed.yaml`
- Reads layered planning entities from seed:
  - `epics`
  - `phase_cards`
  - `win_conditions`
  - `issues`
- Validates that every managed item has task type, outcome, next action, completion check, daily execution, active window, and dependency metadata
- Creates a dedicated GitHub Project and links it to the detected repository
- Syncs managed labels, milestones, issues, project items, and field values
- Computes status from deferred window, active window, dependency blockers, exam-priority windows, and due date
- Audits plan quality before sync so missing DoD or evidence requirements are visible
- Writes dry-run and apply reports under `data/sync-reports/`
- Uses a machine-readable marker in managed issue bodies so reruns stay idempotent

### Setup

```powershell
python -m pip install -r requirements.txt
gh auth status
```

Required GitHub scopes:

- `repo`
- `project`

### Validate seed

```powershell
python scripts/github_project_sync.py --validate
```

### Audit plan quality

```powershell
python scripts/github_project_sync.py --audit --today 2026-03-15
```

### Dry-run

```powershell
python scripts/github_project_sync.py --today 2026-03-15 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
```

### Apply sync

```powershell
python scripts/github_project_sync.py --apply --today 2026-03-15 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
```

### Re-sync flow

```powershell
python scripts/github_project_sync.py --validate
pytest -q
python scripts/github_project_sync.py --audit --today 2026-03-15
python scripts/github_project_sync.py --today 2026-03-15 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
python scripts/github_project_sync.py --apply --today 2026-03-15 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
python scripts/github_project_sync.py --today 2026-03-15 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
```

### Notes

- Managed issues are matched by an embedded sync marker first, then by exact title as a fallback.
- Existing unrelated issues in the repository are left untouched.
- The current implementation syncs epics as managed GitHub issues titled `[Epic] ...`.
- Phase cards are synced as `[PHASE] ...` issues.
- Win-condition cards are synced as `[WIN] ...` issues.
- Project field option updates are supported for single-select fields, including `Status`.
- Status is computed from six rules: deferred window, active window, blockers, exam-priority guard, due-date window, fallback backlog.
- Morning focus notifications run daily at 07:00 JST via `.github/workflows/morning-focus.yml`.
