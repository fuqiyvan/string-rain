import os
import sqlite3
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess

# 关闭多余警告
os.environ["TK_SILENCE_DEPRECATION"] = "1"

DB_NAME = "file_index.db"
SKIP_DIRS = {"Windows", "Program Files", "Program Files (x86)",
             "AppData", "System Volume Information", "ProgramData", "$Recycle.Bin"}


class FileSearchCore:
    def __init__(self):
        self.init_db()

    def get_conn(self):
        return sqlite3.connect(DB_NAME)

    def init_db(self):
        conn = self.get_conn()
        cur = conn.cursor()
        # 统一字段：modify_time
        cur.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            name TEXT NOT NULL,
            size INTEGER,
            modify_time TEXT
        )
        ''')
        cur.execute("CREATE INDEX IF NOT EXISTS idx_name ON files(name)")
        conn.commit()
        conn.close()

    def clear_old_index(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM files")
        conn.commit()
        conn.close()

    def build_scan_index(self, scan_path, ui_callback, finish_callback):
        self.clear_old_index()
        start = time.time()
        count = 0
        conn = self.get_conn()
        cur = conn.cursor()

        for root_dir, dirs, files in os.walk(scan_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for file in files:
                try:
                    full_path = os.path.join(root_dir, file)
                    f_size = os.path.getsize(full_path)
                    t = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M:%S")
                    cur.execute(
                        "INSERT INTO files (path, name, size, modify_time) VALUES (?,?,?,?)",
                        (full_path, file, f_size, t)
                    )
                    count += 1
                    if count % 5000 == 0:
                        conn.commit()
                        ui_callback(f"已扫描：{count} 个文件")
                except:
                    continue

        conn.commit()
        conn.close()
        cost = round(time.time() - start, 2)
        finish_callback(f"✅ 索引完成 | 共 {count} 文件 | 耗时 {cost} 秒")

    def search_file(self, keyword):
        conn = self.get_conn()
        cur = conn.cursor()
        # 严格对应数据表字段
        cur.execute(
            "SELECT path, size, modify_time FROM files WHERE name LIKE ? ORDER BY size DESC",
            (f"%{keyword}%",)
        )
        res = cur.fetchall()
        conn.close()
        return res

    @staticmethod
    def format_size(b: int) -> str:
        if b < 1024:
            return f"{b} B"
        elif b < 1024**2:
            return f"{b/1024:.2f} KB"
        elif b < 1024**3:
            return f"{b/1024**2:.2f} MB"
        else:
            return f"{b/1024**3:.2f} GB"

    # ========== 【修复】Windows 标准打开方式 ==========
    @staticmethod
    def open_file(path):
        if not os.path.exists(path):
            messagebox.showerror("错误", "文件不存在！")
            return
        # 纯Windows原生打开，百分百可用
        os.startfile(path)

    @staticmethod
    def open_folder_select_file(path):
        if not os.path.exists(path):
            messagebox.showerror("错误", "路径不存在！")
            return
        subprocess.run(["explorer", "/select,", path])


class SearchGUI:
    def __init__(self, root_win):
        self.root = root_win
        self.core = FileSearchCore()
        self.scan_path = "D:/"
        self.now_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.root.title("极速文件搜索 | 右键打开文件/目录")
        self.root.geometry("1000x700")

        ttk.Label(self.root, text="🚀 极速磁盘文件搜索", font=("微软雅黑", 20, "bold")).pack(pady=10)

        frame_top = ttk.Frame(self.root)
        frame_top.pack(pady=5)

        ttk.Button(frame_top, text="📂 选择扫描目录", command=self.choose_dir).grid(row=0, column=0, padx=5)
        self.btn_build = ttk.Button(frame_top, text="🔄 构建索引", command=self.start_build)
        self.btn_build.grid(row=0, column=1, padx=5)
        ttk.Button(frame_top, text="🧹 清空结果", command=self.clear_result).grid(row=0, column=2, padx=5)

        frame_search = ttk.Frame(self.root)
        frame_search.pack(pady=10)

        ttk.Label(frame_search, text="关键词：").grid(row=0, column=0)
        self.entry = ttk.Entry(frame_search, width=40, font=("微软雅黑", 11))
        self.entry.grid(row=0, column=1, padx=8)
        self.entry.bind("<Return>", lambda e: self.start_search())
        ttk.Button(frame_search, text="🔍 搜索", command=self.start_search).grid(row=0, column=2)

        self.status = ttk.Label(self.root, text="就绪", foreground="green")
        self.status.pack()

        self.text = scrolledtext.ScrolledText(self.root, font=("Consolas", 10))
        self.text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 右键菜单
        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="打开文件", command=self.do_open_file)
        self.menu.add_command(label="打开所在文件夹", command=self.do_open_dir)
        self.text.bind("<Button-3>", self.on_right_click)

    def choose_dir(self):
        p = filedialog.askdirectory()
        if p:
            self.scan_path = p
            self.status.config(text=f"已选择：{p}", foreground="blue")

    def clear_result(self):
        self.text.delete(1.0, tk.END)

    def update_log(self, msg):
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    def start_build(self):
        self.btn_build.config(state=tk.DISABLED)
        self.clear_result()
        self.status.config(text="正在扫描...", foreground="orange")
        t = threading.Thread(target=self.core.build_scan_index,
                             args=(self.scan_path, self.update_log, self.build_done),
                             daemon=True)
        t.start()

    def build_done(self, msg):
        self.update_log(msg)
        self.status.config(text=msg, foreground="green")
        self.btn_build.config(state=tk.NORMAL)

    def start_search(self):
        threading.Thread(target=self.search, daemon=True).start()

    def search(self):
        key = self.entry.get().strip()
        if not key:
            messagebox.showwarning("提示", "请输入关键词")
            return
        self.status.config(text="搜索中...", foreground="blue")
        res = self.core.search_file(key)
        self.clear_result()

        if not res:
            self.text.insert(tk.END, "未找到该文件\n")
            self.status.config(text="无结果", foreground="red")
            return

        self.text.insert(tk.END, f"找到 {len(res)} 个结果\n" + "-"*80 + "\n\n")
        for path, size, t in res:
            sz = self.core.format_size(size)
            self.text.insert(tk.END, f"路径:{path}\n大小:{sz}  时间:{t}\n" + "-"*80 + "\n\n")
        self.status.config(text=f"搜索完成，共{len(res)}条")

    # 右键选中路径
    def on_right_click(self, event):
        try:
            idx = self.text.index(f"@{event.x},{event.y}")
            line = self.text.get(f"{idx} linestart", f"{idx} lineend")
            if line.startswith("路径:"):
                self.now_path = line.replace("路径:", "").strip()
                self.menu.tk_popup(event.x_root, event.y_root)
        except:
            pass

    def do_open_file(self):
        if self.now_path:
            self.core.open_file(self.now_path)

    def do_open_dir(self):
        if self.now_path:
            self.core.open_folder_select_file(self.now_path)


def main():
    root = tk.Tk()
    app = SearchGUI(root)
    root.attributes('-topmost', True)
    root.mainloop()


if __name__ == "__main__":
    main()