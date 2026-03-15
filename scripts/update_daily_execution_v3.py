# -*- coding: utf-8 -*-
"""
daily_execution v3 - 勉強集中版

改善ポイント:
  1. 【focus】ブラケット廃止 → コンテキストとして吸収
  2. 昼 (30分) = 想起練習（朝の内容を本を閉じて思い出す）→ 管理タスクなし
  3. 記録作業を 夕 の最後15分だけに集約
  4. 動詞を「解く」「書く」「再現する」「実装する」に統一（「確認する」系排除）
  5. 試験当日 (ISS-006/009/031) は専用フォーマット
  6. 平日あり → 3ブロック、週末/休日のみ → セッション形式（work_steps を直接使用）
"""
import sys
import yaml

SEED_PATH = 'data/project-seed.yaml'

EXAM_DAY_IDS = {'ISS-006', 'ISS-009', 'ISS-031'}


def is_weekend_task(issue: dict) -> bool:
    tb = issue.get('time_block', '')
    if '\u5e73\u65e5' in tb:  # 平日 が含まれていれば平日3ブロック
        return False
    return '\u9031\u672b' in tb or '\u4f11\u65e5' in tb  # 週末 or 休日


def trim(s, n=55):
    s = str(s).strip().rstrip('。').rstrip('.')
    return s[:n] if len(s) > n else s


def ws(issue, idx=0):
    steps = issue.get('work_steps', [])
    if not steps:
        return trim(issue.get('next_action', ''), 55)
    i = min(idx, len(steps) - 1)
    return trim(steps[i], 55)


def evd(issue):
    ev = issue.get('evidence_to_keep', [])
    return trim(ev[0], 50) if ev else 'Issue コメントに成果を記録する'


def build(issue: dict) -> list:
    iid       = issue['id']
    task_type = issue.get('task_type', 'study')
    energy    = issue.get('energy', 'Medium')
    steps     = issue.get('work_steps', [])
    focus_raw = trim(issue.get('focus', ''), 30)
    ev        = evd(issue)

    # ── 試験当日 ──────────────────────────────────────────────────────
    if iid in EXAM_DAY_IDS:
        return [
            u'朝 (60分): 弱点ポイントだけ3つ見直す（それ以上は見ない）→ 持ち物・会場を最終確認する',
            u'昼 (30分): 軽食を取る（新しい問題は解かない・これまで積んだ練習を信じる）',
            u'夕 (試験後): 試験を受ける → 終了30分以内に「できた・できなかった問題」を Issue に記録する',
        ]

    # ── 週末/休日専用タスク（セッション形式）────────────────────────
    if is_weekend_task(issue):
        n = len(steps)
        if n == 0:
            s = [trim(issue.get('next_action', ''), 55)] * 3
        elif n == 1:
            s = [trim(steps[0], 55), focus_raw + u'を深掘りする', ev]
        elif n == 2:
            s = [trim(steps[0], 55), trim(steps[1], 55), ev]
        else:
            mid = n // 2
            s = [trim(steps[0], 55), trim(steps[mid], 55), trim(steps[-1], 55)]

        if task_type == 'career':
            return [
                f'土日 セッション1 (3h): {s[0]}',
                f'土日 セッション2 (3h): {s[1]}（声に出して1回話してみる）',
                f'土日 セッション3 (3h): {s[2]} → 模擬面接1回やって違和感を修正 → {ev}',
            ]
        if task_type == 'ai':
            return [
                f'土日 セッション1 (3h): {s[0]}',
                f'土日 セッション2 (3h): {s[1]}',
                f'土日 セッション3 (3h): {s[2]} → GitHub に保存 → {ev}',
            ]
        return [
            f'土日 セッション1 (3h): {s[0]}',
            f'土日 セッション2 (3h): {s[1]}',
            f'土日 セッション3 (3h): {s[2]} → 完成度確認 → {ev}',
        ]

    # ── 平日3ブロック ─────────────────────────────────────────────────

    # exam（学習日）
    if task_type == 'exam':
        topic = focus_raw or u'今日の範囲'
        return [
            f'朝 (60分): {topic}の過去問10問を時間計って解く（採点して正答率をノートに書く）',
            u'昼 (30分): 朝の誤問だけ解き直す → 間違いの理由を1行で書く（答えは見ない）',
            f'夕 (2h): 誤答を科目別に分類して弱点1科目を集中演習 → {ev}',
        ]

    # study / Low（自己学習型オンライン）
    if task_type == 'study' and energy == 'Low':
        step0 = ws(issue, 0)
        return [
            f'朝 (60分): {step0}（1モジュールを完走する）',
            u'昼 (30分): 完了モジュールの重要語彙3つを紙に書いて暗記確認する（テキスト不可）',
            f'夕 (2h): 模擬試験を1回分解いて全問の正誤理由を書く → {ev}',
        ]

    # study / Medium（テキスト・ノート系）
    if task_type == 'study':
        step0 = ws(issue, 0)
        stepL = ws(issue, -1)
        return [
            f'朝 (60分): {step0}（声に出しながら読み、余白に自分の言葉でメモを書く）',
            u'昼 (30分): 本を閉じて朝の要点を5行でノートに書く（想起練習・答え合わせは夕にする）',
            f'夕 (2h): 昼のノートを採点し → {stepL} → 面接で「私はXを確認しました」と言えるか口で試す → {ev}',
        ]

    # setup
    if task_type == 'setup':
        step0 = ws(issue, 0)
        stepL = ws(issue, -1)
        return [
            f'朝 (60分): 手順書を最後まで読んでから {step0}',
            u'昼 (30分): 詰まった箇所を別アプローチで試す or 手順を読み直す',
            f'夕 (2h): {stepL} → 動作確認 → {ev}',
        ]

    # evidence / High（評価・ラボ系）
    if task_type == 'evidence' and energy == 'High':
        step0 = ws(issue, 0)
        stepL = ws(issue, -1)
        return [
            f'朝 (60分): 今日のゴールを1行決めてから {step0}',
            u'昼 (30分): 午前の成果を1行で振り返る → 次の手順を頭の中で順番に追う',
            f'夕 (2h): {stepL} → スクリーンショットを保存 → {ev}',
        ]

    # evidence / Medium（ノート・ドキュメント系）
    if task_type == 'evidence':
        step0 = ws(issue, 0)
        stepL = ws(issue, -1)
        return [
            f'朝 (60分): {step0}（重要箇所に印をつけながら読む）',
            u'昼 (30分): 朝に読んだ内容を技術3点だけノートに書く（本は閉じる）',
            f'夕 (2h): {stepL} → 面接で口頭説明できるか1回試す → {ev}',
        ]

    # ai / High（Claude Code セッション）
    if task_type == 'ai':
        return [
            u'朝 (60分): 前回セッションのログを読み直す → 今日取り組む1テーマを1行で書く',
            u'昼 (30分): テーマに関する公式ドキュメントを30分読む（メモを取る）',
            f'夕 (2h): Claude Code でセッション実施（{focus_raw}） → GitHub に保存 → {ev}',
        ]

    # plc / High
    if task_type == 'plc':
        step0 = ws(issue, 0)
        stepL = ws(issue, -1)
        return [
            f'朝 (60分): {step0}（ラダー回路を手書きして入出力の動作順序を紙で追う）',
            u'昼 (30分): 手書きのラダーを見ずに動作順序を頭で再現できるか試す',
            f'夕 (2h): GX Works3 を起動して {stepL} → シミュレーション動作確認 → {ev}',
        ]

    # deliverable / High
    if task_type == 'deliverable':
        step0 = ws(issue, 0)
        stepL = ws(issue, -1)
        return [
            f'朝 (60分): 今日完成させる1機能を1行で書いてから {step0}',
            u'昼 (30分): 朝に書いた1行を見直して設計の修正点があれば書き直す',
            f'夕 (2h): {stepL} → 動作確認 → {ev}',
        ]

    # career / Medium
    if task_type == 'career':
        step0 = ws(issue, 0)
        stepL = ws(issue, -1)
        return [
            f'朝 (60分): {step0}（STAR形式で1エピソードを頭の中で組み立てる）',
            u'昼 (30分): 朝に組み立てたエピソードをメモ帳に箇条書きで書き出す',
            f'夕 (2h): {stepL} → 口頭で1回話す練習をする → {ev}',
        ]

    # fallback
    step0 = ws(issue, 0)
    stepL = ws(issue, -1)
    return [
        f'朝 (60分): {step0}',
        u'昼 (30分): 朝の内容を本を閉じて思い出しノートに書く',
        f'夕 (2h): {stepL} → {ev}',
    ]


# ── 適用 ──────────────────────────────────────────────────────────────

def format_lines(items):
    return [f"  - '{item}'\n" for item in items]


def replace_de(lines, start_idx, new_items):
    i = start_idx + 1
    while i < len(lines) and lines[i].startswith('  - '):
        i += 1
    return lines[:start_idx + 1] + format_lines(new_items) + lines[i:]


with open(SEED_PATH, encoding='utf-8') as f:
    raw = f.readlines()

seed = yaml.safe_load(open(SEED_PATH, encoding='utf-8'))
issue_map = {i['id']: i for i in seed['issues'] if not i['id'].startswith('ISS-R')}

updated = list(raw)
n = 0
for iid, issue in issue_map.items():
    new_de = build(issue)
    in_i, de_idx = False, None
    for idx, line in enumerate(updated):
        if line.strip() == f'- id: {iid}':
            in_i = True
        elif line.strip().startswith('- id: ISS') and iid not in line and in_i:
            break
        if in_i and line.strip() == 'daily_execution:':
            de_idx = idx
            break
    if de_idx is None:
        print(f'WARN: no daily_execution for {iid}')
        continue
    updated = replace_de(updated, de_idx, new_de)
    n += 1

with open(SEED_PATH, 'w', encoding='utf-8') as f:
    f.writelines(updated)

print(f'Updated {n} issues. File saved.')

# ── スポット確認 ──────────────────────────────────────────────────────
import json
seed2 = yaml.safe_load(open(SEED_PATH, encoding='utf-8'))
spot = {i['id']: i.get('daily_execution', [])
        for i in seed2['issues']
        if i['id'] in ('ISS-001','ISS-006','ISS-011','ISS-020',
                       'ISS-034','ISS-037','ISS-045','ISS-047','ISS-048')}
with open('debug_v3_spot.json', 'w', encoding='utf-8') as f:
    json.dump(spot, f, ensure_ascii=False, indent=2)
print('Spot check written to debug_v3_spot.json')
