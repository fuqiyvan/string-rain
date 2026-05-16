import webbrowser as webb
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import urllib.parse

# 定义带搜索功能的打开函数（逻辑不变，仅美化界面）
def h1(entry):
    keyword = entry.get().strip()
    if not keyword:
        webb.open("https://doaj.org/")
        return
    search_url = f"https://doaj.org/search/journals?source=%7B%22query%22%3A%7B%22query_string%22%3A%7B%22query%22%3A{urllib.parse.quote(keyword)}%2C%22default_operator%22%3A%22AND%22%7D%7D%2C%22track_total_hits%22%3Atrue%7D"
    webb.open(search_url)

def h2(entry):
    keyword = entry.get().strip()
    if not keyword:
        webb.open("https://www.science.org/")
        return
    search_url = f"https://www.science.org/action/doSearch?AllField={urllib.parse.quote(keyword)}"
    webb.open(search_url)

def safe_exit(win):
    if messagebox.askokcancel("退出确认", "确定要退出吗？"):
        win.destroy()
        sys.exit(0)

def build_gui():
    # 主窗口基础设置
    win = tk.Tk()
    win.title("学术论文搜索工具")
    win.resizable(False, False)
    # 设置窗口背景色（柔和浅灰，避免纯白刺眼）
    win.configure(bg="#f0f2f5")
    # 设置窗口图标（可选，替换为自己的图标路径，支持.ico格式）
    # win.iconbitmap("search_icon.ico")

    # ========== 1. 定制ttk组件样式 ==========
    style = ttk.Style(win)
    # 设置ttk主题（可选：clam/alt/default/classic，clam主题更易定制）
    style.theme_use("clam")

    # 定制标签样式（标题/普通标签）
    style.configure("Title.TLabel",
                    font=("微软雅黑", 16, "bold"),
                    foreground="#2d3748",  # 深灰文字
                    background="#f0f2f5")
    style.configure("Normal.TLabel",
                    font=("微软雅黑", 10),
                    foreground="#4a5568",
                    background="#f0f2f5")

    # 定制输入框样式
    style.configure("Search.TEntry",
                    font=("微软雅黑", 10),
                    fieldbackground="white",  # 输入框背景
                    bordercolor="#e2e8f0",
                    borderwidth=1)

    # 定制按钮样式（普通按钮/退出按钮区分）
    # 普通搜索按钮
    style.configure("Search.TButton",
                    font=("微软雅黑", 10, "bold"),
                    foreground="white",
                    background="#4299e1",  # 蓝色主色调
                    borderwidth=0,
                    padding=(15, 8))  # 按钮内边距（左右/上下）
    style.map("Search.TButton",
              background=[("active", "#3182ce")],  # 鼠标悬停颜色
              foreground=[("active", "white")])

    # 退出按钮（警示色）
    style.configure("Exit.TButton",
                    font=("微软雅黑", 10, "bold"),
                    foreground="white",
                    background="#e53e3e",  # 红色警示色
                    borderwidth=0,
                    padding=(15, 8))
    style.map("Exit.TButton",
              background=[("active", "#c53030")],
              foreground=[("active", "white")])

    # ========== 2. 布局组件 ==========
    # 外层容器（增加整体内边距，避免组件贴边）
    main_frame = ttk.Frame(win, style="Normal.TLabel")
    main_frame.grid(row=0, column=0, padx=20, pady=20)

    # 标题标签
    title_label = ttk.Label(main_frame, text="学术论文搜索工具", style="Title.TLabel")
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))  # 下方间距

    # 搜索关键词标签+输入框
    keyword_label = ttk.Label(main_frame, text="搜索关键词：", style="Normal.TLabel")
    keyword_label.grid(row=1, column=0, sticky="e", padx=(0, 10), pady=(0, 15))

    entry = ttk.Entry(main_frame, width=30, style="Search.TEntry")  # 加宽输入框
    entry.grid(row=1, column=1, sticky="w", ipady=3)  # ipady增加输入框高度
    entry.insert(0, "")

    # 分隔线（视觉分区）
    separator = ttk.Separator(main_frame, orient="horizontal")
    separator.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))

    # 网站按钮
    doaj_btn = ttk.Button(main_frame, text="DOAJ", command=lambda: h1(entry), style="Search.TButton")
    doaj_btn.grid(row=3, column=0, padx=(0, 10), pady=(0, 15))

    science_btn = ttk.Button(main_frame, text="Science", command=lambda: h2(entry), style="Search.TButton")
    science_btn.grid(row=3, column=1, padx=(10, 0), pady=(0, 15))

    # 退出按钮
    exit_btn = ttk.Button(main_frame, text="退出", command=lambda: safe_exit(win), style="Exit.TButton")
    exit_btn.grid(row=4, column=0, columnspan=2, pady=(0, 5))

    # ========== 3. 窗口居中（优化版） ==========
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

    win.mainloop()

# 封装可导入调用的函数
def run_paper_search():
    build_gui()

if __name__ == "__main__":
    run_paper_search()