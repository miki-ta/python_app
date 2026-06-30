"""
カテゴリ・タグ・担当者管理とリマインダー機能付きタスク管理アプリ
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dataclasses import dataclass, field
from pathlib import Path
import json as _json
from datetime import datetime, date
import calendar

# ======================== データモデル ========================

@dataclass
class Task:
    task_id: str
    title: str
    category: str
    tags: list
    assignee: str
    status: str            # 未対応 / 処理中 / 完了
    priority: str          # 高 / 中 / 低
    start_date: str        # YYYY-MM-DD or "-"
    due_date: str          # YYYY-MM-DD or "-"
    memo: str
    reminder_minutes: int  # 0 = 通知なし
    created_at: str
    reminded: bool = False
    parent_id: str = None  # None=親タスク、設定時=サブタスク
    comments: list = field(default_factory=list)  # [{author, text, timestamp}]


@dataclass
class Category:
    name: str
    color: str


# ======================== データストレージ（JSON） ========================

DATA_DIR       = Path(__file__).parent / "data"
TASKS_FILE     = DATA_DIR / "tm_tasks.json"
CATS_FILE      = DATA_DIR / "tm_categories.json"
ASSIGNEES_FILE = DATA_DIR / "tm_assignees.json"
COUNTER_FILE   = DATA_DIR / "tm_counter.json"
NOTIFS_FILE    = DATA_DIR / "tm_notifications.json"

DEFAULT_CATEGORIES = [
    Category("仕事",   "#4472C4"),
    Category("個人",   "#ED7D31"),
    Category("学習",   "#70AD47"),
    Category("その他", "#767676"),
]

CATEGORY_COLORS = [
    "#4472C4", "#ED7D31", "#70AD47", "#FFC000",
    "#FF0000", "#9B59B6", "#1ABC9C", "#E74C3C",
]


def _load_json(path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    DATA_DIR.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        _json.dump(data, f, ensure_ascii=False, indent=2)


def init_db():
    """JSON ファイルを初期化し、旧 SQLite があれば一度だけ移行する。"""
    DATA_DIR.mkdir(exist_ok=True)
    if not CATS_FILE.exists():
        _save_json(CATS_FILE, [{"name": c.name, "color": c.color} for c in DEFAULT_CATEGORIES])
    if not ASSIGNEES_FILE.exists():
        _save_json(ASSIGNEES_FILE, ["未割り当て"])
    if not COUNTER_FILE.exists():
        _save_json(COUNTER_FILE, {"counter": 0})
    if not TASKS_FILE.exists():
        _save_json(TASKS_FILE, [])
    if not NOTIFS_FILE.exists():
        _save_json(NOTIFS_FILE, [])


def _dict_to_task(d) -> "Task":
    return Task(
        task_id          = d["task_id"],
        title            = d.get("title", ""),
        category         = d.get("category", ""),
        tags             = d.get("tags", []),
        assignee         = d.get("assignee", ""),
        status           = d.get("status", "未対応"),
        priority         = d.get("priority", "中"),
        start_date       = d.get("start_date", "-"),
        due_date         = d.get("due_date", "-"),
        memo             = d.get("memo", ""),
        reminder_minutes = d.get("reminder_minutes", 0),
        created_at       = d.get("created_at", ""),
        reminded         = d.get("reminded", False),
        parent_id        = d.get("parent_id"),
        comments         = d.get("comments", []),
    )


def _task_to_dict(task: "Task") -> dict:
    return {
        "task_id":          task.task_id,
        "title":            task.title,
        "category":         task.category,
        "tags":             task.tags,
        "assignee":         task.assignee,
        "status":           task.status,
        "priority":         task.priority,
        "start_date":       task.start_date,
        "due_date":         task.due_date,
        "memo":             task.memo,
        "reminder_minutes": task.reminder_minutes,
        "created_at":       task.created_at,
        "reminded":         task.reminded,
        "parent_id":        task.parent_id,
        "comments":         task.comments,
    }


def load_tasks() -> list:
    return [_dict_to_task(d) for d in _load_json(TASKS_FILE, [])]


def upsert_task(task: "Task") -> bool:
    try:
        items = _load_json(TASKS_FILE, [])
        d = _task_to_dict(task)
        for i, item in enumerate(items):
            if item["task_id"] == task.task_id:
                items[i] = d
                break
        else:
            items.append(d)
        _save_json(TASKS_FILE, items)
        return True
    except Exception:
        return False


def delete_tasks_by_ids(ids) -> bool:
    try:
        ids = set(ids)
        items = [t for t in _load_json(TASKS_FILE, []) if t["task_id"] not in ids]
        _save_json(TASKS_FILE, items)
        return True
    except Exception:
        return False


def next_task_counter() -> str:
    data = _load_json(COUNTER_FILE, {"counter": 0})
    n = data["counter"] + 1
    _save_json(COUNTER_FILE, {"counter": n})
    return f"TASK-{n:03d}"


def load_categories() -> list:
    items = _load_json(CATS_FILE, [])
    return [Category(c["name"], c["color"]) for c in items] or list(DEFAULT_CATEGORIES)


def save_categories(cats: list) -> bool:
    try:
        _save_json(CATS_FILE, [{"name": c.name, "color": c.color} for c in cats])
        return True
    except Exception:
        return False


def load_assignees() -> list:
    return _load_json(ASSIGNEES_FILE, ["未割り当て"]) or ["未割り当て"]


def save_assignees(assignees: list) -> bool:
    try:
        _save_json(ASSIGNEES_FILE, assignees)
        return True
    except Exception:
        return False


def load_notifications() -> list:
    items = _load_json(NOTIFS_FILE, [])
    return list(reversed(items[-100:]))


def add_notification_to_db(task_id, task_title, message, assignee, timestamp):
    try:
        items = _load_json(NOTIFS_FILE, [])
        new_id = max((n.get("db_id", 0) for n in items), default=0) + 1
        items.append({
            "db_id":      new_id,
            "task_id":    task_id,
            "task_title": task_title,
            "message":    message,
            "assignee":   assignee,
            "timestamp":  timestamp,
            "read":       False,
        })
        _save_json(NOTIFS_FILE, items)
    except Exception:
        pass


def mark_all_notifications_read():
    try:
        items = _load_json(NOTIFS_FILE, [])
        for n in items:
            n["read"] = True
        _save_json(NOTIFS_FILE, items)
    except Exception:
        pass


def clear_all_notifications():
    try:
        _save_json(NOTIFS_FILE, [])
    except Exception:
        pass


# ======================== カレンダーダイアログ ========================

class DatePickerDialog(tk.Toplevel):
    def __init__(self, parent, on_selected):
        super().__init__(parent)
        self.title("日付を選択")
        self.geometry("310x280")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        self.on_selected = on_selected
        self.cur = datetime.now()

        hdr = ttk.Frame(self)
        hdr.pack(pady=8)
        ttk.Button(hdr, text="◀", width=3, command=self._prev).pack(side=tk.LEFT, padx=5)
        self.lbl = ttk.Label(hdr, text="", font=("Arial", 11, "bold"))
        self.lbl.pack(side=tk.LEFT, padx=20)
        ttk.Button(hdr, text="▶", width=3, command=self._next).pack(side=tk.LEFT, padx=5)

        self.cal_frame = ttk.Frame(self)
        self.cal_frame.pack(padx=10, fill=tk.BOTH, expand=True)

        ttk.Button(self, text="キャンセル", command=self.destroy).pack(pady=8)
        self._draw()

    def _prev(self):
        y, m = self.cur.year, self.cur.month
        self.cur = self.cur.replace(year=y - 1, month=12) if m == 1 else self.cur.replace(month=m - 1)
        self._draw()

    def _next(self):
        y, m = self.cur.year, self.cur.month
        self.cur = self.cur.replace(year=y + 1, month=1) if m == 12 else self.cur.replace(month=m + 1)
        self._draw()

    def _draw(self):
        for w in self.cal_frame.winfo_children():
            w.destroy()
        self.lbl.config(text=f"{self.cur.year}年 {self.cur.month}月")
        for i, d in enumerate(["月", "火", "水", "木", "金", "土", "日"]):
            ttk.Label(self.cal_frame, text=d, width=4, anchor="center").grid(row=0, column=i, padx=1)
        for wi, week in enumerate(calendar.monthcalendar(self.cur.year, self.cur.month), 1):
            for di, day in enumerate(week):
                if day == 0:
                    ttk.Label(self.cal_frame, text="", width=4).grid(row=wi, column=di)
                else:
                    ttk.Button(
                        self.cal_frame, text=str(day), width=4,
                        command=lambda d=day: self._select(d)
                    ).grid(row=wi, column=di, padx=1, pady=1)

    def _select(self, day):
        self.on_selected(f"{self.cur.year:04d}-{self.cur.month:02d}-{day:02d}")
        self.destroy()


# ======================== タスク編集ダイアログ ========================

class TaskEditorDialog(tk.Toplevel):
    REMINDER_OPTIONS = [
        ("通知なし", 0), ("15分前", 15), ("30分前", 30),
        ("1時間前", 60), ("3時間前", 180), ("1日前", 1440),
    ]

    def __init__(self, parent, task, categories, assignees, on_saved, all_tasks=None):
        super().__init__(parent)
        self.title("新規タスク" if not task.title else "タスク編集")
        self.geometry("530x570")
        self.grab_set()
        self.transient(parent)

        self.task       = task
        self.categories = categories
        self.assignees  = assignees
        self.on_saved   = on_saved
        self.all_tasks  = all_tasks or []
        self._start     = task.start_date
        # due_date を日付部分と時刻部分に分割
        if task.due_date != "-" and " " in task.due_date:
            _d, _t = task.due_date.split(" ", 1)
            self._due      = _d
            _th, _tm       = (_t.split(":") + ["0"])[:2]
        else:
            self._due      = task.due_date
            _th, _tm       = "0", "0"
        self._due_hh   = tk.StringVar(value=f"{int(_th):02d}")
        self._due_mm   = tk.StringVar(value=f"{int(_tm):02d}")
        self._use_time = tk.BooleanVar(value=task.due_date != "-" and " " in task.due_date)

        form = ttk.Frame(self)
        form.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)

        r = 0
        ttk.Label(form, text="タスクID:").grid(row=r, column=0, sticky=tk.W, pady=4)
        ttk.Label(form, text=task.task_id).grid(row=r, column=1, sticky=tk.W, pady=4)
        r += 1

        if task.parent_id:
            ttk.Label(form, text="親タスク:").grid(row=r, column=0, sticky=tk.W, pady=4)
            pt = next((t for t in self.all_tasks if t.task_id == task.parent_id), None)
            parent_lbl = task.parent_id + (f"  ({pt.title})" if pt else "")
            ttk.Label(form, text=parent_lbl, foreground="#2980b9").grid(row=r, column=1, sticky=tk.W, pady=4)
            r += 1

        ttk.Label(form, text="タイトル *:").grid(row=r, column=0, sticky=tk.W, pady=4)
        self.title_var = tk.StringVar(value=task.title)
        ttk.Entry(form, textvariable=self.title_var, width=36).grid(row=r, column=1, sticky=tk.EW, pady=4)
        r += 1

        ttk.Label(form, text="カテゴリ:").grid(row=r, column=0, sticky=tk.W, pady=4)
        self.cat_var = tk.StringVar(value=task.category)
        ttk.Combobox(form, textvariable=self.cat_var,
                     values=[c.name for c in categories],
                     state="readonly", width=33).grid(row=r, column=1, sticky=tk.EW, pady=4)
        r += 1

        ttk.Label(form, text="タグ（カンマ区切り）:").grid(row=r, column=0, sticky=tk.W, pady=4)
        self.tags_var = tk.StringVar(value=", ".join(task.tags))
        ttk.Entry(form, textvariable=self.tags_var, width=36).grid(row=r, column=1, sticky=tk.EW, pady=4)
        r += 1

        ttk.Label(form, text="担当者:").grid(row=r, column=0, sticky=tk.W, pady=4)
        self.assignee_var = tk.StringVar(value=task.assignee)
        ttk.Combobox(form, textvariable=self.assignee_var,
                     values=assignees, state="readonly", width=33).grid(row=r, column=1, sticky=tk.EW, pady=4)
        r += 1

        ttk.Label(form, text="状態:").grid(row=r, column=0, sticky=tk.W, pady=4)
        self.status_var = tk.StringVar(value=task.status)
        _STATUS_COLORS = {
            "未対応": {"sel": "#b05050", "unsel_bg": "#f2e8e8", "unsel_fg": "#b05050"},
            "処理中": {"sel": "#b8843a", "unsel_bg": "#f2ece0", "unsel_fg": "#b8843a"},
            "完了":   {"sel": "#4e8068", "unsel_bg": "#e4eeea", "unsel_fg": "#4e8068"},
        }
        _STATUS_ICONS = {"未対応": "⏸", "処理中": "▶", "完了": "✓"}
        sbf = tk.Frame(form)
        sbf.grid(row=r, column=1, sticky=tk.W, pady=4)
        self._status_dialog_btns = {}

        def _pick_status(s):
            self.status_var.set(s)
            for label, b in self._status_dialog_btns.items():
                c = _STATUS_COLORS[label]
                if label == s:
                    b.config(bg=c["sel"], fg="white",
                             activebackground=c["sel"], activeforeground="white")
                else:
                    b.config(bg=c["unsel_bg"], fg=c["unsel_fg"],
                             activebackground=c["sel"], activeforeground="white")

        for s, c in _STATUS_COLORS.items():
            is_sel = (s == task.status)
            b = tk.Button(
                sbf, text=f"{_STATUS_ICONS[s]} {s}",
                font=("Arial", 10, "bold"),
                bg=c["sel"] if is_sel else c["unsel_bg"],
                fg="white" if is_sel else c["unsel_fg"],
                activebackground=c["sel"], activeforeground="white",
                relief="flat", bd=0, padx=12, pady=6,
                cursor="hand2",
                command=lambda v=s: _pick_status(v),
            )
            b.pack(side=tk.LEFT, padx=3)
            self._status_dialog_btns[s] = b
        r += 1

        ttk.Label(form, text="優先度:").grid(row=r, column=0, sticky=tk.W, pady=4)
        self.priority_var = tk.StringVar(value=task.priority)
        _PRIORITY_COLORS = {
            "高": {"sel": "#b05050", "unsel_bg": "#f2e8e8", "unsel_fg": "#b05050"},
            "中": {"sel": "#b8843a", "unsel_bg": "#f2ece0", "unsel_fg": "#b8843a"},
            "低": {"sel": "#4e8068", "unsel_bg": "#e4eeea", "unsel_fg": "#4e8068"},
        }
        _PRIORITY_ICONS = {"高": "🔴", "中": "🟡", "低": "🟢"}
        pbf = tk.Frame(form)
        pbf.grid(row=r, column=1, sticky=tk.W, pady=4)
        self._priority_dialog_btns = {}

        def _pick_priority(p):
            self.priority_var.set(p)
            for label, b in self._priority_dialog_btns.items():
                c = _PRIORITY_COLORS[label]
                if label == p:
                    b.config(bg=c["sel"], fg="white",
                             activebackground=c["sel"], activeforeground="white")
                else:
                    b.config(bg=c["unsel_bg"], fg=c["unsel_fg"],
                             activebackground=c["sel"], activeforeground="white")

        for p, c in _PRIORITY_COLORS.items():
            is_sel = (p == task.priority)
            b = tk.Button(
                pbf, text=f"{_PRIORITY_ICONS.get(p, '')} {p}",
                font=("Arial", 10, "bold"),
                bg=c["sel"] if is_sel else c["unsel_bg"],
                fg="white" if is_sel else c["unsel_fg"],
                activebackground=c["sel"], activeforeground="white",
                relief="flat", bd=0, padx=12, pady=6,
                cursor="hand2",
                command=lambda v=p: _pick_priority(v),
            )
            b.pack(side=tk.LEFT, padx=3)
            self._priority_dialog_btns[p] = b
        r += 1

        # 開始日
        ttk.Label(form, text="開始日:").grid(row=r, column=0, sticky=tk.W, pady=4)
        sf = ttk.Frame(form)
        sf.grid(row=r, column=1, sticky=tk.EW, pady=4)
        self.start_lbl = ttk.Label(sf, text=task.start_date if task.start_date != "-" else "未設定")
        self.start_lbl.pack(side=tk.LEFT)
        ttk.Button(sf, text="選択", width=6,
                   command=lambda: self._pick("start", self.start_lbl)).pack(side=tk.LEFT, padx=4)
        ttk.Button(sf, text="クリア", width=6,
                   command=lambda: self._clear("start", self.start_lbl)).pack(side=tk.LEFT)
        r += 1

        # 期限
        ttk.Label(form, text="期限:").grid(row=r, column=0, sticky=tk.W, pady=4)
        df = ttk.Frame(form)
        df.grid(row=r, column=1, sticky=tk.EW, pady=4)
        self.due_lbl = ttk.Label(df, text=self._due if self._due != "-" else "未設定")
        self.due_lbl.pack(side=tk.LEFT)
        ttk.Button(df, text="選択", width=6,
                   command=lambda: self._pick("due", self.due_lbl)).pack(side=tk.LEFT, padx=4)
        ttk.Button(df, text="クリア", width=6,
                   command=lambda: self._clear("due", self.due_lbl)).pack(side=tk.LEFT)
        ttk.Label(df, text="  ").pack(side=tk.LEFT)
        ttk.Checkbutton(df, text="時間を指定", variable=self._use_time,
                        command=self._toggle_time).pack(side=tk.LEFT, padx=(0, 6))
        self._due_hh_sb = ttk.Spinbox(df, from_=0, to=23, textvariable=self._due_hh,
                                       width=3, format="%02.0f", wrap=True)
        self._due_hh_sb.pack(side=tk.LEFT)
        self._time_colon = ttk.Label(df, text=":")
        self._time_colon.pack(side=tk.LEFT)
        self._due_mm_sb = ttk.Spinbox(df, from_=0, to=59, textvariable=self._due_mm,
                                       width=3, format="%02.0f", wrap=True)
        self._due_mm_sb.pack(side=tk.LEFT)
        self._toggle_time()
        r += 1

        ttk.Label(form, text="リマインダー:").grid(row=r, column=0, sticky=tk.W, pady=4)
        self.reminder_var = tk.StringVar()
        labels = [l for l, _ in self.REMINDER_OPTIONS]
        current_lbl = next((l for l, v in self.REMINDER_OPTIONS if v == task.reminder_minutes), "通知なし")
        self.reminder_var.set(current_lbl)
        ttk.Combobox(form, textvariable=self.reminder_var,
                     values=labels, state="readonly", width=33).grid(row=r, column=1, sticky=tk.EW, pady=4)
        r += 1

        ttk.Label(form, text="メモ:").grid(row=r, column=0, sticky=tk.NW, pady=4)
        self.memo_text = tk.Text(form, height=3, width=36)
        self.memo_text.grid(row=r, column=1, sticky=tk.EW, pady=4)
        self.memo_text.insert("1.0", task.memo)

        form.columnconfigure(1, weight=1)

        bf = ttk.Frame(self)
        bf.pack(pady=10)
        ttk.Button(bf, text="キャンセル", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="保存", command=self._save).pack(side=tk.LEFT, padx=5)

    def _pick(self, field_type, lbl):
        def on_sel(ds):
            if field_type == "start":
                self._start = ds
            else:
                self._due = ds
            lbl.config(text=ds)
        DatePickerDialog(self, on_sel)

    def _clear(self, field_type, lbl):
        if field_type == "start":
            self._start = "-"
        else:
            self._due = "-"
        lbl.config(text="未設定")

    def _toggle_time(self):
        if self._use_time.get():
            self._due_hh_sb.config(state="normal")
            self._due_mm_sb.config(state="normal")
            self._time_colon.config(foreground="black")
        else:
            self._due_hh_sb.config(state="disabled")
            self._due_mm_sb.config(state="disabled")
            self._time_colon.config(foreground="#aaaaaa")

    def _save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("入力エラー", "タイトルは必須です", parent=self)
            return

        tags = [t.strip() for t in self.tags_var.get().split(",") if t.strip()]
        reminder_lbl = self.reminder_var.get()
        reminder_min = next((v for l, v in self.REMINDER_OPTIONS if l == reminder_lbl), 0)

        self.task.title            = title
        self.task.category         = self.cat_var.get()
        self.task.tags             = tags
        self.task.assignee         = self.assignee_var.get()
        self.task.status           = self.status_var.get()
        self.task.priority         = self.priority_var.get()
        self.task.start_date = self._start
        if self._due == "-":
            self.task.due_date = "-"
        elif self._use_time.get():
            try:
                hh = max(0, min(23, int(self._due_hh.get())))
                mm = max(0, min(59, int(self._due_mm.get())))
            except ValueError:
                hh, mm = 0, 0
            self.task.due_date = f"{self._due} {hh:02d}:{mm:02d}"
        else:
            self.task.due_date = self._due
        self.task.reminder_minutes = reminder_min
        self.task.reminded         = False
        self.task.memo             = self.memo_text.get("1.0", tk.END).strip()

        self.on_saved(self.task)
        self.destroy()


# ======================== コメントダイアログ ========================

class CommentDialog(tk.Toplevel):
    def __init__(self, parent, task, assignees, on_comment_added):
        super().__init__(parent)
        self.title(f"コメント — {task.title}")
        self.geometry("520x500")
        self.grab_set()
        self.transient(parent)

        self.task              = task
        self.on_comment_added  = on_comment_added
        self.assignees         = assignees

        ttk.Label(self, text="コメント履歴", font=("Arial", 10, "bold")).pack(
            anchor=tk.W, padx=12, pady=(10, 4))

        # コメント一覧
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12)
        self._canvas = tk.Canvas(list_frame, bg="white", highlightthickness=1,
                                 highlightbackground="#cccccc")
        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._inner = tk.Frame(self._canvas, bg="white")
        self._cwin  = self._canvas.create_window((0, 0), window=self._inner, anchor=tk.NW)
        self._inner.bind("<Configure>", lambda _: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda ev: self._canvas.itemconfig(
            self._cwin, width=ev.width))
        self._canvas.bind("<MouseWheel>", lambda ev: self._canvas.yview_scroll(
            int(-1 * (ev.delta / 120)), "units"))
        self._render_comments()

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=12, pady=6)

        # コメント入力
        add_frame = ttk.LabelFrame(self, text="新しいコメントを追加")
        add_frame.pack(fill=tk.X, padx=12, pady=(0, 6))

        af = ttk.Frame(add_frame)
        af.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(af, text="投稿者:").pack(side=tk.LEFT)
        self.author_var = tk.StringVar(value=assignees[0] if assignees else "")
        ttk.Combobox(af, textvariable=self.author_var, values=assignees,
                     state="readonly", width=14).pack(side=tk.LEFT, padx=6)

        self.comment_text = tk.Text(add_frame, height=3, width=52, wrap=tk.WORD,
                                    font=("Arial", 9))
        self.comment_text.pack(padx=8, pady=(0, 6), fill=tk.X)

        bf = ttk.Frame(self)
        bf.pack(pady=8)
        ttk.Button(bf, text="閉じる",        command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="コメントを追加", command=self._add_comment).pack(side=tk.LEFT, padx=5)

    def _render_comments(self):
        for w in self._inner.winfo_children():
            w.destroy()
        comments = self.task.comments or []
        if not comments:
            ttk.Label(self._inner, text="コメントはまだありません",
                      foreground="#aaaaaa", font=("Arial", 9)).pack(pady=20)
            return
        for c in reversed(comments):
            item_frame = tk.Frame(self._inner, bg="white", bd=1, relief="solid")
            item_frame.pack(fill=tk.X, padx=4, pady=3)

            hdr = tk.Frame(item_frame, bg="#eef3ff")
            hdr.pack(fill=tk.X)
            tk.Label(hdr, text=f"  {c['author']}", font=("Arial", 9, "bold"),
                     bg="#eef3ff", fg="#2c3e50").pack(side=tk.LEFT, pady=3)
            tk.Label(hdr, text=c["timestamp"], font=("Arial", 8),
                     bg="#eef3ff", fg="#7f8c8d").pack(side=tk.RIGHT, padx=8, pady=3)

            tk.Label(item_frame, text=c["text"], font=("Arial", 9), bg="white",
                     wraplength=460, justify=tk.LEFT, anchor=tk.W,
                     padx=8, pady=6).pack(fill=tk.X)

    def _add_comment(self):
        text = self.comment_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("入力エラー", "コメントを入力してください", parent=self)
            return
        author = self.author_var.get()
        if not author:
            messagebox.showwarning("入力エラー", "投稿者を選択してください", parent=self)
            return
        comment = {
            "author":    author,
            "text":      text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.task.comments.append(comment)
        self.comment_text.delete("1.0", tk.END)
        self._render_comments()
        self.on_comment_added(self.task, comment)


# ======================== リマインダー通知ポップアップ ========================

class ReminderPopup(tk.Toplevel):
    def __init__(self, parent, tasks: list):
        super().__init__(parent)
        self.title("⏰ リマインダー")
        self.geometry("420x280")
        self.attributes("-topmost", True)

        ttk.Label(self, text="期限が近いタスクがあります！",
                  font=("Arial", 12, "bold")).pack(pady=10)

        fr = ttk.Frame(self)
        fr.pack(fill=tk.BOTH, expand=True, padx=10)

        tree = ttk.Treeview(fr, columns=("title", "due", "assignee"), show="headings", height=8)
        tree.heading("title",    text="タイトル")
        tree.heading("due",      text="期限")
        tree.heading("assignee", text="担当者")
        tree.column("title",    width=200)
        tree.column("due",      width=100, anchor="center")
        tree.column("assignee", width=90,  anchor="center")
        tree.pack(fill=tk.BOTH, expand=True)

        for t in tasks:
            tree.insert("", "end", values=(t.title, t.due_date, t.assignee))

        ttk.Button(self, text="閉じる", command=self.destroy).pack(pady=10)


# ======================== 通知センターパネル ========================

class NotificationPanel(tk.Toplevel):
    def __init__(self, parent, notifications, on_changed):
        super().__init__(parent)
        self.title("通知センター")
        self.geometry("500x540")
        self.grab_set()
        self.transient(parent)

        self.notifications = notifications
        self.on_changed    = on_changed

        hdr = ttk.Frame(self)
        hdr.pack(fill=tk.X, padx=12, pady=(10, 4))
        ttk.Label(hdr, text="通知センター", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        unread = sum(1 for n in notifications if not n.get("read"))
        self._unread_lbl = ttk.Label(
            hdr, text=f"未読 {unread}件" if unread else "",
            foreground="#e74c3c", font=("Arial", 10))
        self._unread_lbl.pack(side=tk.LEFT, padx=8)

        bf = ttk.Frame(self)
        bf.pack(fill=tk.X, padx=12, pady=4)
        ttk.Button(bf, text="すべて既読",   command=self._mark_all_read).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="通知をクリア", command=self._clear_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="閉じる",       command=self.destroy).pack(side=tk.RIGHT, padx=2)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=12, pady=4)

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self._canvas = tk.Canvas(list_frame, bg="white", highlightthickness=1,
                                 highlightbackground="#cccccc")
        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._inner = tk.Frame(self._canvas, bg="white")
        self._cwin  = self._canvas.create_window((0, 0), window=self._inner, anchor=tk.NW)
        self._inner.bind("<Configure>", lambda _: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda ev: self._canvas.itemconfig(
            self._cwin, width=ev.width))
        self._canvas.bind("<MouseWheel>", lambda ev: self._canvas.yview_scroll(
            int(-1 * (ev.delta / 120)), "units"))
        self._render()

    def _render(self):
        for w in self._inner.winfo_children():
            w.destroy()
        if not self.notifications:
            ttk.Label(self._inner, text="通知はありません",
                      foreground="#aaaaaa", font=("Arial", 9)).pack(pady=20)
            return
        for notif in self.notifications:
            is_read = notif.get("read", False)
            bg = "white" if is_read else "#fff8e1"

            item = tk.Frame(self._inner, bg=bg, bd=1, relief="solid")
            item.pack(fill=tk.X, padx=4, pady=2)

            dot = tk.Label(item, text="●" if not is_read else "○",
                           fg="#e74c3c" if not is_read else "#cccccc",
                           bg=bg, font=("Arial", 9))
            dot.pack(side=tk.LEFT, padx=(6, 2), pady=6)

            body = tk.Frame(item, bg=bg)
            body.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)
            tk.Label(body,
                     text=f"[{notif.get('task_id','')}]  {notif.get('task_title','')}",
                     font=("Arial", 9, "bold"), bg=bg, fg="#2c3e50",
                     anchor=tk.W).pack(anchor=tk.W)
            tk.Label(body, text=notif.get("message", ""),
                     font=("Arial", 9), bg=bg, fg="#555555",
                     anchor=tk.W).pack(anchor=tk.W)

            tk.Label(item, text=notif.get("timestamp", ""),
                     font=("Arial", 8), bg=bg, fg="#aaaaaa").pack(
                side=tk.RIGHT, padx=8, pady=6, anchor=tk.NE)

    def _mark_all_read(self):
        mark_all_notifications_read()
        for n in self.notifications:
            n["read"] = True
        self.on_changed()
        self._unread_lbl.config(text="")
        self._render()

    def _clear_all(self):
        if messagebox.askyesno("確認", "すべての通知を削除しますか？", parent=self):
            clear_all_notifications()
            self.notifications.clear()
            self.on_changed()
            self.destroy()


# ======================== カテゴリ管理ダイアログ ========================

class CategoryManagerDialog(tk.Toplevel):
    def __init__(self, parent, categories, on_saved):
        super().__init__(parent)
        self.title("カテゴリ管理")
        self.geometry("320x380")
        self.grab_set()
        self.transient(parent)

        self.cats     = [Category(c.name, c.color) for c in categories]
        self.on_saved = on_saved

        ttk.Label(self, text="カテゴリ一覧:").pack(anchor=tk.W, padx=10, pady=(10, 0))

        lf = ttk.Frame(self)
        lf.pack(padx=10, fill=tk.BOTH, expand=True)
        self.lb = tk.Listbox(lf, height=12, font=("Arial", 10))
        self.lb.pack(fill=tk.BOTH, expand=True)
        self._refresh()

        bf = ttk.Frame(self)
        bf.pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(bf, text="追加", command=self._add).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="削除", command=self._delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="保存", command=self._save).pack(side=tk.RIGHT, padx=2)

    def _refresh(self):
        self.lb.delete(0, tk.END)
        for c in self.cats:
            self.lb.insert(tk.END, f"  {c.name}")

    def _add(self):
        name = simpledialog.askstring("追加", "カテゴリ名:", parent=self)
        if not name or not name.strip():
            return
        name = name.strip()
        if any(c.name == name for c in self.cats):
            messagebox.showwarning("重複", "既に存在します", parent=self)
            return
        color = CATEGORY_COLORS[len(self.cats) % len(CATEGORY_COLORS)]
        self.cats.append(Category(name, color))
        self._refresh()

    def _delete(self):
        sel = self.lb.curselection()
        if not sel:
            return
        if len(self.cats) <= 1:
            messagebox.showwarning("注意", "最後のカテゴリは削除できません", parent=self)
            return
        self.cats.pop(sel[0])
        self._refresh()

    def _save(self):
        self.on_saved(self.cats)
        self.destroy()


# ======================== 担当者管理ダイアログ ========================

class AssigneeManagerDialog(tk.Toplevel):
    def __init__(self, parent, assignees, on_saved):
        super().__init__(parent)
        self.title("担当者管理")
        self.geometry("300x360")
        self.grab_set()
        self.transient(parent)

        self.assignees = assignees.copy()
        self.on_saved  = on_saved

        ttk.Label(self, text="担当者一覧:").pack(anchor=tk.W, padx=10, pady=(10, 0))

        lf = ttk.Frame(self)
        lf.pack(padx=10, fill=tk.BOTH, expand=True)
        self.lb = tk.Listbox(lf, height=10)
        self.lb.pack(fill=tk.BOTH, expand=True)
        self._refresh()

        bf = ttk.Frame(self)
        bf.pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(bf, text="追加", command=self._add).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="編集", command=self._edit).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="削除", command=self._delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="保存", command=self._save).pack(side=tk.RIGHT, padx=2)

    def _refresh(self):
        self.lb.delete(0, tk.END)
        for a in self.assignees:
            self.lb.insert(tk.END, a)

    def _add(self):
        name = simpledialog.askstring("追加", "担当者名:", parent=self)
        if name and name.strip() and name.strip() not in self.assignees:
            self.assignees.append(name.strip())
            self._refresh()

    def _edit(self):
        sel = self.lb.curselection()
        if not sel:
            return
        new = simpledialog.askstring("編集", "新しい名前:",
                                     initialvalue=self.assignees[sel[0]], parent=self)
        if new and new.strip():
            self.assignees[sel[0]] = new.strip()
            self._refresh()

    def _delete(self):
        sel = self.lb.curselection()
        if not sel:
            return
        if len(self.assignees) <= 1:
            messagebox.showwarning("注意", "最後の担当者は削除できません", parent=self)
            return
        self.assignees.pop(sel[0])
        self._refresh()

    def _save(self):
        self.on_saved(self.assignees)
        self.destroy()


# ======================== メインアプリケーション ========================

class TaskManagerApp:
    REMINDER_INTERVAL_MS = 60_000  # 1分ごとにリマインダーチェック

    STATUS_ICONS = {"未対応": "⏸", "処理中": "▶", "完了": "✓"}
    PRIORITY_ICONS = {"高": "🔴", "中": "🟡", "低": "🟢"}
    STATUS_COLORS_MAP = {
        "未対応": {"bg": "#b05050", "activebg": "#8e3e3e"},
        "処理中": {"bg": "#b8843a", "activebg": "#9a6e2e"},
        "完了":   {"bg": "#4e8068", "activebg": "#3d6654"},
    }
    PRIORITY_COLORS_MAP = {
        "高": {"bg": "#b05050", "activebg": "#8e3e3e"},
        "中": {"bg": "#b8843a", "activebg": "#9a6e2e"},
        "低": {"bg": "#4e8068", "activebg": "#3d6654"},
    }
    COL_DEFS = [
        ("status",     "状態",            100, tk.CENTER),
        ("id",         "ID",               80, tk.CENTER),
        ("title",      "タイトル（メモ）", 220, tk.W    ),
        ("comments",   "コメント",          65, tk.CENTER),
        ("progress",   "進捗",             70,  tk.CENTER),
        ("category",   "カテゴリ",          90, tk.CENTER),
        ("tags",       "タグ",             130, tk.W    ),
        ("assignee",   "担当者",            90, tk.CENTER),
        ("priority",   "優先度",            60, tk.CENTER),
        ("start_date", "開始日",            95, tk.CENTER),
        ("due_date",   "期限",             120, tk.CENTER),
    ]

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("タスク管理 — カテゴリ・タグ・担当者・リマインダー")
        self.root.geometry("1300x760")
        self.root.minsize(900, 600)

        init_db()
        self.tasks      = load_tasks()
        self.categories = load_categories()
        self.assignees  = load_assignees()

        self.filter_category = tk.StringVar(value="すべて")
        self.filter_assignee = tk.StringVar(value="すべて")
        self.filter_status   = tk.StringVar(value="すべて")
        self.filter_tag      = tk.StringVar(value="")
        self.filter_keyword  = tk.StringVar(value="")

        self._sort_col    = "id"
        self._sort_asc    = True
        self._selected_ids: set = set()
        self._row_frames:  dict = {}

        self.notifications    = load_notifications()
        self._notif_badge_var = tk.StringVar()

        self._build_ui()
        self._update_notif_badge()
        self.refresh_table()
        self._schedule_reminder_check()

    # ------------------------------------------------------------------ UI構築

    def _build_ui(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(toolbar, text="＋ 新規タスク",  command=self.add_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✎ 編集",         command=self.edit_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✔ 完了にする",   command=self.complete_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑 削除",           command=self.delete_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="＋ サブタスク追加", command=self.add_subtask).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="🔄 更新",           command=self.reload_data).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="📁 カテゴリ管理", command=self.manage_categories).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="👥 担当者管理",   command=self.manage_assignees).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="💬 コメント",     command=self.show_comments).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, textvariable=self._notif_badge_var,
                   command=self.show_notifications).pack(side=tk.LEFT, padx=2)

        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))

        # 左サイドバー
        self.sidebar = ttk.Frame(main, width=190)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        self.sidebar.pack_propagate(False)

        # 右エリア
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # フィルターバー
        fbar = ttk.LabelFrame(right, text="絞り込み")
        fbar.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(fbar, text="キーワード:").pack(side=tk.LEFT, padx=(8, 2), pady=5)
        kw = ttk.Entry(fbar, textvariable=self.filter_keyword, width=16)
        kw.pack(side=tk.LEFT, padx=2, pady=5)
        kw.bind("<Return>", lambda _: self.refresh_table())

        ttk.Label(fbar, text="タグ:").pack(side=tk.LEFT, padx=(8, 2), pady=5)
        te = ttk.Entry(fbar, textvariable=self.filter_tag, width=12)
        te.pack(side=tk.LEFT, padx=2, pady=5)
        te.bind("<Return>", lambda _: self.refresh_table())

        ttk.Label(fbar, text="担当者:").pack(side=tk.LEFT, padx=(8, 2), pady=5)
        self._assignee_cb = ttk.Combobox(
            fbar, textvariable=self.filter_assignee,
            values=["すべて"] + self.assignees, state="readonly", width=10,
        )
        self._assignee_cb.pack(side=tk.LEFT, padx=2, pady=5)

        ttk.Label(fbar, text="状態:").pack(side=tk.LEFT, padx=(8, 2), pady=5)
        ttk.Combobox(
            fbar, textvariable=self.filter_status,
            values=["すべて", "未対応", "処理中", "完了"], state="readonly", width=8,
        ).pack(side=tk.LEFT, padx=2, pady=5)

        ttk.Button(fbar, text="絞込",   command=self.refresh_table).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(fbar, text="クリア", command=self.clear_filters).pack(side=tk.LEFT, padx=2, pady=5)

        # テーブルコンテナ
        tf = tk.Frame(right)
        tf.pack(fill=tk.BOTH, expand=True)

        # ヘッダー行
        hdr = tk.Frame(tf, bg="#dde3ea")
        hdr.pack(fill=tk.X, side=tk.TOP)
        self._hdr_btns = {}
        for col, label, width, _ in self.COL_DEFS:
            cell = tk.Frame(hdr, width=width, height=28, bg="#dde3ea")
            cell.pack_propagate(False)
            cell.pack(side=tk.LEFT)
            btn = tk.Button(cell, text=label, bg="#dde3ea", fg="#333333",
                            font=("Arial", 9, "bold"), relief="flat", bd=0,
                            cursor="hand2", command=lambda c=col: self._sort_by(c))
            btn.pack(fill=tk.BOTH, expand=True)
            self._hdr_btns[col] = btn
        self._hdr_btns["id"].config(text="ID ▲")
        tk.Frame(tf, height=1, bg="#aaaaaa").pack(fill=tk.X)

        # スクロール可能なボディ
        body = tk.Frame(tf)
        body.pack(fill=tk.BOTH, expand=True)
        self._body_canvas = tk.Canvas(body, bg="white", highlightthickness=0)
        vsb = ttk.Scrollbar(body, orient=tk.VERTICAL, command=self._body_canvas.yview)
        self._body_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._body_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._rows_frame = tk.Frame(self._body_canvas, bg="white")
        self._canvas_win = self._body_canvas.create_window((0, 0), window=self._rows_frame, anchor=tk.NW)
        self._rows_frame.bind("<Configure>", lambda _: self._body_canvas.configure(
            scrollregion=self._body_canvas.bbox("all")))
        self._body_canvas.bind("<Configure>", lambda ev: self._body_canvas.itemconfig(
            self._canvas_win, width=ev.width))
        self._body_canvas.bind("<MouseWheel>", self._on_mousewheel)

        self.status_var = tk.StringVar(value="")
        ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W).pack(fill=tk.X, padx=10, pady=2)

    # ------------------------------------------------------------------ サイドバー

    def _build_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()

        cat_frame = ttk.LabelFrame(self.sidebar, text="カテゴリ")
        cat_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(cat_frame, text="すべて",
                   command=lambda: self._filter_cat("すべて")).pack(fill=tk.X, padx=5, pady=2)
        for cat in self.categories:
            ttk.Button(cat_frame, text=f"  {cat.name}",
                       command=lambda n=cat.name: self._filter_cat(n)).pack(fill=tk.X, padx=5, pady=1)

        stats_frame = ttk.LabelFrame(self.sidebar, text="統計")
        stats_frame.pack(fill=tk.X)

        total        = len(self.tasks)
        parent_count = sum(1 for t in self.tasks if not t.parent_id)
        child_count  = sum(1 for t in self.tasks if t.parent_id)
        todo    = sum(1 for t in self.tasks if t.status == "未対応")
        wip     = sum(1 for t in self.tasks if t.status == "処理中")
        done    = sum(1 for t in self.tasks if t.status == "完了")
        overdue = sum(1 for t in self.tasks if self._is_overdue(t))

        for label, val, red in [
            ("合計",       total,        False),
            ("親タスク",   parent_count, False),
            ("サブタスク", child_count,  False),
            ("未対応",     todo,         False),
            ("処理中",     wip,          False),
            ("完了",       done,         False),
            ("期限切れ",   overdue,      overdue > 0),
        ]:
            row = ttk.Frame(stats_frame)
            row.pack(fill=tk.X, padx=6, pady=1)
            ttk.Label(row, text=f"{label}:").pack(side=tk.LEFT)
            lbl = ttk.Label(row, text=str(val), font=("Arial", 10, "bold"))
            if red:
                lbl.config(foreground="#d9534f")
            lbl.pack(side=tk.RIGHT)

    def _filter_cat(self, name):
        self.filter_category.set(name)
        self.refresh_table()

    # ------------------------------------------------------------------ フィルター・ソート

    def clear_filters(self):
        self.filter_category.set("すべて")
        self.filter_assignee.set("すべて")
        self.filter_status.set("すべて")
        self.filter_tag.set("")
        self.filter_keyword.set("")
        self.refresh_table()

    def _filtered_tasks(self) -> list:
        cat     = self.filter_category.get()
        asn     = self.filter_assignee.get()
        status  = self.filter_status.get()
        tag     = self.filter_tag.get().strip().lower()
        keyword = self.filter_keyword.get().strip().lower()

        result = []
        for t in self.tasks:
            if cat    != "すべて" and t.category != cat:
                continue
            if asn    != "すべて" and t.assignee != asn:
                continue
            if status != "すべて" and t.status   != status:
                continue
            if tag and not any(tag in tg.lower() for tg in t.tags):
                continue
            if keyword and keyword not in t.title.lower() and keyword not in t.memo.lower():
                continue
            result.append(t)
        return result

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        self.refresh_table()

    # ------------------------------------------------------------------ テーブル更新

    def refresh_table(self):
        for w in self._rows_frame.winfo_children():
            w.destroy()
        self._row_frames = {}

        # 全タスクの親子マップを構築（表示・ソート両方で使用）
        children_map: dict = {}
        for t in self.tasks:
            if t.parent_id:
                children_map.setdefault(t.parent_id, []).append(t)

        priority_order = {"高": 0, "中": 1, "低": 2}

        def sort_key(task):
            c = self._sort_col
            if c == "id":
                try:
                    return int(task.task_id.split("-")[1])
                except Exception:
                    return 0
            if c == "priority":
                return priority_order.get(task.priority, 9)
            if c == "start_date":
                return task.start_date if task.start_date != "-" else "9999"
            if c == "due_date":
                return task.due_date if task.due_date != "-" else "9999"
            if c == "tags":
                return ", ".join(task.tags)
            if c == "progress":
                clist = children_map.get(task.task_id, [])
                if not clist:
                    return -1.0
                return sum(1 for ch in clist if ch.status == "完了") / len(clist)
            return getattr(task, c, "")

        filtered = self._filtered_tasks()

        # 親タスクをソートし、各親の直下にサブタスクを配置
        parent_filtered = sorted(
            [t for t in filtered if not t.parent_id],
            key=sort_key, reverse=not self._sort_asc
        )
        arranged: list = []
        shown_ids: set = set()
        for parent in parent_filtered:
            arranged.append((parent, False))
            shown_ids.add(parent.task_id)
            for child_task in sorted(children_map.get(parent.task_id, []), key=lambda t: t.task_id):
                arranged.append((child_task, True))
                shown_ids.add(child_task.task_id)
        # フィルターで親が非表示になったサブタスクを末尾に追加
        for t in filtered:
            if t.task_id not in shown_ids:
                arranged.append((t, bool(t.parent_id)))

        for i, (task, is_child) in enumerate(arranged):
            if is_child:
                base_bg = "#eef3ff" if i % 2 == 0 else "#f5f8ff"
            else:
                base_bg = "#f8f8f8" if i % 2 == 0 else "white"
            is_overdue = self._is_overdue(task)
            if is_overdue:
                base_bg = "#fff3cd"
            is_sel = task.task_id in self._selected_ids
            bg = "#cce5ff" if is_sel else base_bg
            text_fg = "#b05050" if is_overdue else "black"

            row = tk.Frame(self._rows_frame, bg=bg)
            row.pack(fill=tk.X, side=tk.TOP)

            # サブタスク進捗を計算
            clist = children_map.get(task.task_id, [])
            if clist and not is_child:
                done_count  = sum(1 for c in clist if c.status == "完了")
                total_count = len(clist)
                progress_str = f"{done_count}/{total_count}"
                pct = done_count / total_count
            else:
                progress_str = "-"
                pct = 0.0

            indent = "  └ " if is_child else ""
            title_display = (
                task.title if not task.memo
                else f"{task.title}  [{task.memo[:25]}{'…' if len(task.memo) > 25 else ''}]"
            )
            comment_count = len(task.comments) if task.comments else 0
            cell_values = {
                "status":     task.status,
                "id":         task.task_id,
                "title":      indent + title_display,
                "comments":   f"{comment_count}件" if comment_count > 0 else "-",
                "progress":   progress_str,
                "category":   task.category,
                "tags":       "  ".join(f"#{tg}" for tg in task.tags),
                "assignee":   task.assignee,
                "priority":   task.priority,
                "start_date": task.start_date if task.start_date != "-" else "",
                "due_date":   task.due_date if task.due_date != "-" else "",
            }

            for col, _, width, anchor in self.COL_DEFS:
                cell = tk.Frame(row, width=width, height=26, bg=bg)
                cell.pack_propagate(False)
                cell.pack(side=tk.LEFT)
                if col == "status":
                    c = self.STATUS_COLORS_MAP.get(task.status, {"bg": "#999", "activebg": "#777"})
                    sb = tk.Button(
                        cell, text=f"{self.STATUS_ICONS.get(task.status, '')} {task.status}",
                        bg=c["bg"], fg="white",
                        activebackground=c["activebg"], activeforeground="white",
                        font=("Arial", 9, "bold"), relief="flat", bd=0,
                        cursor="hand2",
                    )
                    sb.config(command=lambda t=task, b=sb: self._status_btn_click(t, b))
                    sb.pack(padx=5, pady=3, fill=tk.X)
                elif col == "comments":
                    fg = "#2980b9" if comment_count > 0 else "#aaaaaa"
                    tk.Label(
                        cell, text=cell_values["comments"], bg=bg,
                        anchor=anchor, font=("Arial", 9, "bold"),
                        foreground=fg, padx=4,
                    ).pack(fill=tk.BOTH, expand=True)
                elif col == "progress":
                    if progress_str == "-":
                        fg_color = "#aaaaaa"
                    elif pct == 1.0:
                        fg_color = "#27ae60"  # 全完了: 緑
                    elif pct > 0:
                        fg_color = "#e67e22"  # 一部完了: 橙
                    else:
                        fg_color = "#e74c3c"  # 未着手: 赤
                    tk.Label(
                        cell, text=progress_str, bg=bg,
                        anchor=anchor, font=("Arial", 9, "bold"),
                        foreground=fg_color, padx=4,
                    ).pack(fill=tk.BOTH, expand=True)
                elif col == "priority":
                    c = self.PRIORITY_COLORS_MAP.get(task.priority, {"bg": "#999999", "activebg": "#777777"})
                    pb = tk.Button(
                        cell, text=f"{self.PRIORITY_ICONS.get(task.priority, '')} {task.priority}",
                        bg=c["bg"], fg="white",
                        activebackground=c["activebg"], activeforeground="white",
                        font=("Arial", 9, "bold"), relief="flat", bd=0,
                        cursor="hand2",
                    )
                    pb.config(command=lambda t=task, b=pb: self._priority_btn_click(t, b))
                    pb.pack(padx=5, pady=3, fill=tk.X)
                else:
                    tk.Label(
                        cell, text=cell_values[col], bg=bg,
                        anchor=anchor, font=("Arial", 9), padx=4, fg=text_fg,
                    ).pack(fill=tk.BOTH, expand=True)

            row.bind("<Button-1>",        lambda _, tid=task.task_id: self._select_row(tid))
            row.bind("<Double-Button-1>", lambda _: self.edit_task())
            for child_w in row.winfo_children():
                child_w.bind("<Button-1>",        lambda _, tid=task.task_id: self._select_row(tid))
                child_w.bind("<Double-Button-1>", lambda _: self.edit_task())
                child_w.bind("<MouseWheel>",      self._on_mousewheel)
                for gc in child_w.winfo_children():
                    if not isinstance(gc, tk.Button):
                        gc.bind("<Button-1>",        lambda _, tid=task.task_id: self._select_row(tid))
                        gc.bind("<Double-Button-1>", lambda _: self.edit_task())
                    gc.bind("<MouseWheel>", self._on_mousewheel)
            row.bind("<MouseWheel>", self._on_mousewheel)

            self._row_frames[task.task_id] = (row, base_bg)

        col_label_map = {c: lbl for c, lbl, _, _ in self.COL_DEFS}
        for col, btn in self._hdr_btns.items():
            lbl = col_label_map[col]
            btn.config(text=lbl + (" ▲" if self._sort_asc else " ▼") if col == self._sort_col else lbl)

        self.status_var.set(f"表示: {len(arranged)} 件  ／  全体: {len(self.tasks)} 件")
        self._build_sidebar()

    # ------------------------------------------------------------------ CRUD

    def add_task(self):
        task_id = next_task_counter()
        cat_name = self.categories[0].name if self.categories else "その他"
        new_task = Task(
            task_id=task_id,
            title="",
            category=cat_name,
            tags=[],
            assignee=self.assignees[0] if self.assignees else "未割り当て",
            status="未対応",
            priority="中",
            start_date="-",
            due_date="-",
            memo="",
            reminder_minutes=0,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        def on_saved(task):
            if not task.title:
                return
            if upsert_task(task):
                self.tasks.append(task)
                self._add_notification(task.task_id, task.title,
                                       f"タスクが作成されました（担当: {task.assignee}）",
                                       task.assignee)
                self.refresh_table()

        TaskEditorDialog(self.root, new_task, self.categories, self.assignees, on_saved, self.tasks)

    def edit_task(self):
        sel = list(self._selected_ids)
        if not sel:
            messagebox.showinfo("注意", "編集するタスクを選択してください")
            return
        if len(sel) > 1:
            messagebox.showinfo("注意", "1件のみ選択してください")
            return

        task_id = sel[0]
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if not task:
            return

        old_assignee = task.assignee
        old_status   = task.status

        def on_saved(updated):
            idx = next((i for i, t in enumerate(self.tasks) if t.task_id == task_id), None)
            if idx is not None:
                self.tasks[idx] = updated
                upsert_task(updated)
                self._add_notification(updated.task_id, updated.title,
                                       "タスクが更新されました", updated.assignee)
                if old_assignee != updated.assignee:
                    self._add_notification(updated.task_id, updated.title,
                                           f"{updated.assignee} に担当が変更されました",
                                           updated.assignee)
                if old_status != updated.status:
                    self._add_notification(updated.task_id, updated.title,
                                           f"ステータスが「{old_status}」→「{updated.status}」に変更されました",
                                           updated.assignee)
                self.refresh_table()

        TaskEditorDialog(self.root, task, self.categories, self.assignees, on_saved, self.tasks)

    def add_subtask(self):
        sel = list(self._selected_ids)
        if not sel:
            messagebox.showinfo("注意", "サブタスクを追加する親タスクを選択してください")
            return
        if len(sel) > 1:
            messagebox.showinfo("注意", "1件の親タスクを選択してください")
            return
        parent_id = sel[0]
        parent_task = next((t for t in self.tasks if t.task_id == parent_id), None)
        if not parent_task:
            return
        if parent_task.parent_id:
            messagebox.showwarning("注意", "サブタスクにはサブタスクを追加できません（階層は1段階まで）")
            return

        task_id = next_task_counter()
        new_task = Task(
            task_id=task_id,
            title="",
            category=parent_task.category,
            tags=list(parent_task.tags),
            assignee=parent_task.assignee,
            status="未対応",
            priority=parent_task.priority,
            start_date="-",
            due_date="-",
            memo="",
            reminder_minutes=0,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            parent_id=parent_id,
        )

        def on_saved(task):
            if not task.title:
                return
            if upsert_task(task):
                self.tasks.append(task)
                parent = next((t for t in self.tasks if t.task_id == parent_id), None)
                parent_title = parent.title if parent else parent_id
                self._add_notification(task.task_id, task.title,
                                       f"「{parent_title}」にサブタスクが追加されました",
                                       task.assignee)
                self.refresh_table()

        TaskEditorDialog(self.root, new_task, self.categories, self.assignees, on_saved, self.tasks)

    def complete_task(self):
        sel = list(self._selected_ids)
        if not sel:
            messagebox.showinfo("注意", "完了にするタスクを選択してください")
            return
        count = 0
        for tid in sel:
            task = next((t for t in self.tasks if t.task_id == tid), None)
            if task and task.status != "完了":
                task.status = "完了"
                upsert_task(task)
                self._add_notification(task.task_id, task.title,
                                       f"タスクが完了しました（担当: {task.assignee}）",
                                       task.assignee)
                count += 1
        if count:
            self.refresh_table()
            messagebox.showinfo("完了", f"{count} 件を完了にしました")

    def delete_task(self):
        sel = list(self._selected_ids)
        if not sel:
            messagebox.showinfo("注意", "削除するタスクを選択してください")
            return
        child_tasks = [t for t in self.tasks if t.parent_id in self._selected_ids]
        if child_tasks:
            if not messagebox.askyesno(
                "確認",
                f"{len(sel)} 件を削除しますか？\n"
                f"選択したタスクにはサブタスクが {len(child_tasks)} 件あります。\n"
                f"サブタスクも一緒に削除されます。"
            ):
                return
            ids_to_delete = self._selected_ids | {t.task_id for t in child_tasks}
        else:
            if not messagebox.askyesno("確認", f"{len(sel)} 件を削除しますか?"):
                return
            ids_to_delete = set(sel)
        delete_tasks_by_ids(ids_to_delete)
        self.tasks = [t for t in self.tasks if t.task_id not in ids_to_delete]
        self._selected_ids.clear()
        self.refresh_table()

    # ------------------------------------------------------------------ 同期・更新

    def reload_data(self):
        self.tasks         = load_tasks()
        self.categories    = load_categories()
        self.assignees     = load_assignees()
        self.notifications = load_notifications()
        self._assignee_cb.config(values=["すべて"] + self.assignees)
        self._selected_ids.clear()
        self._update_notif_badge()
        self.refresh_table()
        self.status_var.set(
            f"🔄 更新しました — {datetime.now().strftime('%H:%M:%S')}  ／  "
            f"全体: {len(self.tasks)} 件"
        )

    # ------------------------------------------------------------------ マスタ管理

    def manage_categories(self):
        def on_saved(cats):
            self.categories = cats
            save_categories(cats)
            self.refresh_table()

        CategoryManagerDialog(self.root, self.categories, on_saved)

    def manage_assignees(self):
        def on_saved(assignees):
            self.assignees = assignees
            save_assignees(assignees)
            self._assignee_cb.config(values=["すべて"] + assignees)

        AssigneeManagerDialog(self.root, self.assignees, on_saved)

    # ------------------------------------------------------------------ コメント・通知

    def show_comments(self):
        sel = list(self._selected_ids)
        if not sel:
            messagebox.showinfo("注意", "コメントを表示するタスクを選択してください")
            return
        if len(sel) > 1:
            messagebox.showinfo("注意", "1件のみ選択してください")
            return
        task = next((t for t in self.tasks if t.task_id == sel[0]), None)
        if not task:
            return

        def on_comment_added(updated_task, comment):
            upsert_task(updated_task)
            idx = next((i for i, t in enumerate(self.tasks) if t.task_id == updated_task.task_id), None)
            if idx is not None:
                self.tasks[idx] = updated_task
            snippet = comment["text"][:40] + ("…" if len(comment["text"]) > 40 else "")
            self._add_notification(
                updated_task.task_id, updated_task.title,
                f"{comment['author']} がコメントを追加しました: {snippet}",
                updated_task.assignee,
            )
            self.refresh_table()

        CommentDialog(self.root, task, self.assignees, on_comment_added)

    def show_notifications(self):
        def on_changed():
            self.notifications = load_notifications()
            self._update_notif_badge()

        NotificationPanel(self.root, self.notifications, on_changed)

    def _add_notification(self, task_id: str, task_title: str, message: str, assignee: str = ""):
        add_notification_to_db(task_id, task_title, message, assignee,
                               datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.notifications = load_notifications()
        self._update_notif_badge()

    def _update_notif_badge(self):
        unread = sum(1 for n in self.notifications if not n.get("read"))
        self._notif_badge_var.set(f"🔔 通知 ({unread})" if unread else "🔔 通知")

    # ------------------------------------------------------------------ 状態ボタン・選択・スクロール

    def _priority_btn_click(self, task, btn):
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        self._show_priority_popup(x, y, task)

    def _show_priority_popup(self, x, y, task):
        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)
        popup.geometry(f"+{x}+{y}")
        popup.configure(bg="#444444")

        def set_priority(p):
            task.priority = p
            upsert_task(task)
            self.refresh_table()
            if popup.winfo_exists():
                popup.destroy()

        for priority, colors in self.PRIORITY_COLORS_MAP.items():
            tk.Button(
                popup,
                text=f"  {self.PRIORITY_ICONS.get(priority, '')} {priority}  ",
                bg=colors["bg"], fg="white",
                activebackground=colors["activebg"], activeforeground="white",
                font=("Arial", 10, "bold"),
                relief="flat", bd=0,
                padx=10, pady=7,
                cursor="hand2",
                command=lambda p=priority: set_priority(p),
            ).pack(fill=tk.X, padx=2, pady=1)

        popup.bind("<Escape>", lambda _: popup.destroy())
        popup.bind("<FocusOut>", lambda _: popup.destroy() if popup.winfo_exists() else None)
        popup.update_idletasks()
        popup.focus_set()

    def _status_btn_click(self, task, btn):
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        self._show_status_popup(x, y, task)

    def _show_status_popup(self, x, y, task):
        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)
        popup.geometry(f"+{x}+{y}")
        popup.configure(bg="#444444")

        def set_status(s):
            old = task.status
            task.status = s
            upsert_task(task)
            if old != s:
                self._add_notification(task.task_id, task.title,
                                       f"ステータスが「{old}」→「{s}」に変更されました",
                                       task.assignee)
            self.refresh_table()
            if popup.winfo_exists():
                popup.destroy()

        for status, colors in self.STATUS_COLORS_MAP.items():
            tk.Button(
                popup,
                text=f"  {self.STATUS_ICONS.get(status, '')} {status}  ",
                bg=colors["bg"], fg="white",
                activebackground=colors["activebg"], activeforeground="white",
                font=("Arial", 10, "bold"),
                relief="flat", bd=0,
                padx=10, pady=7,
                cursor="hand2",
                command=lambda s=status: set_status(s),
            ).pack(fill=tk.X, padx=2, pady=1)

        popup.bind("<Escape>", lambda _: popup.destroy())
        popup.bind("<FocusOut>", lambda _: popup.destroy() if popup.winfo_exists() else None)
        popup.update_idletasks()
        popup.focus_set()

    def _select_row(self, task_id):
        # 前の選択を解除して背景を戻す
        for tid in list(self._selected_ids):
            if tid in self._row_frames:
                row, base_bg = self._row_frames[tid]
                self._set_row_bg(row, base_bg)
        # 同じ行を再クリックで解除、別行なら選択
        if task_id in self._selected_ids:
            self._selected_ids.clear()
        else:
            self._selected_ids = {task_id}
            if task_id in self._row_frames:
                self._set_row_bg(self._row_frames[task_id][0], "#cce5ff")

    def _set_row_bg(self, widget, bg):
        widget.config(bg=bg)
        for child in widget.winfo_children():
            if not isinstance(child, tk.Button):
                self._set_row_bg(child, bg)

    def _on_mousewheel(self, event):
        self._body_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------ リマインダー

    def _is_overdue(self, task: Task) -> bool:
        if task.status == "完了" or task.due_date == "-":
            return False
        try:
            if " " in task.due_date:
                return datetime.strptime(task.due_date, "%Y-%m-%d %H:%M") < datetime.now()
            return datetime.strptime(task.due_date, "%Y-%m-%d").date() < date.today()
        except Exception:
            return False

    def _schedule_reminder_check(self):
        self._check_reminders()
        self.root.after(self.REMINDER_INTERVAL_MS, self._schedule_reminder_check)

    def _check_reminders(self):
        now = datetime.now()
        triggered = []
        for task in self.tasks:
            if task.status == "完了" or task.reminded or task.due_date == "-" or task.reminder_minutes == 0:
                continue
            try:
                if " " in task.due_date:
                    due_dt = datetime.strptime(task.due_date, "%Y-%m-%d %H:%M")
                else:
                    due_dt = datetime.strptime(task.due_date + " 23:59", "%Y-%m-%d %H:%M")
                delta_min = (due_dt - now).total_seconds() / 60
                if 0 <= delta_min <= task.reminder_minutes:
                    triggered.append(task)
                    task.reminded = True
            except Exception:
                pass
        if triggered:
            for task in triggered:
                upsert_task(task)
            ReminderPopup(self.root, triggered)


# ======================== エントリーポイント ========================

if __name__ == "__main__":
    root = tk.Tk()
    TaskManagerApp(root)
    root.mainloop()
