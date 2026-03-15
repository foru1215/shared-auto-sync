# GitHub Projects 同期基盤 再設計案

**作成日**: 2026-03-14
**対象スクリプト**: `scripts/github_project_sync.py`
**正本**: `data/project-seed.yaml`
**同期先**: `foru1215/shared-auto-sync` (Project #4)

---

## 1. 調査結果

### 現状の稼働状態（2026-03-14 時点）

| 項目 | 状態 |
|------|------|
| 同期先リポジトリ | `foru1215/shared-auto-sync` |
| Project | `Career Transition 24-Month Plan` (Project #4) |
| Labels | 21件 (noop 確認済み) |
| Milestones | 9件 (noop 確認済み) |
| Managed Issues | 53件 (Epic 7 + Seed 46) (noop 確認済み) |
| Project Items | 53件 (noop 確認済み) |
| Field Values | 636件 (noop 確認済み) |
| Idempotency | 確認済み (2回実行で全 noop) |

### 現スクリプトの骨格

- 言語: Python 3 + `gh` CLI + `gh api graphql`
- Idempotency キー: `seed_id` + `entity_kind` + `fingerprint` (HTML comment marker)
- Status 推論: `due_date` が `DATE_WINDOW_DAYS`(45日) 以内 → `Todo`、それ以外 → `Backlog`
- フィールド: seed 定義 10個 + スクリプト追加 2個 (Task Type, Review Cycle) = 計 12個
- レポート: タイムスタンプ付き JSON + Markdown、`latest_*` コピーあり

### 発見した不一致

- `meta.owner/repo` = `forui/my-app`、Git remote = `foru1215/shared-auto-sync` → warning 出力のみで apply は続行
- `DATE_WINDOW_DAYS = 45` が唯一の Status 判定基準になっている
- `dependencies.backlog_until` の値が Status/Field に全く反映されていない

---

## 2. 現実装の評価

### 良い点 ✅

| 項目 | 評価 |
|------|------|
| seed → GitHub の同期経路 | 確立済み、動いている |
| Idempotency (marker ベース) | seed_id + fingerprint で重複防止、再実行安全 |
| dry-run → apply フロー | 基本フローはある |
| unrelated issue の非破壊 | 既存 unrelated issue を触らない |
| レポート出力 | JSON + Markdown、タイムスタンプ付き保存 |
| UTF-8 で tempfile 経由 | PowerShell との文字化け軽減対応あり |

### 問題のある点 ❌

| # | 問題 | 深刻度 |
|---|------|--------|
| A | issue 本文が seed body そのまま（作業手順・完了条件なし） | **高** |
| B | Definition of Done が issue に存在しない | **高** |
| C | Status が due_date 近接のみで決まる（dependency/backlog 無視） | **高** |
| D | `backlog_until` が Status/Field に反映されていない | **高** |
| E | dependency が blocked 状態として board に現れない | **高** |
| F | 不足 Field が多い (Active Window / Deferred Until / Blocked By 等) | **中** |
| G | recurring task の運用設計が未確定 | **中** |
| H | audit / quality-check コマンドがない | **中** |
| I | target repo 不一致が warning 止まりで apply を止めない | **中** |
| J | テストがゼロ | **低〜中** |
| K | レポートが「操作ログ」のみで「運用判断要約」がない | **低** |

---

## 3. 問題点の優先順位

### P0（今すぐ解決が必要・board が使えない）

1. **Status 推論の再設計** — `backlog_until` / `activate` / dependency block を Status に反映しないと、電験三種や転職準備が「今やるべきタスク」に見えてしまう
2. **issue 本文テンプレート** — issue を開いたときに「今日何をすればよいか」が分からない
3. **完了条件 (DoD) の設計** — 「完了にしてよいか」の判断基準がない

### P1（次に解決・運用品質）

4. **dependency → blocked 反映** — 依存先が未完了の issue を Blocked と表示する
5. **不足 Field の追加** — `Deferred Until` / `Active Window` / `Blocked By` / `DoD Ready` / `Evidence Ready`
6. **recurring task の運用設計** — template vs. instance の明確化

### P2（品質向上・保守）

7. **audit コマンドの設計**
8. **target repo 判定の明確化**
9. **テスト方針**
10. **レポートの運用判断要約**

---

## 4. 再設計方針

### 基本哲学

> **board を見れば「今日やること」と「今やってはいけないこと」が即座に分かる**

これを実現するための3つの原則：

1. **Status は機械的に決まる** — 日付近接ではなく、「phase / dependency / backlog_until / exam_priority_guard の組み合わせ」で一意に決まる
2. **issue 本文は実行仕様書** — 開いたその場で着手でき、完了の判断ができる
3. **seed が唯一の正本** — 手動で GitHub 上を編集しても次の apply で seed の状態に戻る

### 変更しないもの

- `gh` CLI + Python の実装方針
- marker による idempotent 管理（`seed_id` + `fingerprint`）
- dry-run → apply フロー
- レポートの保存先・形式

### 変更するもの

- issue 本文テンプレート（構造化）
- Status 推論ロジック（5段階 → ルールベース）
- Project Field の追加（5〜6 fields 追加）
- seed YAML の拡張（`task_type`, `dod`, `work_steps`, `exam_priority_guard` の追加）
- recurring task の扱い（template + instance 生成の分離）
- audit サブコマンドの追加
- target 判定の明確化（`--strict-target` フラグ）

---

## 5. データモデル案

### seed YAML の拡張項目

現在の issue エントリに以下のキーを追加する。

```yaml
issues:
  - id: "ISS-001"
    title: "..."
    body: "..."           # 既存: 1行の概要（Summary に使う）
    epic: "E-LIC"
    phase: "phase-0"
    labels: [...]
    priority: "p0"
    milestone: "M-2026-Q2"
    due_date: "2026-04-27"
    recurring: false
    dependencies: []
    evidence_type: "Certification"
    monthly_bucket: "2026-04"
    quarter: "2026-Q2"
    career_link: "..."
    ai_link: ""

    # ===== 追加項目 =====
    task_type: "exam"           # enum: exam / study / plc / evidence / ai / career / review / deliverable
    work_steps:                 # 具体的な作業ステップ（箇条書き）
      - "過去問5年分を入手する（市販テキスト or PDF）"
      - "1年分を時間計測で解き、正答率を記録する"
      - "正答率 70% 未満の分野を特定し、翌週の集中テーマに設定する"
    deliverables:               # 完了時に手元に残るもの
      - "正答率記録シート（GitHub Issue コメントに貼る）"
    evidence_to_keep:           # GitHub / ローカルに残す証跡
      - "正答率スクリーンショット or CSV を Issue コメントに添付"
    dod:                        # Definition of Done（完了条件リスト）
      - "過去問5年分を入手している"
      - "最低1年分を解いて正答率を記録している"
      - "苦手分野が1つ以上特定できている"
    exam_priority_guard: true   # true = 試験期間中は他タスクより上位に表示
    active_from: "2026-03-14"   # この日付以降にのみ Todo に昇格する
    deferred_until: null        # null = 即時 active。日付文字列 = その日まで Backlog 固定
    blocked_by: []              # blockers の seed_id リスト（dependencies と同義、field 反映用）
    review_note: ""             # 週次/月次レビュー時のメモ欄（テンプレート用）
```

### task_type 定義

| task_type | 説明 | 完了チェックのポイント |
|-----------|------|----------------------|
| `exam` | 試験対策・受験 | 正答率記録、受験記録 |
| `study` | 資格以外の学習（制御・図面・PLC） | ノート完成、セルフテスト |
| `plc` | PLC 課題 | コード動作確認、GitHub commit |
| `evidence` | 実務証拠の作成 | 文書の存在、内容の確認 |
| `ai` | AI ツール学習・成果物作成 | 動作確認、リポジトリへのコミット |
| `career` | 転職準備 | 文書の完成、提出可能な品質 |
| `review` | 週次/月次/四半期レビュー | レビューコメントの投稿 |
| `deliverable` | 成果物の最終仕上げ | 成果物の公開 or 提出可能な状態 |
| `setup` | 環境構築・初期設定 | 動作確認コマンドの成功 |

### deferred_until と active_from の使い分け

| 項目 | 意味 | 例 |
|------|------|-----|
| `active_from` | この日以前は Backlog 固定 | 制御基礎 → `2026-07-05`（実技試験翌日） |
| `deferred_until` | この日まで Backlog 固定。null = 制約なし | 電験三種 → `2026-12-31` |
| `deferred_until` が `active_from` より後 | `deferred_until` 優先 | — |

**具体的な設定例：**

```yaml
# 電験三種（2026-12-31 まで Backlog 強制）
- id: "ISS-025"
  title: "[E-LIC] 2027-01: 電験三種 理論科目 入門学習開始"
  deferred_until: "2026-12-31"
  active_from: "2027-01-01"
  exam_priority_guard: false

# Phase 2 の制御基礎（実技試験翌日から active）
- id: "ISS-011"
  title: "[E-CTL] 2026-07: 制御基礎ノート 第1章"
  deferred_until: null
  active_from: "2026-07-05"
  exam_priority_guard: false

# 学科試験（即時 active、試験優先ガード）
- id: "ISS-005"
  title: "[E-LIC] 2026-04: 学科試験 過去問5年分×2周"
  deferred_until: null
  active_from: "2026-03-14"
  exam_priority_guard: true
```

---

## 6. Project Field 設計案

### 現在の 12 Fields（維持）

| Field 名 | 型 | 値 |
|----------|----|----|
| Status | SingleSelect | Backlog / Todo / In Progress / Done / Blocked / Deferred |
| Priority | SingleSelect | P0 / P1 / P2 |
| Area | SingleSelect | License / Control / PLC / Drawings / Practice / Evidence / AI / Career |
| Phase | SingleSelect | Written Exam / ... |
| Due Date | Date | — |
| Evidence Type | SingleSelect | Note / Code / Document / Certification / Portfolio / Story |
| Monthly Bucket | Text | 2026-03 ～ 2028-03 |
| Quarter | SingleSelect | 2026-Q1 ～ 2028-Q1 |
| Career Link | Text | — |
| AI Link | Text | — |
| Task Type | SingleSelect | exam / study / plc / evidence / ai / career / review / deliverable / setup |
| Review Cycle | SingleSelect | weekly / monthly / quarterly / none |

### 追加する 6 Fields

| Field 名 | 型 | 値 | 用途 |
|----------|----|----|------|
| **Active From** | Text | YYYY-MM-DD | この日以降に Todo 昇格できる |
| **Deferred Until** | Text | YYYY-MM-DD or "—" | この日まで Backlog 強制 |
| **Blocked By** | Text | "ISS-XXX, ISS-YYY" or "—" | blockers の列挙 |
| **DoD Ready** | SingleSelect | ✅ Done / 🔲 Not yet / ➖ N/A | DoD チェックが全て通過したか |
| **Evidence Ready** | SingleSelect | ✅ Ready / 🔲 Missing / ➖ N/A | 証拠が揃っているか |
| **Exam Guard** | SingleSelect | 🔴 Exam Priority / ➖ Normal | 試験優先期間の識別 |

### field で持つか本文テンプレートで持つかの方針

| 情報 | 配置 | 理由 |
|------|------|------|
| Status / Priority / Phase / Area | Field | board でのソート・フィルタに使う |
| Active From / Deferred Until | Field (Text) | audit スクリプトが読める |
| Blocked By | Field (Text) | board でのフィルタ（Blocked = "ISS-xxx を含む"）|
| DoD Ready / Evidence Ready | Field (SingleSelect) | board で完了判定の状況を一覧できる |
| 作業ステップ / DoD リスト | 本文テンプレート | 詳細は issue を開いて確認 |
| Review Note | 本文テンプレート（空欄） | レビュー時に人間が記入 |

---

## 7. Issue 本文テンプレート案

managed issue の body を以下の構造に統一する。

```markdown
## Summary

{body の1行概要}

---

## Why this matters

{phase の目的と、この issue がそこにどう貢献するか。career_link / ai_link を含める。}

---

## Work steps

- [ ] {work_steps[0]}
- [ ] {work_steps[1]}
- [ ] {work_steps[2]}
...

---

## Deliverables

{deliverables の箇条書き}

---

## Evidence to keep

{evidence_to_keep の箇条書き。Evidence Type: {evidence_type}}

---

## Definition of Done

- [ ] {dod[0]}
- [ ] {dod[1]}
- [ ] {dod[2]}
...

> **Completion check**: 上記の全チェックが完了し、Evidence to keep の証跡が残ったとき、この issue を Close してよい。

---

## Dependencies

{dependencies が空なら "None" と表示。}
{依存 issue がある場合: "Blocked by: #{github_issue_number} ({seed_id}: {title})"}

---

## Timing

- **Active from**: {active_from}
- **Deferred until**: {deferred_until or "—"}
- **Due date**: {due_date or "—"}
- **Phase**: {phase}
- **Monthly bucket**: {monthly_bucket}

---

## Review note

> *(このコメント欄は週次/月次レビュー時に記入する)*

---

<!-- github-project-sync: {"seed_id": "{seed_id}", "entity_kind": "{entity_kind}", "fingerprint": "{fingerprint}", "source": "data/project-seed.yaml"} -->
```

### task_type ごとの差分

各 task_type はデフォルトテンプレートに加えて以下の section を追加する。

| task_type | 追加 section |
|-----------|-------------|
| `exam` | **Exam info** — 試験日・会場・持ち物・正答率目標 |
| `study` | **Self-test** — 口頭で説明できるかのセルフチェック問 |
| `plc` | **Acceptance criteria** — シミュレータで〇〇の動作を確認すること |
| `evidence` | **Evidence format** — どの形式で何をどこに保存するか |
| `review` | **Review checklist** — 週次/月次レビューの標準観点リスト |
| `deliverable` | **Delivery gate** — 完成の定義・公開方法 |

### Epic 本文テンプレート

```markdown
## Epic: {name}

{description}

---

## Scope

このエピックに含まれる issue（自動更新）:
- {月次ロードマップからの抜粋}

## Success criteria

{phases から抜粋した success_criteria}

---

<!-- github-project-sync: {"seed_id": "{id}", "entity_kind": "epic", ...} -->
```

---

## 8. Completion Criteria / Completion Check 設計案

### 完了の3段階定義

```
Stage 1: Work done    → Work steps の全チェックボックスが完了
Stage 2: Evidence     → Evidence to keep の証跡が残っている
Stage 3: DoD passed   → Definition of Done の全項目を確認

3段階全てが通過したとき、DoD Ready = ✅ Done とし、issue を Close してよい。
```

### DoD チェックの実行方法

**人間によるチェック（標準）**:
1. issue を開く
2. Work steps のチェックボックスにチェックを入れる
3. Evidence to keep のものを添付 or コメントに記録する
4. Definition of Done リストを上から確認し、全てチェック
5. Field: `DoD Ready` を `✅ Done` に変更
6. Field: `Evidence Ready` を `✅ Ready` に変更
7. Issue を Close

**`audit` コマンドによる機械チェック**:
- Close 済みで `DoD Ready != ✅ Done` の issue を検出 → warning
- `evidence_type != ""` なのに `Evidence Ready == 🔲 Missing` の issue を検出 → warning
- Phase が試験期なのに `exam_priority_guard != true` の P0 以外タスクが In Progress → warning

### task_type ごとの完了条件早見表

| task_type | 最低完了条件 |
|-----------|------------|
| `exam` | 受験記録 or 正答率記録をコメントに投稿済み |
| `study` | ノートファイルが GitHub にコミット済み |
| `plc` | ラダー図コードが GitHub にコミット済み、動作確認済み |
| `evidence` | 文書が存在し、面接で語れる内容が書かれている |
| `ai` | 成果物が GitHub にコミット済み、動作確認済み |
| `career` | 文書の draft が完成し、提出可能な品質 |
| `review` | レビューコメントを issue に投稿済み |
| `deliverable` | 公開 URL または提出先が記録済み |

---

## 9. Dependency / Deferred / Recurring 運用案

### 9-1. Dependency (Blocked By) の見える化

#### seed 側の定義

```yaml
issues:
  - id: "ISS-020"
    dependencies: ["ISS-014"]   # 既存キー
    blocked_by: ["ISS-014"]     # 新規: field 反映用（同一内容でよい）
```

#### Status 推論ルール（優先順）

```
Rule 1: deferred_until が今日以降 → Status = "Deferred"
Rule 2: active_from が今日以降 → Status = "Backlog"
Rule 3: blocked_by の issue が全て Closed でない → Status = "Blocked"
Rule 4: phase が exam priority 期間 & exam_priority_guard = false → Status = "Backlog"
Rule 5: due_date が 45 日以内 → Status = "Todo"
Rule 6: due_date が 45 日超 or なし → Status = "Backlog"
```

このルールを `compute_status()` 関数に実装し、既存の `DATE_WINDOW_DAYS` ベースの判定を置き換える。

#### board でのフィルタ方法

- `Status = Blocked` でフィルタ → 依存待ちの issue 一覧
- `Blocked By` が "ISS-009" を含む → ISS-009（実技試験）の完了を待っているもの

### 9-2. Deferred / Backlog の見える化

#### Deferred vs Backlog の違い

| Status | 意味 | 操作可否 |
|--------|------|---------|
| **Deferred** | seed の `deferred_until` ルールにより意図的に封印 | 手動で変更しない |
| **Backlog** | まだ時期でないが、unblock されれば Todo に進める | 手動で Todo に変更 OK |

#### board でのカラム設計（推奨）

```
カラム1: Deferred   ← 電験三種、転職準備 (2027/1 まで)
カラム2: Backlog    ← 時期待ち・依存待ち
カラム3: Blocked    ← 依存未完了
カラム4: Todo       ← 今月・来月着手予定
カラム5: In Progress ← 現在進行中
カラム6: Done       ← 完了
```

#### re-sync 時の自動切替

seed を変更せずとも、sync スクリプトが実行日時点で `deferred_until` / `active_from` を評価して Status を自動更新する。

```
毎週日曜の週次レビュー後に sync を実行すれば、
翌週 active になるタスクが自動で Backlog/Todo に昇格する。
```

### 9-3. Recurring Task の運用設計

#### 設計判断

現在の 4種のルーティンタスク：
- `ISS-R01` 週次レビュー
- `ISS-R02` 月次レビュー
- `ISS-R03` 四半期レビュー
- `ISS-R04` 技術メモ（月1件）

**採用する方式: Template + Instance 生成の分離**

| 方式 | 採用理由 |
|------|---------|
| **Template issue を常設** (現行維持) | 手順・完了条件の参照先として維持 |
| **Instance issue を月頭に生成** (新規追加) | GitHub の「今月のタスク」として追跡可能 |
| GitHub Actions は使わない | 外部依存を増やさない。sync スクリプトで足りる |

#### Instance 生成ルール

```yaml
# seed での定義（ISS-R01）
- id: "ISS-R01"
  recurring: "weekly"
  # weekly の場合: instance は生成しない（template として置く）
  # monthly の場合: sync 時に当月 instance を生成
  # quarterly の場合: sync 時に当四半期 instance を生成
```

**月次/四半期 recurring の instance 命名ルール**:
- `[Review] 2026-04 月次レビュー` (seed_id: `ISS-R02-2026-04`)
- `[Review] 2026-Q2 四半期レビュー` (seed_id: `ISS-R03-2026-Q2`)

**週次 recurring の扱い**:
- template issue (`ISS-R01`) を常設し、毎週使い回す
- 週次は instance を作ると 100件以上になるので作らない
- 代わりに issue のコメント欄に週次レビュー記録を積み上げる

#### Instance 生成のロジック概要

```python
def expand_recurring_issues(issues, today):
    expanded = []
    for issue in issues:
        if issue.recurring == "monthly":
            # 当月の instance が存在しなければ追加
            bucket = today.strftime("%Y-%m")
            instance_id = f"{issue.id}-{bucket}"
            if not instance_exists(instance_id):
                expanded.append(make_instance(issue, instance_id, bucket))
        elif issue.recurring == "quarterly":
            quarter = get_quarter(today)
            instance_id = f"{issue.id}-{quarter}"
            if not instance_exists(instance_id):
                expanded.append(make_instance(issue, instance_id, quarter))
        # weekly はテンプレートのみ残す
    return expanded
```

---

## 10. Dry-run / Apply / Audit フロー

### 10-1. コマンド体系（再設計後）

```
python scripts/github_project_sync.py            # dry-run (デフォルト)
python scripts/github_project_sync.py --apply    # apply
python scripts/github_project_sync.py --audit    # 運用品質チェック
python scripts/github_project_sync.py --validate # seed YAML のバリデーションのみ
```

オプション:
```
--seed PATH         # seed ファイルパス指定 (default: data/project-seed.yaml)
--owner OWNER       # リポジトリオーナー override
--repo REPO         # リポジトリ名 override
--project-owner     # Project オーナー override
--strict-target     # meta と git remote の不一致時に abort
--today DATE        # テスト用: 今日の日付を指定 (YYYY-MM-DD)
```

### 10-2. dry-run の仕様

```
dry-run フロー:
1. seed YAML を読み込み (validate して fail させる項目あり)
2. 今日の日付 + deferred_until + active_from + dependencies で Status を計算
3. GitHub の現状 (labels / milestones / issues / fields) を読み込む
4. 差分 (create / update / noop) を計算する
5. レポート出力 (JSON + Markdown)
6. GitHub には一切書き込まない

dry-run レポートに含める情報:
- 現在のフェーズ判定（今日の日付基準）
- Status が変化する issue のリスト
- Deferred → Backlog に昇格する issue（active_from 到達）
- Blocked → Todo に昇格する issue（依存完了）
- 欠損フィールド件数（audit サマリとして表示）
```

### 10-3. apply の仕様

```
apply フロー:
1. dry-run と同じ差分計算
2. dry-run レポートを出力
3. "以下の変更を適用します。続行しますか? [y/N]" (--yes フラグで省略可)
4. 以下の順序で実行:
   a. labels (create / update)
   b. milestones (create / update)
   c. epics (create / update)
   d. seed issues (create / update)
      - recurring instance の生成
   e. Project の確認・作成
   f. Project items の追加
   g. Project field values の設定
5. apply レポート出力 (JSON + Markdown)

冪等性の保証:
- 全操作は seed_id + fingerprint で重複チェック
- fingerprint = SHA256(title + body + labels + milestone + field_values)
- fingerprint が変わらない → noop
- fingerprint が変わった → update (issue body / label を上書き)
- 新規 seed_id → create
```

### 10-4. audit の仕様（新規追加）

```
audit フロー:
1. seed YAML と GitHub の現状を読み込む
2. 以下のルールで問題を検出する
3. レポートを data/sync-reports/<timestamp>_audit.md に出力

audit チェックルール:
[FAIL] seed_id がない managed issue が存在する
[FAIL] required フィールド（due_date / milestone / phase / area）が欠損
[FAIL] deferred_until が過去なのに Status が Deferred のまま
[FAIL] active_from が到達済みなのに Status が Backlog のまま
[FAIL] blocked_by の依存が全て Close 済みなのに Status が Blocked
[WARN] exam 期間中に exam_priority_guard = false の P0 issue が In Progress
[WARN] evidence_type != "" なのに Evidence Ready = 🔲 Missing で Close 済み
[WARN] Due date が過去 14 日以上超過しているのに Done でない
[WARN] DoD が未定義（dod: []）の非 review タスク
[WARN] dependency の blocker が存在しない seed_id を参照
[INFO] deferred 件数の現状サマリ
[INFO] 電験三種 issue の現状（deferred / backlog / active）
[INFO] 試験優先ガード中の issue 件数
```

### 10-5. validate の仕様（新規追加）

```
validate フロー:
seed YAML のみを読み込み、構造チェックを実行する。GitHub API は叩かない。

[FAIL] 必須キーの欠損 (id, title, epic, phase, labels, priority)
[FAIL] task_type が enum 外の値
[FAIL] deferred_until / active_from が YYYY-MM-DD 形式でない
[FAIL] dependencies で参照している seed_id が存在しない
[FAIL] milestone が milestones リストに存在しない
[FAIL] epic が epics リストに存在しない
[WARN] dod が空配列
[WARN] work_steps が空配列
[WARN] evidence_type != "" なのに evidence_to_keep が空
```

---

## 11. 既存 Project からの移行案

### 現状

- Project #4 が稼働済み（53件の managed issue、636件の field value）
- 全 issue に `<!-- github-project-sync: {...} -->` marker が埋め込み済み

### 方針選択

**採用: 既存 Project をそのまま migrate（新規 Project は作らない）**

理由:
- Project #4 の URL (`https://github.com/users/foru1215/projects/4`) がすでに定着している
- 53件の issue に marker が埋め込まれており、fingerprint 更新で上書きできる
- 新規 Project を作ると field 設定・item 追加の作業が二重になる

### 移行手順

**Step 1: seed YAML の拡張（ローカル作業）**

```
1. 各 issue に以下を追加:
   - task_type
   - work_steps
   - deliverables
   - evidence_to_keep
   - dod
   - exam_priority_guard
   - active_from
   - deferred_until
   - blocked_by

2. 電験三種 関連 issue に deferred_until: "2026-12-31" を設定
3. 転職準備 関連 issue に deferred_until: "2027-10-31" を設定
4. AI スペシャリスト関連 issue に deferred_until: "2027-09-30" を設定
```

**Step 2: validate で先行チェック**

```powershell
python scripts/github_project_sync.py --validate
```

エラーが出なければ次へ。

**Step 3: field 追加の dry-run**

```powershell
python scripts/github_project_sync.py
# → レポートで 6 fields の create が表示されることを確認
```

**Step 4: apply**

```powershell
python scripts/github_project_sync.py --apply
# → 6 fields 追加 + 全 issue の body 更新（fingerprint 変更で update）
```

**Step 5: 2回目の dry-run で全 noop 確認**

```powershell
python scripts/github_project_sync.py
# → 全 noop を確認
```

**Step 6: audit で品質確認**

```powershell
python scripts/github_project_sync.py --audit
# → FAIL がゼロであることを確認
```

### rollback 方針

apply は GitHub の状態を更新するが、rollback は以下で対応する：

| ロールバック対象 | 方法 |
|----------------|------|
| Field 追加のロールバック | Project の Settings から手動削除（Issue には影響なし）|
| Issue body の巻き戻し | seed の `work_steps / dod` を削除して再 apply |
| Status の巻き戻し | seed の `active_from / deferred_until` を元に戻して再 apply |
| Issue の削除 | managed issue は Close のみ（削除は行わない） |

> **重要**: apply は Issue の Close / Delete を行わない。Status の変更と body の更新のみ。

---

## 12. テスト方針

### テストの目的

- スクリプトが seed 変更後に期待通りの差分を出すことの確認
- idempotency の保証
- Status 推論ロジックの正確性
- audit ルールの正確性

### テスト構成（推奨）

```
tests/
├── unit/
│   ├── test_status_compute.py      # Status 推論ロジック
│   ├── test_seed_validate.py       # YAML バリデーション
│   ├── test_fingerprint.py         # fingerprint の決定論性
│   ├── test_body_template.py       # issue 本文テンプレート生成
│   └── test_audit_rules.py         # audit ルールの各条件
├── integration/
│   ├── test_idempotency.py         # モック GitHub API で 2回実行 noop 確認
│   └── test_dry_run_snapshot.py    # dry-run の出力スナップショット
└── fixtures/
    ├── seed_minimal.yaml           # 最小構成の seed
    ├── seed_with_deferred.yaml     # deferred を含む seed
    └── seed_with_blocked.yaml      # blocked を含む seed
```

### 単体テストの優先順

1. **`test_status_compute.py`** — Status 推論の 6 ルールを全てテスト（最優先）
2. **`test_seed_validate.py`** — required キー欠損・enum 外値・参照不整合
3. **`test_audit_rules.py`** — FAIL / WARN 条件を各1ケース

### test_status_compute.py のテストケース例

```python
def test_deferred_until_future():
    """deferred_until が今日より後 → Deferred"""
    assert compute_status(deferred_until="2030-01-01", today="2026-03-14") == "Deferred"

def test_active_from_future():
    """active_from が今日より後 → Backlog"""
    assert compute_status(active_from="2027-01-01", today="2026-03-14") == "Backlog"

def test_blocked():
    """blocked_by に未 Close の issue がある → Blocked"""
    assert compute_status(blocked_by=["ISS-009"], closed_ids=set()) == "Blocked"

def test_exam_priority_guard():
    """試験期間中 & exam_priority_guard = False → Backlog"""
    assert compute_status(exam_priority_guard=False, in_exam_period=True) == "Backlog"

def test_due_within_window():
    """due_date が 45 日以内 → Todo"""
    assert compute_status(due_date="2026-04-27", today="2026-03-14") == "Todo"

def test_due_outside_window():
    """due_date が 45 日超 → Backlog"""
    assert compute_status(due_date="2027-01-01", today="2026-03-14") == "Backlog"
```

### GitHub API のモック方針

- `run_command` / `gh_api_json` を `unittest.mock.patch` でモック
- fixture 用の JSON レスポンスを `tests/fixtures/` に保存
- 実際の GitHub API は CI/CD では叩かない

---

## 13. 実装手順

### Phase A: seed YAML の拡張（GitHub API 不要）

**A-1. `validate` サブコマンドを追加**
- `--validate` フラグの実装
- required キー・enum チェック・参照整合性チェック
- GitHub 未接続で実行できること

**A-2. issue エントリに新規キーを追加（seed）**
- `task_type`, `work_steps`, `deliverables`, `evidence_to_keep`, `dod`
- `exam_priority_guard`, `active_from`, `deferred_until`, `blocked_by`
- 全 46 seed issues に設定（ISS-001 〜 ISS-042, ISS-R01〜R04）

**A-3. validate で全件パス確認**

---

### Phase B: Status 推論ロジックの置き換え

**B-1. `compute_status()` 関数を実装**
- 上記 6 ルールを実装
- `--today` オプションで任意日付のテストができること

**B-2. 単体テストを作成**（`test_status_compute.py`）

**B-3. dry-run で Status 変更差分を確認**
- 電験三種 関連が `Deferred` になること
- 制御基礎 関連が `Backlog` になること（`active_from: 2026-07-05`）

---

### Phase C: issue 本文テンプレートの更新

**C-1. `render_issue_body()` 関数を拡張**
- task_type ごとのテンプレートを実装
- Exam / Study / PLC / Evidence / AI / Career / Review / Deliverable

**C-2. dry-run で body 差分を確認**
- fingerprint が変わることを確認

**C-3. apply**
- 全 issue の body を更新（fingerprint 変更で全 update）

---

### Phase D: Field の追加

**D-1. seed `project_fields` に 6 fields を追加**
```yaml
- name: "Active From"
  type: "text"
- name: "Deferred Until"
  type: "text"
- name: "Blocked By"
  type: "text"
- name: "DoD Ready"
  type: "single_select"
  options: ["✅ Done", "🔲 Not yet", "➖ N/A"]
- name: "Evidence Ready"
  type: "single_select"
  options: ["✅ Ready", "🔲 Missing", "➖ N/A"]
- name: "Exam Guard"
  type: "single_select"
  options: ["🔴 Exam Priority", "➖ Normal"]
```

**D-2. field value の設定ロジックを追加**
- `Active From` → `active_from`
- `Deferred Until` → `deferred_until or "—"`
- `Blocked By` → `", ".join(blocked_by) or "—"`
- `DoD Ready` → `"➖ N/A"` (初期値。人間が更新)
- `Evidence Ready` → `"🔲 Missing"` (初期値。人間が更新)
- `Exam Guard` → `"🔴 Exam Priority"` if `exam_priority_guard` else `"➖ Normal"`

**D-3. apply + 2回目 dry-run noop 確認**

---

### Phase E: recurring instance の生成

**E-1. `expand_recurring_issues()` を実装**
- monthly: 当月の instance を生成
- quarterly: 当四半期の instance を生成
- weekly: template のみ（instance 生成しない）

**E-2. dry-run で当月の月次レビュー instance が表示されることを確認**

**E-3. apply**

---

### Phase F: audit サブコマンドの追加

**F-1. `run_audit()` 関数を実装**
- FAIL / WARN / INFO の 3段階
- `data/sync-reports/<timestamp>_audit.md` に出力

**F-2. audit を実行して FAIL がゼロであることを確認**

---

### Phase G: target 判定の強化

**G-1. `--strict-target` フラグの実装**
- git remote と seed meta が不一致の場合に abort

**G-2. README と docs/github-project-sync.md を更新**

---

### Phase H: テストの整備

- `tests/unit/test_status_compute.py`
- `tests/unit/test_seed_validate.py`
- `tests/unit/test_audit_rules.py`
- `tests/unit/test_body_template.py`
- `pytest` を `requirements.txt` に追加

---

### 実装の所要見積もり

| Phase | 作業量 | 優先度 |
|-------|--------|--------|
| A: seed 拡張 | 大（46 issues に設定追加） | 最初 |
| B: Status 推論 | 中 | 次 |
| C: 本文テンプレート | 中 | 次 |
| D: Field 追加 | 小 | 次 |
| E: Recurring instance | 小 | その後 |
| F: audit | 中 | その後 |
| G: target 判定 | 小 | 最後 |
| H: テスト | 中 | Phase B 〜 F と並行 |

---

## 14. 既知の制約

### GitHub API 制約

| 制約 | 内容 | 対処 |
|------|------|------|
| GraphQL API のレート制限 | 5000 req/h | 636件の field value 設定がボトルネックになりうる |
| Project field (Text) の文字数 | 不明（GitHub 公式非明示） | `Blocked By` フィールドは短い seed_id を使う |
| Issue body の文字数制限 | 65536 文字 | work_steps が多い場合に注意 |
| SingleSelect field のオプション追加 | API でできるが削除は不可 | 一度作ったオプションは残り続ける |

### seed YAML 制約

| 制約 | 内容 |
|------|------|
| `dod` の定義 | 現 seed には存在しない → 全 issue に追加が必要（一括対応） |
| `work_steps` の品質 | 粒度が細かすぎると issue が長くなる。3〜7 steps が目安 |
| `recurring` の instance | 月次レビューの instance は毎月 sync を実行しないと生成されない |

### 運用制約

| 制約 | 内容 |
|------|------|
| Status の手動更新 | `DoD Ready` / `Evidence Ready` は人間が GitHub UI で変更する |
| 週次 recurring の記録 | template issue のコメントに積み上げる方式のため、コメントが増える |
| 電験三種の activate 判定 | `deferred_until: "2026-12-31"` を seed で管理するため、活性化には seed 更新 + apply が必要 |
| PowerShell の UTF-8 | Windows 環境では `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` を実行するか、`chcp 65001` を設定することを推奨 |

### スコープ外（今回の再設計には含めない）

- GitHub Actions による自動 sync（手動実行のみ）
- Slack / LINE 通知との連携
- 進捗ダッシュボードの自動生成
- 電験三種の科目別進捗管理（Issue 内のチェックボックスで管理）

---

*この再設計案は `docs/claude-code-redesign-brief.md` の要件を全て対象としています。*
*実装は `scripts/github_project_sync.py` の既存骨格を活かしつつ、上記 Phase A〜H を順に適用してください。*
