"""
シンプルなCUI版ToDoリストです。

このプログラムでできること:
1) タスク追加
2) タスク一覧表示
3) タスク完了
4) タスク削除
5) 終了

初心者向けに、各関数へ説明コメントを多めに入れています。
"""

from dataclasses import dataclass
import json
from pathlib import Path
import unicodedata


# タスク履歴を保存するJSONファイル
DATA_FILE = Path(__file__).with_name("todo_data.json")


@dataclass
class Task:
	# 1件分のタスク情報をまとめる「設計図」
	# dataclass を使うと、初期化などを自動で作ってくれる
	title: str
	due_date: str
	priority: str
	memo: str
	# done は完了フラグ。最初は未完了(False)
	done: bool = False


def load_tasks() -> list[Task]:
	"""保存済みのタスク履歴をJSONから読み込む。"""
	# ファイルがなければ、空のリストから開始
	if not DATA_FILE.exists():
		return []

	try:
		# UTF-8でJSONを読み込み、Taskのリストへ変換
		with DATA_FILE.open("r", encoding="utf-8") as f:
			items = json.load(f)
		return [Task(**item) for item in items]
	except (OSError, json.JSONDecodeError, TypeError, ValueError):
		# ファイル破損などで読めない場合は、空リストで安全に続行
		print("保存データを読み込めなかったため、新規リストで開始します。")
		return []


def save_tasks(tasks: list[Task]) -> None:
	"""現在のタスクリストをJSONへ保存する。"""
	# まれに不正なサロゲート文字が入力されることがあるため、
	# UTF-8で扱える文字へ置き換えてから保存する
	def safe_text(text: str) -> str:
		return text.encode("utf-8", errors="replace").decode("utf-8")

	# dataclassの各Taskを辞書化してJSONへ保存
	items = []
	for task in tasks:
		items.append(
			{
				"title": safe_text(task.title),
				"due_date": safe_text(task.due_date),
				"priority": safe_text(task.priority),
				"memo": safe_text(task.memo),
				"done": task.done,
			}
		)

	# JSON文字列を一度作ってからUTF-8バイトへ変換して保存する。
	# 不正文字が混じっても replace で落ちずに保存できる。
	json_text = json.dumps(items, ensure_ascii=False, indent=2)
	json_bytes = json_text.encode("utf-8", errors="replace")
	with DATA_FILE.open("wb") as f:
		f.write(json_bytes)


def show_menu() -> None:
	"""メニューを画面に表示する。"""
	# 1回のループごとに、このメニューを出して操作を選んでもらう
	print("\n=== TODOメニュー ===")
	print("1) タスクを追加")
	print("2) タスク一覧を表示")
	print("3) タスクを完了にする")
	print("4) タスクを削除")
	print("5) 終了")


def input_task() -> Task:
	"""ユーザーからタスク入力を受け取り、Taskとして返す。"""
	# 入力してもらう項目を先に案内する
	print("\n入力項目: タイトル、期限日、優先度、メモ")

	# Title は必須項目なので、空なら再入力してもらう
	while True:
		title = input("タイトル（必須）: ").strip()
		# 空文字でなければOK
		if title:
			break
		print("タイトルは必須です。")

	# ここからは任意入力(空でも可)
	due_date = input("期限日（例: 2026-06-30）: ").strip()

	# 優先度は番号で入力してもらい、内部で文字へ変換する
	# 1:高 / 2:中 / 3:低
	while True:
		priority_no = input("優先度（１:高/２:中/３:低）: ").strip()
		if priority_no == "":
			priority = "中"
			break
		if priority_no == "1":
			priority = "高"
			break
		if priority_no == "2":
			priority = "中"
			break
		if priority_no == "3":
			priority = "低"
			break
		print("優先度は 1 / 2 / 3 で入力してください。")

	memo = input("メモ: ").strip()

	# 未入力だったときのデフォルト値を決める
	if not due_date:
		due_date = "-"

	# 入力値を Task オブジェクトにまとめて返す
	return Task(title=title, due_date=due_date, priority=priority, memo=memo)


def show_tasks(tasks: list[Task]) -> None:
	"""現在のタスク一覧を表示する。"""
	print("\n=== タスク一覧 ===")
	# リストが空なら、そのことを表示して終了
	if not tasks:
		print("タスクはありません。")
		return

	# 全角文字を含んでもそろうよう、表示幅で列の余白を調整する
	def text_width(text: str) -> int:
		width = 0
		for ch in text:
			if unicodedata.east_asian_width(ch) in ("F", "W", "A"):
				width += 2
			else:
				width += 1
		return width

	def pad_text(text: str, target_width: int) -> str:
		pad = target_width - text_width(text)
		if pad < 0:
			pad = 0
		return text + (" " * pad)

	# タイトル列は「15文字」で固定表示にする。
	# 長いタイトルは15文字で切り、見た目の整列用に表示幅は30桁でそろえる。
	title_char_limit = 15
	title_column_width = 30
	# 期限は日付(YYYY-MM-DD)想定の10桁を最低幅にしてそろえる
	max_due = max(10, max(text_width(task.due_date) for task in tasks))
	max_priority = max(text_width(task.priority) for task in tasks)
	# 1桁番号と2桁番号が混在しても列がずれないよう、番号幅を固定
	index_width = len(str(len(tasks)))

	def format_task_line(index: int, task: Task) -> str:
		index_label = f"{index:>{index_width}}."
		fixed_title = task.title[:title_char_limit]
		title = pad_text(fixed_title, title_column_width)
		due_date = pad_text(task.due_date, max_due)
		priority = pad_text(task.priority, max_priority)
		return (
			f"{index_label} {title} | 期限: {due_date} | "
			f"優先度: {priority} | メモ: {task.memo}"
		)

	def print_box(section_name: str, lines: list[str], empty_message: str) -> None:
		"""1セクション分を枠で囲んで表示する。"""
		content_lines = lines if lines else [empty_message]
		content_width = max(text_width(section_name), *(text_width(line) for line in content_lines))
		horizontal = "+" + ("-" * (content_width + 2)) + "+"

		print("\n" + horizontal)
		print("| " + pad_text(section_name, content_width) + " |")
		print(horizontal)
		for line in content_lines:
			print("| " + pad_text(line, content_width) + " |")
		print(horizontal)

	# 未完了を上、完了を下に分けて表示する
	todo_lines: list[str] = []
	for i, task in enumerate(tasks, start=1):
		if not task.done:
			todo_lines.append(format_task_line(i, task))

	done_lines: list[str] = []
	for i, task in enumerate(tasks, start=1):
		if task.done:
			done_lines.append(format_task_line(i, task))

	print_box("未完了", todo_lines, "（未完了タスクはありません）")
	print_box("完了", done_lines, "（完了タスクはありません）")


def choose_task_index(tasks: list[Task], prompt: str) -> int | None:
	"""
	ユーザーに対象タスク番号を入力してもらい、
	内部で使うインデックス(0始まり)を返す。
	不正入力の場合は None を返す。
	"""
	# そもそもタスクがなければ選択できない
	if not tasks:
		print("タスクはありません。")
		return None

	# 選びやすいように一覧を先に表示
	show_tasks(tasks)

	try:
		# 入力は文字列なので int へ変換
		index = int(input(prompt).strip())
	except ValueError:
		# 数字に変換できない入力(例: abc)はエラー扱い
		print("数字を入力してください。")
		return None

	# 1〜件数の範囲外なら不正
	if index < 1 or index > len(tasks):
		print("存在しないタスク番号です。")
		return None

	# 画面表示は1始まり、リストは0始まりなので -1 する
	return index - 1


def main() -> None:
	"""アプリ本体: メニューを繰り返し表示して操作を受け付ける。"""
	# 起動時に前回までの履歴を読み込む
	tasks = load_tasks()

	# 終了を選ぶまで無限ループ
	while True:
		show_menu()
		choice = input("メニュー番号を選んでください（1-5）: ").strip()

		# 1) 追加
		if choice == "1":
			task = input_task()
			tasks.append(task)
			save_tasks(tasks)
			print("タスクを追加しました。")

		# 2) 一覧表示
		elif choice == "2":
			show_tasks(tasks)

		# 3) 完了にする
		elif choice == "3":
			index = choose_task_index(tasks, "完了にするタスク番号: ")
			if index is not None:
				tasks[index].done = True
				save_tasks(tasks)
				print("タスクを完了にしました。")
				show_tasks(tasks)

		# 4) 削除
		elif choice == "4":
			index = choose_task_index(tasks, "削除するタスク番号: ")
			if index is not None:
				# pop で削除しつつ、削除した要素を受け取る
				deleted = tasks.pop(index)
				save_tasks(tasks)
				print(f"削除しました: {deleted.title}")

		# 5) 終了
		elif choice == "5":
			print("終了します。")
			break

		# 1〜5 以外が入力されたとき
		else:
			print("メニュー番号が正しくありません。")


# このファイルを直接実行したときだけ main() を動かす
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\n操作を中断しました。終了します。")
