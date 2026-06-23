"""チェックボックスで一括完了できる GUI ToDo アプリ。"""

from dataclasses import asdict, dataclass
import calendar
from datetime import date
import json
import unicodedata
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


DATA_FILE = Path(__file__).with_name("todo_data.json")


@dataclass
class Task:
	# 画面に表示するタスク名
	title: str
	# 期限日。未設定の場合は "-" を使う
	due_date: str
	# 優先度（高 / 中 / 低）
	priority: str
	# 自由入力メモ
	memo: str
	# 完了済みなら True
	done: bool = False
	# 入力順を保つための番号
	sort_order: int = 0


def load_tasks() -> list[Task]:
	# 初回起動などで保存ファイルがない場合は空で開始する。
	if not DATA_FILE.exists():
		return []

	try:
		# JSON を読み込み、Task のリストへ変換する。
		with DATA_FILE.open("r", encoding="utf-8") as f:
			items = json.load(f)
		if not isinstance(items, list):
			raise TypeError
		tasks: list[Task] = []
		skipped_count = 0
		for idx, item in enumerate(items, start=1):
			try:
				task = Task(**item)
				# 古いデータで sort_order がない/不正でも入力順を復元する。
				if task.sort_order <= 0:
					task.sort_order = idx
				tasks.append(task)
			except (TypeError, ValueError):
				# 1件だけ壊れていても他のタスクは読み込めるようにする。
				skipped_count += 1

		if skipped_count > 0:
			messagebox.showwarning(
				"一部読み込みエラー",
				f"{skipped_count}件のタスクを読み込めませんでした。\n他のタスクは読み込み済みです。",
			)
		return tasks
	except (OSError, json.JSONDecodeError, TypeError, ValueError):
		# ファイル破損などで読めないときは警告し、空リストで続行する。
		messagebox.showwarning("読み込みエラー", "保存データを読み込めませんでした。")
		return []


def save_tasks(tasks: list[Task]) -> bool:
	def safe_text(text: str) -> str:
		# 不正な文字が混ざっても保存処理で落ちないように置き換える。
		return text.encode("utf-8", errors="replace").decode("utf-8")

	items = []
	for task in tasks:
		# dataclass を辞書へ変換して JSON に書き出す。
		item = asdict(task)
		item["title"] = safe_text(task.title)
		item["due_date"] = safe_text(task.due_date)
		item["priority"] = safe_text(task.priority)
		item["memo"] = safe_text(task.memo)
		items.append(item)

	try:
		# ensure_ascii=False により日本語をそのまま保存する。
		with DATA_FILE.open("w", encoding="utf-8") as f:
			json.dump(items, f, ensure_ascii=False, indent=2)
		return True
	except OSError:
		messagebox.showerror("保存エラー", "保存に失敗しました。\nディスク容量や権限を確認してください。")
		return False


class DatePickerDialog:
	"""シンプルなカレンダーダイアログ。日付を選ぶと callback を呼ぶ。"""

	def __init__(self, parent: tk.Widget, on_date_selected) -> None:
		self.on_date_selected = on_date_selected
		today = date.today()
		self.current_year = today.year
		self.current_month = today.month

		self.top = tk.Toplevel(parent)
		self.top.title("期限日を選択")
		self.top.resizable(False, False)
		self.top.transient(parent.winfo_toplevel())
		self.top.grab_set()

		header = ttk.Frame(self.top, padding=8)
		header.pack(fill="x")

		ttk.Button(header, text="<", width=3, command=self.prev_month).pack(side="left")
		self.month_label = ttk.Label(header, text="", anchor="center")
		self.month_label.pack(side="left", expand=True)
		ttk.Button(header, text=">", width=3, command=self.next_month).pack(side="right")

		self.calendar_frame = ttk.Frame(self.top, padding=(8, 0, 8, 8))
		self.calendar_frame.pack()

		self.draw_calendar()

	def prev_month(self) -> None:
		# 1月の前は前年12月に切り替える。
		if self.current_month == 1:
			self.current_month = 12
			self.current_year -= 1
		else:
			self.current_month -= 1
		self.draw_calendar()

	def next_month(self) -> None:
		# 12月の次は翌年1月に切り替える。
		if self.current_month == 12:
			self.current_month = 1
			self.current_year += 1
		else:
			self.current_month += 1
		self.draw_calendar()

	def draw_calendar(self) -> None:
		# 月送り時は一度中身を消してから描き直す。
		for child in self.calendar_frame.winfo_children():
			child.destroy()

		self.month_label.config(text=f"{self.current_year}年 {self.current_month}月")

		weekdays = ["月", "火", "水", "木", "金", "土", "日"]
		for col, weekday in enumerate(weekdays):
			ttk.Label(self.calendar_frame, text=weekday, width=4, anchor="center").grid(
				row=0,
				column=col,
				padx=1,
				pady=1,
			)

		month_matrix = calendar.monthcalendar(self.current_year, self.current_month)
		for row_idx, week in enumerate(month_matrix, start=1):
			for col_idx, day in enumerate(week):
				# calendar.monthcalendar は月外の日を 0 で返す。
				if day == 0:
					ttk.Label(self.calendar_frame, text="", width=4).grid(row=row_idx, column=col_idx)
					continue

				btn = ttk.Button(
					self.calendar_frame,
					text=str(day),
					width=4,
					command=lambda d=day: self.select_day(d),
				)
				btn.grid(row=row_idx, column=col_idx, padx=1, pady=1)

	def select_day(self, day: int) -> None:
		# アプリ本体側が扱いやすい YYYY-MM-DD 形式で返す。
		selected = f"{self.current_year:04d}-{self.current_month:02d}-{day:02d}"
		self.on_date_selected(selected)
		self.top.destroy()


class TodoApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("ToDoアプリ")
		self.root.geometry("920x680")
		self.root.minsize(860, 620)

		self.tasks = load_tasks()
		# 画面で選択状態を持つためのチェック管理リスト
		self.overdue_checks: list[tuple[int, tk.BooleanVar]] = []
		self.todo_checks: list[tuple[int, tk.BooleanVar]] = []
		self.done_checks: list[tuple[int, tk.BooleanVar]] = []
		# 編集中タスクのインデックス。未編集時は None。
		self.editing_index: int | None = None
		# 並び替えモード（入力順 / 日付順 / 優先度順）
		self.sort_mode = tk.StringVar(value="入力順")

		# モノスペースフォントをチェックボタン用スタイルに登録
		style = ttk.Style()
		style.configure("Mono.TCheckbutton", font=("MS Gothic", 10))
		# 期限切れタスク用のスタイル（赤文字）
		style.configure("Overdue.TCheckbutton", font=("MS Gothic", 10), foreground="red")

		self._build_ui()
		self.refresh_task_view()

	def _build_scrollable_section(
		self,
		parent: tk.Widget,
		title: str,
		pady: tuple[int, int] = (0, 0),
		height: int | None = None,
		top_widget_builder=None,
	) -> tuple[ttk.LabelFrame, tk.Canvas, ttk.Frame]:
		frame = ttk.LabelFrame(parent, text=title, padding=0)
		frame.pack(fill="both", expand=True, pady=pady)

		if top_widget_builder is not None:
			top_bar = ttk.Frame(frame, padding=(10, 8, 10, 0))
			top_bar.pack(fill="x")
			top_widget_builder(top_bar)

		canvas = tk.Canvas(frame, highlightthickness=0, borderwidth=0)
		if height is not None:
			canvas.configure(height=height)
			canvas.pack(side="left", fill="both", expand=True)
		else:
			canvas.pack(side="left", fill="both", expand=True)
		
		scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
		content = ttk.Frame(canvas, padding=10)
		content_window = canvas.create_window((0, 0), window=content, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)
		scrollbar.pack(side="right", fill="y")

		# 中身のサイズ変化に合わせてスクロール範囲と表示幅を更新する。
		content.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
		canvas.bind("<Configure>", lambda e: canvas.itemconfigure(content_window, width=e.width))

		return frame, canvas, content

	def _build_ui(self) -> None:
		# 上部フォーム: タイトル・期限日・優先度・メモを入力する。
		form = ttk.LabelFrame(self.root, text="タスク入力", padding=10)
		form.pack(fill="x", padx=10, pady=10)

		title_area = ttk.Frame(form)
		title_area.grid(row=0, column=0, columnspan=2, sticky="w")

		ttk.Label(title_area, text="タイトル").pack(side="left")
		self.title_entry = ttk.Entry(title_area, width=30)
		self.title_entry.pack(side="left")

		date_area = ttk.Frame(form)
		date_area.grid(row=0, column=2, columnspan=2, sticky="w")

		ttk.Label(date_area, text="期限日").pack(side="left")
		self.due_var = tk.StringVar(value="")
		self.due_entry = ttk.Entry(date_area, width=14, textvariable=self.due_var, state="readonly")
		self.due_entry.pack(side="left")
		ttk.Button(date_area, text="日付を選択", command=self.open_date_picker).pack(side="left")
		ttk.Button(date_area, text="クリア", command=self.clear_due_date).pack(side="left", padx=(4, 0))

		priority_area = ttk.Frame(form)
		priority_area.grid(row=0, column=4, columnspan=2, sticky="w", padx=(16, 0))

		ttk.Label(priority_area, text="優先度").pack(side="left")
		self.priority_box = ttk.Combobox(
			priority_area,
			values=["高", "中", "低"],
			width=6,
			state="readonly",
		)
		self.priority_box.pack(side="left")
		self.priority_box.set("中")

		memo_area = ttk.Frame(form)
		memo_area.grid(row=1, column=0, columnspan=7, sticky="w", pady=(10, 0))

		ttk.Label(memo_area, text="メモ").pack(side="left")
		self.memo_entry = ttk.Entry(memo_area, width=70)
		self.memo_entry.pack(side="left", padx=(16, 0))

		buttons = ttk.Frame(form)
		buttons.grid(row=2, column=0, columnspan=7, sticky="w", pady=(12, 0))

		self.submit_button = ttk.Button(buttons, text="タスク追加", command=self.add_or_update_task)
		self.submit_button.pack(side="left")
		ttk.Button(buttons, text="選択を編集", command=self.edit_selected_task).pack(side="left", padx=8)
		ttk.Button(buttons, text="選択を一括完了", command=self.complete_selected).pack(side="left", padx=8)
		ttk.Button(buttons, text="選択を削除", command=self.delete_selected).pack(side="left", padx=8)
		ttk.Label(buttons, text="並び替え").pack(side="left", padx=(8, 2))
		self.sort_box = ttk.Combobox(
			buttons,
			textvariable=self.sort_mode,
			values=["入力順", "日付順", "優先度順"],
			width=10,
			state="readonly",
		)
		self.sort_box.pack(side="left", padx=(0, 8))
		self.sort_box.bind("<<ComboboxSelected>>", self.on_sort_changed)
		ttk.Button(buttons, text="全選択", command=self.select_all).pack(side="left", padx=8)
		ttk.Button(buttons, text="選択解除", command=self.clear_selection).pack(side="left", padx=8)
		self.cancel_edit_button = ttk.Button(buttons, text="編集解除", command=self.cancel_edit, state="disabled")
		self.cancel_edit_button.pack(side="left", padx=8)

		# 下部エリア: 期限切れ、未完了、完了の3つの一覧を表示する。
		main = ttk.Frame(self.root)
		main.pack(fill="both", expand=True, padx=10, pady=(0, 10))

		self.overdue_frame, self.overdue_canvas, self.overdue_content = self._build_scrollable_section(
			main,
			"期限切れ（チェックで完了）",
			height=90,
		)
		self.todo_frame, self.todo_canvas, self.todo_content = self._build_scrollable_section(
			main,
			"未完了（チェックで一括完了）",
			pady=(8, 0),
		)
		def build_done_top_buttons(parent: ttk.Frame) -> None:
			ttk.Button(
				parent,
				text="未完了に戻す",
				command=self.restore_selected_done,
			).pack(side="left")
			ttk.Button(
				parent,
				text="完了選択を削除",
				command=self.delete_selected_done,
			).pack(side="left", padx=8)

		self.done_frame, self.done_canvas, self.done_content = self._build_scrollable_section(
			main,
			"完了",
			pady=(8, 0),
			top_widget_builder=build_done_top_buttons,
		)

	def refresh_task_view(self) -> None:
		# 画面再描画の前に一覧を空にする。
		for child in self.overdue_content.winfo_children():
			child.destroy()
		for child in self.todo_content.winfo_children():
			child.destroy()
		for child in self.done_content.winfo_children():
			child.destroy()

		self.overdue_checks = []
		self.todo_checks = []
		self.done_checks = []
		overdue_count = 0
		todo_count = 0
		done_count = 0
		overdue_indexes, todo_indexes, done_indexes = self._sorted_task_indexes()

		# 期限切れタスクを表示
		for row_no, idx in enumerate(overdue_indexes, start=1):
			task = self.tasks[idx]
			line = self._task_line(row_no, task)
			# チェック状態は BooleanVar で保持する。
			var = tk.BooleanVar(value=False)
			# 期限切れも未完了/完了と同じ表示項目（タイトル・期限・優先度・メモ）にそろえる。
			chk = ttk.Checkbutton(
				self.overdue_content,
				text=line,
				variable=var,
				style="Overdue.TCheckbutton",
			)
			chk.pack(fill="x", pady=2)
			self.overdue_checks.append((idx, var))
			overdue_count += 1

		# 未完了タスクを表示
		for row_no, idx in enumerate(todo_indexes, start=1):
			task = self.tasks[idx]
			line = self._task_line(row_no, task)
			# チェック状態は BooleanVar で保持する。
			var = tk.BooleanVar(value=False)
			chk = ttk.Checkbutton(self.todo_content, text=line, variable=var, style="Mono.TCheckbutton")
			chk.pack(fill="x", pady=2)
			self.todo_checks.append((idx, var))
			todo_count += 1

		# 完了タスクを表示
		for row_no, idx in enumerate(done_indexes, start=1):
			task = self.tasks[idx]
			line = self._task_line(row_no, task)
			var = tk.BooleanVar(value=False)
			chk = ttk.Checkbutton(self.done_content, text=line, variable=var, style="Mono.TCheckbutton")
			chk.pack(fill="x", pady=2)
			self.done_checks.append((idx, var))
			done_count += 1

		# 各グループが空の場合は空状態メッセージを表示
		if overdue_count == 0:
			ttk.Label(self.overdue_content, text="期限切れタスクはありません", foreground="gray").pack(anchor="w")
		if todo_count == 0:
			# 件数0のときは空状態メッセージを表示する。
			ttk.Label(self.todo_content, text="未完了タスクはありません", foreground="gray").pack(anchor="w")
		if done_count == 0:
			ttk.Label(self.done_content, text="完了タスクはありません", foreground="gray").pack(anchor="w")

		self.overdue_canvas.yview_moveto(0)
		self.todo_canvas.yview_moveto(0)
		self.done_canvas.yview_moveto(0)

		if self.editing_index is not None and self.editing_index >= len(self.tasks):
			self.cancel_edit()

	@staticmethod
	def _pad_title(title: str, max_chars: int = 15) -> str:
		"""タイトルを max_chars 文字に切り詰め、全角換算で幅を揃えてパディングする。"""
		if len(title) > max_chars:
			title = title[: max_chars - 1] + "…"
		# 全角=2, 半角=1 で表示幅を計算
		def _display_width(s: str) -> int:
			return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)
		target = max_chars * 2  # 全角 max_chars 文字分の幅
		padding = target - _display_width(title)
		return title + " " * max(padding, 0)

	def _task_line(self, row_no: int, task: Task) -> str:
		padded = self._pad_title(task.title)
		return f"{row_no:2}. {padded} | 期限: {task.due_date} | 優先度: {task.priority} | メモ: {task.memo}"

	def open_date_picker(self) -> None:
		DatePickerDialog(self.root, self.set_due_date)

	def set_due_date(self, value: str) -> None:
		self.due_var.set(value)

	def clear_due_date(self) -> None:
		# 期限日を未設定（"-"）として扱うため、入力欄を空に戻す。
		self.due_var.set("")

	def add_task(self) -> None:
		self.add_or_update_task()

	def add_or_update_task(self) -> None:
		# 入力欄の値を取り出し、余分な空白を削る。
		title = self.title_entry.get().strip()
		raw_due = self.due_var.get().strip()
		due = raw_due or "-"
		priority = self.priority_box.get().strip() or "中"
		memo = self.memo_entry.get().strip()

		if not title:
			messagebox.showwarning("入力エラー", "タイトルは必須です。")
			return

		# 期限日が指定されており、かつ過去の日付でないかチェック。
		if due != "-":
			try:
				# YYYY-MM-DD 形式の文字列を date オブジェクトに変換。
				due_date = date.fromisoformat(due)
				today = date.today()
				# 期限日が今日より前（過去）の場合はエラーにする。
				if due_date < today:
					messagebox.showerror(
						"期限日エラー",
						f"期限日は今日以降の日付を指定してください。\n（選択日付: {due}, 今日: {today}）",
					)
					return
			except ValueError:
				# 日付の形式が不正な場合もエラーにする。
				messagebox.showerror("期限日エラー", "期限日の形式が不正です。")
				return

		# editing_index が None なら新規追加、そうでなければ更新。
		if self.editing_index is None:
			self.tasks.append(
				Task(
					title=title,
					due_date=due,
					priority=priority,
					memo=memo,
					done=False,
					sort_order=self._next_sort_order(),
				)
			)
			message = "タスクを追加しました。"
		else:
			# 完了状態と入力順番号は維持し、内容だけ上書きする。
			self.tasks[self.editing_index] = Task(
				title=title,
				due_date=due,
				priority=priority,
				memo=memo,
				done=self.tasks[self.editing_index].done,
				sort_order=self.tasks[self.editing_index].sort_order,
			)
			message = "タスクを更新しました。"

		# 保存 -> 編集状態解除 -> 再描画 の順で画面を最新化する。
		if not save_tasks(self.tasks):
			self.refresh_task_view()
			return
		self.cancel_edit(clear_inputs=False)
		self.refresh_task_view()
		messagebox.showinfo("保存", message)

		self.title_entry.delete(0, tk.END)
		self.due_var.set("")
		self.memo_entry.delete(0, tk.END)
		self.priority_box.set("中")

	def edit_selected_task(self) -> None:
		# 編集は "1件だけ選択" を必須にする。
		selected_indexes = [idx for idx, var in self.overdue_checks if var.get()] + [idx for idx, var in self.todo_checks if var.get()]
		if len(selected_indexes) != 1:
			messagebox.showinfo("確認", "編集するタスクを1件だけチェックしてください。")
			return

		index = selected_indexes[0]
		task = self.tasks[index]

		# フォームに既存値を読み込み、更新モードへ切り替える。
		self.editing_index = index
		self.submit_button.config(text="更新")
		self.cancel_edit_button.config(state="normal")

		self.title_entry.delete(0, tk.END)
		self.title_entry.insert(0, task.title)
		self.due_var.set("")
		if task.due_date != "-":
			self.due_var.set(task.due_date)
		self.priority_box.set(task.priority)
		self.memo_entry.delete(0, tk.END)
		self.memo_entry.insert(0, task.memo)
		self.title_entry.focus_set()

	def cancel_edit(self, clear_inputs: bool = True) -> None:
		# 画面のモードを通常の "追加" 状態に戻す。
		self.editing_index = None
		self.submit_button.config(text="タスク追加")
		self.cancel_edit_button.config(state="disabled")

		if clear_inputs:
			self.title_entry.delete(0, tk.END)
			self.due_var.set("")
			self.memo_entry.delete(0, tk.END)
			self.priority_box.set("中")

	def complete_selected(self) -> None:
		# 期限切れ、未完了一覧でチェックされたものを完了済みに変更する。
		selected_indexes = [idx for idx, var in self.overdue_checks if var.get()] + [idx for idx, var in self.todo_checks if var.get()]
		if not selected_indexes:
			messagebox.showinfo("確認", "完了にするタスクをチェックしてください。")
			return

		for idx in selected_indexes:
			self.tasks[idx].done = True

		if not save_tasks(self.tasks):
			self.refresh_task_view()
			return
		self.cancel_edit()
		self.refresh_task_view()
		messagebox.showinfo("完了", f"{len(selected_indexes)}件のタスクを完了にしました。")

	def delete_selected(self) -> None:
		# 後ろから削除し、インデックスずれを防ぐ。
		selected_indexes = [idx for idx, var in self.overdue_checks if var.get()] + [idx for idx, var in self.todo_checks if var.get()]
		if not selected_indexes:
			messagebox.showinfo("確認", "削除するタスクをチェックしてください。")
			return

		for idx in sorted(selected_indexes, reverse=True):
			del self.tasks[idx]

		if not save_tasks(self.tasks):
			self.refresh_task_view()
			return
		self.cancel_edit()
		self.refresh_task_view()

	def select_all(self) -> None:
		for _, var in self.overdue_checks:
			var.set(True)
		for _, var in self.todo_checks:
			var.set(True)

	def clear_selection(self) -> None:
		for _, var in self.overdue_checks:
			var.set(False)
		for _, var in self.todo_checks:
			var.set(False)
		for _, var in self.done_checks:
			var.set(False)

	def restore_selected_done(self) -> None:
		# 完了一覧で選んだものを未完了へ戻す。
		selected_indexes = [idx for idx, var in self.done_checks if var.get()]
		if not selected_indexes:
			messagebox.showinfo("確認", "未完了に戻すタスクをチェックしてください。")
			return

		for idx in selected_indexes:
			self.tasks[idx].done = False

		if not save_tasks(self.tasks):
			self.refresh_task_view()
			return
		self.cancel_edit()
		self.refresh_task_view()
		messagebox.showinfo("戻す", f"{len(selected_indexes)}件のタスクを未完了に戻しました。")

	def delete_selected_done(self) -> None:
		selected_indexes = [idx for idx, var in self.done_checks if var.get()]
		if not selected_indexes:
			messagebox.showinfo("確認", "削除する完了タスクをチェックしてください。")
			return

		for idx in sorted(selected_indexes, reverse=True):
			del self.tasks[idx]

		if not save_tasks(self.tasks):
			self.refresh_task_view()
			return
		self.cancel_edit()
		self.refresh_task_view()

	@staticmethod
	def _input_sort_key(task: Task) -> tuple[int, str]:
		# 入力順を優先し、同順ならタイトルで安定化する。
		return (task.sort_order, task.title)

	@staticmethod
	def _due_sort_key(task: Task) -> tuple[int, str, int, str]:
		due = task.due_date.strip()
		# YYYY-MM-DD 形式のみ日付として扱い、それ以外は末尾に回す。
		if len(due) == 10 and due[4] == "-" and due[7] == "-":
			y, m, d = due.split("-")
			if y.isdigit() and m.isdigit() and d.isdigit():
				return (0, due, task.sort_order, task.title)
		return (1, "9999-99-99", task.sort_order, task.title)

	@staticmethod
	def _priority_sort_key(task: Task) -> tuple[int, tuple[int, str, int, str], int, str]:
		# 優先度が高い順（高 -> 中 -> 低）で並べる。
		priority_order = {"高": 0, "中": 1, "低": 2}
		rank = priority_order.get(task.priority, 9)
		return (rank, TodoApp._due_sort_key(task), task.sort_order, task.title)

	def _next_sort_order(self) -> int:
		# 新しいタスクには既存の最大値 + 1 を採番する。
		if not self.tasks:
			return 1
		return max(task.sort_order for task in self.tasks) + 1

	def _current_sort_key(self):
		mode = self.sort_mode.get()
		if mode == "日付順":
			return self._due_sort_key
		if mode == "優先度順":
			return self._priority_sort_key
		return self._input_sort_key

	def _sorted_task_indexes(self) -> tuple[list[int], list[int], list[int]]:
		sort_key = self._current_sort_key()
		today = date.today()
		
		# 期限切れ: 未完了で、期限が設定されており、かつ今日より前のタスク
		overdue_indexes = []
		todo_indexes = []
		done_indexes = [idx for idx, task in enumerate(self.tasks) if task.done]
		
		for idx, task in enumerate(self.tasks):
			if task.done:
				continue
			
			# 期限が設定されており、過去の日付なら期限切れ
			if task.due_date != "-":
				try:
					due_date = date.fromisoformat(task.due_date)
					if due_date < today:
						overdue_indexes.append(idx)
						continue
				except ValueError:
					pass
			
			todo_indexes.append(idx)
		
		overdue_indexes.sort(key=lambda idx: sort_key(self.tasks[idx]))
		todo_indexes.sort(key=lambda idx: sort_key(self.tasks[idx]))
		done_indexes.sort(key=lambda idx: sort_key(self.tasks[idx]))
		return overdue_indexes, todo_indexes, done_indexes

	def on_sort_changed(self, _event=None) -> None:
		self.cancel_edit()
		self.refresh_task_view()


def main() -> None:
	root = tk.Tk()
	TodoApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
