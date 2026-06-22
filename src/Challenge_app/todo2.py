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
# タスク一覧を保存する JSON ファイル。プログラムと同じ場所に作られる。


@dataclass
class Task:
	# 1件分のタスク情報をまとめるデータ。
	title: str
	due_date: str
	priority: str
	memo: str
	done: bool = False
	sort_order: int = 0


def load_tasks() -> list[Task]:
	# 起動時に JSON ファイルからタスクを読み込む。
	if not DATA_FILE.exists():
		return []

	try:
		with DATA_FILE.open("r", encoding="utf-8") as f:
			items = json.load(f)
		tasks: list[Task] = []
		for idx, item in enumerate(items, start=1):
			# JSON の辞書データを Task オブジェクトに変換する。
			task = Task(**item)
			if task.sort_order <= 0:
				task.sort_order = idx
			tasks.append(task)
		return tasks
	except (OSError, json.JSONDecodeError, TypeError, ValueError):
		messagebox.showwarning("読み込みエラー", "保存データを読み込めませんでした。")
		return []


def save_tasks(tasks: list[Task]) -> None:
	# 現在のタスク一覧を JSON ファイルへ保存する。
	def safe_text(text: str) -> str:
		# 文字化けしそうな文字があっても保存処理が止まらないようにする。
		return text.encode("utf-8", errors="replace").decode("utf-8")

	items = []
	for task in tasks:
		item = asdict(task)
		item["title"] = safe_text(task.title)
		item["due_date"] = safe_text(task.due_date)
		item["priority"] = safe_text(task.priority)
		item["memo"] = safe_text(task.memo)
		items.append(item)

	with DATA_FILE.open("w", encoding="utf-8") as f:
		json.dump(items, f, ensure_ascii=False, indent=2)


class DatePickerDialog:
	"""シンプルなカレンダーダイアログ。日付を選ぶと callback を呼ぶ。"""

	def __init__(self, parent: tk.Widget, on_date_selected) -> None:
		# 呼び出し元へ選択日付を返すための関数を保持。
		self.on_date_selected = on_date_selected
		# 最初は「今月」を表示する。
		today = date.today()
		self.current_year = today.year
		self.current_month = today.month

		# 親ウィンドウの上に小さな子ウィンドウとして表示する。
		self.top = tk.Toplevel(parent)
		self.top.title("期限日を選択")
		self.top.resizable(False, False)
		# transient + grab_set で「このダイアログを閉じるまで親を操作しない」状態にする。
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
		# 1か月前へ移動。1月の場合は前年12月へ戻す。
		if self.current_month == 1:
			self.current_month = 12
			self.current_year -= 1
		else:
			self.current_month -= 1
		# 月が変わったのでカレンダーを描き直す。
		self.draw_calendar()

	def next_month(self) -> None:
		# 1か月先へ移動。12月の場合は翌年1月へ進める。
		if self.current_month == 12:
			self.current_month = 1
			self.current_year += 1
		else:
			self.current_month += 1
		# 月が変わったのでカレンダーを描き直す。
		self.draw_calendar()

	def draw_calendar(self) -> None:
		# まず前回の表示を全消去してから再構築する。
		for child in self.calendar_frame.winfo_children():
			child.destroy()

		self.month_label.config(text=f"{self.current_year}年 {self.current_month}月")

		weekdays = ["月", "火", "水", "木", "金", "土", "日"]
		# 曜日ヘッダーを1行目に表示する。
		for col, weekday in enumerate(weekdays):
			ttk.Label(self.calendar_frame, text=weekday, width=4, anchor="center").grid(
				row=0,
				column=col,
				padx=1,
				pady=1,
			)

		month_matrix = calendar.monthcalendar(self.current_year, self.current_month)
		# monthcalendar は「週ごとの日付配列」を返す。0 はその月に存在しない日。
		for row_idx, week in enumerate(month_matrix, start=1):
			for col_idx, day in enumerate(week):
				if day == 0:
					# 空欄セル（前月/翌月のはみ出し部分）。
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
		# yyyy-mm-dd 形式に整形して呼び出し元へ返す。
		selected = f"{self.current_year:04d}-{self.current_month:02d}-{day:02d}"
		self.on_date_selected(selected)
		# 選択後はダイアログを閉じる。
		self.top.destroy()


class TodoApp:
	def __init__(self, root: tk.Tk) -> None:
		# アプリの基本設定（タイトル、初期サイズ、最小サイズ）。
		self.root = root
		self.root.title("ToDoアプリ")
		self.root.geometry("1100x680")
		self.root.minsize(980, 620)

		# 保存ファイルからタスクを読み込む。
		self.tasks = load_tasks()
		# チェック状態を管理する配列（未完了側/完了側）。
		self.todo_checks: list[tuple[int, tk.BooleanVar]] = []
		self.done_checks: list[tuple[int, tk.BooleanVar]] = []
		# None なら通常モード、数値ならその index を編集中。
		self.editing_index: int | None = None
		# 並び替えの現在値を保持する。
		self.sort_mode = tk.StringVar(value="入力順")

		# モノスペースフォントをチェックボタン用スタイルに登録
		style = ttk.Style()
		style.configure("Mono.TCheckbutton", font=("MS Gothic", 10))

		self._build_ui()
		# 起動時点で一覧を1回描画する。
		self.refresh_task_view()

	def _build_scrollable_section(
		self,
		parent: tk.Widget,
		title: str,
		pady: tuple[int, int] = (0, 0),
	) -> tuple[ttk.LabelFrame, tk.Canvas, ttk.Frame]:
		# 「枠 + キャンバス + スクロールバー + 実コンテンツ」のセットを作る。
		frame = ttk.LabelFrame(parent, text=title, padding=0)
		frame.pack(fill="both", expand=True, pady=pady)

		canvas = tk.Canvas(frame, highlightthickness=0, borderwidth=0)
		scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
		content = ttk.Frame(canvas, padding=10)

		content_window = canvas.create_window((0, 0), window=content, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		# 中身のサイズ変化に合わせてスクロール範囲と表示幅を更新する。
		content.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
		canvas.bind("<Configure>", lambda e: canvas.itemconfigure(content_window, width=e.width))

		return frame, canvas, content

	def _build_ui(self) -> None:
		# 画面上部: タスク入力フォーム。
		form = ttk.LabelFrame(self.root, text="タスク入力", padding=10)
		form.pack(fill="x", padx=10, pady=10)

		ttk.Label(form, text="タイトル").grid(row=0, column=0, sticky="w")
		self.title_entry = ttk.Entry(form, width=30)
		self.title_entry.grid(row=0, column=1, sticky="w", padx=6)

		ttk.Label(form, text="期限日").grid(row=0, column=2, sticky="w", padx=(12, 0))
		self.due_var = tk.StringVar(value="")
		self.due_entry = ttk.Entry(form, width=16, textvariable=self.due_var, state="readonly")
		self.due_entry.grid(row=0, column=3, sticky="w", padx=6)
		ttk.Button(form, text="日付を選択", command=self.open_date_picker).grid(row=0, column=4, sticky="w", padx=(0, 6))

		ttk.Label(form, text="優先度").grid(row=0, column=5, sticky="w", padx=(12, 0))
		self.priority_box = ttk.Combobox(
			form,
			values=["高", "中", "低"],
			width=6,
			state="readonly",
		)
		self.priority_box.grid(row=0, column=6, sticky="w", padx=6)
		self.priority_box.set("中")

		ttk.Label(form, text="メモ").grid(row=1, column=0, sticky="w", pady=(10, 0))
		self.memo_entry = ttk.Entry(form, width=70)
		self.memo_entry.grid(row=1, column=1, columnspan=6, sticky="we", padx=6, pady=(10, 0))

		buttons = ttk.Frame(form)
		buttons.grid(row=2, column=0, columnspan=7, sticky="w", pady=(12, 0))

		# ここで各ボタンと処理関数を紐づける。
		self.submit_button = ttk.Button(buttons, text="タスク追加", command=self.add_or_update_task)
		self.submit_button.pack(side="left")
		ttk.Button(buttons, text="選択を編集", command=self.edit_selected_task).pack(side="left", padx=8)
		ttk.Button(buttons, text="選択を一括完了", command=self.complete_selected).pack(side="left", padx=8)
		ttk.Button(buttons, text="選択を削除", command=self.delete_selected).pack(side="left", padx=8)
		ttk.Button(buttons, text="完了選択を削除", command=self.delete_selected_done).pack(side="left", padx=8)
		ttk.Button(buttons, text="未完了に戻す", command=self.restore_selected_done).pack(side="left", padx=8)
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

		main = ttk.Frame(self.root)
		main.pack(fill="both", expand=True, padx=10, pady=(0, 10))

		# 画面下部: 未完了リストと完了リスト。
		self.todo_frame, self.todo_canvas, self.todo_content = self._build_scrollable_section(
			main,
			"未完了（チェックで一括完了）",
		)
		self.done_frame, self.done_canvas, self.done_content = self._build_scrollable_section(
			main,
			"完了",
			pady=(8, 0),
		)

	def refresh_task_view(self) -> None:
		# 画面のタスク表示を作り直す（追加・更新・削除のたびに呼ぶ）。
		# 先に既存ウィジェットを消して、重複表示を防ぐ。
		for child in self.todo_content.winfo_children():
			child.destroy()
		for child in self.done_content.winfo_children():
			child.destroy()

		self.todo_checks = []
		self.done_checks = []
		todo_count = 0
		done_count = 0

		# 表示順に応じた index 一覧（未完了/完了）を取得する。
		todo_indexes, done_indexes = self._sorted_task_indexes()

		# 未完了タスクをチェックボックスで並べる。
		for row_no, idx in enumerate(todo_indexes, start=1):
			task = self.tasks[idx]
			line = self._task_line(row_no, task)
			var = tk.BooleanVar(value=False)
			chk = ttk.Checkbutton(self.todo_content, text=line, variable=var, style="Mono.TCheckbutton")
			chk.pack(fill="x", pady=2)
			self.todo_checks.append((idx, var))
			todo_count += 1

		# 完了済みタスクを別枠で並べる。
		for row_no, idx in enumerate(done_indexes, start=1):
			task = self.tasks[idx]
			line = self._task_line(row_no, task)
			var = tk.BooleanVar(value=False)
			chk = ttk.Checkbutton(self.done_content, text=line, variable=var, style="Mono.TCheckbutton")
			chk.pack(fill="x", pady=2)
			self.done_checks.append((idx, var))
			done_count += 1

		if todo_count == 0:
			# リストが空のときはガイド文を表示する。
			ttk.Label(self.todo_content, text="未完了タスクはありません", foreground="gray").pack(anchor="w")
		if done_count == 0:
			ttk.Label(self.done_content, text="完了タスクはありません", foreground="gray").pack(anchor="w")

		# 再描画後はスクロール位置を先頭に戻す。
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
		# 1行表示用の文字列を作る。
		padded = self._pad_title(task.title)
		return f"{row_no:2}. {padded} | 期限: {task.due_date} | 優先度: {task.priority} | メモ: {task.memo}"

	def open_date_picker(self) -> None:
		# 日付選択ダイアログを開く（選択結果は set_due_date へ渡される）。
		DatePickerDialog(self.root, self.set_due_date)

	def set_due_date(self, value: str) -> None:
		# ダイアログで選んだ日付を入力欄へ反映する。
		self.due_var.set(value)

	def add_task(self) -> None:
		# 互換用メソッド（内部的には add_or_update_task を使う）。
		self.add_or_update_task()

	def add_or_update_task(self) -> None:
		# 入力欄から値を取り出す。
		title = self.title_entry.get().strip()
		due = self.due_var.get().strip() or "-"
		priority = self.priority_box.get().strip() or "中"
		memo = self.memo_entry.get().strip()

		if not title:
			# 最低限タイトルだけは必須入力にする。
			messagebox.showwarning("入力エラー", "タイトルは必須です。")
			return

		if self.editing_index is None:
			# 編集中でなければ新規追加。
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
			# 編集中なら同じ位置のタスクを更新。
			self.tasks[self.editing_index] = Task(
				title=title,
				due_date=due,
				priority=priority,
				memo=memo,
				done=self.tasks[self.editing_index].done,
				sort_order=self.tasks[self.editing_index].sort_order,
			)
			message = "タスクを更新しました。"

		save_tasks(self.tasks)
		# 入力状態と一覧表示を最新状態にする。
		self.cancel_edit(clear_inputs=False)
		self.refresh_task_view()
		messagebox.showinfo("保存", message)

		# 保存後は入力欄をクリアして次の入力に備える。
		self.title_entry.delete(0, tk.END)
		self.due_var.set("")
		self.memo_entry.delete(0, tk.END)
		self.priority_box.set("中")

	def edit_selected_task(self) -> None:
		# 未完了側でチェックされた項目を集める。
		selected_indexes = [idx for idx, var in self.todo_checks if var.get()]
		if len(selected_indexes) != 1:
			# 編集は1件だけ選んだときに許可する。
			messagebox.showinfo("確認", "編集するタスクを1件だけチェックしてください。")
			return

		index = selected_indexes[0]
		task = self.tasks[index]

		self.editing_index = index
		# ボタン表示を「追加」から「更新」に切り替える。
		self.submit_button.config(text="更新")
		self.cancel_edit_button.config(state="normal")

		self.title_entry.delete(0, tk.END)
		self.title_entry.insert(0, task.title)
		self.due_var.set("")
		# 期限未設定("-")の場合は入力欄を空のままにする。
		if task.due_date != "-":
			self.due_var.set(task.due_date)
		self.priority_box.set(task.priority)
		self.memo_entry.delete(0, tk.END)
		self.memo_entry.insert(0, task.memo)
		self.title_entry.focus_set()

	def cancel_edit(self, clear_inputs: bool = True) -> None:
		# 編集モードを終了して通常の「追加モード」に戻す。
		self.editing_index = None
		self.submit_button.config(text="タスク追加")
		self.cancel_edit_button.config(state="disabled")

		if clear_inputs:
			self.title_entry.delete(0, tk.END)
			self.due_var.set("")
			self.memo_entry.delete(0, tk.END)
			self.priority_box.set("中")

	def complete_selected(self) -> None:
		# 未完了側でチェックされたものを完了状態にする。
		selected_indexes = [idx for idx, var in self.todo_checks if var.get()]
		if not selected_indexes:
			messagebox.showinfo("確認", "完了にするタスクをチェックしてください。")
			return

		# 選択されたタスクの done フラグを True に変更。
		for idx in selected_indexes:
			self.tasks[idx].done = True

		save_tasks(self.tasks)
		self.cancel_edit()
		self.refresh_task_view()
		messagebox.showinfo("完了", f"{len(selected_indexes)}件のタスクを完了にしました。")

	def delete_selected(self) -> None:
		# 未完了側でチェックされた項目を削除する。
		selected_indexes = [idx for idx, var in self.todo_checks if var.get()]
		if not selected_indexes:
			messagebox.showinfo("確認", "削除するタスクをチェックしてください。")
			return

		# 後ろから消すことで index ずれを防ぐ。
		for idx in sorted(selected_indexes, reverse=True):
			del self.tasks[idx]

		save_tasks(self.tasks)
		self.cancel_edit()
		self.refresh_task_view()

	def select_all(self) -> None:
		# 未完了リストだけを一括選択する。
		for _, var in self.todo_checks:
			var.set(True)

	def clear_selection(self) -> None:
		# 未完了・完了の両方の選択を外す。
		for _, var in self.todo_checks:
			var.set(False)
		for _, var in self.done_checks:
			var.set(False)

	def restore_selected_done(self) -> None:
		# 完了側で選んだ項目を未完了へ戻す。
		selected_indexes = [idx for idx, var in self.done_checks if var.get()]
		if not selected_indexes:
			messagebox.showinfo("確認", "未完了に戻す完了タスクをチェックしてください。")
			return

		# done=False にすることで未完了リストへ移動する。
		for idx in selected_indexes:
			self.tasks[idx].done = False

		save_tasks(self.tasks)
		self.cancel_edit()
		self.refresh_task_view()
		messagebox.showinfo("戻す", f"{len(selected_indexes)}件のタスクを未完了に戻しました。")

	def delete_selected_done(self) -> None:
		# 完了側でチェックされた項目を削除する。
		selected_indexes = [idx for idx, var in self.done_checks if var.get()]
		if not selected_indexes:
			messagebox.showinfo("確認", "削除する完了タスクをチェックしてください。")
			return

		# 後ろから消すことで index ずれを防ぐ。
		for idx in sorted(selected_indexes, reverse=True):
			del self.tasks[idx]

		save_tasks(self.tasks)
		self.cancel_edit()
		self.refresh_task_view()

	@staticmethod
	def _input_sort_key(task: Task) -> tuple[int, str]:
		# 入力順で並べるためのキー。
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
		# 優先度(高→中→低)で並べ、同じ優先度なら期限日などで並べる。
		priority_order = {"高": 0, "中": 1, "低": 2}
		rank = priority_order.get(task.priority, 9)
		return (rank, TodoApp._due_sort_key(task), task.sort_order, task.title)

	def _next_sort_order(self) -> int:
		# 新規タスクに割り当てる連番を返す。
		if not self.tasks:
			return 1
		return max(task.sort_order for task in self.tasks) + 1

	def _current_sort_key(self):
		# コンボボックスの選択に応じて並び替え関数を返す。
		mode = self.sort_mode.get()
		if mode == "日付順":
			return self._due_sort_key
		if mode == "優先度順":
			return self._priority_sort_key
		return self._input_sort_key

	def _sorted_task_indexes(self) -> tuple[list[int], list[int]]:
		# 実データ self.tasks は並べ替えず、表示用の index だけソートする。
		sort_key = self._current_sort_key()
		todo_indexes = [idx for idx, task in enumerate(self.tasks) if not task.done]
		done_indexes = [idx for idx, task in enumerate(self.tasks) if task.done]
		todo_indexes.sort(key=lambda idx: sort_key(self.tasks[idx]))
		done_indexes.sort(key=lambda idx: sort_key(self.tasks[idx]))
		return todo_indexes, done_indexes

	def on_sort_changed(self, _event=None) -> None:
		# 並び替え種別が変わったら編集状態を解除して再描画する。
		self.cancel_edit()
		self.refresh_task_view()


def main() -> None:
	# アプリ本体を起動し、ウィンドウのイベント待ちを開始する。
	root = tk.Tk()
	TodoApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
