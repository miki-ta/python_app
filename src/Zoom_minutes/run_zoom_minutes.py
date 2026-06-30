import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Zoom_minutes.main import ZoomMinutesApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ZoomMinutesApp(root)
    # 起動時に最前面へ（1秒後に通常モードに戻す）
    root.lift()
    root.attributes("-topmost", True)
    root.after(1000, lambda: root.attributes("-topmost", False))
    root.mainloop()
