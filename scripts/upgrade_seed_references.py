"""
全 Issue の inputs を具体的な参照元（教材・URL・章番号）に差し替え、
outcome の汎用テンプレートを Issue 固有の記述に改善するスクリプト。

使い方:
  python scripts/upgrade_seed_references.py
  → data/project-seed.yaml を直接更新する
"""
from __future__ import annotations
import re, sys
from pathlib import Path

SEED = Path("data/project-seed.yaml")

# ── 参照元マッピング ──────────────────────────────────────────
INPUTS: dict[str, list[str]] = {
    # ── Phase 0: 第一種電気工事士 学科 ──
    "ISS-001": [
        "「第一種電気工事士 筆記試験 完全解答」（オーム社 or 電気書院）",
        "過去問ドットコム https://kakomonn.com/denki-kouji/1syu/",
        "誤答メモ用ノート",
    ],
    "ISS-005": [
        "ISS-001 で使った過去問題集（5年分）",
        "ISS-001 の弱点 Top5 リスト",
        "「すいーっと合格 第1種電気工事士 筆記試験」弱点分野の章",
    ],
    "ISS-006": [
        "受験票",
        "ISS-005 の弱点リスト（直前確認用 Top3）",
        "試験案内 https://www.shiken.or.jp/examination/e-construction02.html",
    ],
    # ── Phase 1: 実技 ──
    "ISS-007": [
        "電気技術者試験センター 候補問題公表ページ https://www.shiken.or.jp/",
        "「第一種電気工事士 技能試験 候補問題できた!」（電気書院）",
        "複線図練習ノート",
    ],
    "ISS-008": [
        "ISS-007 の複線図練習結果",
        "候補問題13問の複線図集",
        "工具一式（圧着ペンチ・VVFストリッパー・電工ナイフ等）",
    ],
    "ISS-009": [
        "受験票",
        "ISS-008 の苦手問題リスト",
        "試験案内 https://www.shiken.or.jp/examination/e-construction02.html",
    ],
    # ── Setup ──
    "ISS-002": [
        "GitHub Docs: Projects https://docs.github.com/ja/issues/planning-and-tracking-with-projects",
        "gh CLI リファレンス https://cli.github.com/manual/",
        "data/project-seed.yaml（正本）",
    ],
    "ISS-003": [
        "Claude Code ドキュメント https://docs.anthropic.com/",
        "Anthropic API リファレンス",
        "Codex CLI https://github.com/openai/codex",
    ],
    # ── Evidence ──
    "ISS-004": [
        "自社の仕様書1件（発電機盤 or ポンプ盤 等）",
        "ISS-011 制御基礎ノート（参照用）",
        "技術メモ用テンプレート（Issue コメント形式）",
    ],
    "ISS-017": [
        "自社の発電機盤仕様書",
        "ISS-011〜014 の制御基礎ノート（参照用）",
        "技術メモ用テンプレート",
    ],
    "ISS-018": [
        "自社のポンプ盤仕様書",
        "ISS-017 の発電機盤技術メモ（比較用）",
        "制御フロー図作成用ツール（draw.io 等）",
    ],
    "ISS-033": [
        "自社の業務フローまたは現場課題リスト",
        "ISS-017〜018 の技術メモ",
        "改善提案テンプレート",
    ],
    "ISS-R04": [
        "業務中の仕様書・現場メモ",
        "ISS-017〜018 の技術メモ（テンプレート参考）",
        "GitHub Issue コメント（証跡保存先）",
    ],
    # ── AI ──
    "ISS-010": [
        "Claude Code Academy 入門 https://docs.anthropic.com/",
        "Anthropic API リファレンス https://docs.anthropic.com/en/api/",
        "入門チュートリアル成果物保存先リポジトリ",
    ],
    "ISS-019": [
        "Claude Code Academy 中級コース",
        "ISS-010 の学習ログ",
        "Anthropic Cookbook https://github.com/anthropics/anthropic-cookbook",
    ],
    "ISS-034": [
        "Anthropic API ドキュメント https://docs.anthropic.com/en/api/",
        "自社の仕様書テンプレート",
        "ISS-019 の学習ログ（プロンプト集）",
    ],
    "ISS-035": [
        "ISS-034 の AI 業務改善成果物",
        "ISS-015〜016 の図面読解ノート",
        "Claude Code プロンプト集（ISS-019）",
    ],
    # ── 制御基礎 ──
    "ISS-011": [
        "「よくわかるシーケンス制御」大浜庄司 著（オーム社）第1章",
        "自社制御盤の実物 or 写真（あれば）",
        "学習ノート",
    ],
    "ISS-012": [
        "「よくわかるシーケンス制御」第2〜3章（自己保持回路・a/b接点）",
        "ISS-011 のノート（復習用）",
        "回路図の例題（教科書 or Web）",
    ],
    "ISS-013": [
        "「よくわかるシーケンス制御」第4〜5章（インターロック・タイマー回路）",
        "ISS-012 のノート",
        "タイマー回路の例題",
    ],
    "ISS-014": [
        "「よくわかるシーケンス制御」全章（総復習用）",
        "ISS-011〜013 のノート一式",
        "セルフテスト用チェックリスト（口頭説明できるか）",
    ],
    # ── 図面読解 ──
    "ISS-015": [
        "JIS C 0617（電気用図記号）の概要資料",
        "自社の展開接続図（実務参照）",
        "「よくわかるシーケンス制御」の回路図部分（参照用）",
    ],
    "ISS-016": [
        "JIS C 0617 記号一覧表",
        "自社の単線結線図（実務参照）",
        "ISS-015 のノート",
    ],
    "ISS-026": [
        "ISS-015〜016 の図面読解ノート全章",
        "JIS C 0617 記号一覧",
        "自社図面の実例3件以上",
    ],
    # ── PLC ──
    "ISS-020": [
        "三菱電機 GX Works3 入門マニュアル（公式 PDF）",
        "GX Works3 + GX Simulator3（シミュレータ環境）",
        "ラダー図記号一覧表（AND/OR/NOT/コイル/接点）",
    ],
    "ISS-021": [
        "三菱電機 MELSEC プログラミングマニュアル（基本命令編）",
        "ISS-020 で構築したシミュレータ環境",
        "基本命令リファレンス（タイマー T / カウンタ C）",
    ],
    "ISS-022": [
        "ISS-011〜014 の制御基礎ノート（自己保持回路）",
        "GX Works3 シミュレータ",
        "シーケンス制御実習の課題仕様",
    ],
    "ISS-023": [
        "「よくわかるシーケンス制御」（総復習用）",
        "ISS-020〜022 の PLC ノート",
        "シーケンス制御体系図（教科書 or 自作）",
    ],
    "ISS-024": [
        "ISS-020〜023 の全課題成果物",
        "GX Works3",
        "ISS-015〜016 の図面読解ノート",
    ],
    "ISS-032": [
        "ISS-020〜024 の PLC 課題成果物",
        "GX Works3 タイマー・カウンタ応用マニュアル",
        "自社設備の制御仕様（参考）",
    ],
    # ── 電験三種 ──
    "ISS-025": [
        "「みんなが欲しかった! 電験三種 理論の教科書&問題集」（TAC出版）",
        "電験三種ドットコム https://denken-3.com/",
        "学習計画ノート",
    ],
    "ISS-027": [
        "「みんなが欲しかった! 電験三種 理論」第3〜4章（磁気・静電気）",
        "「みんなが欲しかった! 電験三種 電力」第1章",
        "ISS-025 のノート",
    ],
    "ISS-028": [
        "「みんなが欲しかった! 電験三種 理論」第5章（電子回路）",
        "「みんなが欲しかった! 電験三種 電力」第2〜3章（変電・配電）",
        "ISS-027 のノート",
    ],
    "ISS-029": [
        "電験三種 公式過去問題集（電気技術者試験センター）",
        "「みんなが欲しかった! 電験三種 機械」第1章",
        "ISS-025〜028 の弱点リスト",
    ],
    "ISS-030": [
        "過去問題集（理論・電力 重点周回用）",
        "「みんなが欲しかった! 電験三種 法規」要点集",
        "ISS-029 の弱点分析",
    ],
    "ISS-031": [
        "受験票",
        "ISS-030 の直前弱点リスト（Top5）",
        "試験案内 https://www.shiken.or.jp/examination/e-construction03.html",
    ],
    # ── セキュリティ ──
    "ISS-043": [
        "NIST SP 800-82 Rev.3 https://csrc.nist.gov/publications/detail/sp/800-82/rev-3/final",
        "IT vs OT 比較ノート（自作）",
        "用語メモ",
    ],
    "ISS-044": [
        "CISA ICS Training https://www.cisa.gov/ics-training",
        "ISS-043 の NIST ノート（参照用）",
        "ICS アーキテクチャ図（Purdue Model）",
    ],
    "ISS-045": [
        "ISS-043〜044 の OT セキュリティノート",
        "ISS-020〜024 の PLC 課題成果物",
        "IEC 62443 概要資料",
    ],
    "ISS-046": [
        "ISS-035 の制御 × AI 成果物",
        "ISS-045 のセキュリティチェックリスト",
        "ポートフォリオ原稿",
    ],
    # ── Deliverable ──
    "ISS-036": [
        "ISS-034〜035 の AI 成果物一式",
        "GitHub リポジトリ（公開用）",
        "ポートフォリオ構成案",
    ],
    "ISS-039": [
        "ISS-036 のポートフォリオ v1",
        "ISS-034〜035 の AI 成果物",
        "面接デモ用スクリプト",
    ],
    # ── Career ──
    "ISS-037": [
        "現職の業務実績リスト（案件・規模・成果）",
        "ISS-033 の社内改善提案",
        "転職先の求人要件例 3 社分",
    ],
    "ISS-038": [
        "ISS-037 の職務経歴書ドラフト",
        "ISS-036 のポートフォリオ v1",
        "面接想定質問リスト（技術・志望動機・転職理由）",
    ],
    "ISS-040": [
        "ISS-038 の職務経歴書 v2",
        "ISS-039 のポートフォリオ最終版",
        "転職エージェント比較リスト（制御・設備系に強いところ）",
    ],
    "ISS-041": [
        "ISS-038 の面接ストーリー集",
        "ISS-039 のポートフォリオ",
        "応募先企業リスト（3社以上）",
    ],
    "ISS-042": [
        "応募状況一覧（企業名・進捗・面接日程）",
        "面接振り返りメモ",
        "24か月計画の完了チェックリスト（docs/overall-roadmap.md）",
    ],
    # ── Review ──
    "ISS-R01": [
        "GitHub Projects ボード https://github.com/users/foru1215/projects/4",
        "今週の実績ログ（Issue コメント）",
        "前回レビューの振り返り",
    ],
    "ISS-R02": [
        "GitHub Projects ボード",
        "今月の実績サマリー",
        "docs/overall-roadmap.md（進捗確認用）",
    ],
    "ISS-R03": [
        "GitHub Projects ボード",
        "今四半期の実績サマリー",
        "docs/overall-roadmap.md + docs/current-focus-guide.md",
    ],
}

# ── outcome 改善マッピング ───────────────────────────────────
# 汎用テンプレート「…を完了し、必要な成果物と証跡を残して次のタスクへ接続できる状態にする。」を Issue 固有の記述に置換
OUTCOMES: dict[str, str] = {
    "ISS-002": "GitHub Projects のボード・ラベル・フィールドが稼働し、全 seed Issue が同期済みの状態。",
    "ISS-003": "Claude Code と Codex CLI が動作確認済みで、Issue コメントへの記録ワークフローが回る状態。",
    "ISS-004": "仕様書1件の技術要点が技術メモとして残り、面接で説明できる状態。",
    "ISS-007": "候補問題13問のうち6問以上を複線図から組み立てまで見ないで完成できる状態。",
    "ISS-008": "13問すべてを試験時間内に欠陥なしで完成できる状態。",
    "ISS-009": "実技試験を受験し、自己評価と次フェーズへの移行判断が記録されている状態。",
    "ISS-010": "Claude Code Academy 入門コースを修了し、基本的なプロンプト・ツール操作ができる状態。",
    "ISS-011": "リレーシーケンスの基本（リレー・接点・コイル）を自分の言葉で説明できるノートがある状態。",
    "ISS-012": "自己保持回路・a接点/b接点の動作を図と文で説明できるノートがある状態。",
    "ISS-013": "インターロック回路・タイマー回路の動作を図と文で説明できるノートがある状態。",
    "ISS-014": "制御基礎ノート全章を口頭で説明でき、セルフテストに合格した状態。",
    "ISS-015": "展開接続図の基本記号と読み方が分かり、自社図面で試し読みできる状態。",
    "ISS-016": "単線結線図と JIS C 0617 の記号体系が分かるノートがある状態。",
    "ISS-017": "発電機盤の制御方式・回路構成が技術メモに残り、面接で説明できる状態。",
    "ISS-018": "ポンプ盤の制御フロー図が完成し、ISS-017 と比較して制御パターンの違いを説明できる状態。",
    "ISS-019": "Claude Code Academy 中級コースを修了し、業務適用アイデアが3件以上リストにある状態。",
    "ISS-020": "GX Works3 + シミュレータが動作し、ラダー図で AND/OR/NOT の基本回路を動かせる状態。",
    "ISS-021": "タイマー・カウンタを含む基本命令を使って課題2件を動作確認済みの状態。",
    "ISS-022": "自己保持回路を PLC で実装し、シーケンス制御実習の課題3件目が完了した状態。",
    "ISS-023": "シーケンス制御の体系（順序制御・条件制御・タイマー）をノートにまとめた状態。",
    "ISS-024": "PLC 課題5件以上が完成し、図面読解と組み合わせたポートフォリオ素材がある状態。",
    "ISS-025": "電験三種 理論科目の全体像を把握し、学習計画が月単位で組めている状態。",
    "ISS-026": "展開接続図・単線結線図・JIS 記号をまとめた図面読解ノート完成版がある状態。",
    "ISS-027": "理論（磁気・静電気）の過去問正答率60%以上、電力科目の入門が完了した状態。",
    "ISS-028": "理論（電子回路）と電力（変電・配電）の基本問題が解ける状態。",
    "ISS-029": "理論・電力の過去問周回が完了し、弱点が3つ以内に絞れている状態。機械入門も開始済み。",
    "ISS-030": "理論・電力・法規の直前仕上げが完了し、合格ラインに自信がある状態。",
    "ISS-031": "電験三種を受験し、自己採点結果と次年度の方針が記録されている状態。",
    "ISS-032": "タイマー・カウンタ応用の PLC 課題が完成し、社内設備への適用アイデアがある状態。",
    "ISS-033": "社内改善提案1件が完成し、上長に提出 or 提出準備が整った状態。",
    "ISS-034": "仕様書テンプレート自動生成ツールが動作し、業務改善の実例1件が記録されている状態。",
    "ISS-035": "制御図面の記号・用語を自動抽出するツールが動作し、制御×AI の成果物1件がある状態。",
    "ISS-036": "AI 活用事例をまとめたポートフォリオ v1 が GitHub で公開されている状態。",
    "ISS-037": "職務経歴書ドラフトが完成し、電気×制御×AI のストーリーが1本通っている状態。",
    "ISS-038": "職務経歴書 v2 と面接ストーリー集が完成し、模擬面接で使える状態。",
    "ISS-039": "ポートフォリオ最終版と面接デモが準備され、応募開始できる状態。",
    "ISS-040": "転職エージェント2社以上に登録し、初回面談で方向性が確認できた状態。",
    "ISS-041": "3社以上に応募し、面接を通じて市場フィードバックを得ている状態。",
    "ISS-042": "内定を獲得し、24か月計画の全フェーズ完了記録が残っている状態。",
    "ISS-043": "NIST SP 800-82 の要点ノートが完成し、IT/OT の違いを説明できる状態。",
    "ISS-044": "ICS アーキテクチャと基本対策を整理したノートがあり、ISS-043 と接続できる状態。",
    "ISS-045": "PLC / 制御盤向けのセキュリティ観点チェックリストが完成した状態。",
    "ISS-046": "制御×AI 成果物に OT セキュリティ視点が加わり、ポートフォリオに統合できる状態。",
    "ISS-R01": "今週の完了・未完了・弱点が記録され、来週の最優先3件が決まっている状態。",
    "ISS-R02": "今月の進捗サマリーが記録され、来月の計画が調整されている状態。",
    "ISS-R03": "今四半期の成果と課題が記録され、次四半期のフェーズ移行判断ができる状態。",
    "ISS-R04": "技術メモが月1件以上作成され、面接素材として使える形で保存されている状態。",
}


def replace_inputs(text: str) -> str:
    """各 Issue の inputs セクションを新しい参照元に差し替え"""
    lines = text.split("\n")
    i = 0
    current_issue_id = None
    while i < len(lines):
        line = lines[i]
        # issue id の検出: YAML リスト項目は "- id: ISS-xxx" で始まる
        m = re.match(r"- id: (\S+)", line)
        if m:
            current_issue_id = m.group(1)

        # inputs: の検出 (2 spaces indentation)
        if line.strip() == "inputs:" and current_issue_id in INPUTS:
            # inputs リストの行を消費
            j = i + 1
            while j < len(lines) and lines[j].startswith("  - "):
                j += 1
            # 新しい inputs に差し替え
            new_lines = ["  inputs:"]
            for item in INPUTS[current_issue_id]:
                new_lines.append(f"  - {item}")
            lines[i:j] = new_lines
            del INPUTS[current_issue_id]  # 同一 id の二重置換を防ぐ
            i += len(new_lines)
            continue
        i += 1
    return "\n".join(lines)


def replace_outcomes(text: str) -> str:
    """汎用 outcome テンプレートを Issue 固有の記述に差し替え"""
    lines = text.split("\n")
    i = 0
    current_issue_id = None
    while i < len(lines):
        line = lines[i]
        # YAML リスト項目は "- id: ISS-xxx" で始まる
        m = re.match(r"- id: (\S+)", line)
        if m:
            current_issue_id = m.group(1)

        if current_issue_id in OUTCOMES and line.strip().startswith("outcome:"):
            new_val = OUTCOMES[current_issue_id]
            lines[i] = f"  outcome: {new_val}"
            del OUTCOMES[current_issue_id]
        i += 1
    return "\n".join(lines)


def main() -> int:
    text = SEED.read_text(encoding="utf-8")

    text = replace_inputs(text)
    text = replace_outcomes(text)

    SEED.write_text(text, encoding="utf-8")
    print(f"Updated {len(INPUTS)} inputs + {len(OUTCOMES)} outcomes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
