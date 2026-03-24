#!/usr/bin/env python3
"""
Phase 3: Add new Issues ISS-051~064 to project-seed.yaml
"""
import sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SEED = Path(__file__).resolve().parent.parent / "data" / "project-seed.yaml"

# All new issues as YAML text
NEW_ISSUES = """\
- id: ISS-051
  title: '[AWS] 2026-05: AWS アカウント + 無料枠セットアップ'
  body: |-
    AWS アカウントを作成し、無料枠の範囲と請求アラートを把握する。
    IAM ユーザー・MFA 設定・CloudTrail 有効化まで完了し、安全に使える状態を作る。
  epic: E-AWS
  phase: phase-aws-basic
  labels:
  - area:aws
  - pillar:aws
  - phase:aws-basic
  - priority:p1
  priority: p1
  milestone: M-2026-Q2
  due_date: '2026-05-31'
  recurring: false
  dependencies: []
  evidence_type: ドキュメント
  monthly_bucket: '2026-05'
  quarter: 2026-Q2
  career_link: AWS 環境を自力で立ち上げられる基礎力の証拠
  ai_link: Claude Code で AWS CLI スクリプトを効率的に作成する
  task_type: setup
  work_steps:
  - AWS アカウントを作成する
  - IAM ユーザーを作成し MFA を設定する
  - CloudTrail を有効化する
  - 請求アラート（$5, $10）を設定する
  - 無料枠の範囲を確認しメモする
  deliverables:
  - AWS アカウント設定メモ
  - 請求アラート設定のスクリーンショット
  evidence_to_keep:
  - 設定手順メモ（GitHub）
  - スクリーンショット
  dod:
  - AWS アカウントが作成され IAM + MFA が設定済み
  - 請求アラートが動作している
  active_from: '2026-05-01'
  deferred_until: null
  blocked_by: []
  exam_priority_guard: true
  review_note: セキュリティ設定の漏れがないか確認する。
  outcome: AWS アカウントが安全に使える状態。
  next_action: AWS 無料アカウント https://aws.amazon.com/free/ にアクセスしてサインアップを開始する。
  why_this_matters: 全AWS学習の起点。安全な環境がなければ何も始まらない。
  device: PC
  inputs:
  - "AWS 無料アカウント https://aws.amazon.com/free/"
  - "IAM ベストプラクティス https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"
  things_to_make:
  - AWS アカウント設定メモ
  completion_check:
  - AWS マネジメントコンソールにログインできる
  - IAM ユーザー + MFA が設定済み
  - 請求アラートが設定済み
  daily_execution:
  - '休日 (60分): アカウント作成 → IAM + MFA → 請求アラート → メモ保存'
  time_block: 休日 60分
  estimate: 1 session
  energy: Low
  focus: AWS アカウントの安全なセットアップ
- id: ISS-052
  title: '[AWS] 2026-08: SAA 学習開始（AWS Solutions Architect Associate）'
  body: |-
    CLF-C02 取得後、SAA-C03 の学習を開始する。
    公式学習パス + Udemy/書籍で主要サービス（VPC, EC2, S3, RDS, IAM, Lambda）を理解する。
  epic: E-AWS
  phase: phase-aws-basic
  labels:
  - area:aws
  - pillar:aws
  - phase:aws-basic
  - priority:p1
  priority: p1
  milestone: M-2026-Q4-AWS
  due_date: '2026-11-30'
  recurring: false
  dependencies:
  - ISS-047
  evidence_type: ノート
  monthly_bucket: '2026-08'
  quarter: 2026-Q3
  career_link: SAA はクラウドエンジニアの基本資格。転職市場での価値が高い。
  ai_link: Claude Code で AWS 構成図や CloudFormation テンプレートを生成する
  task_type: study
  work_steps:
  - SAA-C03 の出題範囲を確認する
  - AWS Skill Builder の SAA 学習パスを開始する
  - VPC / EC2 / S3 / RDS / IAM / Lambda を順に学習する
  - 模擬試験を2回以上実施する
  deliverables:
  - SAA 学習ノート
  - 模擬試験結果記録
  evidence_to_keep:
  - 学習ログ（GitHub）
  - 模擬試験スコア
  dod:
  - 主要サービスの基本概念を説明できる
  - 模擬試験で 720 点以上を安定して取れる
  active_from: '2026-08-01'
  deferred_until: '2026-07-31'
  blocked_by:
  - ISS-047
  exam_priority_guard: false
  review_note: 模擬試験スコアの推移と弱点分野を確認する。
  outcome: SAA の主要範囲を理解し、受験準備が整った状態。
  next_action: SAA-C03 の公式試験ガイドを確認し、出題ドメインを把握する。
  why_this_matters: SAA は AWS 実務力の証明。IoT / Bedrock 活用の基盤になる。
  device: PC
  inputs:
  - "AWS Skill Builder https://skillbuilder.aws/"
  - "SAA-C03 試験ガイド https://aws.amazon.com/certification/certified-solutions-architect-associate/"
  things_to_make:
  - SAA 学習ノート
  completion_check:
  - 出題範囲の全ドメインを学習済み
  - 模擬試験スコア 720+ を2回以上記録
  daily_execution:
  - '朝 (60分): AWS Skill Builder で1モジュールを完走する'
  - '昼 (30分): 前日の学習内容を復習する'
  time_block: 平日朝 60分 + 週末 120分
  estimate: 8-12 sessions
  energy: High
  focus: SAA-C03 の主要サービス理解と模擬試験
- id: ISS-053
  title: '[AWS] 2026-12: SAA 合格'
  body: |-
    SAA-C03 試験を受験し合格する。
    CLF-C02 + SAA の2資格で AWS の基礎〜設計レベルを証明する。
  epic: E-AWS
  phase: phase-aws-basic
  labels:
  - area:aws
  - pillar:aws
  - phase:aws-basic
  - priority:p0
  priority: p0
  milestone: M-2026-Q4-AWS
  due_date: '2026-12-31'
  recurring: false
  dependencies:
  - ISS-052
  evidence_type: 認定証
  monthly_bucket: '2026-12'
  quarter: 2026-Q4
  career_link: SAA は転職市場で最も評価される AWS 資格
  ai_link: ''
  task_type: exam
  work_steps:
  - 模擬試験で最終確認する
  - 試験を予約し受験する
  - 結果を記録する
  deliverables:
  - SAA 認定証
  - 受験記録
  evidence_to_keep:
  - AWS Certification ページのスクリーンショット
  - 認定証PDF
  dod:
  - SAA-C03 試験に合格した
  - 認定証が取得できている
  active_from: '2026-12-01'
  deferred_until: '2026-11-30'
  blocked_by:
  - ISS-052
  exam_priority_guard: true
  review_note: 試験日前後2週間は SAA 優先。
  outcome: SAA 合格。AWS 基礎〜設計レベルの証明。
  next_action: Pearson VUE で SAA-C03 の試験日を予約する。
  why_this_matters: CLF + SAA の2資格で AWS 基盤力を証明する
  device: PC
  inputs:
  - ISS-052 の学習成果
  - "Pearson VUE https://www.pearsonvue.com/aws/"
  things_to_make:
  - 受験記録メモ
  completion_check:
  - SAA-C03 に合格した
  - 認定証を取得した
  daily_execution:
  - '試験前2週間: 朝 (60分) 模擬試験 + 弱点補強'
  time_block: 試験前2週間集中
  estimate: 2-3 sessions
  energy: High
  focus: SAA 合格
- id: ISS-054
  title: '[AWS] 2027-04: Greengrass エッジ体験'
  body: |-
    AWS IoT Greengrass を使い、エッジデバイスでの Lambda 実行と IoT Core 連携を体験する。
    ISS-048 の IoT Core 環境を拡張し、エッジ側でのデータ前処理を実装する。
  epic: E-AWS
  phase: phase-aws-iot
  labels:
  - area:aws
  - pillar:aws
  - phase:aws-iot
  - priority:p1
  priority: p1
  milestone: M-2027-Q2-AWS
  due_date: '2027-04-30'
  recurring: false
  dependencies:
  - ISS-048
  - ISS-053
  evidence_type: コード
  monthly_bucket: '2027-04'
  quarter: 2027-Q2
  career_link: エッジコンピューティング経験は制御×クラウドの差別化要素
  ai_link: Claude Code でエッジ Lambda のスクリプトを生成する
  task_type: AWS
  work_steps:
  - Greengrass Core ソフトウェアをローカル環境にインストールする
  - エッジ Lambda を作成し、IoT Core からのメッセージを処理する
  - ISS-048 の PLC シミュレータデータをエッジで前処理する
  - 動作確認と構成図を記録する
  deliverables:
  - Greengrass セットアップ手順
  - エッジ Lambda スクリプト
  - 構成図
  evidence_to_keep:
  - GitHub リポジトリ
  - 動作確認スクリーンショット
  dod:
  - Greengrass Core が動作している
  - エッジ Lambda で PLC データを前処理できている
  active_from: '2027-04-01'
  deferred_until: '2027-03-31'
  blocked_by:
  - ISS-048
  - ISS-053
  exam_priority_guard: false
  review_note: エッジ処理の実用性とデモ性を確認する。
  outcome: Greengrass でエッジ処理が動作し、IoT Core と連携できている状態。
  next_action: Greengrass 公式ドキュメントのチュートリアルを開始する。
  why_this_matters: OT × クラウドのエッジ層を理解する。実案件でのGreengrass活用に直結。
  device: PC / ローカル環境
  inputs:
  - "AWS IoT Greengrass ドキュメント https://docs.aws.amazon.com/greengrass/"
  - ISS-048 の IoT Core 環境
  things_to_make:
  - Greengrass セットアップ手順 + エッジ Lambda スクリプト
  completion_check:
  - Greengrass Core が動作確認済み
  - エッジ Lambda で PLC データを処理できている
  daily_execution:
  - '休日 セッション1 (3h): Greengrass Core のインストールと初期設定'
  - '休日 セッション2 (3h): エッジ Lambda の作成と IoT Core 連携'
  time_block: 休日 3時間 × 2-3回
  estimate: 3-4 sessions
  energy: Medium
  focus: Greengrass エッジコンピューティングの基本体験
- id: ISS-055
  title: '[AWS] 2027-06: SiteWise でデータモデリング'
  body: |-
    AWS IoT SiteWise を使い、PLC シミュレータの制御データを産業用データモデルで管理する。
    IoT Core → SiteWise のパイプラインを構築し、ダッシュボードで可視化する。
  epic: E-AWS
  phase: phase-aws-iot
  labels:
  - area:aws
  - pillar:aws
  - phase:aws-iot
  - priority:p1
  priority: p1
  milestone: M-2027-Q2-AWS
  due_date: '2027-06-30'
  recurring: false
  dependencies:
  - ISS-048
  - ISS-054
  evidence_type: コード
  monthly_bucket: '2027-06'
  quarter: 2027-Q2
  career_link: 産業 IoT データモデリングは制御 DX の中核スキル
  ai_link: Claude Code で SiteWise モデル定義を効率化する
  task_type: AWS
  work_steps:
  - SiteWise のアセットモデルを作成する
  - IoT Core ルールで SiteWise にデータを送る
  - SiteWise Monitor でダッシュボードを作成する
  - 制御データの可視化結果を記録する
  deliverables:
  - SiteWise アセットモデル定義
  - ダッシュボードスクリーンショット
  - 構成図
  evidence_to_keep:
  - GitHub リポジトリ
  - ダッシュボードスクリーンショット
  dod:
  - SiteWise でデータモデルが動作している
  - ダッシュボードで PLC データを可視化できている
  active_from: '2027-05-01'
  deferred_until: '2027-04-30'
  blocked_by:
  - ISS-048
  - ISS-054
  exam_priority_guard: false
  review_note: データモデルの設計品質とダッシュボードの見やすさを確認する。
  outcome: SiteWise で産業用データモデリングが動作し、可視化ダッシュボードが完成した状態。
  next_action: SiteWise 公式ドキュメントのチュートリアルを開始する。
  why_this_matters: 産業 IoT のデータ管理・可視化は実案件の核心
  device: PC
  inputs:
  - "AWS IoT SiteWise ドキュメント https://docs.aws.amazon.com/iot-sitewise/"
  - ISS-048 の IoT Core パイプライン
  - ISS-054 の Greengrass 環境
  things_to_make:
  - SiteWise アセットモデル + ダッシュボード
  completion_check:
  - SiteWise アセットモデルが作成済み
  - ダッシュボードで PLC データが表示されている
  daily_execution:
  - '休日 セッション1 (3h): SiteWise アセットモデルの作成'
  - '休日 セッション2 (3h): IoT Core → SiteWise パイプライン構築'
  - '休日 セッション3 (3h): ダッシュボード作成と記録'
  time_block: 休日 3時間 × 3回
  estimate: 3-5 sessions
  energy: Medium
  focus: 産業用データモデリングと可視化
- id: ISS-056
  title: '[AWS] 2027-09: Lambda + Step Functions で制御ワークフロー'
  body: |-
    Lambda と Step Functions を使い、IoT Core データの異常検知→通知→ログ記録のワークフローを構築する。
    制御×クラウドのサーバーレスパターンを体験する。
  epic: E-AWS
  phase: phase-aws-iot
  labels:
  - area:aws
  - pillar:aws
  - phase:aws-iot
  - priority:p1
  priority: p1
  milestone: M-2027-Q3
  due_date: '2027-09-30'
  recurring: false
  dependencies:
  - ISS-055
  evidence_type: コード
  monthly_bucket: '2027-09'
  quarter: 2027-Q3
  career_link: サーバーレスアーキテクチャは AWS 実務の基本パターン
  ai_link: Claude Code で Lambda 関数と Step Functions 定義を生成する
  task_type: AWS
  work_steps:
  - Lambda 関数で IoT Core データの異常判定を実装する
  - Step Functions で異常検知→SNS 通知→S3 ログ保存のワークフローを構築する
  - ISS-055 の SiteWise データをトリガーとして動作確認する
  - 構成図と動作ログを記録する
  deliverables:
  - Lambda 関数コード
  - Step Functions 定義（ASL）
  - 構成図
  evidence_to_keep:
  - GitHub リポジトリ
  - 動作確認ログ
  dod:
  - 異常検知→通知→ログ記録のワークフローが動作している
  - Step Functions の実行ログが確認できる
  active_from: '2027-07-01'
  deferred_until: '2027-06-30'
  blocked_by:
  - ISS-055
  exam_priority_guard: false
  review_note: ワークフローの実用性とエラーハンドリングを確認する。
  outcome: サーバーレスワークフローで IoT データの異常検知→通知が自動化された状態。
  next_action: Lambda の公式チュートリアルを開始する。
  why_this_matters: Lambda + Step Functions は AWS の実装パターンの基本。実案件でも活用。
  device: PC
  inputs:
  - "AWS Lambda ドキュメント https://docs.aws.amazon.com/lambda/"
  - "AWS Step Functions ドキュメント https://docs.aws.amazon.com/step-functions/"
  - ISS-055 の SiteWise パイプライン
  things_to_make:
  - Lambda + Step Functions ワークフロー
  completion_check:
  - 異常検知ワークフローが動作確認済み
  - 構成図とログが保存されている
  daily_execution:
  - '休日 セッション1 (3h): Lambda 関数の作成と単体テスト'
  - '休日 セッション2 (3h): Step Functions ワークフロー構築'
  - '休日 セッション3 (3h): 統合テストと記録'
  time_block: 休日 3時間 × 3-4回
  estimate: 4-6 sessions
  energy: High
  focus: サーバーレスワークフローの構築
- id: ISS-057
  title: '[AWS] Phase 2 概要: SAP 学習・取得（2028-04〜2029-09）'
  body: |-
    Phase 2 の概要Issue。AWS Solutions Architect Professional の学習と取得。
    詳細タスクは Phase 2 開始時に具体化する。
  epic: E-AWS
  phase: phase-highclass
  labels:
  - area:aws
  - pillar:aws
  - phase:highclass
  - priority:p2
  priority: p2
  milestone: M-2029-Q2
  due_date: '2029-06-30'
  recurring: false
  dependencies:
  - ISS-053
  evidence_type: 認定証
  monthly_bucket: ''
  quarter: 2029-Q2
  career_link: SAP はハイクラスポジションへのパスポート
  ai_link: ''
  task_type: AWS
  work_steps:
  - Phase 2 開始時に詳細化する
  deliverables:
  - SAP 認定証
  evidence_to_keep:
  - 認定証PDF
  dod:
  - SAP 試験に合格した
  active_from: '2028-04-01'
  deferred_until: '2028-03-31'
  blocked_by:
  - ISS-053
  exam_priority_guard: false
  review_note: Phase 2 開始時に計画を具体化する。
  outcome: SAP 取得。ハイクラス到達の基盤。
  next_action: Phase 2 開始時に学習計画を策定する。
  why_this_matters: ハイクラス深化期の中核資格
  device: PC
  inputs: []
  things_to_make:
  - SAP 学習計画
  completion_check:
  - SAP に合格した
  daily_execution:
  - Phase 2 開始時に策定
  time_block: TBD
  estimate: TBD
  energy: High
  focus: SAP 取得
- id: ISS-058
  title: '[AWS] Phase 2 概要: Specialty 取得（2029-10〜2030-03）'
  body: |-
    Phase 2 の概要Issue。AWS Specialty 認定（IoT or Security or ML）の取得。
    詳細タスクは Phase 2 中盤で具体化する。
  epic: E-AWS
  phase: phase-expert
  labels:
  - area:aws
  - pillar:aws
  - phase:expert
  - priority:p2
  priority: p2
  milestone: M-2030-Q1
  due_date: '2030-03-31'
  recurring: false
  dependencies:
  - ISS-057
  evidence_type: 認定証
  monthly_bucket: ''
  quarter: 2030-Q1
  career_link: Specialty はエキスパート到達の証明
  ai_link: ''
  task_type: AWS
  work_steps:
  - Phase 2 中盤で詳細化する
  deliverables:
  - Specialty 認定証
  evidence_to_keep:
  - 認定証PDF
  dod:
  - Specialty 試験に合格した
  active_from: '2029-10-01'
  deferred_until: '2029-09-30'
  blocked_by:
  - ISS-057
  exam_priority_guard: false
  review_note: Phase 2 中盤で計画を具体化する。
  outcome: Specialty 取得。エキスパート到達。
  next_action: Phase 2 中盤に Specialty の種類を決定する。
  why_this_matters: エキスパート到達の証明
  device: PC
  inputs: []
  things_to_make:
  - Specialty 学習計画
  completion_check:
  - Specialty に合格した
  daily_execution:
  - Phase 2 中盤で策定
  time_block: TBD
  estimate: TBD
  energy: High
  focus: Specialty 取得
- id: ISS-059
  title: '[AWS] Phase 2 概要: 高度アーキテクチャ実践（2030-04〜2031-03）'
  body: |-
    Phase 2 の概要Issue。高度 AWS アーキテクチャの実践とエキスパート領域の確立。
    詳細タスクは Phase 2 後半で具体化する。
  epic: E-AWS
  phase: phase-expert
  labels:
  - area:aws
  - pillar:aws
  - phase:expert
  - priority:p2
  priority: p2
  milestone: ''
  due_date: '2031-03-31'
  recurring: false
  dependencies:
  - ISS-058
  evidence_type: ポートフォリオ
  monthly_bucket: ''
  quarter: 2031-Q1
  career_link: ハイクラス到達の最終証明
  ai_link: ''
  task_type: AWS
  work_steps:
  - Phase 2 後半で詳細化する
  deliverables:
  - 高度アーキテクチャ実践記録
  evidence_to_keep:
  - ポートフォリオ
  dod:
  - 高度実践記録が残っている
  active_from: '2030-04-01'
  deferred_until: '2030-03-31'
  blocked_by:
  - ISS-058
  exam_priority_guard: false
  review_note: Phase 2 後半で計画を具体化する。
  outcome: エキスパート領域の確立。
  next_action: Phase 2 後半に計画を策定する。
  why_this_matters: 5年計画の最終到達点
  device: PC
  inputs: []
  things_to_make:
  - 実践記録
  completion_check:
  - 実践記録が残っている
  daily_execution:
  - Phase 2 後半で策定
  time_block: TBD
  estimate: TBD
  energy: High
  focus: エキスパート到達
- id: ISS-060
  title: '[ENG] 2026-06: 技術英単語100語（AWS / 制御 / AI）'
  body: |-
    AWS / 制御 / AI 領域の技術英単語を100語習得する。
    AWS ドキュメントや技術記事を読むための語彙基盤を作る。
  epic: E-ENG
  phase: phase-aws-basic
  labels:
  - area:english
  - priority:p2
  priority: p2
  milestone: M-2026-Q2
  due_date: '2026-06-30'
  recurring: false
  dependencies: []
  evidence_type: ノート
  monthly_bucket: '2026-06'
  quarter: 2026-Q2
  career_link: 技術英語力は外資・グローバル企業への応募に必須
  ai_link: Claude Code で英単語リストと例文を効率的に生成する
  task_type: study
  work_steps:
  - AWS / 制御 / AI の技術文書から頻出英単語を抽出する
  - 100語のリストを作成する
  - Anki などで反復学習する
  deliverables:
  - 技術英単語100語リスト
  evidence_to_keep:
  - 単語リスト（GitHub）
  dod:
  - 100語リストが完成している
  - 80語以上を説明できる
  active_from: '2026-05-01'
  deferred_until: null
  blocked_by: []
  exam_priority_guard: false
  review_note: 主計画を圧迫しない範囲で進める。英語はP2。
  outcome: 技術英語の基本語彙100語を習得した状態。
  next_action: AWS ドキュメントから頻出単語を10語抽出する。
  why_this_matters: 英語は3本柱を支える補助スキル。語彙がなければドキュメントが読めない。
  device: PC / スマホ
  inputs:
  - AWS ドキュメント（英語版）
  - 制御系英語用語集
  things_to_make:
  - 技術英単語100語リスト
  completion_check:
  - 100語リストが GitHub に保存されている
  daily_execution:
  - '通勤時間 (15分): 5語ずつ覚える'
  time_block: 通勤 15分
  estimate: 20日間
  energy: Low
  focus: 技術英単語の習得
- id: ISS-061
  title: '[ENG] 2027-01: AWS ドキュメント英読（週1ページ）'
  body: |-
    AWS 公式ドキュメントを英語で週1ページ読む習慣を作る。
    ISS-060 の語彙基盤を活用し、読解力を実践的に鍛える。
  epic: E-ENG
  phase: phase-aws-iot
  labels:
  - area:english
  - area:aws
  - priority:p2
  priority: p2
  milestone: M-2027-Q1
  due_date: '2027-03-31'
  recurring: false
  dependencies:
  - ISS-060
  evidence_type: ノート
  monthly_bucket: '2027-01'
  quarter: 2027-Q1
  career_link: 英語ドキュメントを読める力は日常業務に直結
  ai_link: Claude Code で不明な技術表現の解説を得る
  task_type: study
  work_steps:
  - 毎週1ページの AWS ドキュメント（英語）を選ぶ
  - 読んで要約を日本語でメモする
  - 不明な表現をリストに追加する
  deliverables:
  - 英読ログ（週次）
  evidence_to_keep:
  - 英読ログ（GitHub）
  dod:
  - 12週以上の英読ログが残っている
  active_from: '2027-01-01'
  deferred_until: '2026-12-31'
  blocked_by:
  - ISS-060
  exam_priority_guard: false
  review_note: 英語は主計画を遅らせない範囲で。P2維持。
  outcome: AWS ドキュメントを英語で読む習慣が定着した状態。
  next_action: 今週読む AWS ドキュメントのページを1つ選ぶ。
  why_this_matters: 英語ドキュメントの読解は AWS 実務の日常
  device: PC
  inputs:
  - "AWS ドキュメント（英語版）https://docs.aws.amazon.com/"
  things_to_make:
  - 英読ログ
  completion_check:
  - 12件以上の英読ログが GitHub に保存されている
  daily_execution:
  - '週末 (30分): AWS ドキュメント1ページを英語で読み、要約をメモする'
  time_block: 週末 30分
  estimate: 12+ sessions
  energy: Low
  focus: AWS ドキュメントの英語読解
- id: ISS-062
  title: '[ENG] 2027-06: 英語 README 作成'
  body: |-
    ポートフォリオリポジトリの README を英語で作成する。
    制御 × AI × AWS の成果物を英語で説明できるようにする。
  epic: E-ENG
  phase: phase-aws-iot
  labels:
  - area:english
  - area:career
  - priority:p2
  priority: p2
  milestone: M-2027-Q2
  due_date: '2027-06-30'
  recurring: false
  dependencies:
  - ISS-061
  evidence_type: ドキュメント
  monthly_bucket: '2027-06'
  quarter: 2027-Q2
  career_link: 英語 README は海外チームとの協業力の証明
  ai_link: Claude Code で英語 README のドラフトを生成する
  task_type: deliverable
  work_steps:
  - ポートフォリオの主要成果物を英語で説明する構成を決める
  - Claude Code で英語 README のドラフトを生成する
  - ネイティブチェックまたは Grammarly で校正する
  deliverables:
  - 英語 README
  evidence_to_keep:
  - GitHub リポジトリの README.md
  dod:
  - 英語 README が GitHub に公開されている
  - 技術的内容が正確に伝わる
  active_from: '2027-05-01'
  deferred_until: '2027-04-30'
  blocked_by:
  - ISS-061
  exam_priority_guard: false
  review_note: 英語表現の正確性と技術的な分かりやすさを確認する。
  outcome: 英語 README が公開され、海外からもポートフォリオが理解できる状態。
  next_action: README に含める成果物のリストを日本語で作る。
  why_this_matters: グローバルに見せられるポートフォリオの仕上げ
  device: PC
  inputs:
  - ポートフォリオリポジトリ
  - ISS-060〜061 の英語学習成果
  things_to_make:
  - 英語 README
  completion_check:
  - 英語 README が GitHub に公開されている
  daily_execution:
  - '休日 (2h): README 構成決定 → ドラフト → 校正 → 公開'
  time_block: 休日 2時間
  estimate: 2-3 sessions
  energy: Medium
  focus: 英語 README の作成
- id: ISS-064
  title: '[統合] 2028-01: 3本柱統合ポートフォリオ — 制御盤図面 AI 解析デモ'
  body: |-
    制御 × AI × AWS の3本柱を統合した最重要ポートフォリオ。
    PLC シミュレータ → Greengrass → IoT Core → SiteWise / Lambda / Bedrock / S3 / QuickSight の
    フルパイプラインを構築し、制御盤図面のAI解析デモとして完成させる。

    この Issue は 3本柱の交差点を示す最重要成果物であり、
    転職面接での技術デモ・ポートフォリオの核として位置づける。
  epic: E-AI  # E-AWS にも所属（3柱交点）
  phase: phase-3pillar
  labels:
  - area:ai
  - area:aws
  - area:control
  - pillar:ai
  - pillar:aws
  - pillar:control
  - pillar:integration
  - phase:3pillar
  - priority:p0
  priority: p0
  milestone: M-2028-Q1
  due_date: '2028-01-31'
  recurring: false
  dependencies:
  - ISS-050
  - ISS-054
  - ISS-055
  - ISS-056
  evidence_type: ポートフォリオ
  monthly_bucket: '2028-01'
  quarter: 2028-Q1
  career_link: 制御 × AI × AWS の三角形がポートフォリオの核。転職面接の最大武器。
  ai_link: Bedrock + Claude Code で制御データの AI 分析を実装する
  task_type: deliverable
  work_steps:
  - PLC シミュレータ → Greengrass → IoT Core のデータパイプラインを統合する
  - SiteWise でデータモデリング + Lambda / Step Functions でワークフロー構築
  - Bedrock で制御データの AI 分析を実装する
  - S3 + QuickSight で結果の可視化
  - デモ動画 or 画面録画を作成する
  - GitHub リポジトリに公開する
  deliverables:
  - 3本柱統合デモ（動作するシステム）
  - 構成図
  - デモ動画
  - README（日英）
  evidence_to_keep:
  - GitHub リポジトリ
  - デモ動画
  - 構成図
  dod:
  - フルパイプラインが動作している
  - 面接で3分以内にデモできる
  - GitHub に公開済み
  active_from: '2027-11-01'
  deferred_until: '2027-10-31'
  blocked_by:
  - ISS-050
  - ISS-054
  - ISS-055
  - ISS-056
  exam_priority_guard: false
  review_note: デモの完成度と面接での説明しやすさを確認する。3本柱の接続が見えるか。
  outcome: 制御 × AI × AWS の統合デモが面接用ポートフォリオとして完成した状態。
  next_action: ISS-050〜056 の成果物を統合する計画を立てる。
  why_this_matters: 3本柱統合の証明。転職活動の最大武器。実案件の図面AI解析計画に直結。
  device: PC
  inputs:
  - ISS-050 の Amazon Bedrock 環境
  - ISS-054 の Greengrass エッジ環境
  - ISS-055 の SiteWise データモデル
  - ISS-056 の Lambda + Step Functions ワークフロー
  - ISS-020〜024 の PLC シミュレータ環境
  things_to_make:
  - 3本柱統合デモシステム + README + デモ動画
  completion_check:
  - フルパイプラインが動作確認済み
  - GitHub に公開されている
  - デモ動画が作成されている
  daily_execution:
  - '休日 セッション1 (3h): データパイプラインの統合'
  - '休日 セッション2 (3h): AI 分析 + 可視化'
  - '休日 セッション3 (3h): デモ動画作成 + README + 公開'
  time_block: 休日 3時間 × 5-8回
  estimate: 8-12 sessions
  energy: High
  focus: 3本柱統合ポートフォリオの完成
"""


def main():
    text = SEED.read_text(encoding="utf-8")

    # Insert new issues before ISS-R01
    anchor = "- id: ISS-R01\n"
    if anchor not in text:
        print("ERROR: anchor ISS-R01 not found!")
        sys.exit(1)

    text = text.replace(anchor, NEW_ISSUES + anchor, 1)

    SEED.write_text(text, encoding="utf-8")

    # Count new issues
    new_count = sum(1 for line in NEW_ISSUES.splitlines() if line.startswith("- id: ISS-"))
    print(f"Added {new_count} new issues before ISS-R01")
    print(f"File: {len(text)} bytes")


if __name__ == "__main__":
    main()
