#!/usr/bin/env python3
"""GitHub Project の英語フィールド・選択肢・タイトルを日本語に一括移行するスクリプト。"""
import subprocess
import json
import sys
import re
import pathlib

PROJECT_ID = "PVT_kwHOD5C6os4BRuWs"
REPO = "foru1215/shared-auto-sync"
SEED_PATH = pathlib.Path(__file__).parent.parent / "data" / "project-seed.yaml"
SYNC_SCRIPT_PATH = pathlib.Path(__file__).parent / "github_project_sync.py"

# ─── 翻訳マッピング ────────────────────────────────────────────────

PREFIX_MAP = {
    "[E-LIC]": "[資格]",
    "[E-AI]":  "[AI]",
    "[E-EVD]": "[証跡]",
    "[E-CTL]": "[制御]",
    "[E-DRW]": "[図面]",
    "[E-PLC]": "[PLC]",
    "[E-CAR]": "[キャリア]",
    "[E-SEC]": "[SEC]",
    "[Review]": "[レビュー]",
}

# GitHub Project SingleSelectField option renames: field_id -> [(option_id, old_name, new_name, color)]
FIELD_RENAMES = {
    # フィールド名の変更: field_id -> new_name
    "PVTSSF_lAHOD5C6os4BRuWszg_d-e4": "ステータス",      # Status
    "PVTSSF_lAHOD5C6os4BRuWszg_d-gY": "優先度",          # Priority
    "PVTSSF_lAHOD5C6os4BRuWszg_d-gc": "分野",            # Area
    "PVTSSF_lAHOD5C6os4BRuWszg_d-hM": "フェーズ",        # Phase
    "PVTF_lAHOD5C6os4BRuWszg_d-h4":   "期日",            # Due Date
    "PVTSSF_lAHOD5C6os4BRuWszg_d-i8": "エビデンス種別",  # Evidence Type
    "PVTF_lAHOD5C6os4BRuWszg_d-jA":   "月次バケット",    # Monthly Bucket
    "PVTF_lAHOD5C6os4BRuWszg_d-jI":   "キャリアリンク",  # Career Link
    "PVTF_lAHOD5C6os4BRuWszg_d-j0":   "AIリンク",        # AI Link
    "PVTSSF_lAHOD5C6os4BRuWszg_d-lI": "タスク種別",      # Task Type
    "PVTSSF_lAHOD5C6os4BRuWszg_d-lM": "レビューサイクル", # Review Cycle
    "PVTF_lAHOD5C6os4BRuWszg_eQwE":   "活動期間",        # Active Window
    "PVTF_lAHOD5C6os4BRuWszg_eQwI":   "延期期日",        # Deferred Until
    "PVTSSF_lAHOD5C6os4BRuWszg_eQwM": "延期フラグ",      # Deferred Flag
    "PVTF_lAHOD5C6os4BRuWszg_eQw4":   "ブロック元",      # Blocked By
    "PVTSSF_lAHOD5C6os4BRuWszg_eQxk": "完了定義",        # DoD Ready
    "PVTSSF_lAHOD5C6os4BRuWszg_eQy8": "エビデンス準備",  # Evidence Ready
    "PVTSSF_lAHOD5C6os4BRuWszg_eQzo": "試験優先ガード",  # Exam Priority Guard
    "PVTF_lAHOD5C6os4BRuWszg_egfc":   "開始日",          # Start Date
    "PVTF_lAHOD5C6os4BRuWszg_egfg":   "終了日",          # End Date
}

# SingleSelectField のオプション変更: field_id -> [(option_id, new_name, color)]
OPTION_RENAMES = {
    # Status (ステータス)
    "PVTSSF_lAHOD5C6os4BRuWszg_d-e4": [
        ("4a8e48d0", "バックログ", "GRAY"),
        ("fa0d324b", "未着手",    "BLUE"),
        ("8612dc0a", "進行中",    "YELLOW"),
        ("f4359256", "完了",      "GREEN"),
        ("fd4701e8", "ブロック中", "RED"),
        ("96443ab2", "延期",      "ORANGE"),
    ],
    # Area (分野)
    "PVTSSF_lAHOD5C6os4BRuWszg_d-gc": [
        ("9ddb2b2d", "資格",       "BLUE"),
        ("29267fe8", "制御",       "GREEN"),
        ("6c20842d", "PLC",        "YELLOW"),
        ("bc5ae5bf", "図面",       "ORANGE"),
        ("23324bbc", "実習",       "PINK"),
        ("a74a1d18", "エビデンス", "PURPLE"),
        ("77f66509", "AI",         "BLUE"),
        ("80fe089b", "キャリア",   "GREEN"),
        ("ac569181", "セキュリティ","RED"),
    ],
    # Phase (フェーズ)
    "PVTSSF_lAHOD5C6os4BRuWszg_d-hM": [
        ("d5718a8f", "学科試験",         "RED"),
        ("af160e31", "実技試験",         "ORANGE"),
        ("eb44cf93", "制御基礎",         "BLUE"),
        ("afb332af", "PLC強化",          "YELLOW"),
        ("1e602678", "電験準備",         "PURPLE"),
        ("a020939d", "AIスペシャリスト", "GREEN"),
        ("06c870fd", "転職仕上げ",       "PINK"),
    ],
    # Evidence Type (エビデンス種別)
    "PVTSSF_lAHOD5C6os4BRuWszg_d-i8": [
        ("2d225a35", "ノート",         "GRAY"),
        ("bd1785f3", "コード",         "BLUE"),
        ("df162cb7", "ドキュメント",   "GREEN"),
        ("b2e5de21", "認定証",         "YELLOW"),
        ("05e67925", "ポートフォリオ", "ORANGE"),
        ("15434e61", "ストーリー",     "PINK"),
    ],
    # Task Type (タスク種別)
    "PVTSSF_lAHOD5C6os4BRuWszg_d-lI": [
        ("d7c85435", "エピック",       "PURPLE"),
        ("3547b339", "フェーズカード", "BLUE"),
        ("ee64fdff", "目標条件",       "GREEN"),
        ("c7d00d35", "試験",           "RED"),
        ("3237671f", "学習",           "BLUE"),
        ("970be246", "PLC",            "YELLOW"),
        ("f306c0a9", "エビデンス",     "ORANGE"),
        ("c619448f", "AIスキル",       "PURPLE"),
        ("0b471c0a", "キャリア準備",   "GREEN"),
        ("69bd0528", "定期レビュー",   "PINK"),
        ("27d66be1", "成果物",         "PINK"),
        ("649cbbea", "セットアップ",   "GRAY"),
    ],
    # Review Cycle (レビューサイクル)
    "PVTSSF_lAHOD5C6os4BRuWszg_d-lM": [
        ("3a718266", "週次",     "BLUE"),
        ("ff815f65", "月次",     "GREEN"),
        ("381a67ed", "四半期次", "ORANGE"),
        ("59f7b192", "なし",     "GRAY"),
    ],
    # Deferred Flag (延期フラグ)
    "PVTSSF_lAHOD5C6os4BRuWszg_eQwM": [
        ("8b2ce602", "アクティブ", "BLUE"),
        ("c3425f8f", "延期",       "ORANGE"),
        ("c9c9d243", "N/A",        "GRAY"),
    ],
    # DoD Ready (完了定義)
    "PVTSSF_lAHOD5C6os4BRuWszg_eQxk": [
        ("ec45c9a4", "完了",   "GREEN"),
        ("28329ed1", "未完了", "RED"),
        ("e528afe1", "N/A",    "GRAY"),
    ],
    # Evidence Ready (エビデンス準備)
    "PVTSSF_lAHOD5C6os4BRuWszg_eQy8": [
        ("e7c5e28b", "完了",   "GREEN"),
        ("4760bef9", "未完了", "RED"),
        ("608974e8", "N/A",    "GRAY"),
    ],
    # Exam Priority Guard (試験優先ガード)
    "PVTSSF_lAHOD5C6os4BRuWszg_eQzo": [
        ("f8205a0c", "試験優先", "RED"),
        ("62a70a36", "通常",     "GRAY"),
        ("205948c1", "N/A",      "GRAY"),
    ],
}

# seed の evidence_type 値の変換
EVIDENCE_TYPE_MAP = {
    "Note":        "ノート",
    "Code":        "コード",
    "Document":    "ドキュメント",
    "Certification": "認定証",
    "Portfolio":   "ポートフォリオ",
    "Story":       "ストーリー",
}

# sync script の文字列置換マッピング
SYNC_SCRIPT_REPLACEMENTS = [
    # TASK_TYPE_TO_FIELD values
    ('"Phase Card"',      '"フェーズカード"'),
    ('"Win Condition"',   '"目標条件"'),
    ('"Exam"',            '"試験"'),
    ('"Study"',           '"学習"'),
    ('"Evidence"',        '"エビデンス"'),
    ('"AI Skill Building"', '"AIスキル"'),
    ('"Career Prep"',     '"キャリア準備"'),
    ('"Recurring Review"', '"定期レビュー"'),
    ('"Deliverable"',     '"成果物"'),
    ('"Setup"',           '"セットアップ"'),
    ('"Epic"',            '"エピック"'),
    # REVIEW_CYCLE_TO_FIELD values
    ('"Weekly"',          '"週次"'),
    ('"Monthly"',         '"月次"'),
    ('"Quarterly"',       '"四半期次"'),
    # compute_status / infer_status return values
    ('"Deferred"',        '"延期"'),
    ('"Backlog"',         '"バックログ"'),
    ('"Blocked"',         '"ブロック中"'),
    ('"Todo"',            '"未着手"'),
    ('"Done"',            '"完了"'),
    ('"In Progress"',     '"進行中"'),
    # area_from_labels values
    ('"License"',         '"資格"'),
    ('"Control"',         '"制御"'),
    ('"Drawings"',        '"図面"'),
    ('"Practice"',        '"実習"'),
    ('"Security"',        '"セキュリティ"'),
    ('"Career"',          '"キャリア"'),
    # phase_from_labels values
    ('"Written Exam"',    '"学科試験"'),
    ('"Practical Exam"',  '"実技試験"'),
    ('"Control Foundation"', '"制御基礎"'),
    ('"PLC Growth"',      '"PLC強化"'),
    ('"Denken Ramp"',     '"電験準備"'),
    ('"AI Specialist"',   '"AIスペシャリスト"'),
    ('"Career Finish"',   '"転職仕上げ"'),
    # option_color field name keys
    ('"Status"',          '"ステータス"'),
    ('"Priority"',        '"優先度"'),
    ('"Task Type"',       '"タスク種別"'),
    ('"Review Cycle"',    '"レビューサイクル"'),
    ('"DoD Ready"',       '"完了定義"'),
    ('"Evidence Ready"',  '"エビデンス準備"'),
    ('"Deferred Flag"',   '"延期フラグ"'),
    ('"Exam Priority Guard"', '"試験優先ガード"'),
    # option_color option name keys
    ('"Exam Priority"',   '"試験優先"'),
    ('"Normal"',          '"通常"'),
    ('"Active"',          '"アクティブ"'),
    ('"Ready"',           '"完了"'),
    ('"Missing"',         '"未完了"'),
    # field_values dict keys in planned_issue_from_issue & build_planned_*
    ('"Area"',            '"分野"'),
    ('"Phase"',           '"フェーズ"'),
    ('"Due Date"',        '"期日"'),
    ('"Evidence Type"',   '"エビデンス種別"'),
    ('"Monthly Bucket"',  '"月次バケット"'),
    ('"Career Link"',     '"キャリアリンク"'),
    ('"AI Link"',         '"AIリンク"'),
    ('"Active Window"',   '"活動期間"'),
    ('"Deferred Until"',  '"延期期日"'),
    ('"Blocked By"',      '"ブロック元"'),
    ('"Start Date"',      '"開始日"'),
    ('"End Date"',        '"終了日"'),
    # validate / audit field name references
    ('"Status"',          '"ステータス"'),   # already covered above
    # build_project_readme title
    ('# Career Transition 24-Month Plan', '# 24ヶ月キャリア転換計画'),
]


def run_graphql(query: str) -> dict:
    """gh api graphql でクエリを実行して結果を返す。"""
    result = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=json.dumps({"query": query}),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"  GraphQL error: {result.stderr.strip()}", file=sys.stderr)
        return {}
    data = json.loads(result.stdout)
    if "errors" in data:
        print(f"  GraphQL errors: {data['errors']}", file=sys.stderr)
    return data


def step1_update_project_title():
    print("① プロジェクトタイトルを更新...")
    query = f"""
    mutation {{
      updateProjectV2(input: {{
        projectId: "{PROJECT_ID}",
        title: "24ヶ月キャリア転換計画"
      }}) {{
        projectV2 {{ title }}
      }}
    }}
    """
    r = run_graphql(query)
    title = r.get("data", {}).get("updateProjectV2", {}).get("projectV2", {}).get("title", "?")
    print(f"   → {title}")


def step2_rename_field_options():
    print("② GitHub Project フィールド選択肢を日本語に変更...")
    for field_id, options in OPTION_RENAMES.items():
        field_new_name = FIELD_RENAMES.get(field_id, "")
        # id は渡せない。name/color/description のみ
        options_gql = "\n".join(
            f'{{name: "{name}", color: {color}, description: ""}}'
            for _oid, name, color in options
        )
        query = f"""
        mutation {{
          updateProjectV2Field(input: {{
            fieldId: "{field_id}",
            name: "{field_new_name}",
            singleSelectOptions: [{options_gql}]
          }}) {{
            projectV2Field {{
              ... on ProjectV2SingleSelectField {{ id name options {{ name }} }}
            }}
          }}
        }}
        """
        r = run_graphql(query)
        f = r.get("data", {}).get("updateProjectV2Field", {}).get("projectV2Field", {})
        opts = [o["name"] for o in f.get("options", [])]
        print(f"   {field_new_name}: {opts}")


def step3_rename_text_fields():
    print("③ テキスト/日付フィールド名を日本語に変更...")
    text_field_ids = [fid for fid in FIELD_RENAMES if fid not in OPTION_RENAMES]
    for field_id in text_field_ids:
        new_name = FIELD_RENAMES[field_id]
        query = f"""
        mutation {{
          updateProjectV2Field(input: {{
            fieldId: "{field_id}",
            name: "{new_name}"
          }}) {{
            projectV2Field {{
              ... on ProjectV2Field {{ id name }}
            }}
          }}
        }}
        """
        r = run_graphql(query)
        f = r.get("data", {}).get("updateProjectV2Field", {}).get("projectV2Field", {})
        print(f"   {f.get('name', '?')} ({field_id[:20]}...)")


def step4_update_seed_evidence_type():
    print("④ seed の evidence_type を日本語に変換...")
    text = SEED_PATH.read_text(encoding="utf-8")
    count = 0
    for en, ja in EVIDENCE_TYPE_MAP.items():
        new_text = re.sub(
            rf"^(\s+evidence_type:\s+){re.escape(en)}\s*$",
            rf"\g<1>{ja}",
            text,
            flags=re.MULTILINE,
        )
        if new_text != text:
            count += text.count(f"evidence_type: {en}")
            text = new_text
    SEED_PATH.write_text(text, encoding="utf-8")
    print(f"   {count} 件更新")


def step5_update_seed_prefixes():
    print("⑤ seed の Issue タイトルプレフィックスを日本語に変換...")
    text = SEED_PATH.read_text(encoding="utf-8")
    count = 0
    for en, ja in PREFIX_MAP.items():
        n = text.count(en)
        text = text.replace(en, ja)
        count += n
    SEED_PATH.write_text(text, encoding="utf-8")
    print(f"   {count} 件更新")


def step6_update_sync_script():
    print("⑥ sync スクリプトの文字列を日本語に置換...")
    text = SYNC_SCRIPT_PATH.read_text(encoding="utf-8")
    count = 0
    seen = set()
    for old, new in SYNC_SCRIPT_REPLACEMENTS:
        if old in seen:
            continue
        seen.add(old)
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            count += n
            print(f"   {old} → {new} ({n}箇所)")
    SYNC_SCRIPT_PATH.write_text(text, encoding="utf-8")
    print(f"   合計 {count} 箇所更新")


def step7_update_github_issues():
    print("⑦ GitHub Issue タイトルを更新...")
    # 全 Open Issues を取得
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", REPO, "--limit", "200",
         "--json", "number,title", "--state", "all"],
        capture_output=True, text=True, encoding="utf-8"
    )
    issues = json.loads(result.stdout)
    updated = 0
    for issue in issues:
        title = issue["title"]
        new_title = title
        for en, ja in PREFIX_MAP.items():
            new_title = new_title.replace(en, ja)
        if new_title != title:
            subprocess.run(
                ["gh", "issue", "edit", str(issue["number"]),
                 "--repo", REPO, "--title", new_title],
                capture_output=True, text=True, encoding="utf-8"
            )
            print(f"   #{issue['number']}: {title[:50]} → {new_title[:50]}")
            updated += 1
    print(f"   {updated} 件更新")


if __name__ == "__main__":
    step1_update_project_title()
    step2_rename_field_options()
    step3_rename_text_fields()
    step4_update_seed_evidence_type()
    step5_update_seed_prefixes()
    step6_update_sync_script()
    step7_update_github_issues()
    print("\nOK")
