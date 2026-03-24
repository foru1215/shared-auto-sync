#!/usr/bin/env python3
"""
Phase 2: Structural changes to project-seed.yaml
- Period extension
- New phases, labels, fields, milestones, epics
- ISS-047~050 modifications
"""
import sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SEED = Path(__file__).resolve().parent.parent / "data" / "project-seed.yaml"


def r(old, new, text, label=""):
    if old not in text:
        print(f"  WARNING: anchor not found for '{label or old[:60]}'")
        return text
    text = text.replace(old, new, 1)
    print(f"  OK: {label or old[:60]}")
    return text


def main():
    text = SEED.read_text(encoding="utf-8")

    # ── 1. Period extension ──
    print("=== Period Extension ===")
    text = r(
        "  end_date: '2028-03-31'",
        "  end_date: '2031-03-31'\n  phase_1_end: '2028-03-31'\n  phase_2_end: '2031-03-31'",
        text, "end_date → 2031 + phase fields"
    )

    # ── 2. New phases (after phase-6) ──
    print("\n=== New Phases ===")
    new_phases = """- id: phase-aws-basic
  name: AWS 基礎構築期
  start: '2026-05-01'
  end: '2026-12-31'
  priority: p1
  focus:
  - AWS Cloud Practitioner (CLF-C02) 取得
  - AWS アカウント設定・無料枠活用
  - SAA 学習開始
  success_criteria:
  - CLF-C02 合格
  - AWS アカウントが稼働し基本操作ができる
  note: Phase 1 と並行実施。電工試験後の余力でAWSを開始
- id: phase-aws-iot
  name: AWS IoT 実践期
  start: '2027-01-01'
  end: '2027-09-30'
  priority: p1
  focus:
  - AWS IoT Core + PLC シミュレータ連携
  - Greengrass エッジ体験
  - SiteWise データモデリング
  success_criteria:
  - IoT Core 経由で PLC データを受信できる
  - Greengrass デバイスが動作する
  note: PLC強化・電験準備と並行でIoT連携を構築
- id: phase-3pillar
  name: 3柱統合期
  start: '2027-10-01'
  end: '2028-03-31'
  priority: p0
  focus:
  - 制御 × AI × AWS の統合ポートフォリオ構築
  - Lambda + Step Functions 実装
  - 転職活動との接続
  success_criteria:
  - 3本柱統合デモが動作する
  - ポートフォリオに組み込まれている
  note: AI スペシャリスト強化期・転職仕上げ期と重なる
- id: phase-highclass
  name: ハイクラス深化期
  start: '2028-04-01'
  end: '2029-09-30'
  priority: p1
  focus:
  - SAP 学習・取得
  - 高度 AWS アーキテクチャ実践
  - エキスパート領域への深化
  success_criteria:
  - SAP 取得
  - 高度実装経験の蓄積
- id: phase-expert
  name: エキスパート到達期
  start: '2029-10-01'
  end: '2031-03-31'
  priority: p1
  focus:
  - AWS Specialty 取得
  - 業界エキスパートとしての実績構築
  success_criteria:
  - Specialty 取得
  - ハイクラス到達
"""
    text = r(
        "  - 全成果物の最終整備完了\nepics:",
        "  - 全成果物の最終整備完了\n" + new_phases + "epics:",
        text, "new phases after phase-6"
    )

    # ── 3. New Epics (E-AWS, E-ENG) ──
    print("\n=== New Epics ===")
    # Insert after E-CAR. E-CAR ends, then milestones: starts.
    # After side-biz deletion, E-CAR is the last epic.
    new_epics = """- id: E-AWS
  name: AWS Cloud & IoT
  description: AWS 資格取得（CLF → SAA → SAP）・IoT Core / Greengrass / SiteWise
    / Lambda / Bedrock 統合までを含む。制御柱・AI柱と並ぶ独立柱。
  labels:
  - area:aws
  - pillar:aws
  priority: p1
- id: E-ENG
  name: English Support
  description: AWS・AI・制御の3本柱を支える英語力の補強。英語は独立柱ではなく、AWS・AI・制御の3本柱を支える補助スキルとして扱う。
  labels:
  - area:english
  priority: p2
"""
    # E-CAR block: ends with "priority: p1\n" right before "milestones:"
    # We need a unique anchor. E-CAR has specific content.
    text = r(
        "  - area:career\n  priority: p1\nmilestones:",
        "  - area:career\n  priority: p1\n" + new_epics + "milestones:",
        text, "E-AWS + E-ENG epics"
    )

    # ── 4. New milestones ──
    print("\n=== New Milestones ===")
    new_ms = """- id: M-2026-Q3-AWS
  title: '2026 Q3: AWS 基礎 + CLP'
  start: '2026-07-01'
  end: '2026-09-30'
  goal: AWS Cloud Practitioner (CLF-C02) 取得
- id: M-2026-Q4-AWS
  title: '2026 Q4: SAA 取得'
  start: '2026-10-01'
  end: '2026-12-31'
  goal: AWS Solutions Architect Associate 合格
- id: M-2027-Q2-AWS
  title: '2027 Q2: IoT 連携構築'
  start: '2027-04-01'
  end: '2027-06-30'
  goal: AWS IoT Core + PLC シミュレータ連携が動作
- id: M-2027-Q4-AWS
  title: '2027 Q4: SAP 学習開始'
  start: '2027-10-01'
  end: '2027-12-31'
  goal: SAP 学習計画策定
- id: M-2029-Q2
  title: '2029 Q2: SAP 取得'
  start: '2029-04-01'
  end: '2029-06-30'
  goal: AWS Solutions Architect Professional 合格
- id: M-2030-Q1
  title: '2030 Q1: Specialty 取得'
  start: '2030-01-01'
  end: '2030-03-31'
  goal: AWS Specialty 認定取得
"""
    # Insert before labels: section
    text = r(
        "labels:\n  area:",
        new_ms + "labels:\n  area:",
        text, "new milestones"
    )

    # ── 5. New labels ──
    print("\n=== New Labels ===")
    # area:aws and area:english (after area:security)
    text = r(
        "  - name: area:security\n    color: 0052cc\n    description: OT / ICS セキュリティ\n  tool:",
        "  - name: area:security\n    color: 0052cc\n    description: OT / ICS セキュリティ\n"
        "  - name: area:aws\n    color: ff9900\n    description: AWS クラウド\n"
        "  - name: area:english\n    color: 7057ff\n    description: 英語学習\n  tool:",
        text, "area:aws + area:english labels"
    )

    # pillar labels (before phase:)
    text = r(
        "  phase:\n  - name: phase:written-exam",
        "  pillar:\n"
        "  - name: pillar:control\n    color: 008672\n    description: 制御柱\n"
        "  - name: pillar:ai\n    color: 1d76db\n    description: AI柱\n"
        "  - name: pillar:aws\n    color: ff9900\n    description: AWS柱\n"
        "  - name: pillar:integration\n    color: e36209\n    description: 3柱統合\n"
        "  phase:\n  - name: phase:written-exam",
        text, "pillar labels"
    )

    # phase:aws-basic etc. (after phase:career-finish)
    text = r(
        "  - name: phase:career-finish\n    color: e4e669\n    description: 転職仕上げ期\nproject_fields:",
        "  - name: phase:career-finish\n    color: e4e669\n    description: 転職仕上げ期\n"
        "  - name: phase:aws-basic\n    color: ff9900\n    description: AWS 基礎構築期\n"
        "  - name: phase:aws-iot\n    color: ffb84d\n    description: AWS IoT 実践期\n"
        "  - name: phase:3pillar\n    color: e36209\n    description: 3柱統合期\n"
        "  - name: phase:highclass\n    color: d73a49\n    description: ハイクラス深化期\n"
        "  - name: phase:expert\n    color: 6f42c1\n    description: エキスパート到達期\n"
        "project_fields:",
        text, "phase:aws-* labels"
    )

    # ── 6. Field option additions ──
    print("\n=== Field Options ===")
    # 分野: add AWS, 英語
    text = r(
        "  - セキュリティ\n- name: フェーズ",
        "  - セキュリティ\n  - AWS\n  - 英語\n- name: フェーズ",
        text, "分野: +AWS +英語"
    )

    # フェーズ: add new phases
    text = r(
        "  - 転職仕上げ\n- name: 期日",
        "  - 転職仕上げ\n  - AWS基礎\n  - AWS_IoT実践\n  - 3柱統合\n  - ハイクラス深化\n  - エキスパート到達\n- name: 期日",
        text, "フェーズ: +AWS基礎 etc."
    )

    # タスク種別: add AWS
    text = r(
        "  - セットアップ\n- name: レビューサイクル",
        "  - セットアップ\n  - AWS\n- name: レビューサイクル",
        text, "タスク種別: +AWS"
    )

    # Quarter: add 2028-Q2 through 2031-Q1
    text = r(
        "  - 2028-Q1\n- name: キャリアリンク",
        "  - 2028-Q1\n  - 2028-Q2\n  - 2028-Q3\n  - 2028-Q4\n"
        "  - 2029-Q1\n  - 2029-Q2\n  - 2029-Q3\n  - 2029-Q4\n"
        "  - 2030-Q1\n  - 2030-Q2\n  - 2030-Q3\n  - 2030-Q4\n"
        "  - 2031-Q1\n- name: キャリアリンク",
        text, "Quarter: +2028-Q2..2031-Q1"
    )

    # ── 7. ISS-047: Epic E-AI → E-AWS, labels ──
    print("\n=== ISS-047 Modifications ===")
    # Change epic
    # Find ISS-047 block's epic line
    text = re.sub(
        r"(- id: ISS-047\n  title: '[^']+'\n  body: [^\n]+\n  epic: )E-AI",
        r"\g<1>E-AWS",
        text, count=1
    )
    print("  OK: ISS-047 epic → E-AWS")

    # Change area:ai → area:aws for ISS-047
    # This is tricky - need to find within ISS-047 block only
    # Use a targeted approach: find the ISS-047 block, replace within it
    iss047_match = re.search(r"(- id: ISS-047\n(?:  [^\n]+\n)+)", text)
    if iss047_match:
        block = iss047_match.group(0)
        new_block = block.replace("  - area:ai\n", "  - area:aws\n  - pillar:aws\n", 1)
        # Also change title prefix [AI] → [AWS]
        new_block = new_block.replace("[AI] 2026-05:", "[AWS] 2026-05:", 1)
        text = text.replace(block, new_block, 1)
        print("  OK: ISS-047 labels + title prefix")

    # ── 8. ISS-048: Epic, labels, monthly_bucket, blocked_by ──
    print("\n=== ISS-048 Modifications ===")
    iss048_match = re.search(r"(- id: ISS-048\n(?:  [^\n]+\n)+)", text)
    if iss048_match:
        block = iss048_match.group(0)
        new_block = block
        # Epic
        new_block = new_block.replace("  epic: E-AI\n", "  epic: E-AWS\n", 1)
        # Labels
        new_block = new_block.replace("  - area:ai\n", "  - area:aws\n  - pillar:aws\n", 1)
        # Title prefix
        new_block = new_block.replace("[AI] 2026-09:", "[AWS] 2026-11:", 1)
        # Monthly bucket: 2026-09 → 2026-11
        new_block = new_block.replace("  monthly_bucket: 2026-09\n",
                                       "  monthly_bucket: '2026-11'  # 後ろ倒し: SAA+制御並走負荷を考慮\n", 1)
        # Due date: keep or push back? Instruction says push back.
        # Original due: 2026-10-31, with monthly_bucket 2026-09.
        # With pushback to 2026-11, due_date should be 2026-12-31
        new_block = new_block.replace("  due_date: '2026-10-31'\n",
                                       "  due_date: '2026-12-31'\n", 1)
        # Add ISS-047 to blocked_by (after ISS-020)
        new_block = new_block.replace(
            "  blocked_by:\n  - ISS-020\n",
            "  blocked_by:\n  - ISS-020\n  - ISS-047\n", 1
        )
        text = text.replace(block, new_block, 1)
        print("  OK: ISS-048 epic/labels/bucket/blocked_by updated")

    # ── 9. ISS-049: Complete overwrite ──
    print("\n=== ISS-049 Complete Overwrite ===")
    iss049_match = re.search(r"(- id: ISS-049\n(?:  [^\n]+\n)+)", text)
    if iss049_match:
        old_block = iss049_match.group(0)
        new_049 = """- id: ISS-049
  title: '[SEC] 2027-03: AWS IoT Device Defender 体験 + OT 環境評価ラボ'
  body: |-
    ## 概要
    このIssueは AWS IoT 実践期 に進める セキュリティ学習Issue です。
    AWS IoT Device Defender を使い、ISS-048 で構築した IoT Core 環境に対して監査（Audit）と検知（Detect）の基本を体験する。
    狙い: OTセキュリティを「概念」ではなく「AWS上の具体運用」で説明できる状態を作る。

    ## 完了条件
    - AWS IoT Device Defender の Audit 機能を1回以上実行した
    - 少なくとも3件の監査項目について「何を見ているか」を説明できる
    - IoT Core 環境の改善アクションを3件以上記録した
    - 実施記録を Markdown で GitHub に残した

    ## 今回の到達目標
    - Device Defender が「何を守るか」「どこまで守れるか」を説明できる状態
    - 作るもの: Audit 実施記録 + 改善メモ + 簡易構成図
    - 重点: Audit / Detect / Policy の違いを理解すること

    ## 最初の一手（5分で開始できる行動）
    - [ ] AWS IoT Device Defender のドキュメントを開き、Audit のチェック項目一覧を確認する

    ## タスクリスト
    - [ ] AWS IoT Device Defender の公式ドキュメントを読む
    - [ ] ISS-048 の IoT Core 環境が利用できることを確認する
    - [ ] Audit を実行し、検出内容を記録する
    - [ ] 検出結果から改善アクションを3件以上洗い出す
    - [ ] OT観点で「現場的に意味がある注意点」を日本語で整理する
    - [ ] Markdown レポートを GitHub に保存する

    ## 補足メモ
    - 使う資料・入力:
      - AWS IoT Device Defender ドキュメント https://docs.aws.amazon.com/iot-device-defender/
      - ISS-048 の AWS IoT Core 構成
      - ISS-044, ISS-045 の OT セキュリティ学習内容
    - 依存Issue:
      - ISS-044
      - ISS-045
      - ISS-048
    - 時間の目安: 休日 2-3時間 × 2〜3回
    - 想定セッション数: 3-5 sessions
    - 負荷感: Medium
    - 注意: これはペンテストではない。AWS の監査・設定観点で「安全な構成」を確認する学習である
  epic: E-SEC
  phase: phase-aws-iot
  labels:
  - area:security
  - area:aws
  - priority:p1
  - phase:aws-iot
  - pillar:aws
  - pillar:integration
  priority: p1
  milestone: M-2027-Q1
  due_date: '2027-03-31'
  recurring: false
  dependencies:
  - ISS-044
  - ISS-045
  - ISS-048
  evidence_type: ドキュメント
  monthly_bucket: '2027-03'
  quarter: 2027-Q1
  career_link: OTセキュリティを AWS IoT 環境で説明できる証拠
  ai_link: Claude Code で Audit 結果の分析を補助する
  task_type: study
  work_steps:
  - AWS IoT Device Defender の公式ドキュメントを読む
  - ISS-048 の IoT Core 環境が利用できることを確認する
  - Audit を実行し、検出内容を記録する
  - 検出結果から改善アクションを3件以上洗い出す
  - OT観点で「現場的に意味がある注意点」を日本語で整理する
  - Markdown レポートを GitHub に保存する
  deliverables:
  - Audit 実施記録
  - 改善メモ
  - 簡易構成図
  evidence_to_keep:
  - Audit 実施記録（Markdown）
  - 検出結果と改善アクションの記録
  dod:
  - Audit 実施済み
  - 検出結果の記録あり
  - 改善アクションを3件以上説明可能
  active_from: '2027-03-01'
  deferred_until: null
  blocked_by:
  - ISS-044
  - ISS-045
  - ISS-048
  exam_priority_guard: false
  review_note: Audit / Detect / Policy の観点でレビューする。面接で語れるポイントを整理する。
  outcome: ISS-048 の IoT Core 環境に対して、監査・検知・改善提案を説明できる状態
  next_action: AWS IoT Device Defender の公式ドキュメントを開き、Audit チェック一覧を確認する
  why_this_matters: OTセキュリティをAWS上の具体運用で説明できる差別化ポイント
  device: PC
  inputs:
  - "AWS IoT Device Defender ドキュメント https://docs.aws.amazon.com/iot-device-defender/"
  - ISS-048 の AWS IoT Core 構成
  - ISS-044, ISS-045 の OT セキュリティ学習内容
  things_to_make:
  - Audit 実施記録 + 改善メモ + 簡易構成図
  completion_check:
  - Audit 実施済み / 検出結果の記録あり / 改善アクションを3件以上説明可能
  daily_execution:
  - '休日 セッション1 (2-3h): AWS IoT Device Defender の公式ドキュメントを読む → Audit のチェック項目を確認'
  - '休日 セッション2 (2-3h): ISS-048 の IoT Core 環境で Audit を実行し、検出内容を記録する'
  - '休日 セッション3 (2-3h): 検出結果から改善アクションを洗い出し、Markdown レポートを作成'
  time_block: 休日 2-3時間
  estimate: 3-5 sessions
  energy: Medium
  focus: AWS IoT Device Defender の Audit / Detect の体験
"""
        text = text.replace(old_block, new_049, 1)
        print("  OK: ISS-049 completely rewritten")

    # ── 10. ISS-050: Epic + labels ──
    print("\n=== ISS-050 Modifications ===")
    iss050_match = re.search(r"(- id: ISS-050\n(?:  [^\n]+\n)+)", text)
    if iss050_match:
        block = iss050_match.group(0)
        new_block = block
        # Title: [AI] → [AI/AWS]
        new_block = new_block.replace("[AI] 2027-11:", "[AI/AWS] 2027-11:", 1)
        # Add E-AWS as secondary epic (add comment)
        new_block = new_block.replace(
            "  epic: E-AI\n",
            "  epic: E-AI  # E-AWS にも所属（3柱交点）\n", 1
        )
        # Add pillar labels
        new_block = new_block.replace(
            "  - area:ai\n",
            "  - area:ai\n  - area:aws\n  - pillar:ai\n  - pillar:aws\n  - pillar:integration\n", 1
        )
        text = text.replace(block, new_block, 1)
        print("  OK: ISS-050 labels/title/epic updated")

    SEED.write_text(text, encoding="utf-8")
    print(f"\nPhase 2 done. File: {len(text)} bytes")


if __name__ == "__main__":
    main()
