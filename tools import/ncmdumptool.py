import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import subprocess
import sys

# ====================== 核心配置 ======================
DELETE_NCM = True  # 解密后删除原NCM文件（False=保留）

# ======================================================

class NCMDumpGUI:
    """NCM解密工具GUI（调用ncmdump核心）"""
    def __init__(self, root):
        self.root = root
        self.root.title("NCM批量解密工具 | 基于ncmdump核心")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")
        self.work_dir = ""

        # 检查ncmdump是否安装
        self._check_ncmdump()

        # 初始化界面
        self._setup_style()
        self._create_widgets()
        self._center_window()

    def _check_ncmdump(self):
        """检查ncmdump是否安装"""
        try:
            # 尝试调用ncmdump -h验证
            subprocess.run(
                ["ncmdump", "-h"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8"
            )
            self.ncmdump_available = True
        except FileNotFoundError:
            self.ncmdump_available = False
            messagebox.showwarning(
                "依赖缺失",
                "未找到ncmdump！请先安装：\n"
                "方法1（推荐）：pip install ncmdump\n"
                "方法2：下载二进制文件并添加到环境变量"
            )

    def _setup_style(self):
        """设置界面样式"""
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # 标题样式
        style.configure("Title.TLabel",
                        font=("微软雅黑", 16, "bold"),
                        foreground="#2d3748",
                        background="#f0f2f5")

        # 普通标签样式
        style.configure("Normal.TLabel",
                        font=("微软雅黑", 10),
                        foreground="#4a5568",
                        background="#f0f2f5")

        # 蓝色按钮（主要操作）
        style.configure("Primary.TButton",
                        font=("微软雅黑", 10, "bold"),
                        foreground="white",
                        background="#4299e1",
                        padding=(15, 8))
        style.map("Primary.TButton",
                  background=[("active", "#3182ce")])

        # 红色按钮（退出/危险操作）
        style.configure("Danger.TButton",
                        font=("微软雅黑", 10, "bold"),
                        foreground="white",
                        background="#e53e3e",
                        padding=(15, 8))
        style.map("Danger.TButton",
                  background=[("active", "#c53030")])

    def _center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, style="Normal.TLabel")
        main_frame.grid(row=0, column=0, padx=30, pady=30)

        # 标题
        title_label = ttk.Label(main_frame, text="🎵 NCM批量解密工具（ncmdump核心）", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 选择目录按钮
        dir_btn = ttk.Button(main_frame,
                             text="选择NCM文件目录",
                             style="Primary.TButton",
                             command=self._select_directory)
        dir_btn.grid(row=1, column=0, padx=8, pady=10)

        # 开始解密按钮
        self.start_btn = ttk.Button(main_frame,
                                    text="开始批量解密",
                                    style="Primary.TButton",
                                    command=self._start_decrypt_thread)
        self.start_btn.grid(row=1, column=1, padx=8, pady=10)

        # 日志区域（带滚动条）
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=2, column=0, columnspan=2, pady=15)

        self.log_text = tk.Text(log_frame,
                                width=55,
                                height=15,
                                font=("微软雅黑", 9),
                                bg="white",
                                relief=tk.FLAT,
                                wrap=tk.WORD)
        self.log_text.config(state=tk.NORMAL)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 退出按钮
        exit_btn = ttk.Button(main_frame,
                              text="退出工具",
                              style="Danger.TButton",
                              command=self._safe_exit)
        exit_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def _log(self, message):
        """添加日志信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def _select_directory(self):
        """选择工作目录"""
        dir_path = filedialog.askdirectory(title="选择包含NCM文件的目录")
        if dir_path:
            self.work_dir = dir_path
            self._log(f"✅ 已选择目录：{self.work_dir}")

    def _dump_single_file(self, file_path):
        """调用ncmdump解密单个文件"""
        try:
            self._log(f"🔄 正在处理：{os.path.basename(file_path)}")

            # 调用ncmdump核心命令（官方标准用法）
            result = subprocess.run(
                ["ncmdump", "-o", os.path.dirname(file_path), file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                timeout=30  # 超时保护
            )

            # 检查执行结果
            if result.returncode == 0:
                # 解密成功，可选删除原NCM文件
                if DELETE_NCM:
                    try:
                        os.remove(file_path)
                        self._log(f"✅ 解密完成：{os.path.basename(file_path)} → MP3（已删除原NCM）")
                    except Exception as e:
                        self._log(f"✅ 解密完成：{os.path.basename(file_path)} → MP3（删除原文件失败：{e}）")
                else:
                    self._log(f"✅ 解密完成：{os.path.basename(file_path)} → MP3（保留原NCM）")
            else:
                # 解密失败，输出错误信息
                error_msg = result.stderr.strip() or "未知错误"
                self._log(f"❌ 解密失败：{os.path.basename(file_path)} | 错误：{error_msg[:100]}")

        except subprocess.TimeoutExpired:
            self._log(f"❌ 处理超时：{os.path.basename(file_path)}")
        except Exception as e:
            self._log(f"❌ 处理失败：{os.path.basename(file_path)} | 错误：{str(e)}")

    def _batch_dump(self):
        """批量解密目录下的所有NCM文件"""
        # 前置检查
        if not self.ncmdump_available:
            messagebox.showwarning("依赖缺失", "请先安装ncmdump后再运行！")
            self.start_btn.config(state=tk.NORMAL)
            return

        if not self.work_dir:
            messagebox.showwarning("提示", "请先选择NCM文件目录！")
            self.start_btn.config(state=tk.NORMAL)
            return

        self._log("=" * 60)
        self._log("🔍 开始扫描NCM文件...")

        # 遍历目录查找所有NCM文件
        ncm_files = []
        for root, _, files in os.walk(self.work_dir):
            for file in files:
                if file.lower().endswith(".ncm"):
                    ncm_files.append(os.path.join(root, file))

        if not ncm_files:
            self._log("⚠️ 未找到任何NCM文件！")
            self.start_btn.config(state=tk.NORMAL)
            return

        self._log(f"📊 共找到 {len(ncm_files)} 个NCM文件，开始解密...")

        # 批量调用ncmdump处理
        for file_path in ncm_files:
            self._dump_single_file(file_path)

        self._log("🎉 所有文件处理完成！")
        self._log("=" * 60)
        self.start_btn.config(state=tk.NORMAL)

    def _start_decrypt_thread(self):
        """启动解密线程（避免界面卡顿）"""
        self.start_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._batch_dump, daemon=True)
        thread.start()

    def _safe_exit(self):
        """安全退出"""
        if messagebox.askokcancel("退出确认", "确定要退出NCM解密工具吗？"):
            self.root.destroy()

# 封装可导入调用的函数
def run_ncm_dump_tool():
    """启动NCM批量解密工具"""
    root = tk.Tk()
    app = NCMDumpGUI(root)

    root.attributes("-topmost", True)
    root.mainloop()

if __name__ == "__main__":
    run_ncm_dump_tool()