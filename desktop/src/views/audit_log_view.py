import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class AuditLogView:
    PER_PAGE = 50

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.session = Session()
        self.api_client = APIClient(self.session)
        self._is_destroyed = False
        self._current_page = 1
        self._total = 0
        self._loading = False

        self.create_widgets()
        self.page.after(100, self._initial_load)

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

        filter_shell, filter_inner = UIStyle.panel(self.page, padx=16, pady=10)
        filter_shell.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        filter_inner.columnconfigure(9, weight=1)

        row = 0

        tk.Label(filter_inner, text="Table", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=row, column=0, padx=(0, 4), pady=2)
        self.table_var = tk.StringVar()
        ttk.Entry(filter_inner, textvariable=self.table_var, width=14, font=UIStyle.FONT).grid(row=row, column=1, padx=(0, 10), pady=2)

        tk.Label(filter_inner, text="Action", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=row, column=2, padx=(0, 4), pady=2)
        self.action_var = tk.StringVar()
        ttk.Combobox(filter_inner, textvariable=self.action_var, values=["", "INSERT", "UPDATE", "DELETE"], width=10, font=UIStyle.FONT).grid(row=row, column=3, padx=(0, 10), pady=2)

        tk.Label(filter_inner, text="User", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=row, column=4, padx=(0, 4), pady=2)
        self.user_var = tk.StringVar()
        ttk.Entry(filter_inner, textvariable=self.user_var, width=8, font=UIStyle.FONT).grid(row=row, column=5, padx=(0, 10), pady=2)

        tk.Label(filter_inner, text="From", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=row, column=6, padx=(0, 4), pady=2)
        self.start_var = tk.StringVar()
        ttk.Entry(filter_inner, textvariable=self.start_var, width=12, font=UIStyle.FONT).grid(row=row, column=7, padx=(0, 4), pady=2)
        tk.Label(filter_inner, text="To", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).grid(row=row, column=8, padx=(0, 4), pady=2)
        self.end_var = tk.StringVar()
        ttk.Entry(filter_inner, textvariable=self.end_var, width=12, font=UIStyle.FONT).grid(row=row, column=9, padx=(0, 6), pady=2)

        UIStyle.filled_button(filter_inner, "Apply", self.apply_filters).grid(row=row, column=10, padx=(0, 4), pady=2)
        UIStyle.secondary_button(filter_inner, "Clear", self.clear_filters).grid(row=row, column=11, pady=2)
        UIStyle.secondary_button(filter_inner, "Refresh", self.refresh).grid(row=row, column=12, padx=(6, 0), pady=2)

        table_shell, table_body = UIStyle.panel(self.page, padx=0, pady=0)
        table_shell.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 8))
        table_body.columnconfigure(0, weight=1)
        table_body.rowconfigure(0, weight=1)

        columns = ("timestamp", "username", "action", "table", "record_id", "notes")
        self.tree = ttk.Treeview(table_body, columns=columns, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        col_config = {
            "timestamp": ("Timestamp", 160),
            "username": ("User", 110),
            "action": ("Action", 80),
            "table": ("Table", 120),
            "record_id": ("Record", 70),
            "notes": ("Notes", 200),
        }
        for col, (heading, width) in col_config.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor="w", minwidth=60)

        y_scroll = ttk.Scrollbar(table_body, orient="vertical", command=self.tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=8)
        self.tree.configure(yscrollcommand=y_scroll.set)

        footer_shell, footer_body = UIStyle.panel(self.page, padx=16, pady=8)
        footer_shell.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 24))
        footer_body.columnconfigure(0, weight=1)

        self.total_label = tk.Label(footer_body, text="", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT)
        self.total_label.grid(row=0, column=0, sticky="w")

        self.retention_label = tk.Label(footer_body, text="", font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT)
        self.retention_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        nav_frame = tk.Frame(footer_body, bg=UIStyle.CARD_BG)
        nav_frame.grid(row=0, column=2, sticky="e")

        self.page_btn_frame = tk.Frame(nav_frame, bg=UIStyle.CARD_BG)
        self.page_btn_frame.pack(side="left")

        self.purge_btn = UIStyle.danger_button(nav_frame, "Purge Old Logs", self.purge_old_logs)
        self.purge_btn.pack(side="left", padx=(12, 0))

    def _rebuild_page_nav(self):
        for widget in self.page_btn_frame.winfo_children():
            widget.destroy()
        total_pages = max(1, (self._total + self.PER_PAGE - 1) // self.PER_PAGE)

        max_visible = 7
        half = max_visible // 2
        if total_pages <= max_visible:
            start_page, end_page = 1, total_pages
        elif self._current_page <= half + 1:
            start_page, end_page = 1, max_visible
        elif self._current_page >= total_pages - half:
            start_page, end_page = total_pages - max_visible + 1, total_pages
        else:
            start_page = self._current_page - half
            end_page = self._current_page + half

        def go_page(p):
            self._current_page = p
            self.load_logs()

        if self._current_page > 1:
            btn = UIStyle.secondary_button(self.page_btn_frame, "\u00ab", lambda: go_page(1))
            btn.pack(side="left", padx=1)
            btn = UIStyle.secondary_button(self.page_btn_frame, "\u2039", lambda: go_page(self._current_page - 1))
            btn.pack(side="left", padx=1)

        for p in range(start_page, end_page + 1):
            if p == self._current_page:
                btn = tk.Button(
                    self.page_btn_frame,
                    text=str(p),
                    font=UIStyle.FONT_BOLD,
                    bg=UIStyle.ACCENT,
                    fg="white",
                    relief="flat",
                    padx=10, pady=4,
                    cursor="hand2",
                )
            else:
                btn = UIStyle.secondary_button(self.page_btn_frame, str(p), lambda p=p: go_page(p))
            btn.pack(side="left", padx=1)

        if self._current_page < total_pages:
            btn = UIStyle.secondary_button(self.page_btn_frame, "\u203a", lambda: go_page(self._current_page + 1))
            btn.pack(side="left", padx=1)
            btn = UIStyle.secondary_button(self.page_btn_frame, "\u00bb", lambda: go_page(total_pages))
            btn.pack(side="left", padx=1)

    def _update_pagination(self):
        self.total_label.config(text=f"Total: {self._total}")
        self._rebuild_page_nav()

    def apply_filters(self):
        self._current_page = 1
        self.load_logs()

    def clear_filters(self):
        self.table_var.set("")
        self.action_var.set("")
        self.user_var.set("")
        self.start_var.set("")
        self.end_var.set("")
        self._current_page = 1
        self.load_logs()

    def refresh(self):
        self.load_logs()
        self.load_retention()
        self.load_diagnostics()

    def load_retention(self):
        def worker():
            try:
                data, error = self.api_client.get_audit_retention()
                if not error and data:
                    self.parent.after(0, lambda: self._display_retention(data))
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _display_retention(self, data):
        total = data.get("total_logs", 0)
        days = data.get("retention_days", 90)
        oldest = data.get("oldest", "N/A") or "N/A"
        newest = data.get("newest", "N/A") or "N/A"
        if oldest != "N/A":
            oldest = oldest[:10]
        if newest != "N/A":
            newest = newest[:10]
        self.retention_label.config(text=f"Retention: {days}d | Range: {oldest} ~ {newest}")

    def load_logs(self):
        if self._loading:
            return
        self._loading = True
        self.total_label.config(text="Loading...")
        self.page.update_idletasks()

        params = {"page": self._current_page, "per_page": self.PER_PAGE}
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

        def worker(p):
            try:
                response, error = self.api_client.get_audit_logs(params=p)
            except Exception as e:
                response, error = None, str(e)
            if self._is_destroyed:
                return
            self.page.after(0, lambda: self._display_logs(response, error))

        threading.Thread(target=worker, args=(params,), daemon=True).start()

    def _initial_load(self):
        self.load_diagnostics()
        self.load_retention()
        self.load_logs()

    def load_diagnostics(self):
        def worker():
            try:
                data, error = self.api_client.get_audit_diagnostics()
                if not error and data and not self._is_destroyed:
                    self.page.after(0, lambda: self._display_diagnostics(data))
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _display_diagnostics(self, data):
        msg = data.get("message", "")
        total = data.get("total_logs", 0)
        has_triggers = data.get("triggers_installed", False)
        if total == 0 and msg:
            self.total_label.config(text=f"Diagnostic: {msg}")
            self.total_label.config(fg=UIStyle.WARNING_ORANGE)
            if not has_triggers:
                self.purge_btn.config(state="disabled")
        else:
            self.total_label.config(fg=UIStyle.TEXT_LIGHT)

    def _display_logs(self, response, error):
        self._loading = False
        if error:
            self.total_label.config(text=f"Error: {error}")
            self.total_label.config(fg=UIStyle.ERROR_RED)
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        logs = response.get("logs", []) if response else []
        self._total = response.get("total", 0) if response else 0

        for log in logs:
            ts = log.get("timestamp", "")
            if ts and len(ts) > 19:
                ts = ts[:19].replace("T", " ")
            self.tree.insert("", "end", values=(
                ts,
                log.get("username"),
                log.get("action"),
                log.get("table"),
                log.get("record_id"),
                log.get("notes", ""),
            ))

        self._update_pagination()

    def purge_old_logs(self):
        if self.session.role != "ADMIN":
            messagebox.showerror("Access Denied", "Only administrators can purge audit logs.")
            return
        days = simpledialog.askinteger(
            "Purge Audit Logs",
            "Delete logs older than how many days?\n(minimum 1, maximum 3650)",
            parent=self.page,
            minvalue=1, maxvalue=3650, initialvalue=90,
        )
        if days is None:
            return
        if not messagebox.askyesno("Confirm Purge", f"Delete all audit logs older than {days} days?\nThis action cannot be undone."):
            return

        def worker():
            try:
                data, error = self.api_client.cleanup_audit_logs(days=days)
                if self._is_destroyed:
                    return
                if error:
                    self.page.after(0, lambda: messagebox.showerror("Error", f"Purge failed: {error}"))
                else:
                    self.page.after(0, lambda: self._purge_done(data.get("deleted", 0)))
            except Exception as e:
                self.page.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def _purge_done(self, deleted):
        messagebox.showinfo("Purge Complete", f"Deleted {deleted} old audit log(s).")
        self.load_logs()
        self.load_retention()

    def destroy(self):
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
