import argparse
import json
import csv
import sys
from collections import defaultdict


def load_from_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        # expect top-level list under 'items'
        data = data.get("items", [])
    return data


def load_from_csv(path):
    items = []
    with open(path, encoding="utf-8", newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            items.append({
                "category": r.get("category", r.get("カテゴリ", "")),
                "title": r.get("title", r.get("タイトル", "")),
                "description": r.get("description", r.get("説明", "")),
            })
    return items


def interactive_input():
    print("対話モード：Enterで終了します。")
    items = []
    i = 1
    while True:
        cat = input(f"[{i}] カテゴリ: ").strip()
        if cat == "":
            break
        title = input(f"[{i}] タイトル: ").strip()
        desc = input(f"[{i}] 説明: ").strip()
        items.append({"category": cat, "title": title, "description": desc})
        i += 1
    return items


def group_items(items):
    groups = defaultdict(list)
    for it in items:
        cat = it.get("category") or "未分類"
        groups[cat].append(it)
    return groups


def render_markdown(groups):
    lines = ["# コールセンター運用マニュアル\n"]
    for cat in sorted(groups.keys()):
        lines.append(f"## {cat}\n")
        for idx, it in enumerate(groups[cat], start=1):
            title = it.get("title", "（無題）")
            desc = it.get("description", "")
            lines.append(f"{idx}. **{title}**")
            if desc:
                lines.append(f"   - {desc}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="カテゴリ分けでコールセンター運用マニュアルを生成します")
    p.add_argument("--input", "-i", help="入力ファイル（JSONまたはCSV）")
    p.add_argument("--format", "-f", choices=["json", "csv"], help="入力フォーマット（自動判定可能）")
    p.add_argument("--output", "-o", help="出力ファイル（省略すると標準出力）")
    args = p.parse_args(argv)

    if args.input:
        fmt = args.format
        if not fmt:
            if args.input.lower().endswith(".json"):
                fmt = "json"
            elif args.input.lower().endswith(".csv"):
                fmt = "csv"
        if fmt == "json":
            items = load_from_json(args.input)
        elif fmt == "csv":
            items = load_from_csv(args.input)
        else:
            # try json first
            try:
                items = load_from_json(args.input)
            except Exception:
                items = load_from_csv(args.input)
    else:
        items = interactive_input()

    groups = group_items(items)
    md = render_markdown(groups)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"書き出しました: {args.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()
