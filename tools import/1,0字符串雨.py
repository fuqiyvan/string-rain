import tkinter as tk
import random as r
import sys
import importlib

# ========== 优化配置项（纯2D数字雨） ==========
BASE_WIDTH = 2000
BASE_HEIGHT = 1100
FONT_MIN_SIZE = 12
FONT_MAX_SIZE = 30
SPEED_MIN = 2
SPEED_MAX = 9
STREAM_MIN_LEN = 25
STREAM_MAX_LEN = 55
SUPER_STREAM_CHANCE = 0.005
BASE_SPAWN_PROB = 0.05
MAX_STREAMS = 45
HEAD_BRIGHTNESS = 255
TAIL_BRIGHTNESS = 30
UPDATE_INTERVAL = 38
COLORS = ["#00FF00", "#00FFFF", "#0080FF", "#8000FF"]

# ====================== 提示系统 ======================
class MCTip:
    def __init__(self, root):
        self.root = root
        self.tips = []
        self.help_frame = None

    def show_error(self, msg="Unknown command. Type /help for help."):
        self.clear()
        error_frame = tk.Frame(self.root, bg="#220000", bd=1, highlightbackground="#ff3333", highlightthickness=1)
        tip = tk.Label(error_frame, text=msg, font=("Consolas", 13, "bold"), fg="#ff5555", bg="#220000", padx=15, pady=5)
        tip.pack()
        x = (self.root.winfo_width() - len(msg) * 8) // 2
        y = self.root.winfo_height() - 80
        error_frame.place(x=x, y=y)
        self.tips.append(error_frame)
        self.root.after(3000, lambda: self._safe_destroy(error_frame))

    def show_help(self):
        self.clear()
        self.help_frame = tk.Frame(self.root, bg="#0a0a0a", bd=2, highlightbackground="#00cccc", highlightthickness=2)
        title = tk.Label(self.help_frame, text="=== Available Commands ===", font=("Consolas", 14, "bold"), fg="#00ffff", bg="#0a0a0a")
        title.grid(row=0, column=0, columnspan=2, pady=(5, 8), padx=15)

        commands = [("/quit | /exit", "Close program"),("/clear", "Clear all streams"),("/search", "Web spider tool"),
                    ("/thesis", "Paper query tool"),("/ncmdump", "NCM music decrypt"),("/translation", "Language translate"),("/help", "Show this help info")]
        for idx, (cmd, desc) in enumerate(commands):
            cmd_label = tk.Label(self.help_frame, text=cmd, font=("Consolas", 13), fg="#ffff55", bg="#0a0a0a", anchor="w")
            desc_label = tk.Label(self.help_frame, text=desc, font=("Consolas", 12), fg="#88ff88", bg="#0a0a0a", anchor="w")
            cmd_label.grid(row=idx + 1, column=0, padx=(15, 20), pady=3, sticky="w")
            desc_label.grid(row=idx + 1, column=1, padx=(0, 15), pady=3, sticky="w")

        win_w = self.root.winfo_width()
        frame_w = 450
        frame_h = 220
        x = (win_w - frame_w) // 2
        y = self.root.winfo_height() - frame_h - 30
        self.help_frame.place(x=x, y=y, width=frame_w, height=frame_h)
        self.tips.append(self.help_frame)
        self.root.after(8000, self.clear)

    def clear(self):
        for t in self.tips:
            self._safe_destroy(t)
        self.tips = []
        self.help_frame = None

    def _safe_destroy(self, widget):
        try:
            widget.destroy()
        except:
            pass


# ====================== 输入框 ======================
class MCInputBox:
    def __init__(self, root, canvas, callback):
        self.root = root
        self.canvas = canvas
        self.execute_command = callback
        self.is_open = False

        self.cmd_history = []
        self.history_index = -1
        self.COMMANDS = ["/quit", "/exit", "/clear", "/search", "/thesis", "/ncmdump", "/translation", "/help"]

        self.bg_frame = tk.Frame(root, bg="#0f0f0f", bd=2, highlightbackground="#00cccc", highlightthickness=1, highlightcolor="#00ffff")
        self.entry = tk.Entry(self.bg_frame, font=("Consolas", 14), bg="#111111", fg="#f0f0f0",
                              insertbackground="#00ffff", bd=0, relief=tk.FLAT, insertwidth=2,
                              selectbackground="#004444", selectforeground="#ffffff")

        self.suggest_label = tk.Label(root, font=("Consolas", 13), fg="#888888", bg="#000", anchor="w", justify="left")

        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Escape>", self.close)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Up>", self.on_up)
        self.entry.bind("<Down>", self.on_down)
        self.entry.bind("<KeyRelease>", self.update_suggest)
        self.entry.bind("<Tab>", self.on_tab)
        self.root.bind("</>", self._on_slash_open)

    def _on_focus_out(self, event):
        focused = self.root.focus_get()
        if focused not in [self.entry, self.bg_frame]:
            self.close()

    def _on_slash_open(self, event):
        if self.is_open:
            return "break"
        self.open()
        self.entry.insert(0, "/")
        self.entry.icursor(1)
        self.update_suggest()
        return "break"

    def open(self):
        if self.is_open: return
        self.is_open = True
        self.history_index = -1
        win_h = self.root.winfo_height()
        self.bg_frame.place(x=20, y=win_h - 50, width=540, height=38)
        self.entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.entry.focus_set()
        self.suggest_label.place(x=570, y=win_h - 50, width=350, height=38)

    def close(self, event=None):
        if not self.is_open: return
        self.is_open = False
        self.entry.delete(0, tk.END)
        self.bg_frame.place_forget()
        self.suggest_label.place_forget()
        self.root.focus_set()

    def update_suggest(self, event=None):
        text = self.entry.get().strip().lower()
        if not text or not text.startswith("/"):
            self.suggest_label.config(text="")
            return
        matched = None
        for cmd in self.COMMANDS:
            if cmd.lower().startswith(text):
                matched = cmd
                break
        if matched:
            self.suggest_label.config(text=matched, fg="#00ffff" if len(text) > 1 else "#888888")
        else:
            self.suggest_label.config(text="No matching command")

    def on_tab(self, event):
        text = self.entry.get().strip().lower()
        if not text or not text.startswith("/"):
            return "break"
        matches = [cmd for cmd in self.COMMANDS if cmd.lower().startswith(text)]
        if matches:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, matches[0])
            self.update_suggest()
        return "break"

    def on_up(self, event):
        if not self.cmd_history: return
        self.history_index = (self.history_index + 1) % len(self.cmd_history)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.cmd_history[self.history_index])
        self.update_suggest()

    def on_down(self, event):
        if not self.cmd_history: return
        self.history_index = (self.history_index - 1) % len(self.cmd_history)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.cmd_history[self.history_index])
        self.update_suggest()

    def on_enter(self, event=None):
        cmd = self.entry.get().strip().lower()
        if cmd:
            if cmd in self.cmd_history:
                self.cmd_history.remove(cmd)
            self.cmd_history.insert(0, cmd)
            if len(self.cmd_history) > 20:
                self.cmd_history.pop()
            self.execute_command(cmd)
        self.close()


# ====================== 纯2D数字雨 ======================
class StringStream:
    def __init__(self, canvas, x, w, h):
        self.canvas = canvas
        self.x = x
        self.width = w
        self.height = h
        self.length = r.randint(STREAM_MIN_LEN, STREAM_MAX_LEN)
        if r.random() < SUPER_STREAM_CHANCE:
            self.length = r.randint(STREAM_MAX_LEN + 10, STREAM_MAX_LEN + 25)
        self.font_size = r.randint(FONT_MIN_SIZE + 1, FONT_MAX_SIZE - 1)
        self.font = ("Consolas", self.font_size, "bold")
        self.speed = r.uniform(SPEED_MIN, SPEED_MAX)
        self.color = r.choice(COLORS)

        self.chars = []
        self.items = []
        self.ys = []
        self.init_stream()

    def init_stream(self):
        step = (HEAD_BRIGHTNESS - TAIL_BRIGHTNESS) / self.length
        for i in range(self.length):
            c = r.choice("01")
            self.chars.append(c)
            bright = int(HEAD_BRIGHTNESS - i * step) if i != 0 else 255
            main_col = "#ffffff" if i == 0 else self._get_color(bright)
            y = -i * (self.font_size + 2)
            self.ys.append(y)

            # 仅创建主文字，无3D图层
            main_item = self.canvas.create_text(self.x, y, text=c, fill=main_col, font=self.font, anchor="nw")
            self.items.append(main_item)

    def _get_color(self, b):
        try:
            r_ = int(min(255, max(0, int(self.color[1:3], 16) * b / 255)))
            g_ = int(min(255, max(0, int(self.color[3:5], 16) * b / 255)))
            b_ = int(min(255, max(0, int(self.color[5:7], 16) * b / 255)))
            return f"#{r_:02x}{g_:02x}{b_:02x}"
        except:
            return "#006600"

    def update(self):
        # 更新头部字符
        self.chars[0] = r.choice("01")
        self.canvas.itemconfig(self.items[0], text=self.chars[0], fill="#ffffff")

        # 随机更新身体字符
        for i in range(1, self.length):
            if r.random() < 0.03:
                self.chars[i] = r.choice("01")
                self.canvas.itemconfig(self.items[i], text=self.chars[i])

        # 更新坐标（无3D偏移）
        for i in range(self.length):
            self.ys[i] += self.speed
            if self.ys[i] > self.height + self.font_size:
                self.ys[i] = -self.length * (self.font_size + 2)
            self.canvas.coords(self.items[i], self.x, self.ys[i])

    def destroy(self):
        try:
            # 仅删除主文字元素
            for item in self.items:
                self.canvas.delete(item)
        except:
            pass


# ====================== 主程序 ======================
class StringRain:
    def __init__(self, win):
        self.win = win
        self.canvas = tk.Canvas(win, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.streams = []
        self.win.protocol("WM_DELETE_WINDOW", self.safe_exit)
        self.win.bind("<Configure>", self.resize)
        self.mc_box = MCInputBox(win, self.canvas, self.run_cmd)
        self.tip = MCTip(win)
        self.loop()

    def safe_exit(self):
        for stream in self.streams:
            stream.destroy()
        sys.exit(0)

    def run_cmd(self, cmd):
        cmd = cmd.strip().lower()
        cmd_map = {
            "/quit": self.safe_exit,
            "/exit": self.safe_exit,
            "/clear": self.clear_streams,
            "/help": self.tip.show_help,
            "/search": lambda: self._run_external_tool("netbug", "run_spider_tool"),
            "/thesis": lambda: self._run_external_tool("thesisquery", "run_paper_search"),
            "/ncmdump": lambda: self._run_external_tool("ncmdumptool", "run_ncm_dump_tool"),
            "/translation": lambda: self._run_external_tool("translation", "run_translate_tool")
        }
        if cmd in cmd_map:
            try:
                cmd_map[cmd]()
            except ImportError as e:
                self.tip.show_error(f"Tool not found: {e.name}")
            except Exception as e:
                self.tip.show_error(f"Command error: {str(e)}")
        else:
            self.tip.show_error(f"Unknown command: {cmd}")

    def _run_external_tool(self, module_name, func_name):
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        func()

    def clear_streams(self):
        for stream in self.streams:
            stream.destroy()
        self.streams.clear()
        self.tip.show_error("All streams cleared")

    def resize(self, e):
        if e.widget == self.win:
            self.canvas.config(width=e.width, height=e.height)

    def spawn(self):
        if len(self.streams) >= MAX_STREAMS:
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50:
            return
        if r.random() < BASE_SPAWN_PROB:
            x = r.randint(10, w - 10)
            self.streams.append(StringStream(self.canvas, x, w, h))

    def loop(self):
        self.spawn()
        alive_streams = []
        for stream in self.streams:
            try:
                stream.update()
                alive_streams.append(stream)
            except:
                stream.destroy()
        self.streams = alive_streams
        self.win.after(UPDATE_INTERVAL, self.loop)


def run_cyber_rain():
    win = tk.Tk()
    win.title("Digital Rain")  # 移除标题中的3D
    win.config(bg="#000000")

    # 全屏无边框
    win.overrideredirect(True)
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    win.geometry(f"{screen_w}x{screen_h}+0+0")
    win.attributes("-topmost", True)

    # Esc一键退出
    win.bind("<Escape>", lambda e: win.destroy())

    StringRain(win)
    win.mainloop()


if __name__ == "__main__":
    try:
        run_cyber_rain()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)