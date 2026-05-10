import tkinter as tk
from tkinter import ttk


class UIStyle:
    BG = "#edf3f8"
    SURFACE = "#f7fafc"
    CARD_BG = "#ffffff"
    CARD_ALT = "#f4f8fc"
    HEADER_BG = "#132238"
    HEADER_BG_ALT = "#203552"
    HEADER_TEXT = "#f8fafc"
    ACCENT = "#0f6cbd"
    ACCENT_HOVER = "#0b5a9e"
    ACCENT_SOFT = "#d9eaf8"
    TEXT = "#243447"
    TEXT_DARK = "#102033"
    TEXT_LIGHT = "#63758a"
    BORDER = "#d7e2ed"
    BORDER_STRONG = "#bfd2e2"
    DANGER = "#c2410c"
    DANGER_HOVER = "#9a3412"
    ERROR_RED = "#dc2626"
    SUCCESS_GREEN = "#059669"
    WARNING_ORANGE = "#d97706"

    FONT = ("Segoe UI", 11)
    FONT_BOLD = ("Segoe UI Semibold", 11)
    SMALL_FONT = ("Segoe UI", 10)
    HEADER_FONT = ("Segoe UI Semibold", 24)
    TITLE_FONT = ("Segoe UI Semibold", 18)
    SUBTITLE_FONT = ("Segoe UI", 11)
    CARD_TITLE = ("Segoe UI Semibold", 13)
    CARD_VALUE = ("Segoe UI Semibold", 24)
    MONO_FONT = ("Consolas", 10)

    @classmethod
    def configure_ttk(cls, root):
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background=cls.BG)
        style.configure(
            "TLabel", background=cls.BG, foreground=cls.TEXT_DARK, font=cls.FONT
        )
        style.configure("TNotebook", background=cls.BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            font=cls.FONT_BOLD,
            padding=(16, 10),
            background=cls.SURFACE,
            foreground=cls.TEXT_DARK,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", cls.CARD_BG)],
            foreground=[("selected", cls.TEXT_DARK)],
        )
        style.configure(
            "Treeview",
            background=cls.CARD_BG,
            fieldbackground=cls.CARD_BG,
            foreground=cls.TEXT_DARK,
            rowheight=30,
            bordercolor=cls.BORDER,
            lightcolor=cls.BORDER,
            darkcolor=cls.BORDER,
        )
        style.configure(
            "Treeview.Heading",
            background=cls.SURFACE,
            foreground=cls.TEXT_DARK,
            font=cls.FONT_BOLD,
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", cls.ACCENT_SOFT)],
            foreground=[("selected", cls.TEXT_DARK)],
        )
        style.configure(
            "TScrollbar",
            background=cls.SURFACE,
            troughcolor=cls.BG,
            bordercolor=cls.BORDER,
            arrowcolor=cls.TEXT_LIGHT,
        )
        style.configure(
            "TProgressbar",
            troughcolor=cls.SURFACE,
            background=cls.ACCENT,
            bordercolor=cls.BORDER,
        )
        style.configure(
            "TCheckbutton",
            background=cls.CARD_BG,
            foreground=cls.TEXT_DARK,
            font=cls.FONT,
        )
        style.configure(
            "TCombobox",
            fieldbackground=cls.CARD_BG,
            foreground=cls.TEXT_DARK,
            bordercolor=cls.BORDER,
            arrowcolor=cls.TEXT_DARK,
            padding=6,
        )
        style.configure(
            "TSpinbox",
            fieldbackground=cls.CARD_BG,
            foreground=cls.TEXT_DARK,
            bordercolor=cls.BORDER,
            arrowsize=12,
            padding=4,
        )
        return style

    @classmethod
    def page(cls, parent):
        page = tk.Frame(parent, bg=cls.BG)
        page.pack(fill="both", expand=True)
        return page

    @classmethod
    def panel(cls, parent, *, bg=None, padx=20, pady=18):
        frame = tk.Frame(
            parent,
            bg=bg or cls.CARD_BG,
            highlightbackground=cls.BORDER,
            highlightthickness=1,
        )
        inner = tk.Frame(frame, bg=bg or cls.CARD_BG)
        inner.pack(fill="both", expand=True, padx=padx, pady=pady)
        return frame, inner

    @classmethod
    def section_header(cls, parent, title, subtitle=None, *, padx=24, pady=(24, 14)):
        header = tk.Frame(parent, bg=cls.BG)
        header.pack(fill="x", padx=padx, pady=pady)
        tk.Label(
            header, text=title, font=cls.TITLE_FONT, bg=cls.BG, fg=cls.TEXT_DARK
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                header,
                text=subtitle,
                font=cls.SUBTITLE_FONT,
                bg=cls.BG,
                fg=cls.TEXT_LIGHT,
            ).pack(anchor="w", pady=(4, 0))
        return header

    @classmethod
    def create_scrollable_area(cls, parent, *, bg=None):
        bg_color = bg or cls.BG

        outer = tk.Frame(parent, bg=bg_color)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=bg_color, highlightthickness=0, bd=0, height=400)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)

        content = tk.Frame(canvas, bg=bg_color)
        content_window = canvas.create_window((0, 0), window=content, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        def on_content_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(content_window, width=canvas.winfo_width())

        def on_canvas_configure(event=None):
            canvas.itemconfig(content_window, width=event.width)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                canvas.yview_scroll(3, "units")

        def on_enter(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            canvas.bind_all("<Button-4>", on_mousewheel_linux)
            canvas.bind_all("<Button-5>", on_mousewheel_linux)

        def on_leave(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        content.bind("<Configure>", on_content_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return outer, content

    @classmethod
    def stat_card(cls, parent, title, subtitle=""):
        shell, body = cls.panel(parent, bg=cls.CARD_BG, padx=18, pady=18)
        tk.Label(
            body, text=title, font=cls.CARD_TITLE, bg=cls.CARD_BG, fg=cls.TEXT_DARK
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                body,
                text=subtitle,
                font=cls.SUBTITLE_FONT,
                bg=cls.CARD_BG,
                fg=cls.TEXT_LIGHT,
            ).pack(anchor="w", pady=(4, 16))
        return shell, body

    @classmethod
    def filled_button(cls, parent, text, command, *, width=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=cls.FONT_BOLD,
            bg=cls.ACCENT,
            fg="white",
            activebackground=cls.ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=16,
            pady=10,
            width=width,
        )

    @classmethod
    def secondary_button(cls, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=cls.FONT,
            bg=cls.CARD_BG,
            fg=cls.TEXT_DARK,
            activebackground=cls.SURFACE,
            activeforeground=cls.TEXT_DARK,
            relief="flat",
            highlightbackground=cls.BORDER,
            highlightthickness=1,
            borderwidth=0,
            cursor="hand2",
            padx=16,
            pady=10,
        )

    @classmethod
    def danger_button(cls, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=cls.FONT_BOLD,
            bg=cls.DANGER,
            fg="white",
            activebackground=cls.DANGER_HOVER,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=16,
            pady=10,
        )

    @classmethod
    def form_entry(cls, parent):
        return tk.Entry(
            parent,
            font=cls.FONT,
            bg=cls.CARD_BG,
            fg=cls.TEXT_DARK,
            relief="flat",
            highlightthickness=1,
            highlightbackground=cls.BORDER,
            highlightcolor=cls.ACCENT,
            insertbackground=cls.TEXT_DARK,
        )

    @classmethod
    def form_text(cls, parent, *, height=4):
        return tk.Text(
            parent,
            height=height,
            font=cls.FONT,
            bg=cls.CARD_BG,
            fg=cls.TEXT_DARK,
            relief="flat",
            highlightthickness=1,
            highlightbackground=cls.BORDER,
            highlightcolor=cls.ACCENT,
            insertbackground=cls.TEXT_DARK,
            padx=8,
            pady=8,
        )
