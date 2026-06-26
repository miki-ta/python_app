import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Zoom_minutes.main import ZoomMinutesApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ZoomMinutesApp(root)
    root.mainloop()
