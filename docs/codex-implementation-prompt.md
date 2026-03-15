# Codex 実装指示書
## GitHub Projects 細粒度再構成実装

このファイルは、Codex に最初に読ませる実装指示書です。  
目的は、既存の同期基盤を壊さずに、Project 1 を参考にした細粒度の GitHub Projects 運用へ再構成することです。

## 前提・必読ファイル

次の順で必ず参照してください。
1. `data/project-seed.yaml`
2. `docs/project1-reference-notes.md`
3. `docs/claude-code-redesign-brief.md`
4. `docs/claude-code-redesign-prompt.md`
5. `scripts/github_project_sync.py`
6. `docs/github-project-sync.md`
7. `README.md`
8. `data/sync-reports/latest_dry-run.md`
9. `data/sync-reports/latest_apply.md`

補足:
- `data/project-seed.yaml` が GitHub Projects 同期の唯一の正本です。
- `docs/project1-reference-notes.md` は粒度と運用の参照正本です。
- Markdown docs は補助参照であり、seed より優先してはいけません。

## 絶対条件

以下は変更禁止レベルの制約です。
- `data/project-seed.yaml` を唯一の正本として扱うこと
- 先に必ず `dry-run` を行うこと
- idempotent であること
- 2 回実行しても duplicate issue / duplicate project item / duplicate field value update loop を起こさないこと
- sync report を残すこと
- `validate` と `audit` を通せること
- silent failure しないこと
- unrelated issue / unrelated project item を触らないこと
- 既存 Project 4 を破壊しないこと
- 2026-04-27 までは第一種電気工事士 学科最優先
- 2026-04-28 から 2026-07-04 までは第一種電気工事士 実技最優先
- 電験三種は backlog / deferred として安全に保持できること
- AI 学習は主役ではなく補助戦力として扱うこと
- seed `meta.owner/repo` と実同期先の不一致を silent に飲み込まないこと

## 今回の実装ゴール

現在の board は「同期できる」状態にはあります。  
今回のゴールは、そこから一段進めて、Project 1 と同じく board を見れば次が迷わない状態にすることです。

最終的に、board は次の 4 層で表現されている必要があります。
1. `Phase`
2. `勝ち条件`
3. `具体作業`
4. `日次実行`

重要:
- 既存の 46 issue を単に太らせるだけでは不十分です。
- 必要なら finer-grained issues に分割してください。
- 1 issue は原則として「1週間以内」または「1〜3 セッション」で終わる粒度にしてください。
- 開いた瞬間に `Outcome` と `Next Action` が見えない card は不十分です。

## Project 1 から取り込むべき核

必ず次を実装設計へ反映してください。
- `Phase -> 勝ち条件 -> 具体作業` の階層
- 1 Phase あたり勝ち条件は 3 つ以内
- `Outcome（完了条件）`
- `Next Action（5分で開始できる最初の一手）`
- `成果の証跡`
- `日次実行`
- `Time Block`
- `Estimate`
- `Energy`
- `Focus`

## 実装の核心ポイント

Codex が最初に手をつけるべき場所は次の 3 つです。
1. Phase A:
   seed YAML に `task_type / outcome / next_action / completion_check / daily_execution / work_steps / dod` などを全 issue に追加する  
   必要なら `phase_cards` と `win_conditions` も追加し、粗い issue を分割する
2. Phase B:
   `compute_status()` の 6 ルールを維持しつつ、細粒度 issue に対して `Deferred / Backlog / Blocked / Todo` が自然に決まるようにする
3. Phase C:
   issue 本文テンプレートを Project 1 型へ更新し、issue を開けば即着手できる状態にする

seed の拡張と分割が今回の最大作業です。  
既存 46 issue を「そのまま扱う前提」ではなく、「細粒度へ書き換える前提」で進めてください。

## Phase A: seed YAML 再構造化と `--validate`

### 実装内容

`data/project-seed.yaml` を Project 1 型へ再構造化してください。

最低限、次を実装します。

### A-1. トップレベル構造の追加
- `phase_cards`
- `win_conditions`
- `issues`
- `project_fields`
- `issue_blueprints`

### A-2. 各 concrete issue に追加するキー
- `task_type`
- `outcome`
- `next_action`
- `why_this_matters`
- `device`
- `inputs`
- `things_to_make`
- `work_steps`
- `deliverables`
- `evidence_to_keep`
- `dod`
- `completion_check`
- `daily_execution`
- `active_from`
- `deferred_until`
- `blocked_by`
- `exam_priority_guard`
- `review_note`
- `time_block`
- `estimate`
- `energy`
- `focus`

### A-3. 分割ルール

次に当てはまる issue は分割してください。
- 複数の知識塊をまたいでいる
- 3 ステップを超える
- 1 週間を超える
- 5 分で始める最初の一手が書けない
- Completion Check が曖昧
- 証跡が曖昧
- 今日やることを書けない

### A-4. 勝ち条件の要件

各 `win_conditions` には最低限以下を持たせてください。
- `id`
- `title`
- `phase`
- `outcome`
- `completion_check`
- `evidence_to_keep`
- `linked_issue_ids`
- `active_from`
- `deferred_until`

### A-5. validate の強化

`scripts/github_project_sync.py` の `--validate` で最低限次を検査してください。
- 必須キー欠落
- enum 不正
- 日付不正
- `active_from > due_date`
- `blocked_by` が未知 issue を指す
- `linked_issue_ids` が未知 issue を指す
- `completion_check` 欠落
- `outcome` 欠落
- `next_action` 欠落
- `daily_execution` 欠落

### 完了確認コマンド
```powershell
python scripts/github_project_sync.py --validate
```

### 完了条件
- `FAIL: 0`
- `WARN: 0`
- seed 内で粗すぎる issue が残っていない

## Phase B: `compute_status()` の 6 ルール実装

### 実装内容

細粒度 issue に対しても一貫して状態が決まるように、現在の 6 ルールを維持・明確化してください。

1. `deferred_until >= today` なら `Deferred`
2. `active_from > today` なら `Backlog`
3. `blocked_by` に未完了 issue があるなら `Blocked`
4. 試験優先期間で `exam_priority_guard == false` なら `Backlog`
5. `due_date <= today + DATE_WINDOW_DAYS` なら `Todo`
6. それ以外は `Backlog`

追加要件:
- win condition card と concrete issue の両方に適用できること
- recurring review が試験主軸を壊さないこと
- Denken が 2026 年は不自然に前面化しないこと
- career prep が早すぎる時期に active にならないこと

### 完了確認コマンド
```powershell
pytest tests/unit/test_status_compute.py -q
python scripts/github_project_sync.py --today 2026-03-14
python scripts/github_project_sync.py --today 2026-04-15
```

### 完了条件
- status が試験優先・deferred・blocked を正しく反映する
- 細粒度 issue でも不自然な `Todo` 量産が起きない

## Phase C: issue 本文テンプレート更新

### 実装内容

`render_issue_body()` を Project 1 型へ更新してください。  
Concrete issue は、開けば即着手できる本文でなければいけません。

### 必須セクション
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

### テンプレート要件
- `next_action` は 5 分で始められる一手にする
- `completion_check` は自己採点でなく確認可能な行動にする
- `daily_execution` は日別またはセッション別にする
- `blocked_by` は seed ID と人間可読 title の両方を出す
- `career_link` と `ai_link` は `Why this matters` に接続する

### 完了確認コマンド
```powershell
pytest tests/unit/test_body_template.py -q
python scripts/github_project_sync.py --today 2026-03-14
```

### 完了条件
- issue を開いた瞬間に着手手順が分かる
- 完了チェックと証跡が本文だけで判断できる

## Phase D: Project field 拡張

### 実装内容

既存 field を維持しつつ、Project 1 型の実行 field を追加してください。

### 維持する field
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

### 追加する field
- `Start Date`
- `End Date`
- `Time Block`
- `Estimate`
- `Energy`
- `Focus`
- `Next Action`
- `Outcome`
- `Completion Check`

### 注意
- 本文と field で責務を分けること
- 本文を field の代用にしないこと
- field 追加は idempotent に行うこと

### 完了確認コマンド
```powershell
pytest tests/unit/test_field_mapping.py -q
python scripts/github_project_sync.py --today 2026-03-14
```

### 完了条件
- 新規 field が dry-run に出る
- 再 dry-run で `noop` に収束する

## Phase E: `--audit` 強化

### 実装内容

`--audit` を「構文監査」ではなく「運用品質監査」にしてください。

### 監査項目
- 必須 field 欠落
- due date 欠落
- milestone 欠落
- phase / priority / task_type の不整合
- blocked 状態不整合
- `outcome` 欠落
- `next_action` 欠落
- `completion_check` 欠落
- `evidence_to_keep` 欠落
- `daily_execution` 欠落
- active window 外で active になっている issue
- exam priority 違反

### 出力要件
- Markdown report
- JSON report
- `FAIL / WARN / INFO` の明確な分類

### 完了確認コマンド
```powershell
pytest tests/unit/test_audit_rules.py -q
python scripts/github_project_sync.py --audit --today 2026-03-14
```

### 完了条件
- `FAIL: 0`
- `WARN: 0`
- report から board 品質の弱点が読める

## Phase F: target 安全化と apply 前ガード

### 実装内容

seed `meta.owner/repo` と実ターゲット不一致を、より明確に扱ってください。

### 要件
- 不一致時は warning を出す
- override なし apply を危険扱いにする
- `--owner --repo --project-owner` 指定時のみ apply を進める設計を維持する
- 既存 Project 4 の managed item を二重作成しない

### 完了確認コマンド
```powershell
python scripts/github_project_sync.py --validate
python scripts/github_project_sync.py --owner foru1215 --repo shared-auto-sync --project-owner foru1215
```

### 完了条件
- target 誤判定で本投入しない
- mismatch が silent にならない

## Phase G: dry-run -> 差分確認 -> apply

### 実装内容

実行順は必ず次です。
1. `validate`
2. tests
3. `audit`
4. `dry-run`
5. 差分確認
6. `apply`
7. 再 `dry-run`

### 差分確認で見るもの
- 新規 phase card 数
- 新規 win condition 数
- 分割後 concrete issue 数
- field 追加数
- field value 更新数
- duplicate の有無

### 完了確認コマンド
```powershell
python scripts/github_project_sync.py --validate
pytest -q
python scripts/github_project_sync.py --audit --today 2026-03-14
python scripts/github_project_sync.py --today 2026-03-14 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
python scripts/github_project_sync.py --apply --today 2026-03-14 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
python scripts/github_project_sync.py --today 2026-03-14 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
```

### 完了条件
- apply 後の再 dry-run が `noop` 中心に収束する
- duplicate がない
- report が更新される

## Phase H: テストとドキュメント更新

### 実装内容

最低限、次のテストと docs を更新してください。

### テスト
- `tests/unit/test_seed_validate.py`
- `tests/unit/test_status_compute.py`
- `tests/unit/test_body_template.py`
- `tests/unit/test_field_mapping.py`
- `tests/unit/test_audit_rules.py`

### ドキュメント
- `README.md`
- `docs/github-project-sync.md`

### docs に必ず書くこと
- `phase_cards` と `win_conditions` の意味
- 具体作業 issue の粒度ルール
- `Outcome / Next Action / Completion Check / Daily execution` の意味
- dry-run / apply / resync 方法
- target mismatch の扱い

### 完了確認コマンド
```powershell
pytest -q
Select-String -Path README.md,docs/github-project-sync.md -Pattern "phase_cards","win_conditions","Outcome","Next Action","Completion Check","Daily execution","dry-run","apply"
```

### 完了条件
- tests が通る
- docs が新しい粒度設計を説明できる

## Phase I: 最終確認と報告

### 実装内容

最後に、結果レポートを次の順で整理してください。
1. 調査結果
2. 実装方針
3. 変更ファイル一覧
4. seed 分割結果
5. dry-run 結果
6. apply 結果
7. 再同期方法
8. 既知の制約
9. 注意点

### 完了確認コマンド
```powershell
python scripts/github_project_sync.py --validate
pytest -q
python scripts/github_project_sync.py --audit --today 2026-03-14
python scripts/github_project_sync.py --today 2026-03-14 --owner foru1215 --repo shared-auto-sync --project-owner foru1215
```

### 完了条件
- 何をどう細かくしたかが明文化される
- board の見え方が Project 1 寄りに改善される

## 完了チェックリスト

実装後、全件確認してください。
- seed に `phase_cards` と `win_conditions` がある
- coarse issue が分割されている
- 全 concrete issue に `outcome` がある
- 全 concrete issue に `next_action` がある
- 全 concrete issue に `completion_check` がある
- 全 concrete issue に `daily_execution` がある
- `validate` が通る
- tests が通る
- `audit` が通る
- dry-run で差分が可視化される
- apply 後の再 dry-run が `noop` に収束する
- duplicate issue / project item がない
- exam priority が壊れていない
- Denken が前面化していない
- AI が主役化していない
- docs が更新されている

## 注意事項

- seed `meta.owner/repo` は現状 `forui/my-app`
- 実同期先は `foru1215/shared-auto-sync`
- live project は [Project 4](https://github.com/users/foru1215/projects/4)
- 既存 managed issue / project item がすでに存在するため、移行は update ベースで行うこと
- `gh` CLI の rate limit を避けるため、read キャッシュと差分更新を優先すること
- PowerShell 上では UTF-8 日本語が見えにくいことがあるが、ファイルは UTF-8 で扱うこと

## 最後に

今回の実装で目指すのは、情報量の多い board ではありません。  
目指すのは、board を開いたときに次の 4 つが即座に分かる board です。
- 何をするか
- 何をまだやらないか
- 何をもって完了か
- 今日の限られた時間で何をやるか

最初に着手する順番は必ず次です。
1. Phase A
2. Phase B
3. Phase C
