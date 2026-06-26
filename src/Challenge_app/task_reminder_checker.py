"""
タスクリマインダーチェッカー
Windowsタスクスケジューラから定期実行し、reminded フラグを更新する。
"""

import sqlite3
import contextlib
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
DB_FILE  = DATA_DIR / "tm_tasks.db"
STATE_DB_TABLE = "reminder_notified"  # 期限切れ通知済みIDを tasks テーブルで管理


@contextlib.contextmanager
def _db():
    conn = sqlite3.connect(str(DB_FILE), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check():
    if not DB_FILE.exists():
        return

    with _db() as conn:
        rows = conn.execute(
            "SELECT task_id, status, due_date, reminder_minutes, reminded"
            " FROM tasks WHERE status != '完了' AND due_date != '-'"
        ).fetchall()

        now = datetime.now()
        remind_ids = []

        for row in rows:
            task_id          = row["task_id"]
            due              = row["due_date"]
            reminder_minutes = row["reminder_minutes"]
            reminded         = bool(row["reminded"])

            try:
                if " " in due:
                    due_dt = datetime.strptime(due, "%Y-%m-%d %H:%M")
                else:
                    due_dt = datetime.strptime(due + " 23:59", "%Y-%m-%d %H:%M")
            except Exception:
                continue

            delta_min = (due_dt - now).total_seconds() / 60

            if (
                reminder_minutes > 0
                and not reminded
                and 0 <= delta_min <= reminder_minutes
            ):
                remind_ids.append(task_id)

        if remind_ids:
            conn.executemany(
                "UPDATE tasks SET reminded=1 WHERE task_id=?",
                [(tid,) for tid in remind_ids],
            )


if __name__ == "__main__":
    check()
