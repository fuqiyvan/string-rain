import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

# --- 配置项 ---
# 默认打开的目录
DEFAULT_INPUT_DIR = Path("D:/fqy/tkinter/new")
# 打包输出目录（相对于本脚本）
BUILD_OUTPUT_DIR = Path("build_output")
# 历史记录文件路径
HISTORY_FILE = Path(__file__).parent / "pack_history.json"
# 窗口大小
WINDOW_SIZE = "500x220"
# 支持的文件类型
SUPPORTED_FILE_TYPES = [("Python文件", "*.py")]


class PackagerGUI:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Python 打包工具 📦")
        self.win.geometry(WINDOW_SIZE)
        # 禁止窗口缩放
        self.win.resizable(False, False)

        # 初始化变量
        self.input_path = tk.StringVar()
        self.status_text = tk.StringVar(value="等待输入...")
        self.status_color = tk.StringVar(value="blue")

        # 加载历史记录（可选）
        self.load_history()

        # 构建界面
        self.build_ui()

    def load_history(self):
        """加载历史打包记录"""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            self.history = []

    def save_history(self, file_path):
        """保存打包记录"""
        try:
            record = {
                "file": file_path,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "output_dir": str(self.get_build_dir())
            }
            self.history.append(record)
            # 只保留最近10条记录
            self.history = self.history[-10:]
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def get_build_dir(self):
        """获取打包输出目录（确保存在）"""
        base_dir = Path(__file__).parent.resolve()
        build_dir = base_dir / BUILD_OUTPUT_DIR
        build_dir.mkdir(exist_ok=True)
        return build_dir

    def validate_file_path(self, file_path):
        """验证文件路径有效性"""
        if not file_path:
            return False, "请选择或输入Python文件路径"

        path = Path(file_path)
        if not path.exists():
            return False, f"文件不存在: {file_path}"

        if path.suffix.lower() != ".py":
            return False, "请选择.py后缀的Python文件"

        return True, ""

    def select_file(self):
        """文件选择对话框"""
        # 确定初始目录
        initial_dir = DEFAULT_INPUT_DIR if DEFAULT_INPUT_DIR.exists() else Path.home()

        file_path = filedialog.askopenfilename(
            title="选择要打包的Python文件",
            filetypes=SUPPORTED_FILE_TYPES,
            initialdir=str(initial_dir)
        )

        if file_path:
            self.input_path.set(str(Path(file_path).absolute()))

    def run_packaging(self):
        """执行打包逻辑"""
        # 清空之前的状态
        self.status_text.set("打包中...")
        self.status_color.set("gold")
        self.win.update()

        # 1. 获取并验证输入路径
        input_path_str = self.input_path.get().strip()
        is_valid, msg = self.validate_file_path(input_path_str)
        if not is_valid:
            self.status_text.set(f"错误: {msg}")
            self.status_color.set("red")
            return

        target_file = Path(input_path_str)
        base_dir = Path(__file__).parent.resolve()
        setup_path = base_dir / "setup.py"

        # 2. 检查setup.py是否存在
        if not setup_path.exists():
            self.status_text.set(f"错误: 找不到setup.py\n路径: {setup_path}")
            self.status_color.set("red")
            return

        # 3. 构建打包命令（修改：传递完整文件路径，而非仅文件名）
        python_exe = sys.executable
        command = [
            python_exe, str(setup_path), "build",
            "--filename", str(target_file.absolute())  # 关键修改：传完整路径
        ]

        try:
            # 4. 执行打包命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                cwd=str(base_dir)
            )

            # 5. 打包成功处理
            build_dir = self.get_build_dir()
            self.status_text.set(f"✅ 打包成功！\n输出目录: {build_dir}/{target_file.stem}")
            self.status_color.set("green")
            self.save_history(str(target_file))
            print(f"打包成功日志:\n{result.stdout}")

        except subprocess.CalledProcessError as e:
            # 打包失败处理
            error_msg = f"❌ 打包失败！\n错误信息: {e.stderr[:100]}..."
            self.status_text.set(error_msg)
            self.status_color.set("red")
            print(f"打包失败 - Stdout: {e.stdout}")
            print(f"打包失败 - Stderr: {e.stderr}")

        except Exception as e:
            # 其他异常处理
            self.status_text.set(f"❌ 未知错误: {str(e)}")
            self.status_color.set("red")
            print(f"未知错误: {e}")

    def build_ui(self):
        """构建用户界面"""
        # 标题标签
        title_label = tk.Label(
            self.win,
            text="Python 文件打包工具",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=8)

        # 提示标签
        hint_label = tk.Label(
            self.win,
            text="请选择或输入要打包的.py文件路径",
            font=("Arial", 9)
        )
        hint_label.pack(pady=2)

        # 输入框框架
        input_frame = tk.Frame(self.win)
        input_frame.pack(pady=8, padx=20, fill=tk.X)

        # 输入框
        entry = tk.Entry(
            input_frame,
            textvariable=self.input_path,
            font=("Arial", 10)
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # 浏览按钮
        browse_btn = tk.Button(
            input_frame,
            text="📂 浏览",
            command=self.select_file,
            width=8,
            bg="#e0e0e0"
        )
        browse_btn.pack(side=tk.LEFT)

        # 操作按钮框架
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=5)

        # 确定按钮
        confirm_btn = tk.Button(
            btn_frame,
            text="🚀 开始打包",
            command=self.run_packaging,
            width=10,
            bg="#4CAF50",
            fg="white"
        )
        confirm_btn.pack(side=tk.LEFT, padx=5)

        # 退出按钮
        exit_btn = tk.Button(
            btn_frame,
            text="❌ 退出",
            command=self.win.quit,
            width=10,
            bg="#f44336",
            fg="white"
        )
        exit_btn.pack(side=tk.LEFT, padx=5)

        # 状态标签
        status_label = tk.Label(
            self.win,
            textvariable=self.status_text,
            fg=self.status_color.get(),
            font=("Arial", 9),
            wraplength=450
        )
        status_label.pack(pady=10)

        # 绑定状态颜色变化
        self.status_color.trace_add("write", lambda *args: setattr(status_label, "fg", self.status_color.get()))

    def run(self):
        self.win.attributes('-topmost', True)
        """运行GUI主循环"""
        self.win.mainloop()


def build_run():
    """主函数"""
    try:
        app = PackagerGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    build_run()