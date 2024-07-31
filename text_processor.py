import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, font
from PIL import Image, ImageTk
import webbrowser
import keyboard

class TextProcessor:
    def __init__(self, master):
        self.master = master
        master.title("Текстовый процессор")


        self.default_font = font.Font(family="Arial", size=13)

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, font=self.default_font)
        self.text_area.pack(expand=True, fill="both")

        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Новый", command=self.new_file)
        filemenu.add_separator()
        filemenu.add_command(label="Выход", command=master.quit)
        menubar.add_cascade(label="Файл", menu=filemenu)



        formatmenu = tk.Menu(menubar, tearoff=0)
        formatmenu.add_command(label="Жирный", command=self.bold_text)
        formatmenu.add_command(label="Курсив", command=self.italic_text)
        formatmenu.add_command(label="Подчеркивание", command=self.underline_text)
        formatmenu.add_separator()
        self.font_var = tk.StringVar(value="Arial")
        fontmenu = tk.Menu(formatmenu, tearoff=0)
        for f in font.families():
            fontmenu.add_radiobutton(label=f, variable=self.font_var,
                                    command=self.change_font)
        formatmenu.add_cascade(label="Шрифт", menu=fontmenu)
        self.size_var = tk.IntVar(value=12)
        sizemenu = tk.Menu(formatmenu, tearoff=0)
        for s in range(8, 32, 2):
            sizemenu.add_radiobutton(label=str(s), variable=self.size_var,
                                    command=self.change_font_size)
        formatmenu.add_cascade(label="Размер", menu=sizemenu)
        menubar.add_cascade(label="Формат", menu=formatmenu)

        insertmenu = tk.Menu(menubar, tearoff=0)
        insertmenu.add_command(label="Вставить изображение", command=self.insert_image)
        insertmenu.add_command(label="Вставить ссылку", command=self.insert_link)
        menubar.add_cascade(label="Вставка", menu=insertmenu)

        master.config(menu=menubar)

        keyboard.add_hotkey("ctrl+c", self.copy)
        keyboard.add_hotkey("ctrl+v", self.paste)
        keyboard.add_hotkey("ctrl+x", self.cut)
        keyboard.add_hotkey("ctrl+z", self.undo)

        self.pages = []


        self.page_number = 1
        self.lines_per_page = 40
        self.update_pages()


        self.page_label = tk.Label(master, text=f"Страница {self.page_number}", font=("Arial", 10))
        self.page_label.pack(side="bottom")


        self.current_line = 0

    def update_pages(self):

        self.pages = [[" " for _ in range(self.lines_per_page)]
                      for _ in range(10)]

        self.page_number = 1

    def update_page_numbers(self):

        current_line = int(self.text_area.yview()[0] * self.lines_per_page)
        self.current_line = current_line


        page_number = current_line // self.lines_per_page + 1
        self.page_label.config(text=f"Страница {page_number}")


    def new_file(self):
        if tk.messagebox.askokcancel("Новый файл", "Создать новый файл?"):
            self.text_area.delete("1.0", tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert("1.0", file.read())
            except FileNotFoundError:
                tk.messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")

    def copy(self):
        try:
            self.text_area.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def paste(self):
        self.text_area.event_generate("<<Paste>>")

    def cut(self):
        try:
            self.text_area.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def undo(self):
        self.text_area.event_generate("<<Undo>>")



    def apply_format(self, tag, font_style=None):
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                if font_style:
                    self.text_area.tag_add(tag, tk.SEL_FIRST, tk.SEL_LAST)
                    self.text_area.tag_config(tag, font=font_style)
                else:
                    self.text_area.tag_add(tag, tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass    

    def bold_text(self):
        self.apply_format("bold", font.Font(weight="bold"))

    def italic_text(self):
        self.apply_format("italic", font.Font(slant="italic"))

    def underline_text(self):
        self.apply_format("underline", font.Font(underline=1))

    def change_font(self):
        font_style = font.Font(family=self.font_var.get(), size=self.size_var.get())
        self.apply_format("font", font_style)

    def change_font_size(self):
        font_style = font.Font(family=self.font_var.get(), size=self.size_var.get())
        self.apply_format("font", font_style)

    def insert_image(self):
        image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")]
        )
        if image_path:
            try:
                image = Image.open(image_path)
                image.thumbnail((250, 250))
                photo = ImageTk.PhotoImage(image)
                self.text_area.image_create(tk.END, image=photo)
                self.text_area.image = photo
            except FileNotFoundError:
                tk.messagebox.showerror("Ошибка", f"Изображение не найдено: {image_path}")

    def insert_link(self):
        link = tk.simpledialog.askstring("Вставить ссылку", "Введите URL:")
        if link:
            self.text_area.insert(tk.END, link)
            self.text_area.tag_add("link", "insert -%dc" % len(link), tk.INSERT)
            self.text_area.tag_config("link", foreground="blue", underline=True)
            self.text_area.tag_bind("link", "<Button-1>", self.open_link)

    def open_link(self, event):
        start_index = self.text_area.tag_prevrange("link", event.charpos)[1]
        end_index = self.text_area.tag_nextrange("link", event.charpos)[0]
        url = self.text_area.get(start_index, end_index)
        webbrowser.open_new(url)

root = tk.Tk()
text_processor = TextProcessor(root)
root.mainloop()
