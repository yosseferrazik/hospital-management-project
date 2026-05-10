import tkinter as tk
from tkinter import ttk, messagebox
from views.maintenance_view import MaintenanceView
from views.resource_browser import ResourceBrowser
from views.surgeries_view import SurgeriesView
from views.visits_view import VisitsView
from services.api_client import APIClient
from utils.session import Session


class MainMenu:
    BG = "#f0f2f5"
    CARD_BG = "#ffffff"
    SHADOW = "#d1d5db"
    ACCENT = "#2563eb"
    ACCENT_HOVER = "#1d4ed8"
    TEXT_DARK = "#1f2937"
    TEXT_LIGHT = "#6b7280"
    BORDER = "#d1d5db"
    HEADER_BG = "#1e293b"
    HEADER_TEXT = "#f8fafc"
    SUCCESS_GREEN = "#10b981"
    WARN_ORANGE = "#f59e0b"
    DANGER_RED = "#ef4444"
    CARD_WIDTH = 260
    CARD_HEIGHT = 260

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg=self.BG)
        self.frame.pack(fill="both", expand=True)

        self.style = ttk.Style(self.frame)
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=self.BG, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=self.CARD_BG,
            foreground=self.TEXT_DARK,
            padding=[20, 8],
            font=("Segoe UI", 11),
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.ACCENT), ("active", "#e2e8f0")],
            foreground=[("selected", "white")],
        )
        self.style.configure("TFrame", background=self.BG)

        self.create_widgets()

    def create_widgets(self):
        header_shadow = tk.Frame(self.frame, bg=self.SHADOW, height=100)
        header_shadow.pack(fill="x")
        header_shadow.pack_propagate(False)

        header = tk.Frame(header_shadow, bg=self.HEADER_BG)
        header.place(relwidth=1, relheight=1, y=-2)

        header_content = tk.Frame(header, bg=self.HEADER_BG)
        header_content.pack(fill="both", expand=True, padx=30, pady=18)

        title = tk.Label(
            header_content,
            text="Sa Palomera Hospital",
            font=("Segoe UI", 22, "bold"),
            bg=self.HEADER_BG,
            fg=self.HEADER_TEXT,
            anchor="w",
        )
        title.pack(side="left")

        user = Session().username or "User"
        user_label = tk.Label(
            header_content,
            text=f"👤  Welcome, {user}",
            font=("Segoe UI", 12),
            bg=self.HEADER_BG,
            fg="#cbd5e1",
            anchor="e",
        )
        user_label.pack(side="right")

        cards_area = tk.Frame(self.frame, bg=self.BG)
        cards_area.pack(expand=True, fill="both", padx=40, pady=(40, 20))

        section_title = tk.Label(
            cards_area,
            text="Management Menu",
            font=("Segoe UI", 16, "bold"),
            bg=self.BG,
            fg=self.TEXT_DARK,
            anchor="w",
        )
        section_title.pack(anchor="w", pady=(0, 20))

        grid = tk.Frame(cards_area, bg=self.BG)
        grid.pack(expand=True, fill="both")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        grid.rowconfigure(0, weight=1)
        grid.rowconfigure(1, weight=1)

        self._create_card(
            grid,
            row=0,
            col=0,
            icon="🔧",
            title="Maintenance",
            description="Register staff, patients and manage records.",
            bg_color=self.ACCENT,
            command=self.open_maintenance,
        )

        self._create_card(
            grid,
            row=0,
            col=1,
            icon="🗂",
            title="Hospital Data",
            description="Browse resources and manage backend records.",
            bg_color="#0f766e",
            command=self.open_resource_browser,
        )

        self._create_card(
            grid,
            row=1,
            col=0,
            icon="📊",
            title="Queries & Reports",
            description="View surgeries and visits by date.",
            bg_color="#7c3aed",
            command=self.open_consultations,
        )

        self._create_card(
            grid,
            row=1,
            col=1,
            icon="🧪",
            title="Test Data",
            description="Generate or cleanup dummy records.",
            bg_color=self.WARN_ORANGE,
            command=self.dummy_options,
        )

        logout_frame = tk.Frame(self.frame, bg=self.BG)
        logout_frame.pack(side="bottom", fill="x", pady=(0, 20))

        logout_btn = tk.Button(
            logout_frame,
            text="Logout",
            font=("Segoe UI", 11, "bold"),
            bg=self.CARD_BG,
            fg=self.DANGER_RED,
            activebackground="#fee2e2",
            activeforeground=self.DANGER_RED,
            relief="flat",
            borderwidth=0,
            highlightbackground=self.DANGER_RED,
            highlightthickness=1.5,
            padx=30,
            pady=8,
            cursor="hand2",
            command=self.logout,
        )
        logout_btn.pack()

    def _create_card(
        self,
        parent,
        row,
        col,
        icon,
        title,
        description,
        bg_color,
        command,
        state="normal",
    ):
        shadow = tk.Frame(
            parent,
            bg=self.SHADOW,
            width=self.CARD_WIDTH + 8,
            height=self.CARD_HEIGHT + 8,
        )
        shadow.grid(row=row, column=col, padx=15, pady=15, sticky="")
        shadow.grid_propagate(False)

        card = tk.Frame(
            shadow, bg=self.CARD_BG, width=self.CARD_WIDTH, height=self.CARD_HEIGHT
        )
        card.place(relx=0.5, rely=0.5, anchor="center", x=-2, y=-3)
        card.pack_propagate(False)

        inner = tk.Frame(card, bg=self.CARD_BG)
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        icon_label = tk.Label(
            inner, text=icon, font=("Segoe UI", 28), bg=self.CARD_BG, fg=bg_color
        )
        icon_label.pack(anchor="w")

        tk.Label(
            inner,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=self.CARD_BG,
            fg=self.TEXT_DARK,
            anchor="w",
        ).pack(anchor="w", pady=(10, 4))

        tk.Label(
            inner,
            text=description,
            font=("Segoe UI", 10),
            bg=self.CARD_BG,
            fg=self.TEXT_LIGHT,
            anchor="w",
            wraplength=200,
            justify="left",
        ).pack(anchor="w", fill="x", expand=True)

        if state == "disabled":
            card.config(cursor="")
            return

        btn_frame = tk.Frame(inner, bg=self.CARD_BG)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        open_btn = tk.Button(
            btn_frame,
            text="Open →",
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg="white",
            activebackground=self._darken_color(bg_color),
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=14,
            pady=5,
            cursor="hand2",
            command=command,
        )
        open_btn.pack(side="right")

    def _darken_color(self, hex_color):
        r, g, b = (
            int(hex_color[1:3], 16),
            int(hex_color[3:5], 16),
            int(hex_color[5:7], 16),
        )
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f"#{r:02x}{g:02x}{b:02x}"

    def open_maintenance(self):
        window = tk.Toplevel(self.parent)
        window.title("Maintenance Management")
        window.geometry("800x600")
        window.configure(bg=self.BG)
        MaintenanceView(window, self.app)

    def open_consultations(self):
        window = tk.Toplevel(self.parent)
        window.title("Queries and Reports")
        window.geometry("900x600")
        window.configure(bg=self.BG)

        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        surgeries_frame = ttk.Frame(notebook)
        visits_frame = ttk.Frame(notebook)

        notebook.add(surgeries_frame, text="Surgeries by Day")
        notebook.add(visits_frame, text="Visits by Day")

        SurgeriesView(surgeries_frame, self.app)
        VisitsView(visits_frame, self.app)

    def dummy_options(self):
        choice = messagebox.askquestion(
            "Test Data",
            "Choose Yes to generate dummy data, No to cleanup existing dummy data.",
            icon="question",
        )
        if choice == "yes":
            self.generate_dummy()
        else:
            self.cleanup_dummy()

    def generate_dummy(self):
        client = APIClient(Session())
        response, error = client.generate_dummy()

        if error:
            messagebox.showerror("Error", f"Failed to generate: {error}")
        else:
            messagebox.showinfo("Success", "Test data generated successfully")

    def cleanup_dummy(self):
        confirmed = messagebox.askyesno(
            "Cleanup Test Data",
            "Remove previously generated dummy records from the database?",
        )
        if not confirmed:
            return

        client = APIClient(Session())
        _, error = client.cleanup_dummy()
        if error:
            messagebox.showerror("Error", f"Failed to cleanup: {error}")
        else:
            messagebox.showinfo("Success", "Dummy records cleaned successfully")

    def open_resource_browser(self):
        window = tk.Toplevel(self.parent)
        window.title("Hospital Resource Explorer")
        window.geometry("1100x700")
        window.configure(bg=self.BG)
        ResourceBrowser(window, self.app)

    def logout(self):
        Session().clear()
        self.destroy()
        self.app.show_login()

    def destroy(self):
        self.frame.destroy()
