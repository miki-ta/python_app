"""
タスクリマインダーチェッカー
Windowsタスクスケジューラから定期実行し、reminded フラグを更新する。
GUI モードで起動するとチェック結果を画面に表示する。
"""

import json
import tkinter as tk
from tkinter import ttk
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


def check() -> list[dict]:
    """リマインダー対象タスクを確認し、トリガーされたタスクのリストを返す。"""
    tasks = _load_json(TASKS_FILE, [])
    if not tasks:
        return []

    now = datetime.now()
    triggered = []
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
            triggered.append(task)

    if updated:
        _save_json(TASKS_FILE, tasks)

    return triggered


# ======================== GUI ========================

class ReminderCheckerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("タスクリマインダーチェッカー")
        self.root.geometry("760x500")
        self.root.minsize(600, 400)

        self._build_ui()
        self._run_check()

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(toolbar, text="今すぐチェック", command=self._run_check).pack(side=tk.LEFT, padx=2)
        self._status_var = tk.StringVar()
        ttk.Label(toolbar, textvariable=self._status_var, foreground="#555555").pack(side=tk.LEFT, padx=12)

        ttk.Button(toolbar, text="閉じる", command=self.root.destroy).pack(side=tk.RIGHT, padx=2)

        # --- リマインダー対象タスク一覧 ---
        lf = ttk.LabelFrame(self.root, text="リマインダー設定済みタスク（未完了）", padding=6)
        lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))

        cols = ("id", "title", "due_date", "reminder", "delta", "assignee", "triggered")
        self._tree = ttk.Treeview(lf, columns=cols, show="headings", height=15)

        headers = {
            "id":        ("タスクID",   80),
            "title":     ("タイトル",  200),
            "due_date":  ("期限",      130),
            "reminder":  ("通知タイミング", 110),
            "delta":     ("残り時間",  110),
            "assignee":  ("担当者",    100),
            "triggered": ("今回通知",   80),
        }
        for col, (label, width) in headers.items():
            self._tree.heading(col, text=label)
            self._tree.column(col, width=width, anchor=tk.CENTER if col != "title" else tk.W)

        vsb = ttk.Scrollbar(lf, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(fill=tk.BOTH, expand=True)

        self._tree.tag_configure("triggered", background="#fff3cd", foreground="#856404")
        self._tree.tag_configure("overdue",   background="#f8d7da", foreground="#721c24")

    def _run_check(self) -> None:
        triggered = check()
        triggered_ids = {t.get("task_id") for t in triggered}

        self._tree.delete(*self._tree.get_children())

        tasks = _load_json(TASKS_FILE, [])
        now = datetime.now()
        shown = 0

        for task in tasks:
            if task.get("status") == "完了":
                continue
            reminder_minutes = task.get("reminder_minutes", 0)
            if reminder_minutes == 0:
                continue

            due = task.get("due_date", "-")
            if due == "-":
                continue

            try:
                if " " in due:
                    due_dt = datetime.strptime(due, "%Y-%m-%d %H:%M")
                else:
                    due_dt = datetime.strptime(due + " 23:59", "%Y-%m-%d %H:%M")
                delta_sec = (due_dt - now).total_seconds()
                delta_min = delta_sec / 60
                if delta_sec < 0:
                    delta_str = f"期限切れ {abs(int(delta_min))}分前"
                    tag = "overdue"
                elif delta_min < 60:
                    delta_str = f"あと {int(delta_min)}分"
                    tag = "triggered" if task.get("task_id") in triggered_ids else ""
                elif delta_min < 1440:
                    delta_str = f"あと {int(delta_min / 60)}時間"
                    tag = "triggered" if task.get("task_id") in triggered_ids else ""
                else:
                    delta_str = f"あと {int(delta_min / 1440)}日"
                    tag = ""
            except Exception:
                delta_str = "-"
                tag = ""

            reminder_labels = {0: "通知なし", 15: "15分前", 30: "30分前",
                               60: "1時間前", 180: "3時間前", 1440: "1日前"}
            reminder_str = reminder_labels.get(reminder_minutes, f"{reminder_minutes}分前")

            is_triggered = task.get("task_id") in triggered_ids
            triggered_str = "✔ 通知済み" if is_triggered else ""
            if is_triggered:
                tag = "triggered"

            self._tree.insert(
                "", tk.END,
                values=(
                    task.get("task_id", ""),
                    task.get("title", ""),
                    task.get("due_date", ""),
                    reminder_str,
                    delta_str,
                    task.get("assignee", ""),
                    triggered_str,
                ),
                tags=(tag,),
            )
            shown += 1

        now_str = now.strftime("%H:%M:%S")
        if triggered:
            self._status_var.set(f"最終チェック: {now_str} — {len(triggered)} 件の通知をトリガーしました")
        else:
            self._status_var.set(f"最終チェック: {now_str} — 新しい通知はありません（表示中: {shown} 件）")


def main() -> None:
    root = tk.Tk()
    ReminderCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
