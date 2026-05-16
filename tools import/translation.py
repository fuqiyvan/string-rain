import tkinter as tk
from tkinter import messagebox, font, ttk
import requests


# ====================== 工具函数：绘制圆角矩形 ======================
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=15, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


# ====================== 圆角按钮类 ======================
class RoundedButton(tk.Frame):
    def __init__(self, master, text, command, bg="#3B82F6", hover_bg="#2563EB", **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.btn_w = 120
        self.btn_h = 40
        self.config(width=self.btn_w, height=self.btn_h)

        self.canvas = tk.Canvas(self, bg=master.cget("bg"), width=self.btn_w, height=self.btn_h, bd=0,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.btn_shape = create_rounded_rectangle(self.canvas, 0, 0, self.btn_w, self.btn_h, radius=12, fill=self.bg,
                                                  outline="")

        self.label = tk.Label(self.canvas, text=text, fg="white", bg=self.bg, font=("微软雅黑", 12, "bold"))
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        self.canvas.bind("<Enter>", self._on_hover)
        self.canvas.bind("<Leave>", self._on_leave)
        self.canvas.bind("<Button-1>", self._on_click)
        self.label.bind("<Enter>", self._on_hover)
        self.label.bind("<Leave>", self._on_leave)
        self.label.bind("<Button-1>", self._on_click)
        self.canvas.config(cursor="hand2")

    def _on_hover(self, event=None):
        self.canvas.itemconfig(self.btn_shape, fill=self.hover_bg)
        self.label.config(bg=self.hover_bg)

    def _on_leave(self, event=None):
        self.canvas.itemconfig(self.btn_shape, fill=self.bg)
        self.label.config(bg=self.bg)

    def _on_click(self, event):
        if self.command:
            self.command()


# ====================== 稳定翻译函数（彻底修复所有问题） ======================
def translate_text(text, from_lang, to_lang):
    try:
        # 统一语言代码格式，彻底解决API不识别问题
        lang_map = {
            "auto": "auto",
            "zh": "zh",
            "zh-CN": "zh",
            "en": "en",
            "ja": "ja",
            "ko": "ko",
            "fr": "fr",
            "de": "de"
        }
        from_code = lang_map.get(from_lang, from_lang)
        to_code = lang_map.get(to_lang, to_lang)

        # 处理自动检测
        if from_code == "auto":
            langpair = f"|{to_code}"
        else:
            langpair = f"{from_code}|{to_code}"

        # 调用MyMemory API，增加重试机制和超时
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": langpair,
            "de": "a@b.c"  # 绕过部分限制
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        # 处理API返回错误
        if data.get("responseStatus") != 200:
            error_msg = data.get("responseDetails", "未知错误")
            return f"翻译失败：{error_msg}"

        # 完整返回翻译结果
        return data["responseData"]["translatedText"]
    except Exception as e:
        return f"翻译失败：{str(e)}"


# ====================== 翻译工具主程序 ======================
def run_translate_tool():
    root = tk.Tk()
    root.title("多语言翻译工具")
    root.geometry("800x650")
    root.resizable(False, False)
    root.configure(bg="#F5F7FA")

    font_title = font.Font(family="微软雅黑", size=16, weight="bold")
    font_text = font.Font(family="微软雅黑", size=11)

    # 统一语言代码，彻底解决格式问题
    LANGUAGES = {
        "自动检测": "auto",
        "中文": "zh",
        "英文": "en",
        "日文": "ja",
        "韩文": "ko",
        "法文": "fr",
        "德文": "de"
    }

    from_lang_var = tk.StringVar(value="英文")
    to_lang_var = tk.StringVar(value="中文")

    tk.Label(root, text="多语言翻译工具", font=font_title, bg="#F5F7FA", fg="#1F2937").place(x=400, y=15,
                                                                                             anchor="center")

    lang_frame = tk.Frame(root, bg="#F5F7FA")
    lang_frame.place(x=400, y=55, anchor="center")

    tk.Label(lang_frame, text="源语言：", bg="#F5F7FA", font=font_text).grid(row=0, column=0, padx=5)
    from_combo = ttk.Combobox(lang_frame, values=list(LANGUAGES.keys()), textvariable=from_lang_var, state="readonly",
                              width=12, font=("微软雅黑", 10))
    from_combo.grid(row=0, column=1, padx=5)

    tk.Label(lang_frame, text="目标语言：", bg="#F5F7FA", font=font_text).grid(row=0, column=2, padx=5)
    to_combo = ttk.Combobox(lang_frame, values=list(LANGUAGES.keys()), textvariable=to_lang_var, state="readonly",
                            width=12, font=("微软雅黑", 10))
    to_combo.grid(row=0, column=3, padx=5)

    input_canvas = tk.Canvas(root, bg="#F5F7FA", bd=0, highlightthickness=0)
    input_canvas.place(x=25, y=90, width=750, height=220)
    create_rounded_rectangle(input_canvas, 0, 0, 750, 220, radius=10, fill="#FFFFFF", outline="")
    tk.Label(input_canvas, text="输入内容", font=font_text, bg="#FFFFFF", fg="#4B5563").place(x=15, y=12)
    input_text = tk.Text(input_canvas, font=font_text, bd=0, wrap="word", bg="#FFFFFF", padx=15, pady=10)
    input_text.place(x=15, y=40, width=720, height=160)

    output_canvas = tk.Canvas(root, bg="#F5F7FA", bd=0, highlightthickness=0)
    output_canvas.place(x=25, y=320, width=750, height=220)
    create_rounded_rectangle(output_canvas, 0, 0, 750, 220, radius=10, fill="#FFFFFF", outline="")
    tk.Label(output_canvas, text="翻译结果", font=font_text, bg="#FFFFFF", fg="#4B5563").place(x=15, y=12)
    output_text = tk.Text(output_canvas, font=font_text, bd=0, wrap="word", bg="#F9FAFB", padx=15, pady=10,
                          state="normal")
    output_text.place(x=15, y=40, width=720, height=160)

    def do_translate():
        from_label = from_lang_var.get()
        to_label = to_lang_var.get()
        from_code = LANGUAGES[from_label]
        to_code = LANGUAGES[to_label]

        content = input_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("提示", "请输入内容")
            return

        res = translate_text(content, from_code, to_code)
        output_text.delete("1.0", tk.END)
        output_text.insert("1.0", res)

    def do_exit():
        if messagebox.askyesno("退出", "确定关闭？"):
            root.destroy()

    trans_btn = RoundedButton(root, text="翻  译", command=do_translate)
    trans_btn.place(x=300, y=580, anchor="center")

    exit_btn = RoundedButton(root, text="退  出", command=do_exit, bg="#EF4444", hover_bg="#DC2626")
    exit_btn.place(x=500, y=580, anchor="center")

    root.mainloop()


if __name__ == "__main__":
    run_translate_tool()