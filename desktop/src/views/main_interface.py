import threading
import tkinter as tk
from tkinter import messagebox

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle
from views.dashboard_view import DashboardView
from views.maintenance_view import MaintenanceView
from views.queries_reports_view import QueriesReportsView
from views.resource_browser import ResourceBrowser
from views.test_data_view import TestDataView
from views.statistics_view import StatisticsView
from views.user_management_view import UserManagementView
from views.audit_log_view import AuditLogView


class MainInterface:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.session = Session()
        self.current_view = None
        self.current_section = None
        self._is_destroyed = False

        self.create_widgets()
        self.navigate("dashboard")

    def create_widgets(self):
        self.frame = tk.Frame(self.parent, bg=UIStyle.BG)
        self.frame.pack(fill="both", expand=True)
        UIStyle.configure_ttk(self.frame)

        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(self.frame, bg=UIStyle.HEADER_BG, width=270)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        header = tk.Frame(self.sidebar, bg=UIStyle.HEADER_BG)
        header.pack(fill="x", padx=20, pady=(24, 20))
        tk.Label(
            header,
            text="Sa Palomera",
            font=UIStyle.HEADER_FONT,
            bg=UIStyle.HEADER_BG,
            fg=UIStyle.HEADER_TEXT,
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Hospital management workspace",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.HEADER_BG,
            fg="#bfd2e2",
        ).pack(anchor="w", pady=(4, 0))

        nav_group = tk.Frame(self.sidebar, bg=UIStyle.HEADER_BG)
        nav_group.pack(fill="x", padx=12, pady=(8, 0))

        base_items = [
            ("Dashboard", "dashboard"),
            ("Maintenance", "maintenance"),
            ("Data Workspace", "data"),
            ("Operational Reports", "queries"),
            ("Statistics", "statistics"),
            ("Dummy Data", "test"),
        ]
        admin_items = [
            ("Users", "users"),
            ("Audit Logs", "audit"),
        ]

        self.nav_buttons = {}
        for text, key in base_items:
            self._add_nav_button(nav_group, text, key)
        if self.session.role == "ADMIN":
            sep = tk.Frame(nav_group, bg="#2a4a6a", height=1)
            sep.pack(fill="x", pady=8)
            for text, key in admin_items:
                self._add_nav_button(nav_group, text, key, admin=True)

        footer = tk.Frame(self.sidebar, bg=UIStyle.HEADER_BG)
        footer.pack(side="bottom", fill="x", padx=12, pady=18)
        info = f"User: {self.session.username or 'User'} | {self.session.role or 'N/A'}"
        tk.Label(
            footer,
            text=info,
            font=UIStyle.SMALL_FONT,
            bg=UIStyle.HEADER_BG,
            fg="#bfd2e2",
            anchor="w",
        ).pack(fill="x", pady=(0, 6))
        btn_row = tk.Frame(footer, bg=UIStyle.HEADER_BG)
        btn_row.pack(fill="x", pady=(6, 0))
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, weight=1)
        UIStyle.secondary_button(btn_row, "Change Password", self._change_password).grid(row=0, column=0, sticky="ew", padx=(0, 3))
        UIStyle.danger_button(btn_row, "Logout", self.logout).grid(row=0, column=1, sticky="ew", padx=(3, 0))

    def _add_nav_button(self, parent, text, key, admin=False):
        fg_color = "#fbbf24" if admin else UIStyle.HEADER_TEXT
        button = tk.Button(
            parent,
            text=text,
            font=UIStyle.FONT,
            bg=UIStyle.HEADER_BG,
            fg=fg_color,
            activebackground=UIStyle.HEADER_BG_ALT,
            activeforeground=fg_color,
            relief="flat",
            anchor="w",
            padx=18,
            pady=12,
            cursor="hand2",
            command=lambda value=key: self.navigate(value),
        )
        button.pack(fill="x", pady=3)
        self.nav_buttons[key] = button

        topbar = tk.Frame(
            self.frame,
            bg=UIStyle.SURFACE,
            highlightbackground=UIStyle.BORDER,
            highlightthickness=1,
        )
        topbar.grid(row=0, column=1, sticky="ew", padx=(0, 0), pady=(0, 0))
        topbar.columnconfigure(0, weight=1)
        self.title_var = tk.StringVar(value="Dashboard")
        self.subtitle_var = tk.StringVar(value="Overview")
        tk.Label(
            topbar,
            textvariable=self.title_var,
            font=UIStyle.TITLE_FONT,
            bg=UIStyle.SURFACE,
            fg=UIStyle.TEXT_DARK,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(16, 2))
        tk.Label(
            topbar,
            textvariable=self.subtitle_var,
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.SURFACE,
            fg=UIStyle.TEXT_LIGHT,
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 16))

        self.content = tk.Frame(self.frame, bg=UIStyle.BG)
        self.content.grid(row=1, column=1, sticky="nsew")

    def navigate(self, section):
        if self.current_section == section:
            return

        self.current_section = section
        config = {
            "dashboard": (
                "Dashboard",
                "Overview of hospital capacity and today's agenda",
                DashboardView,
            ),
            "maintenance": (
                "Maintenance",
                "Specialized registration and assignment workflows",
                MaintenanceView,
            ),
            "data": (
                "Data Workspace",
                "CRUD access to operational database resources",
                ResourceBrowser,
            ),
            "queries": (
                "Operational Reports",
                "Visits and surgeries by date using reporting endpoints",
                QueriesReportsView,
            ),
            "statistics": (
                "Statistics",
                "Hospital operational insights and performance metrics",
                StatisticsView,
            ),
            "test": (
                "Dummy Data",
                "Generate and clean sample records safely",
                TestDataView,
            ),
            "users": (
                "User Management",
                "Create and manage system accounts",
                UserManagementView,
            ),
            "audit": (
                "Audit Logs",
                "View database change logs",
                AuditLogView,
            ),
        }

        for key, button in self.nav_buttons.items():
            button.config(
                bg=UIStyle.HEADER_BG_ALT if key == section else UIStyle.HEADER_BG
            )

        title, subtitle, view_class = config[section]
        self.title_var.set(title)
        self.subtitle_var.set(subtitle)
        self._switch_view(view_class)

    def _switch_view(self, view_class):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        self.current_view = view_class(self.content, self.app)

    def _change_password(self):
        from tkinter import simpledialog
        old = simpledialog.askstring("Change Password", "Current password:", parent=self.frame, show="*")
        if not old:
            return
        new = simpledialog.askstring("Change Password", "New password:", parent=self.frame, show="*")
        if not new:
            return
        confirm = simpledialog.askstring("Change Password", "Confirm new password:", parent=self.frame, show="*")
        if new != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        def worker():
            client = APIClient(self.session)
            response, error = client.change_own_password(old, new)
            self.frame.after(0, lambda: self._finish_change_pw(response, error))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_change_pw(self, response, error):
        if error:
            messagebox.showerror("Error", f"Failed to change password: {error}")
            return
        messagebox.showinfo("Success", "Password changed successfully")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.session.clear()
            self.app.show_login()

    def destroy(self):
        if self._is_destroyed:
            return
        self._is_destroyed = True
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        if hasattr(self, "frame") and self.frame.winfo_exists():
            self.frame.destroy()
