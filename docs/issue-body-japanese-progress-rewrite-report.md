# Issue本文 日本語化・進捗自動計算対応 修正報告

## 目的
GitHub Projects / GitHub Issue の本文を、以下の方針に合わせて実用レベルへ改善した。

- Issue本文を日本語で、具体的かつ行動可能にする
- 進捗は本文内の GitHub Task List だけで自動計算させる
- 各Issueを見た瞬間に「何をやれば完了か」「最初の一手は何か」「次に何を残すか」が分かるようにする
- Claude Code がこの変更を評価し、必要なら追加修正できる状態にする

## 今回受けた指示の要点
今回の指示では、特に次を満たすことが求められた。

1. 出力は日本語中心にする
2. 抽象表現を避け、5分以内に着手できる粒度まで具体化する
3. 進捗率は本文へ直書きせず、`- [ ]` / `- [x]` のタスクリストで管理する
4. 各Issueに最低でも以下を持たせる
   - 概要
   - 完了条件
   - 今回の到達目標
   - 最初の一手（5分で開始できる行動）
   - タスクリスト
   - 補足メモ
   - 記録欄
5. Epic / Phase / 学習Issue / 実務Issue なども同じ思想で統一する
6. 「読むためのIssue」ではなく「行動するためのIssue」にする

## 実際に修正したこと

### 1. Issue本文テンプレートを全面的に日本語化
[github_project_sync.py](C:/Users/forui/my-app/shared/scripts/github_project_sync.py) の本文生成を差し替え、通常Issueを以下の構造へ統一した。

```md
## 概要
## 完了条件
## 今回の到達目標
## 最初の一手（5分で開始できる行動）
## タスクリスト
## 補足メモ
## 記録欄
```

変更内容のポイント:

- `Summary / Outcome / Next Action` のような英語見出しを廃止
- `完了条件` は箇条書きで観測可能な条件へ統一
- `最初の一手` は必ずチェックボックス 1 個で表示
- `タスクリスト` は `work_steps` を中心に 4〜10 個程度へ収まるよう整形
- `記録欄` は `実績 / 気づき / 次回への引き継ぎ` に統一
- 進捗率の数値直書きは行わず、GitHub 標準の Task List のみで進捗表示

### 2. Epic本文も同じ思想で再設計
Epic は親Issueとして扱い、以下を明示する形へ変更した。

- 何を束ねるEpicなのか
- 主要マイルストーンは何か
- 含まれる Seed Issue はどれか
- 次に確認するべき子Issue群は何か

Epic の `タスクリスト` は詳細作業ではなく、主要マイルストーン単位に留めている。

### 3. 日本語中心で読めるようにフォールバック文言も修正
本文中に混ざるノイズを減らすため、以下も調整した。

- `None` → `未設定`
- `Phase Issue` → `フェーズ管理Issue`
- `Epic Issue` → `Epic親Issue`
- 期間表記の `From ...` → 日本語表現へ変更

### 4. テストを更新
[test_body_template.py](C:/Users/forui/my-app/shared/tests/unit/test_body_template.py) を日本語テンプレート前提に更新した。

確認している内容:

- 日本語見出しが入ること
- 最初の一手がチェックボックスになること
- 関連Issue / 依存Issue が本文に出ること
- Epic本文にも含まれる Seed Issue 一覧が出ること
- machine-readable marker が残ること

## 変更ファイル
- [github_project_sync.py](C:/Users/forui/my-app/shared/scripts/github_project_sync.py)
- [test_body_template.py](C:/Users/forui/my-app/shared/tests/unit/test_body_template.py)
- [issue-body-japanese-progress-rewrite-report.md](C:/Users/forui/my-app/shared/docs/issue-body-japanese-progress-rewrite-report.md)

## 実行した確認

### ローカル確認
- `python scripts/github_project_sync.py --validate`
  - 結果: `FAIL 0 / WARN 0`
- `pytest -q`
  - 結果: `18 passed`
- `python scripts/github_project_sync.py --audit --today 2026-03-15`
  - 結果: `FAIL 0 / WARN 0 / INFO 2`

### GitHub 反映前 dry-run
1回目の dry-run:

- `issue update=85`
- `project_field_value set=77`

レポート:
- [20260315T022525Z_dry-run.md](C:/Users/forui/my-app/shared/data/sync-reports/20260315T022525Z_dry-run.md)

### 1回目の apply
本文テンプレート全面差し替えを反映:

- `issue update=85`

レポート:
- [20260315T022823Z_apply.md](C:/Users/forui/my-app/shared/data/sync-reports/20260315T022823Z_apply.md)

### 追加微修正
Epic 本文とフェーズ系種別名の表現をさらに日本語寄りへ調整した。

2回目の dry-run:

- `issue update=15`

レポート:
- [20260315T022954Z_dry-run.md](C:/Users/forui/my-app/shared/data/sync-reports/20260315T022954Z_dry-run.md)

### 2回目の apply
微修正を反映:

- `issue update=15`

レポート:
- [20260315T023037Z_apply.md](C:/Users/forui/my-app/shared/data/sync-reports/20260315T023037Z_apply.md)

### 最終収束確認
最終 dry-run:

- `issue noop=85`
- `project_field_value noop=2308`

レポート:
- [20260315T023100Z_dry-run.md](C:/Users/forui/my-app/shared/data/sync-reports/20260315T023100Z_dry-run.md)

## ライブ反映サンプル
実際に GitHub 上で更新済みの例:

- Epic 例: [[Epic] License](https://github.com/foru1215/shared-auto-sync/issues/12)
- 学習Issue 例: [[E-LIC] 2026-04: 学科試験 過去問5年分×2周](https://github.com/foru1215/shared-auto-sync/issues/23)

どちらも以下を確認済み:

- 日本語見出し
- 最初の一手のチェックボックス
- タスクリストでの進捗計算
- 記録欄
- machine-readable marker

## Claude Code に評価してほしい点

### 1. 本文の粒度が十分か
現状は seed に入っている `work_steps / next_action / dod / deliverables / evidence_to_keep` を使って本文を組み立てている。
そのため、本文品質は seed の粒度に強く依存する。

見てほしい点:

- 各 Issue の `最初の一手` が本当に 5 分以内で着手できるか
- `タスクリスト` の 1 チェックが 1 ステップとして十分明確か
- 学習Issueで「何問やるか」「どう記録するか」がまだ弱い項目がないか

### 2. Phase / Win Condition の役割が十分に伝わるか
今回の修正は主に本文テンプレート改善であり、Phase / Win Condition 自体の情報設計は大きく変えていない。

見てほしい点:

- Phase Issue を Weekly / Daily にさらに落とすべきか
- Win Condition の完了条件がまだ抽象的な箇所はないか
- 「今何をやれば良いか」が board 上で迷わず分かるか

### 3. 日本語中心という条件に対して十分か
本文は日本語中心にしたが、以下はまだ残る。

- タイトル中の英語名
- 一部 seed 由来の用語
- GitHub Project field 名の英語

必要なら次の修正候補:

- Epic 名そのものの見直し
- seed 側の `next_action / work_steps` の再分解
- field 名や option 名の日本語化方針整理

## 既知の制約
- 本文品質は seed の各項目品質に依存する
- `project link` は dry-run / apply で毎回 `link=1` が出るが、重複作成はされていない
- `phase_cards / win_conditions / issues` は同一テンプレート思想でそろえたが、Weekly / Daily 専用 seed はまだ持っていない
- `GitHub Projects` の field 名そのものは現在の運用互換性を優先し、今回は本文改善を優先した

## まとめ
今回の修正で、Issue本文は「読むだけ」から「開いた瞬間に動ける」方向へかなり改善された。
少なくとも以下は満たしている。

- 日本語中心
- チェックボックスによる進捗自動計算
- 完了条件の明示
- 最初の一手の明示
- 記録欄の統一
- GitHub への反映と再 dry-run での収束確認

次に Claude Code に依頼するなら、本文テンプレートそのものの再設計ではなく、`seed` の各Issue内容をさらに細分化して「1チェックの粒度」を上げる評価・修正が適している。
