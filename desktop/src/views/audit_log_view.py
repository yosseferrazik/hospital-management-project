import threading
import tkinter as tk
from tkinter import ttk, messagebox

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class AuditLogView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.session = Session()
        self.api_client = APIClient(self.session)
        self._is_destroyed = False
        self.logs_data = []

        self.create_widgets()
        self.load_logs()

    def create_widgets(self):
        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)
        self.page.grid_rowconfigure(2, weight=1)
        self.page.grid_columnconfigure(0, weight=1)

        UIStyle.section_header(
            self.page,
            "Audit Logs",
            "Track all database changes recorded by the server.",
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 14))

        filter_shell, filter_inner = UIStyle.panel(self.page, padx=16, pady=12)
        filter_shell.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        filter_inner.columnconfigure(9, weight=1)

        tk.Label(filter_inner, text="Table:", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=0, column=0, padx=(0, 4))
        self.table_var = tk.StringVar()
        self.table_entry = ttk.Entry(filter_inner, textvariable=self.table_var, width=14, font=UIStyle.FONT)
        self.table_entry.grid(row=0, column=1, padx=(0, 12))

        tk.Label(filter_inner, text="Action:", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=0, column=2, padx=(0, 4))
        self.action_var = tk.StringVar()
        self.action_combo = ttk.Combobox(filter_inner, textvariable=self.action_var, values=["", "INSERT", "UPDATE", "DELETE"], width=10, font=UIStyle.FONT)
        self.action_combo.grid(row=0, column=3, padx=(0, 12))

        tk.Label(filter_inner, text="User ID:", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=0, column=4, padx=(0, 4))
        self.user_var = tk.StringVar()
        self.user_entry = ttk.Entry(filter_inner, textvariable=self.user_var, width=8, font=UIStyle.FONT)
        self.user_entry.grid(row=0, column=5, padx=(0, 12))

        tk.Label(filter_inner, text="From:", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=0, column=6, padx=(0, 4))
        self.start_var = tk.StringVar()
        self.start_entry = ttk.Entry(filter_inner, textvariable=self.start_var, width=12, font=UIStyle.FONT)
        self.start_entry.grid(row=0, column=7, padx=(0, 4))
        tk.Label(filter_inner, text="To:", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=0, column=8, padx=(0, 4))
        self.end_var = tk.StringVar()
        self.end_entry = ttk.Entry(filter_inner, textvariable=self.end_var, width=12, font=UIStyle.FONT)
        self.end_entry.grid(row=0, column=9, padx=(0, 8))

        UIStyle.filled_button(filter_inner, "Apply", self.apply_filters).grid(row=0, column=10, padx=(0, 6))
        UIStyle.secondary_button(filter_inner, "Clear", self.clear_filters).grid(row=0, column=11)

        table_shell, table_body = UIStyle.panel(self.page, padx=0, pady=0)
        table_shell.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        table_body.columnconfigure(0, weight=1)
        table_body.rowconfigure(0, weight=1)

        columns = ("log_id", "username", "timestamp", "action", "table", "record_id", "notes")
        self.tree = ttk.Treeview(table_body, columns=columns, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        headings = {"log_id": "ID", "username": "User", "timestamp": "Timestamp", "action": "Action", "table": "Table", "record_id": "Record", "notes": "Notes"}
        for col, heading in headings.items():
            self.tree.heading(col, text=heading)
            width = 60 if col == "log_id" else 80 if col == "record_id" else 120 if col in ("username", "action", "table") else 200
            self.tree.column(col, width=width, anchor="w")

        y_scroll = ttk.Scrollbar(table_body, orient="vertical", command=self.tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=12)
        self.tree.configure(yscrollcommand=y_scroll.set)

    def apply_filters(self):
        self.load_logs()

    def clear_filters(self):
        self.table_var.set("")
        self.action_var.set("")
        self.user_var.set("")
        self.start_var.set("")
        self.end_var.set("")
        self.load_logs()

    def load_logs(self):
        def worker():
            params = {}
            if self.table_var.get():
                params["table"] = self.table_var.get().strip()
            if self.action_var.get():
                params["action"] = self.action_var.get().strip()
            if self.user_var.get():
                params["user_id"] = self.user_var.get().strip()
            if self.start_var.get():
                params["start_date"] = self.start_var.get().strip()
            if self.end_var.get():
                params["end_date"] = self.end_var.get().strip()
            response, error = self.api_client.get_audit_logs(params=params)
            if self._is_destroyed:
                return
            self.page.after(0, lambda: self._display_logs(response, error))

        threading.Thread(target=worker, daemon=True).start()

    def _display_logs(self, response, error):
        if error:
            messagebox.showerror("Error", f"Failed to load audit logs: {error}")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        logs = response.get("logs", []) if response else []
        for log in logs:
            self.tree.insert("", "end", values=(
                log.get("log_id"),
                log.get("username"),
                log.get("timestamp", ""),
                log.get("action"),
                log.get("table"),
                log.get("record_id"),
                log.get("notes", ""),
            ))

    def destroy(self):
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
