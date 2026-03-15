# Claude Code Redesign Prompt

以下のリポジトリについて、GitHub Projects 同期基盤と seed 設計の再設計案を出してください。  
今回は「同期できること」ではなく、「Project を見れば次にやることと完了条件が迷わないこと」を最優先にしてください。

## 必読順

次の順で読んでください。
1. `data/project-seed.yaml`
2. `docs/project1-reference-notes.md`
3. `docs/claude-code-redesign-brief.md`
4. `docs/project-plan-summary.md`
5. `docs/project-plan.md`
6. `scripts/github_project_sync.py`
7. `docs/github-project-sync.md`
8. `README.md`
9. `data/sync-reports/latest_dry-run.md`
10. `data/sync-reports/latest_apply.md`

参考 Project:
- [foru1215 Project 1](https://github.com/users/foru1215/projects/1)

## 現状

現実装では次はできています。
- `dry-run`
- `apply`
- idempotent sync
- labels / milestones / issues / project items / fields の同期
- `--validate`
- `--audit`
- machine-readable marker による重複防止

ただし、次がまだ弱いです。
- タスクが粗い
- 完了条件が弱い
- Completion Check が弱い
- dependency / blocked / deferred の人間向け運用が弱い
- recurring / review の設計が粗い
- board を見ても「今日なにをやるか」が弱い

## 今回の再設計の主眼

Project 1 を参考に、現在の board を次の4層へ細分化してください。
1. `Phase`
2. `勝ち条件`
3. `具体作業`
4. `日次実行`

重要:
- 既存の 46 issue をただ情報追加で厚くするだけでは不十分です。
- 必要なら issue をさらに分割してください。
- 1 issue は「1週間以内」または「1〜3回の集中作業」で完了できる粒度を目安にしてください。
- `Outcome` と `Next Action` がない issue は、開いても動けない issue とみなしてください。

## 絶対条件

- `data/project-seed.yaml` を唯一の正本とすること
- `dry-run` を先に行うこと
- idempotent
- 2回実行しても重複作成しないこと
- 実行ログと差分レポートを残すこと
- silent failure しないこと
- unrelated issue / item を壊さないこと
- 2026-04-27 までは第一種電気工事士 学科最優先
- 2026-04-28 から 2026-07-04 までは第一種電気工事士 実技最優先
- 電験三種は backlog / deferred で安全に管理できること
- AI学習は武器だが、試験主軸を崩さないこと

## Project 1 から必ず取り込む観点

- `Phase -> 勝ち条件 -> 具体作業` の構造
- 1 phase あたり勝ち条件は 3 つ以内
- `Outcome（完了条件）`
- `Next Action（5分で開始できる最初の一手）`
- `進め方`
- `成果の証跡`
- `日次実行`
- `Time Block`
- `Estimate`
- `Energy`
- `Focus`

## ほしい再設計内容

必ず次の順で出してください。
1. 調査結果
2. 現実装の評価
3. 問題点の優先順位
4. どの issue をどの単位で分割すべきか
5. 目標データモデル
6. `phase_cards` / `win_conditions` / `issues` の役割分担
7. issue 本文テンプレート案
8. Project field 設計案
9. completion criteria / completion check 設計案
10. dependency / blocked / deferred / recurring 運用案
11. `compute_status()` の人間向け意味づけ
12. dry-run / apply / audit フロー
13. 既存 Project 4 からの移行案
14. テスト方針
15. 実装手順
16. 既知の制約

## 粒度の評価ルール

次のいずれかに当てはまる issue は「粗すぎる」と判断してください。
- 複数の知識塊をまたいでいる
- 3 ステップを超える
- 1 週間を超える
- 5 分で始める最初の一手が書けない
- 完了証跡が曖昧
- 今日は何をやるかを書けない

## 期待する結論

「同期ロジックは維持しつつ、seed と board 運用を Project 1 レベルの実行粒度へ再構成する」提案をください。  
抽象論ではなく、seed に追加すべきキー、Project field 名、issue 本文セクション名、分割単位、移行順まで具体化してください。
