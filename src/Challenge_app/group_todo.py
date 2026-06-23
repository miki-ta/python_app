"""
複数担当者対応のタスク管理表 - GUI版
テーブル形式での見やすい表示とタスク管理機能
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from datetime import datetime, timedelta
import calendar

# ===================== データモデル =====================

@dataclass
class Task:
    """タスク情報を管理するデータクラス"""
    task_id: str          # ユニークID（TASK-001など）
    title: str            # タスクタイトル
    assignee: str         # 担当者名
    status: str           # 状態：「未対応」「処理中」「完了」
    priority: str         # 優先度：「高」「中」「低」
    start_date: str       # 開始日（YYYY-MM-DD または "-"）
    due_date: str         # 期限（YYYY-MM-DD または "-"）
    memo: str = ""        # メモ
    created_at: str = ""  # 作成日時


@dataclass
class HistoryEntry:
    """操作履歴の1件"""
    timestamp: str    # 操作日時（YYYY-MM-DD HH:MM:SS）
    action: str       # 操作種別：「作成」「編集」「削除」「状態変更」「担当者変更」
    task_id: str      # 対象タスクID
    task_title: str   # 対象タスクタイトル（削除後でも参照できるよう保持）
    detail: str       # 変更内容の説明


# ===================== ファイル操作 =====================

DATA_DIR = Path(__file__).parent / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
ASSIGNEES_FILE = DATA_DIR / "assignees.json"
HISTORY_FILE = DATA_DIR / "history.json"
COUNTER_FILE = DATA_DIR / "counter.json"
TRASH_FILE = DATA_DIR / "trash.json"

def ensure_data_dir():
    """データディレクトリを作成"""
    DATA_DIR.mkdir(exist_ok=True)

def load_counter() -> int:
    """タスク連番カウンターを読み込む"""
    if not COUNTER_FILE.exists():
        return 0
    try:
        with open(COUNTER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get("counter", 0)
    except:
        return 0

def save_counter(counter: int) -> None:
    """タスク連番カウンターを保存"""
    try:
        ensure_data_dir()
        with open(COUNTER_FILE, 'w', encoding='utf-8') as f:
            json.dump({"counter": counter}, f)
    except:
        pass

def load_tasks() -> list[Task]:
    """タスクデータを読み込む"""
    if not TASKS_FILE.exists():
        return []
    
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Task(**item) for item in data]
    except Exception as e:
        messagebox.showerror("読み込みエラー", f"タスクデータの読み込みに失敗しました:\n{e}")
        return []

def save_tasks(tasks: list[Task]) -> bool:
    """タスクデータを保存"""
    try:
        ensure_data_dir()
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([asdict(task) for task in tasks], f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("保存エラー", f"タスク保存に失敗しました:\n{e}")
        return False

def load_assignees() -> list[str]:
    """担当者リストを読み込む"""
    if not ASSIGNEES_FILE.exists():
        return ["未割り当て"]
    
    try:
        with open(ASSIGNEES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if data else ["未割り当て"]
    except:
        return ["未割り当て"]

def save_assignees(assignees: list[str]) -> bool:
    """担当者リストを保存"""
    try:
        ensure_data_dir()
        with open(ASSIGNEES_FILE, 'w', encoding='utf-8') as f:
            json.dump(assignees, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("保存エラー", f"担当者リスト保存に失敗しました:\n{e}")
        return False



def load_history() -> list[HistoryEntry]:
    """履歴データを読み込む"""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [HistoryEntry(**item) for item in data]
    except:
        return []

def save_history(history: list[HistoryEntry]) -> None:
    """履歴データを保存（最新1000件に制限）"""
    try:
        ensure_data_dir()
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([asdict(h) for h in history[-1000:]], f, ensure_ascii=False, indent=2)
    except:
        pass  # 履歴保存失敗は握り潰す（主機能に影響させない）

def add_history(history: list[HistoryEntry], action: str, task_id: str, task_title: str, detail: str) -> None:
    """履歴を1件追加"""
    history.append(HistoryEntry(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        action=action,
        task_id=task_id,
        task_title=task_title,
        detail=detail,
    ))
    save_history(history)

def load_trash() -> list[Task]:
    """削除済みタスクを読み込む"""
    if not TRASH_FILE.exists():
        return []
    try:
        with open(TRASH_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Task(**item) for item in data]
    except:
        return []

def save_trash(trash: list[Task]) -> bool:
    """削除済みタスクを保存"""
    try:
        ensure_data_dir()
        with open(TRASH_FILE, 'w', encoding='utf-8') as f:
            json.dump([asdict(t) for t in trash], f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


# ===================== ダイアログクラス =====================

class DatePickerDialog(tk.Toplevel):
    """カレンダー形式の日付選択ダイアログ"""
    
    def __init__(self, parent, on_date_selected):
        super().__init__(parent)
        self.title("日付を選択")
        self.geometry("300x300")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        
        self.on_date_selected = on_date_selected
        self.current_date = datetime.now()
        
        # ヘッダー（年月選択）
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=10)
        
        ttk.Button(header_frame, text="◀", width=3, command=self.prev_month).pack(side=tk.LEFT, padx=5)
        self.month_label = ttk.Label(header_frame, text="", font=("Arial", 12, "bold"))
        self.month_label.pack(side=tk.LEFT, padx=20)
        ttk.Button(header_frame, text="▶", width=3, command=self.next_month).pack(side=tk.LEFT, padx=5)
        
        # カレンダーフレーム
        self.cal_frame = ttk.Frame(self)
        self.cal_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # ボタンフレーム
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="キャンセル", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        self.draw_calendar()
    
    def prev_month(self):
        """前月に移動"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.draw_calendar()
    
    def next_month(self):
        """次月に移動"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.draw_calendar()
    
    def draw_calendar(self):
        """カレンダーを描画"""
        for widget in self.cal_frame.winfo_children():
            widget.destroy()
        
        # 年月表示
        self.month_label.config(text=f"{self.current_date.year}年 {self.current_date.month}月")
        
        # 曜日ヘッダー
        days = ["月", "火", "水", "木", "金", "土", "日"]
        for i, day in enumerate(days):
            ttk.Label(self.cal_frame, text=day, font=("Arial", 9)).grid(row=0, column=i, padx=2)
        
        # 日付ボタン
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        for week_idx, week in enumerate(cal, 1):
            for day_idx, day in enumerate(week):
                if day == 0:
                    ttk.Label(self.cal_frame, text="").grid(row=week_idx, column=day_idx, padx=2)
                else:
                    btn = ttk.Button(
                        self.cal_frame, text=str(day), width=3,
                        command=lambda d=day: self.select_day(d)
                    )
                    btn.grid(row=week_idx, column=day_idx, padx=2)
    
    def select_day(self, day):
        """日付を選択"""
        selected = self.current_date.replace(day=day)
        date_str = selected.strftime("%Y-%m-%d")
        self.on_date_selected(date_str)
        self.destroy()


class AssigneeManagerDialog(tk.Toplevel):
    """担当者管理ダイアログ"""
    
    def __init__(self, parent, assignees, on_saved):
        super().__init__(parent)
        self.title("担当者管理")
        self.geometry("300x400")
        self.grab_set()
        self.transient(parent)
        
        self.assignees = assignees.copy()
        self.on_saved = on_saved
        
        # リストボックス
        list_frame = ttk.Frame(self)
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text="担当者一覧:").pack(anchor=tk.W)
        
        self.listbox = tk.Listbox(list_frame, height=10)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.refresh_list()
        
        # ボタンフレーム
        btn_frame = ttk.Frame(self)
        btn_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Button(btn_frame, text="追加", command=self.add_assignee).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="編集", command=self.edit_assignee).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="削除", command=self.delete_assignee).pack(side=tk.LEFT, padx=2)
        
        # 確定ボタン
        ttk.Button(btn_frame, text="保存", command=self.save_and_close).pack(side=tk.RIGHT, padx=2)
    
    def refresh_list(self):
        """リストを更新"""
        self.listbox.delete(0, tk.END)
        for assignee in self.assignees:
            self.listbox.insert(tk.END, assignee)
    
    def add_assignee(self):
        """担当者を追加"""
        name = simpledialog.askstring("追加", "担当者名を入力:")
        if name and name not in self.assignees:
            self.assignees.append(name)
            self.refresh_list()
        elif name and name in self.assignees:
            messagebox.showwarning("重複", "既に存在する担当者です")
    
    def edit_assignee(self):
        """選択した担当者を編集"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("注意", "編集する担当者を選択してください")
            return
        
        idx = selection[0]
        new_name = simpledialog.askstring("編集", f"新しい担当者名を入力:", initialvalue=self.assignees[idx])
        if new_name:
            self.assignees[idx] = new_name
            self.refresh_list()
    
    def delete_assignee(self):
        """選択した担当者を削除"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("注意", "削除する担当者を選択してください")
            return
        
        idx = selection[0]
        if len(self.assignees) <= 1:
            messagebox.showwarning("注意", "最後の担当者は削除できません")
            return
        
        self.assignees.pop(idx)
        self.refresh_list()
    
    def save_and_close(self):
        """保存して閉じる"""
        self.on_saved(self.assignees)
        self.destroy()


class TaskEditorDialog(tk.Toplevel):
    """タスク編集ダイアログ"""
    
    def __init__(self, parent, task, assignees, on_saved):
        super().__init__(parent)
        self.title("タスク編集")
        self.geometry("500x400")
        self.grab_set()
        self.transient(parent)
        
        self.task = task
        self.assignees = assignees
        self.on_saved = on_saved
        self.selected_start = task.start_date
        self.selected_due = task.due_date
        
        # フォームフレーム
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # ID
        ttk.Label(form_frame, text="タスクID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(form_frame, text=task.task_id).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # タイトル
        ttk.Label(form_frame, text="タイトル:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=task.title)
        ttk.Entry(form_frame, textvariable=self.title_var, width=30).grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # 担当者
        ttk.Label(form_frame, text="担当者:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.assignee_var = tk.StringVar(value=task.assignee)
        ttk.Combobox(form_frame, textvariable=self.assignee_var, values=assignees, state="readonly", width=27).grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # 状態
        ttk.Label(form_frame, text="状態:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value=task.status)
        ttk.Combobox(form_frame, textvariable=self.status_var, values=["未対応", "処理中", "完了"], state="readonly", width=27).grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # 優先度
        ttk.Label(form_frame, text="優先度:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar(value=task.priority)
        ttk.Combobox(form_frame, textvariable=self.priority_var, values=["高", "中", "低"], state="readonly", width=27).grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # 開始日
        ttk.Label(form_frame, text="開始日:").grid(row=5, column=0, sticky=tk.W, pady=5)
        start_frame = ttk.Frame(form_frame)
        start_frame.grid(row=5, column=1, sticky=tk.EW, pady=5)
        self.start_label = ttk.Label(start_frame, text=task.start_date if task.start_date != "-" else "未設定")
        self.start_label.pack(side=tk.LEFT)
        ttk.Button(start_frame, text="選択", width=8, command=lambda: self.pick_date("start")).pack(side=tk.LEFT, padx=5)
        
        # 期限
        ttk.Label(form_frame, text="期限:").grid(row=6, column=0, sticky=tk.W, pady=5)
        due_frame = ttk.Frame(form_frame)
        due_frame.grid(row=6, column=1, sticky=tk.EW, pady=5)
        self.due_label = ttk.Label(due_frame, text=task.due_date if task.due_date != "-" else "未設定")
        self.due_label.pack(side=tk.LEFT)
        ttk.Button(due_frame, text="選択", width=8, command=lambda: self.pick_date("due")).pack(side=tk.LEFT, padx=5)
        
        # メモ
        ttk.Label(form_frame, text="メモ:").grid(row=7, column=0, sticky=tk.NW, pady=5)
        self.memo_text = tk.Text(form_frame, height=4, width=30)
        self.memo_text.grid(row=7, column=1, sticky=tk.EW, pady=5)
        self.memo_text.insert("1.0", task.memo)
        
        form_frame.columnconfigure(1, weight=1)
        
        # ボタンフレーム
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="キャンセル", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=5)
    
    def pick_date(self, field_type):
        """日付を選択"""
        def on_date_selected(date_str):
            if field_type == "start":
                self.selected_start = date_str
                self.start_label.config(text=date_str)
            else:
                self.selected_due = date_str
                self.due_label.config(text=date_str)
        
        DatePickerDialog(self, on_date_selected)
    
    def save(self):
        """保存"""
        self.task.title = self.title_var.get()
        self.task.assignee = self.assignee_var.get()
        self.task.status = self.status_var.get()
        self.task.priority = self.priority_var.get()
        self.task.start_date = self.selected_start
        self.task.due_date = self.selected_due
        self.task.memo = self.memo_text.get("1.0", tk.END).strip()
        
        self.on_saved(self.task)
        self.destroy()


# ===================== メインアプリケーション =====================

class HistoryDialog(tk.Toplevel):
    """操作履歴表示ダイアログ"""

    def __init__(self, parent, history: list[HistoryEntry], tasks_list, app_ref=None):
        super().__init__(parent)
        self.title("操作履歴")
        self.geometry("800x500")
        self.grab_set()
        self.transient(parent)
        self.tasks_list = tasks_list
        self.app_ref = app_ref

        # フィルターバー
        filter_frame = ttk.Frame(self)
        filter_frame.pack(padx=10, pady=(10, 5), fill=tk.X)

        ttk.Label(filter_frame, text="絞り込み：").pack(side=tk.LEFT)

        self.filter_action = tk.StringVar(value="すべて")
        action_cb = ttk.Combobox(
            filter_frame, textvariable=self.filter_action,
            values=["すべて", "作成", "編集", "削除", "状態変更", "担当者変更"],
            state="readonly", width=10
        )
        action_cb.pack(side=tk.LEFT, padx=5)
        action_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh(history))

        ttk.Label(filter_frame, text="キーワード：").pack(side=tk.LEFT, padx=(10, 0))
        self.filter_kw = tk.StringVar()
        kw_entry = ttk.Entry(filter_frame, textvariable=self.filter_kw, width=20)
        kw_entry.pack(side=tk.LEFT, padx=5)
        kw_entry.bind("<KeyRelease>", lambda e: self._refresh(history))

        ttk.Button(filter_frame, text="クリア", command=lambda: self._clear_filter(history)).pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="（新しい順）").pack(side=tk.RIGHT)

        # テーブル
        table_frame = ttk.Frame(self)
        table_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("timestamp", "action", "task_id", "task_title", "detail"),
            show="headings",
        )
        self.tree.column("timestamp",  width=145, anchor=tk.CENTER)
        self.tree.column("action",     width=80,  anchor=tk.CENTER)
        self.tree.column("task_id",    width=80,  anchor=tk.CENTER)
        self.tree.column("task_title", width=180, anchor=tk.W)
        self.tree.column("detail",     width=260, anchor=tk.W)

        self.tree.heading("timestamp",  text="日時")
        self.tree.heading("action",     text="操作")
        self.tree.heading("task_id",    text="タスクID")
        self.tree.heading("task_title", text="タイトル")
        self.tree.heading("detail",     text="変更内容")

        # 操作種別ごとの色
        self.tree.tag_configure("作成",     foreground="#5cb85c")
        self.tree.tag_configure("編集",     foreground="#0275d8")
        self.tree.tag_configure("削除",     foreground="#d9534f")
        self.tree.tag_configure("状態変更", foreground="#9b59b6")
        self.tree.tag_configure("担当者変更", foreground="#e67e22")

        sb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # ボタンフレーム
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="復元", command=lambda: self._restore_task(history)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="閉じる", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self._refresh(history)

    def _clear_filter(self, history):
        self.filter_action.set("すべて")
        self.filter_kw.set("")
        self._refresh(history)

    def _refresh(self, history: list[HistoryEntry]):
        """フィルターを適用して表示更新"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        action_filter = self.filter_action.get()
        kw = self.filter_kw.get().lower()

        for entry in reversed(history):  # 新しい順
            if action_filter != "すべて" and entry.action != action_filter:
                continue
            if kw and kw not in (entry.task_title + entry.detail + entry.task_id).lower():
                continue
            self.tree.insert(
                "", "end",
                values=(entry.timestamp, entry.action, entry.task_id, entry.task_title, entry.detail),
                tags=(entry.action,),
            )

    def _restore_task(self, history: list[HistoryEntry]):
        """選択された履歴からタスクを復元"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("注意", "復元するタスクを選択してください")
            return
        
        # 選択行のデータを取得
        values = self.tree.item(selection[0])["values"]
        task_id = values[2]  # task_id は3番目のカラム
        
        # 現在のタスク一覧から該当タスクを探す
        task = next((t for t in self.tasks_list if t.task_id == task_id), None)
        
        if task is None:
            # タスクが削除されている場合、履歴から復元
            entry = next((e for e in history if e.task_id == task_id), None)
            if entry:
                messagebox.showinfo("情報", f"タスク '{entry.task_title}' は削除されています")
            else:
                messagebox.showerror("エラー", "タスクが見つかりません")
            return
        
        # app_ref（TodoApp）が渡されている場合、タスク編集ダイアログを開く
        if self.app_ref:
            def on_saved(updated_task):
                idx = self.tasks_list.index(task)
                self.tasks_list[idx] = updated_task
                if save_tasks(self.tasks_list):
                    messagebox.showinfo("成功", "タスクが復元されました")
                    self.app_ref.refresh_table()
            
            TaskEditorDialog(self, task, self.app_ref.assignees, on_saved)
        else:
            messagebox.showinfo("情報", f"タスク '{task.title}' が復元されました")


class TrashDialog(tk.Toplevel):
    """削除済みタスク管理ダイアログ"""
    def __init__(self, parent, trash: list[Task], app_ref):
        super().__init__(parent)
        self.title("ゴミ箱")
        self.geometry("800x500")
        
        self.trash = trash
        self.app_ref = app_ref
        
        # 検索フレーム
        search_frame = ttk.Frame(self)
        search_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(search_frame, text="検索:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="🔍 絞込", command=self._apply_search).pack(side=tk.LEFT, padx=2)
        
        # テーブル
        columns = ("id", "title", "assignee", "status", "priority", "start_date", "due_date")
        self.tree = ttk.Treeview(self, columns=columns, show="tree headings", height=18)
        
        # 列幅
        widths = {"id": 80, "title": 450, "assignee": 100, "status": 80, "priority": 70, "start_date": 100, "due_date": 100}
        for col in columns:
            self.tree.column(col, width=widths.get(col, 100), anchor="center")
            self.tree.heading(col, text=col)
        
        # ステータスの色分け
        self.tree.tag_configure("status_未対応", foreground="#d9534f")
        self.tree.tag_configure("status_処理中", foreground="#0275d8")
        self.tree.tag_configure("status_完了", foreground="#5cb85c")
        for col in ["title", "assignee", "priority", "start_date", "due_date"]:
            self.tree.tag_configure(f"text_{col}", foreground="#000000")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # ボタンフレーム
        btn_frame = ttk.Frame(self)
        btn_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Button(btn_frame, text="♻ 復元", command=self._restore_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑 完全削除", command=self._permanent_delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="閉じる", command=self.destroy).pack(side=tk.LEFT, padx=2)
        
        # 最初は全件表示
        self.refresh_list()
    
    def refresh_list(self):
        """テーブルをリフレッシュ"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for t in self.trash:
            memo_prefix = f" ({t.memo.split(chr(10))[0][:20]})" if t.memo else ""
            display_title = f"{t.title}{memo_prefix}"
            status_tag = f"status_{t.status}" if t.status in ["未対応", "処理中", "完了"] else ""
            self.tree.insert("", "end", values=(
                t.task_id, display_title, t.assignee, t.status, t.priority, t.start_date, t.due_date
            ), tags=(status_tag,))
    
    def _apply_search(self):
        """検索を適用"""
        keyword = self.search_var.get().lower()
        if not keyword:
            self.refresh_list()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for t in self.trash:
            if keyword in t.title.lower() or keyword in t.task_id.lower() or keyword in t.assignee.lower():
                memo_prefix = f" ({t.memo.split(chr(10))[0][:20]})" if t.memo else ""
                display_title = f"{t.title}{memo_prefix}"
                status_tag = f"status_{t.status}" if t.status in ["未対応", "処理中", "完了"] else ""
                self.tree.insert("", "end", values=(
                    t.task_id, display_title, t.assignee, t.status, t.priority, t.start_date, t.due_date
                ), tags=(status_tag,))
    
    def _restore_task(self):
        """選択したタスクを復元"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("注意", "復元するタスクを選択してください")
            return
        
        if messagebox.askyesno("確認", "選択したタスクを復元しますか?"):
            # 選択された行のIDを取得
            item_id = selection[0]
            values = self.tree.item(item_id)["values"]
            task_id = values[0]
            
            # ゴミ箱からタスクを取得
            task = None
            for t in self.trash:
                if t.task_id == task_id:
                    task = t
                    break
            
            if not task:
                messagebox.showerror("エラー", "タスクが見つかりません")
                return
            
            # アクティブタスク一覧に追加
            self.app_ref.tasks.append(task)
            if save_tasks(self.app_ref.tasks):
                # ゴミ箱から削除
                self.trash.remove(task)
                save_trash(self.trash)
                # 履歴に記録
                add_history(self.app_ref.history, "復元", task.task_id, task.title, "ゴミ箱から復元")
                messagebox.showinfo("成功", "タスクが復元されました")
                self.app_ref.refresh_table()
                self.refresh_list()
    
    def _permanent_delete(self):
        """選択したタスクを完全削除"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("注意", "削除するタスクを選択してください")
            return
        
        if messagebox.askyesno("確認", "選択したタスクを完全に削除しますか? この操作は取り消せません。"):
            item_id = selection[0]
            values = self.tree.item(item_id)["values"]
            task_id = values[0]
            
            # ゴミ箱から削除
            self.trash = [t for t in self.trash if t.task_id != task_id]
            if save_trash(self.trash):
                messagebox.showinfo("成功", "タスクが完全に削除されました")
                self.refresh_list()


# ===================== メインアプリケーション =====================

class TodoApp:
    """タスク管理アプリケーション"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("タスク管理表 - グループタスク管理")
        self.root.geometry("1200x700")
        self.root.minsize(900, 500)
        
        self.tasks = load_tasks()
        self.assignees = load_assignees()
        self.history = load_history()
        self.trash = load_trash()
        # カウンターは専用ファイルから読み込み（削除しても番号は戻らない）
        saved = load_counter()
        existing_max = max([int(t.task_id.split('-')[1]) for t in self.tasks], default=0)
        self.task_counter = max(saved, existing_max)
        
        self._build_ui()
        self.refresh_table()
        
        # 起動時に期限切れタスクの警告を表示
        self._check_overdue_on_startup()
    
    def _build_ui(self):
        """UIを構築"""
        # ツールバー
        toolbar = ttk.Frame(self.root)
        toolbar.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Button(toolbar, text="+ 新規タスク", command=self.add_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✎ 編集", command=self.edit_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑 削除", command=self.delete_task).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar, text="👥 担当者管理", command=self.manage_assignees).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar, text="♻ ゴミ箱", command=self.show_trash).pack(side=tk.LEFT, padx=2)
        
        # 期限切れタスク枠
        overdue_frame = ttk.LabelFrame(self.root, text="⚠️ 期限切れのタスク")
        overdue_frame.pack(padx=10, pady=(5, 10), fill=tk.X)
        
        self.overdue_tree = ttk.Treeview(
            overdue_frame,
            columns=("id", "title", "assignee", "status", "priority", "start_date", "due_date"),
            height=3,
            show="headings"
        )
        
        self.overdue_tree.column("id", width=80, anchor=tk.CENTER)
        self.overdue_tree.column("title", width=380, anchor=tk.W)
        self.overdue_tree.column("assignee", width=100, anchor=tk.CENTER)
        self.overdue_tree.column("status", width=80, anchor=tk.CENTER)
        self.overdue_tree.column("priority", width=70, anchor=tk.CENTER)
        self.overdue_tree.column("start_date", width=100, anchor=tk.CENTER)
        self.overdue_tree.column("due_date", width=100, anchor=tk.CENTER)
        
        for col, label in [("id", "キー"), ("title", "タイトル（メモ）"), ("assignee", "担当者"), ("status", "状態"), ("priority", "優先度"), ("start_date", "開始日"), ("due_date", "期限")]:
            self.overdue_tree.heading(col, text=label)
        
        # 状態列の色分け
        self.overdue_tree.tag_configure("status_未対応", foreground="#d9534f")  # 赤
        self.overdue_tree.tag_configure("status_処理中", foreground="#0275d8")  # 青
        self.overdue_tree.tag_configure("priority_高", foreground="#000000")    # 黒
        self.overdue_tree.tag_configure("priority_中", foreground="#000000")    # 黒
        self.overdue_tree.tag_configure("priority_低", foreground="#000000")    # 黒
        self.overdue_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # テーブル
        table_frame = ttk.Frame(self.root)
        table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Treeviewの定義
        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "title", "assignee", "status", "priority", "start_date", "due_date"),
            height=25,
            show="headings"
        )
        
        # 列の定義
        self.tree.column("#0", width=0)
        self.tree.column("id", width=80, anchor=tk.CENTER)
        self.tree.column("title", width=400, anchor=tk.W)
        self.tree.column("assignee", width=100, anchor=tk.CENTER)
        self.tree.column("status", width=80, anchor=tk.CENTER)
        self.tree.column("priority", width=70, anchor=tk.CENTER)
        self.tree.column("start_date", width=100, anchor=tk.CENTER)
        self.tree.column("due_date", width=100, anchor=tk.CENTER)
        
        # ヘッダークリックでソート。デフォルトはキー（入力順）
        self._sort_col = "id"
        self._sort_asc = True
        
        for col, label in [
            ("id", "キー"), ("title", "タイトル（メモ）"), ("assignee", "担当者"),
            ("status", "状態"), ("priority", "優先度"),
            ("start_date", "開始日"), ("due_date", "期限")
        ]:
            self.tree.heading(col, text=label, command=lambda c=col: self._sort_by(c))
        
        # 初期表示はキー昇順を示す矢印
        self.tree.heading("id", text="キー ▲")
        
        # 状態列のクリックでインライン編集
        self.tree.bind("<ButtonRelease-1>", self._on_cell_click)
        self._inline_combo = None  # インラインコンボボックス（1つだけ使い回す）
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # タグ定義（状態の色付け）
        self.tree.tag_configure("status_未対応", foreground="#d9534f")  # 赤
        self.tree.tag_configure("status_処理中", foreground="#0275d8")  # 青
        self.tree.tag_configure("status_完了", foreground="#5cb85c")    # 緑
        
        # その他の列は全て黒色
        self.tree.tag_configure("black", foreground="#000000")        # 黒
        self.tree.tag_configure("priority_高", foreground="#000000")    # 黒
        
        # 期限切れタスク用の警告スタイル
        self.tree.tag_configure("overdue", background="#fff3cd", foreground="#856404")  # 黄色警告
        self.tree.tag_configure("priority_中", foreground="#000000")    # 黒
        self.tree.tag_configure("priority_低", foreground="#000000")    # 黒
    
    def _on_cell_click(self, event):
        """セルクリック時の処理 - 状態列のみインライン編集"""
        # 既存のコンボボックスを閉じる
        if self._inline_combo:
            self._inline_combo.destroy()
            self._inline_combo = None
        
        # クリックされた行と列を特定
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        col_id = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        
        # 列インデックス → 列名に変換（#1=id, #2=title, ... #4=status）
        col_index = int(col_id.replace("#", "")) - 1
        cols = ("id", "title", "assignee", "status", "priority", "start_date", "due_date")
        if col_index < 0 or col_index >= len(cols):
            return
        
        col_name = cols[col_index]
        
        # 状態列・担当者列（未割り当て時）のみインライン編集
        task_id = self.tree.item(item_id)["values"][0]
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if not task:
            return
        
        if col_name == "assignee" and task.assignee != "未割り当て":
            return  # 担当者が設定済みの場合は通常クリック
        if col_name not in ("status", "assignee"):
            return
        
        # セルの座標を取得してコンボボックスを配置
        bbox = self.tree.bbox(item_id, col_id)
        if not bbox:
            return
        x, y, width, height = bbox
        
        if col_name == "status":
            combo_values = ["未対応", "処理中", "完了"]
            current_val = task.status
        else:  # assignee
            combo_values = self.assignees
            current_val = task.assignee
        
        combo_var = tk.StringVar(value=current_val)
        combo = ttk.Combobox(
            self.tree, textvariable=combo_var,
            values=combo_values,
            state="readonly", width=max(8, max(len(v) for v in combo_values) + 1)
        )
        combo.place(x=x, y=y, width=width, height=height)
        combo.focus_set()
        self._inline_combo = combo
        
        def on_select(e=None):
            new_val = combo_var.get()
            old_val = task.status if col_name == "status" else task.assignee
            if col_name == "status":
                task.status = new_val
                action_type = "状態変更"
                detail = f"{old_val} → {new_val}"
            else:
                task.assignee = new_val
                action_type = "担当者変更"
                detail = f"{old_val} → {new_val}"
            combo.destroy()
            self._inline_combo = None
            if save_tasks(self.tasks):
                add_history(self.history, action_type, task.task_id, task.title, detail)
                self.refresh_table()
        
        def on_cancel(e=None):
            combo.destroy()
            self._inline_combo = None
        
        combo.bind("<<ComboboxSelected>>", on_select)
        combo.bind("<Escape>", on_cancel)
        combo.bind("<FocusOut>", on_cancel)
    
    def _sort_by(self, col):
        """列ヘッダークリックでソート"""
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        
        # 矢印をリセットしてクリックされた列に表示
        col_labels = {
            "id": "キー", "title": "タイトル（メモ）", "assignee": "担当者",
            "status": "状態", "priority": "優先度",
            "start_date": "開始日", "due_date": "期限"
        }
        for c, lbl in col_labels.items():
            self.tree.heading(c, text=lbl)
        arrow = " ▲" if self._sort_asc else " ▼"
        self.tree.heading(col, text=col_labels[col] + arrow)
        
        self.refresh_table()
    
    def refresh_table(self):
        """テーブルを更新（現在のソート順で表示）"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # ソートキー定義
        priority_order = {"高": 0, "中": 1, "低": 2}
        
        def sort_key(task):
            if self._sort_col == "id":
                # TASK-001 → 001 の数値順（入力順）
                try:
                    return int(task.task_id.split('-')[1])
                except:
                    return 0
            elif self._sort_col == "title":
                return task.title
            elif self._sort_col == "assignee":
                return task.assignee
            elif self._sort_col == "status":
                return task.status
            elif self._sort_col == "priority":
                return priority_order.get(task.priority, 9)
            elif self._sort_col == "start_date":
                return task.start_date if task.start_date != "-" else "9999"
            elif self._sort_col == "due_date":
                return task.due_date if task.due_date != "-" else "9999"
            return ""
        
        sorted_tasks = sorted(self.tasks, key=sort_key, reverse=not self._sort_asc)
        
        for task in sorted_tasks:
            tags = ["black"]  # 全行に黒色タグを適用
            # 期限切れチェック（完了でないかつ期限がある場合）
            if self._is_overdue(task):
                tags.append("overdue")  # 期限切れ背景色
            if task.status in ["未対応", "処理中", "完了"]:
                tags.append(f"status_{task.status}")
            if task.priority in ["高", "中", "低"]:
                tags.append(f"priority_{task.priority}")
            
            # タイトルの右側にメモを表示
            title_with_memo = task.title
            if task.memo:
                first_line = task.memo.splitlines()[0]
                title_with_memo = f"{task.title}    {first_line}"
            
            # statusタグは前景色を状態で優先指定
            row_tags = tags.copy()
            if task.status in ["未対応", "処理中", "完了"]:
                # statusタグが指定されている場合は、それが優先される（後付けされたタグが優先）
                row_tags.remove(f"status_{task.status}") if f"status_{task.status}" in row_tags else None
                row_tags.append(f"status_{task.status}")
            
            self.tree.insert(
                "", "end",
                iid=task.task_id,
                values=(
                    task.task_id,
                    title_with_memo,
                    task.assignee,
                    task.status,
                    task.priority,
                    task.start_date if task.start_date != "-" else "",
                    task.due_date if task.due_date != "-" else ""
                ),
                tags=row_tags
            )
        
        # 期限切れタスクを更新
        self._refresh_overdue_display()
    
    def _refresh_overdue_display(self):
        """期限切れタスク枠を更新"""
        # 既存の行を削除
        for item in self.overdue_tree.get_children():
            self.overdue_tree.delete(item)
        
        # 期限切れタスクを取得（未対応、処理中のみ）
        overdue_tasks = [t for t in self.tasks if self._is_overdue(t) and t.status in ["未対応", "処理中"]]
        
        # 期限切れタスクを期限順でソート
        overdue_tasks_sorted = sorted(overdue_tasks, key=lambda t: t.due_date)
        
        # テーブルに追加
        for task in overdue_tasks_sorted:
            title_with_memo = task.title
            if task.memo:
                first_line = task.memo.splitlines()[0]
                title_with_memo = f"{task.title}    {first_line}"
            
            # タグを計算
            tags = []
            if task.status in ["未対応", "処理中"]:
                tags.append(f"status_{task.status}")
            if task.priority in ["高", "中", "低"]:
                tags.append(f"priority_{task.priority}")
            
            self.overdue_tree.insert(
                "", "end",
                values=(
                    task.task_id,
                    title_with_memo,
                    task.assignee,
                    task.status,
                    task.priority,
                    task.start_date if task.start_date != "-" else "",
                    task.due_date
                ),
                tags=tuple(tags) if tags else ()
            )
    
    def add_task(self):
        """新規タスクを作成"""
        self.task_counter += 1
        save_counter(self.task_counter)  # 削除しても番号が戻らないよう即座に保存
        new_task = Task(
            task_id=f"TASK-{self.task_counter:03d}",
            title="",
            assignee=self.assignees[0],
            status="未対応",
            priority="中",
            start_date="-",
            due_date="-",
            memo=""
        )
        
        def on_saved(task):
            self.tasks.append(task)
            if save_tasks(self.tasks):
                add_history(self.history, "作成", task.task_id, task.title,
                            f"担当者:{task.assignee} 優先度:{task.priority} 期限:{task.due_date}")
                self.refresh_table()
        
        TaskEditorDialog(self.root, new_task, self.assignees, on_saved)
    
    def edit_task(self):
        """選択したタスクを編集"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("注意", "編集するタスクを選択してください")
            return
        
        if len(selection) > 1:
            messagebox.showinfo("注意", "1つのタスクのみ編集できます")
            return
        
        item_id = selection[0]
        task_id = self.tree.item(item_id)["values"][0]
        
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task:
            old_status    = task.status
            old_assignee  = task.assignee
            old_title     = task.title
            old_priority  = task.priority
            old_due       = task.due_date

            def on_saved(updated_task):
                idx = self.tasks.index(task)
                self.tasks[idx] = updated_task
                if save_tasks(self.tasks):
                    # 変更点を検出して履歴に記録
                    changes = []
                    if updated_task.title    != old_title:    changes.append(f"タイトル:{old_title}→{updated_task.title}")
                    if updated_task.status   != old_status:   changes.append(f"状態:{old_status}→{updated_task.status}")
                    if updated_task.assignee != old_assignee: changes.append(f"担当者:{old_assignee}→{updated_task.assignee}")
                    if updated_task.priority != old_priority: changes.append(f"優先度:{old_priority}→{updated_task.priority}")
                    if updated_task.due_date != old_due:      changes.append(f"期限:{old_due}→{updated_task.due_date}")
                    detail = " / ".join(changes) if changes else "変更なし"
                    add_history(self.history, "編集", updated_task.task_id, updated_task.title, detail)
                    self.refresh_table()

            TaskEditorDialog(self.root, task, self.assignees, on_saved)
    
    def delete_task(self):
        """選択したタスクをゴミ箱に移動"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("注意", "削除するタスクを選択してください")
            return
        
        if messagebox.askyesno("確認", "選択したタスクをゴミ箱に移動しますか?"):
            task_ids = [self.tree.item(item)["values"][0] for item in selection]
            deleted = [t for t in self.tasks if t.task_id in task_ids]
            self.tasks = [t for t in self.tasks if t.task_id not in task_ids]
            if save_tasks(self.tasks):
                # ゴミ箱に追加
                self.trash.extend(deleted)
                save_trash(self.trash)
                # 履歴に記録
                for t in deleted:
                    add_history(self.history, "削除", t.task_id, t.title,
                                f"担当者:{t.assignee} 状態:{t.status}")
                self.refresh_table()
    
    def manage_assignees(self):
        """担当者を管理"""
        def on_saved(assignees):
            self.assignees = assignees
            if save_assignees(self.assignees):
                messagebox.showinfo("完了", "担当者リストを保存しました")
        
        AssigneeManagerDialog(self.root, self.assignees, on_saved)
    
    def show_trash(self):
        """ゴミ箱ダイアログを表示"""
        TrashDialog(self.root, self.trash, self)
    
    def _is_overdue(self, task: Task) -> bool:
        """タスクが期限切れかチェック（完了でない場合のみ）"""
        if task.status == "完了" or task.due_date == "-":
            return False
        try:
            due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return due < today
        except:
            return False
    
    def _check_overdue_on_startup(self):
        """起動時に期限切れタスクをチェック"""
        overdue_tasks = [t for t in self.tasks if self._is_overdue(t)]
        if overdue_tasks:
            count = len(overdue_tasks)
            task_list = "\n".join([f"・{t.task_id}: {t.title}" for t in overdue_tasks[:5]])
            if count > 5:
                task_list += f"\n... ほか {count - 5} 件"
            messagebox.showwarning(
                "⚠️ 期限切れタスク",
                f"期限切れタスクが {count} 件あります:\n\n{task_list}"
            )


# ===================== メイン実行 =====================

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
