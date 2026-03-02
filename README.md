# SKK — 案件管理リポジトリ

## 運用ルール

### 1. Googleカレンダー ＝ タスクのみ
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

### 2. GitHub ＝ 案件台帳の正
- **案件1件 ＝ Issue 1枚**
- 状態・履歴・金額・先方反応はすべてIssueに集約する
- Issueタイトル規約：`<案件ID> <顧客略号> <案件名>`（例：`Q12345 A社 盤改造見積`）

### 3. Statusの正は Project（SKK）
- **Project の Status フィールドが唯一の正**
- Issue本文にステータスを重複管理しない（参照のみ）
- Status値：Backlog → Estimating → Submitted → Re-submitting → Waiting Reply → On-site → Won / Lost / On Hold

### 4. 更新は最低限「3点だけ」
案件に動きがあったら：

1. **Issue本文にログ追記**（提出 / 回答 / 立会）
2. **ProjectのStatus更新**
3. **Due & Last Action 更新**（必要なら Amount Latest / Submitted At / Quote Ver / Reply Summary も更新）

### 5. ラベル運用
| ラベル | 用途 |
|--------|------|
| `type:quote` | 見積案件 |
| `type:onsite` | 現地立会あり |
| `type:customer-reply` | 先方回答待ち / 回答あり |
| `type:internal` | 社内タスク |
| `priority:high` | 高優先 |
| `priority:mid` | 中優先 |
| `priority:low` | 低優先 |

---

## テンプレート
新しい案件は Issues → New Issue → 「案件台帳」テンプレートを選択して作成する。

## Project
[SKK Project](../../projects) の Board / Table ビューで一覧管理する。
