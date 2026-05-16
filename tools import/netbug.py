import tkinter as tk
from tkinter import messagebox, font, ttk
import requests
from bs4 import BeautifulSoup
import urllib.parse
import random
import time

# ====================== 绘制圆角矩形 ======================
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=15, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

# ====================== 圆角按钮 ======================
class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command, bg="#3B82F6", hover_bg="#2563EB", radius=12, width=140, height=42, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.bg_color = bg
        self.hover_color = hover_bg
        self.radius = radius
        self.btn_width = width
        self.btn_height = height
        self.disabled = False

        self.shape = create_rounded_rectangle(self, 0, 0, self.btn_width, self.btn_height, radius=radius, fill=self.bg_color, outline="")
        self.text = self.create_text(self.btn_width/2, self.btn_height/2, text=text, fill="white", font=("微软雅黑",12,"bold"))

        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.config(width=self.btn_width, height=self.btn_height, cursor="hand2", highlightthickness=0, bd=0)

    def _on_hover(self, event):
        if not self.disabled: self.itemconfig(self.shape, fill=self.hover_color)
    def _on_leave(self, event):
        if not self.disabled: self.itemconfig(self.shape, fill=self.bg_color)
    def _on_click(self, event):
        if not self.disabled and self.command: self.command()
    def config(self, **kwargs):
        if "state" in kwargs:
            state = kwargs.pop("state")
            self.disabled = (state == tk.DISABLED)
            self.itemconfig(self.shape, fill="#94a3b8" if self.disabled else self.bg_color)
            self.config(cursor="arrow" if self.disabled else "hand2")
        super().config(**kwargs)

# ====================== 工具函数 ======================
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")
def clean_text(text):
    return text.strip().replace("\n"," ").replace("\t"," ").replace("\r","")

# ====================== 爬虫工具 ======================
def run_spider_tool():
    spider_content = ""
    spider_title = ""
    saved_links = set()

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    ]

    def start_spider():
        nonlocal spider_content, spider_title
        mode = spider_mode.get()
        input_text = entry_input.get("1.0", tk.END).strip()
        saved_links.clear()

        if not input_text:
            messagebox.showwarning("提示","请输入内容")
            return

        btn_start.config(state=tk.DISABLED)
        btn_save.config(state=tk.DISABLED)
        text_status.delete("1.0",tk.END)
        text_status.insert(tk.END,f"[{get_time()}] 开始爬取...\n")
        root.update()

        try:
            session = requests.Session()
            session.headers.update({
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language":"zh-CN,zh;q=0.9",
                "Referer":"https://www.baidu.com"
            })
            time.sleep(0.5)

            if mode == "url":
                if not input_text.startswith("http"):
                    input_text = "https://"+input_text
                res = session.get(input_text, timeout=12)
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text,"html.parser")
                title = soup.title.string[:18] if soup.title else "网页"
                spider_title=f"网页_{title}"
                spider_content=f"【网页爬取】\n网址：{input_text}\n时间：{get_time()}\n{'='*50}\n\n"
                for p in soup.find_all(["p","h1","h2","h3"],limit=25):
                    t=clean_text(p.get_text())
                    if 30<len(t)<600:
                        spider_content+=t+"\n\n"

            elif mode == "keyword":
                kw = urllib.parse.quote(input_text)
                url = f"https://www.baidu.com/s?wd={kw}&rn=15&ie=utf-8"
                res = session.get(url, timeout=12)
                res.encoding="utf-8"
                soup = BeautifulSoup(res.text,"html.parser")
                spider_title=f"搜索_{input_text[:8]}"
                spider_content=f"【百度搜索结果】\n关键词：{input_text}\n时间：{get_time()}\n{'='*50}\n\n"
                valid = 0

                for result in soup.select(".result,c-container,div[tpl]"):
                    if valid >=10: break

                    try:
                        h3 = result.find("h3")
                        if not h3: continue
                        a = h3.find("a")
                        if not a: continue

                        # 去重
                        raw_link = a.get("href","")
                        if raw_link in saved_links:
                            continue
                        saved_links.add(raw_link)

                        title = clean_text(h3.get_text())
                        if len(title)<5 or "广告" in title:
                            continue

                        # 正确提取摘要
                        abstract = result.find("span", class_="content-right__1ZJmp") or result.find("div", class_="abstract-content")
                        if not abstract:
                            abstract = result.find("div", class_=lambda c: c and ("abstract" in str(c) or "content" in str(c)))

                        summary = clean_text(abstract.get_text()) if abstract else "无简介"
                        if len(summary) < 6 or "相关搜索" in summary:
                            continue

                        valid +=1
                        spider_content += f"📌 结果{valid}\n标题：{title}\n链接：{raw_link}\n摘要：{summary}\n{'-'*50}\n\n"

                    except:
                        continue

                if valid ==0:
                    spider_content+="未找到有效结果"

            text_status.insert(tk.END,f"[{get_time()}] ✅ 完成！\n")
            btn_save.config(state=tk.NORMAL)

        except Exception as e:
            text_status.insert(tk.END,f"错误：{str(e)}\n")
        finally:
            btn_start.config(state=tk.NORMAL)

    def save_file():
        if not spider_content:
            messagebox.showwarning("提示","无内容")
            return
        fmt = combo_fmt.get()
        fn = f"{spider_title}.{fmt}"
        with open(fn,"w",encoding="utf-8") as f:
            f.write(spider_content)
        messagebox.showinfo("成功",f"已保存：{fn}")

    # ====================== GUI ======================
    root = tk.Tk()
    root.title("搜索爬虫工具（纯净摘要版）")
    root.geometry("880x680")
    root.resizable(False,False)
    root.config(bg="#f8fafc")

    font_title = font.Font(family="微软雅黑",size=17,weight="bold")
    font_text = font.Font(family="微软雅黑",size=11)
    mode_dict = {"url":"网页","keyword":"关键词"}
    spider_mode = tk.StringVar(value="keyword")

    tk.Label(root,text="🔍 搜索爬虫工具（标题+链接+纯净摘要）",font=font_title,bg="#f8fafc").place(relx=0.5,rely=0.03,anchor="center")

    tk.Label(root,text="模式：",bg="#f8fafc",font=font_text).place(x=40,y=65)
    tk.Radiobutton(root,text="网页爬取",variable=spider_mode,value="url",bg="#f8fafc").place(x=100,y=65)
    tk.Radiobutton(root,text="关键词爬取",variable=spider_mode,value="keyword",bg="#f8fafc").place(x=210,y=65)

    tk.Label(root,text="输入：",bg="#f8fafc",font=font_text).place(x=40,y=105)
    entry_input = tk.Text(root,font=font_text,wrap="word",bd=0,relief=tk.FLAT,bg="white",padx=10,pady=8)
    entry_input.place(x=40,y=130,width=800,height=70)
    entry_input.insert("end","EAST")

    tk.Label(root,text="格式：",bg="#f8fafc",font=font_text).place(x=40,y=215)
    combo_fmt = ttk.Combobox(root,values=["txt","md"],state="readonly",font=font_text)
    combo_fmt.place(x=100,y=215,width=120)
    combo_fmt.current(0)

    tk.Label(root,text="日志：",bg="#f8fafc",font=font_text).place(x=40,y=255)
    text_status = tk.Text(root,font=font_text,wrap="word",bd=0,relief=tk.FLAT,bg="white",padx=10,pady=8)
    text_status.place(x=40,y=280,width=800,height=300)

    btn_start = RoundedButton(root,text="开始爬取",command=start_spider,bg="#059669")
    btn_start.place(x=330,y=620,anchor="center")
    btn_save = RoundedButton(root,text="保存文件",command=save_file,bg="#3b82f6")
    btn_save.place(x=550,y=620,anchor="center")
    btn_save.config(state=tk.DISABLED)

    root.mainloop()

if __name__=="__main__":
    run_spider_tool()