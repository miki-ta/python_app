"""
タスクリマインダーチェッカー
Windowsタスクスケジューラから定期実行し、reminded フラグを更新する。
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR   = Path(__file__).parent / "data"
TASKS_FILE = DATA_DIR / "tm_tasks.json"


def _load_json(path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check():
    tasks = _load_json(TASKS_FILE, [])
    if not tasks:
        return

    now = datetime.now()
    updated = False

    for task in tasks:
        if task.get("status") == "完了":
            continue
        due = task.get("due_date", "-")
        if due == "-":
            continue
        reminder_minutes = task.get("reminder_minutes", 0)
        reminded = task.get("reminded", False)

        try:
            if " " in due:
                due_dt = datetime.strptime(due, "%Y-%m-%d %H:%M")
            else:
                due_dt = datetime.strptime(due + " 23:59", "%Y-%m-%d %H:%M")
        except Exception:
            continue

        delta_min = (due_dt - now).total_seconds() / 60

        if reminder_minutes > 0 and not reminded and 0 <= delta_min <= reminder_minutes:
            task["reminded"] = True
            updated = True

    if updated:
        _save_json(TASKS_FILE, tasks)


if __name__ == "__main__":
    check()
