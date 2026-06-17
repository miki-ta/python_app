import json
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
import os


def load_from_json(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get('items', [])
    return data


def load_from_csv(path):
    items = []
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            items.append({
                'category': r.get('category', r.get('カテゴリ', '')),
                'title': r.get('title', r.get('タイトル', '')),
                'description': r.get('description', r.get('説明', '')),
            })
    return items


def render_markdown(groups):
    lines = ['# コールセンター運用マニュアル\n']
    for cat in sorted(groups.keys()):
        lines.append(f'## {cat}\n')
        for idx, it in enumerate(groups[cat], start=1):
            title = it.get('title', '（無題）')
            desc = it.get('description', '')
            lines.append(f'{idx}. **{title}**')
            if desc:
                lines.append(f'   - {desc}')
        lines.append('')
    return '\n'.join(lines)


class ManualGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('マニュアルビルダー')
        self.geometry('900x600')
        self.create_widgets()
        self.items = []

    def create_widgets(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='開く (JSON/CSV)', command=self.on_open)
        filemenu.add_command(label='Markdownで保存', command=self.on_save_markdown)
        filemenu.add_separator()
        filemenu.add_command(label='終了', command=self.quit)
        menubar.add_cascade(label='ファイル', menu=filemenu)
        self.config(menu=menubar)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=6, pady=6)

        ttk.Button(toolbar, text='追加', command=self.on_add).pack(side='left')
        ttk.Button(toolbar, text='削除', command=self.on_delete).pack(side='left')
        ttk.Button(toolbar, text='上へ', command=lambda: self.move_selected(-1)).pack(side='left')
        ttk.Button(toolbar, text='下へ', command=lambda: self.move_selected(1)).pack(side='left')

        self.tree = ttk.Treeview(self, columns=('category', 'title', 'description'), show='headings')
        self.tree.heading('category', text='カテゴリ')
        self.tree.heading('title', text='タイトル')
        self.tree.heading('description', text='説明')
        self.tree.column('category', width=150)
        self.tree.column('title', width=250)
        self.tree.column('description', width=450)
        self.tree.pack(fill='both', expand=True, padx=6, pady=6)

        editor = ttk.Frame(self)
        editor.pack(fill='x', padx=6, pady=6)
        ttk.Label(editor, text='カテゴリ').grid(row=0, column=0, sticky='w')
        ttk.Label(editor, text='タイトル').grid(row=1, column=0, sticky='w')
        ttk.Label(editor, text='説明').grid(row=2, column=0, sticky='nw')

        self.var_cat = tk.StringVar()
        self.var_title = tk.StringVar()
        self.txt_desc = tk.Text(editor, height=4)

        ttk.Entry(editor, textvariable=self.var_cat).grid(row=0, column=1, sticky='we')
        ttk.Entry(editor, textvariable=self.var_title).grid(row=1, column=1, sticky='we')
        self.txt_desc.grid(row=2, column=1, sticky='we')

        editbtn = ttk.Frame(editor)
        editbtn.grid(row=0, column=2, rowspan=3, padx=6)
        ttk.Button(editbtn, text='選択を編集', command=self.on_apply_edit).pack(fill='x')
        ttk.Button(editbtn, text='クリア', command=self.clear_editor).pack(fill='x', pady=4)

        editor.columnconfigure(1, weight=1)

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def on_open(self):
        path = filedialog.askopenfilename(filetypes=[('JSON/CSV', '*.json;*.csv'), ('All', '*.*')])
        if not path:
            return
        try:
            if path.lower().endswith('.json'):
                items = load_from_json(path)
            else:
                items = load_from_csv(path)
        except Exception as e:
            messagebox.showerror('読み込みエラー', str(e))
            return
        self.items = items
        self.refresh_tree()

    def on_save_markdown(self):
        if not self.items:
            messagebox.showinfo('情報', '項目がありません')
            return
        groups = defaultdict(list)
        for it in self.items:
            groups[(it.get('category') or '未分類')].append(it)
        md = render_markdown(groups)
        path = filedialog.asksaveasfilename(defaultextension='.md', filetypes=[('Markdown', '*.md'), ('Text', '*.txt'), ('All', '*.*')])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(md)
        except Exception as e:
            messagebox.showerror('保存エラー', str(e))
            return
        messagebox.showinfo('完了', f'書き出しました: {os.path.basename(path)}')

    def on_add(self):
        cat = self.var_cat.get().strip()
        title = self.var_title.get().strip()
        desc = self.txt_desc.get('1.0', 'end').strip()
        if not (cat or title):
            messagebox.showwarning('入力不足', 'カテゴリまたはタイトルを入力してください')
            return
        self.items.append({'category': cat, 'title': title, 'description': desc})
        self.refresh_tree()
        self.clear_editor()

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self.items):
            del self.items[idx]
        self.refresh_tree()

    def move_selected(self, delta):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        new = idx + delta
        if 0 <= new < len(self.items):
            self.items[idx], self.items[new] = self.items[new], self.items[idx]
            self.refresh_tree()
            self.tree.selection_set(str(new))

    def on_select(self, _ev=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        it = self.items[idx]
        self.var_cat.set(it.get('category', ''))
        self.var_title.set(it.get('title', ''))
        self.txt_desc.delete('1.0', 'end')
        self.txt_desc.insert('1.0', it.get('description', ''))

    def on_apply_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('選択なし', '編集する行を選択してください')
            return
        idx = int(sel[0])
        self.items[idx] = {
            'category': self.var_cat.get().strip(),
            'title': self.var_title.get().strip(),
            'description': self.txt_desc.get('1.0', 'end').strip(),
        }
        self.refresh_tree()

    def clear_editor(self):
        self.var_cat.set('')
        self.var_title.set('')
        self.txt_desc.delete('1.0', 'end')

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, it in enumerate(self.items):
            cat = it.get('category', '')
            title = it.get('title', '')
            desc = it.get('description', '')
            self.tree.insert('', 'end', iid=str(i), values=(cat, title, desc))


def main():
    app = ManualGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
