#!/usr/bin/env python3
"""
Azure → AWS migration for project-seed.yaml — Phase 1
Handles: side-biz deletion, text replacements, structural additions.
"""
import re
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SEED = Path(__file__).resolve().parent.parent / "data" / "project-seed.yaml"


def read():
    return SEED.read_text(encoding="utf-8")


def write(text):
    SEED.write_text(text, encoding="utf-8")


# ── Azure→AWS text replacements (longest first) ─────────────
REPLACEMENTS = [
    ("Azure 無料アカウント https://azure.microsoft.com/ja-jp/free/",
     "AWS 無料アカウント https://aws.amazon.com/free/"),
    ("https://docs.microsoft.com/ja-jp/azure/iot-hub/",
     "https://docs.aws.amazon.com/iot/"),
    ("https://azure.microsoft.com/ja-jp/products/defender-for-iot/",
     "https://docs.aws.amazon.com/iot-device-defender/"),
    ("https://azure.microsoft.com/ja-jp/products/ai-foundry/",
     "https://docs.aws.amazon.com/bedrock/"),
    ("https://learn.microsoft.com/ja-jp/certifications/azure-fundamentals/",
     "https://skillbuilder.aws/"),
    ("AZ-900 を取得し、Azure の基本語彙（VM / Storage / IoT Hub / IAM 等）",
     "CLF-C02 を取得し、AWS の基本語彙（EC2 / S3 / IoT Core / IAM 等）"),
    ("Azure の基本語彙（VM / Storage / IoT Hub / IAM 等）",
     "AWS の基本語彙（EC2 / S3 / IoT Core / IAM 等）"),
    ("Microsoft Learn の AZ-900 学習パスを全モジュール完了する（無料・絀10時間）",
     "AWS Skill Builder の CLF-C02 学習パスを全モジュール完了する（無料）"),
    ("Microsoft Learn の AZ-900 学習パストップを開いて最初のモジュールを始める。",
     "AWS Skill Builder の CLF-C02 学習パストップを開いて最初のモジュールを始める。"),
    ("Microsoft Learn の AZ-900 学習パスを全モジュール完了した",
     "AWS Skill Builder の CLF-C02 学習パスを全モジュール完了した"),
    ("Microsoft Learn AZ-900 学習パス", "AWS Skill Builder CLF-C02 学習パス"),
    ("Microsoft Learn の AZ-900", "AWS Skill Builder の CLF-C02"),
    ("Microsoft Credential ページ", "AWS Certification ページ"),
    ("「合格対策 Microsoft 認定 AZ-900 試験対策テキスト」（翔泳社）",
     "「AWS認定クラウドプラクティショナー CLF-C02 対策テキスト」"),
    ("Microsoft Defender for IoT", "AWS IoT Device Defender"),
    ("Azure AI Foundry", "Amazon Bedrock"),
    ("Azure IoT Hub", "AWS IoT Core"),
    ("AZ-900 Azure 基礎認定取得", "AWS Cloud Practitioner (CLF-C02) 取得"),
    ("AZ-900 認定証", "CLF-C02 認定証"),
    ("AZ-900 試験に合格した", "CLF-C02 試験に合格した"),
    ("AZ-900 試験", "CLF-C02 試験"),
    ("AZ-900", "CLF-C02"),
    ("Azure ポータルで有効化する", "AWS マネジメントコンソールで有効化する"),
    ("Azure ポータル", "AWS マネジメントコンソール"),
    ("Azure 無料アカウントを作成し", "AWS 無料アカウントを作成し"),
    ("Azure 無料アカウントで", "AWS 無料アカウントで"),
    ("Azure 無料アカウント", "AWS 無料アカウント"),
    ("Azure 知識で", "AWS 知識で"),
    ("Azure AI / IoT Hub", "Amazon Bedrock / IoT Core"),
    ("Azure AI +", "Amazon Bedrock +"),
    ("Azure 実務経験", "AWS 実務経験"),
    ("Azure 上で動かせる", "AWS 上で動かせる"),
    ("Azure デプロイ画面", "AWS デプロイ画面"),
    ("Azure デプロイ", "AWS デプロイ"),
    ("Azure + Claude Code", "AWS + Claude Code"),
    ("IoT Hub データ", "IoT Core データ"),
    ("IoT Hub 環境", "IoT Core 環境"),
    ("IoT Hub を作成し", "IoT Core を作成し"),
    ("IoT Hub の作成チュートリアル", "IoT Core の作成チュートリアル"),
    ("IoT Hub データパイプライン", "IoT Core データパイプライン"),
    ("IoT Hub を作成しデバイス登録", "IoT Core を作成しデバイス登録"),
    ("IoT Hub で", "IoT Core で"),
    ("Defender for IoT", "IoT Device Defender"),
]


def delete_side_biz(lines):
    """Remove side-biz-video related blocks from lines."""
    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.rstrip("\n")

        # Delete E-VID epic block
        if stripped.startswith("- id: E-VID"):
            i += 1
            while i < n and not (lines[i].startswith("- id: ") or lines[i].startswith("milestones:")):
                i += 1
            continue

        # Delete M-SB-90DAY milestone block
        if "id: M-SB-90DAY" in stripped:
            i += 1
            while i < n and not (lines[i].startswith("- id: ") or lines[i].startswith("labels:")):
                i += 1
            continue

        # Delete area:side-biz-video label block
        if "name: area:side-biz-video" in stripped:
            # Remove the "  - name:" line
            i += 1
            while i < n and lines[i].startswith("    "):
                i += 1
            continue

        # Delete phase:side-biz-launch label block
        if "name: phase:side-biz-launch" in stripped:
            i += 1
            while i < n and lines[i].startswith("    "):
                i += 1
            continue

        # Delete ISS-051 through ISS-058
        m = re.match(r"- id: ISS-05([1-8])\s*$", stripped)
        if m:
            i += 1
            while i < n and lines[i].startswith("  ") and not lines[i].startswith("- "):
                i += 1
            continue

        # Delete ISS-R05
        if stripped.startswith("- id: ISS-R05"):
            i += 1
            while i < n and lines[i].startswith("  ") and not lines[i].startswith("- "):
                i += 1
            continue

        result.append(line)
        i += 1

    return result


def main():
    text = read()
    lines = text.splitlines(keepends=True)

    # Step 0: Delete side-biz
    print("Deleting side-biz content...")
    lines = delete_side_biz(lines)
    text = "".join(lines)

    # Remove side-biz field options
    text = re.sub(r"  - 副業動画\n", "", text)
    text = re.sub(r"  - 副業立上\n", "", text)
    text = re.sub(r"  - 副業制作\n", "", text)

    # Step 1: Azure → AWS text replacements
    print("Applying Azure → AWS replacements...")
    for old, new in REPLACEMENTS:
        count = text.count(old)
        if count > 0:
            text = text.replace(old, new)
            print(f"  Replaced '{old[:50]}...' ({count}x)")

    # Check remaining Azure/AZ-900 references
    remaining = []
    for i, line in enumerate(text.splitlines(), 1):
        for kw in ["Azure", "AZ-900", "Microsoft Defender for IoT",
                    "azure.microsoft", "docs.microsoft", "learn.microsoft"]:
            if kw in line:
                remaining.append(f"  L{i}: {line.strip()[:120]}")
                break
    if remaining:
        print(f"\nWARNING: {len(remaining)} lines still have Azure refs:")
        for r in remaining:
            print(r)
    else:
        print("\nAll Azure/Microsoft references replaced!")

    # Save intermediate
    write(text)

    # Check side-biz cleanup
    sb_count = text.count("side-biz") + text.count("副業")
    if sb_count > 0:
        print(f"\nWARNING: {sb_count} side-biz/副業 references remain")
        for i, line in enumerate(text.splitlines(), 1):
            if "side-biz" in line or "副業" in line:
                print(f"  L{i}: {line.strip()[:120]}")
    else:
        print("Side-biz content fully removed!")

    print(f"\nDone. File: {len(text)} bytes")


if __name__ == "__main__":
    main()
