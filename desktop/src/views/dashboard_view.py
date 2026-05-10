import threading
import tkinter as tk
from datetime import date
from tkinter import ttk

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class DashboardView:
    STAT_CARDS = [
        ("Patients", "/patients"),
        ("Staff", "/staff"),
        ("Rooms", "/rooms"),
        ("Visits", "/visits"),
    ]

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.session = Session()
        self.api_client = APIClient(self.session)
        self.value_labels = {}
        self._is_destroyed = False

        self.create_widgets()
        self.page.after(60, self.load_dashboard)

    def create_widgets(self):
        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)

        UIStyle.section_header(
            self.page,
            "Operations Dashboard",
            "A full-screen command overview with quick insight into capacity and today's clinical schedule.",
        )

        stats = tk.Frame(self.page, bg=UIStyle.BG)
        stats.pack(fill="x", padx=24, pady=(0, 14))
        for column in range(len(self.STAT_CARDS)):
            stats.grid_columnconfigure(column, weight=1)

        for column, (title, _endpoint) in enumerate(self.STAT_CARDS):
            shell, body = UIStyle.stat_card(stats, title, "Current records")
            shell.grid(row=0, column=column, sticky="nsew", padx=8)
            value = tk.Label(
                body,
                text="Loading...",
                font=UIStyle.CARD_VALUE,
                bg=UIStyle.CARD_BG,
                fg=UIStyle.ACCENT,
            )
            value.pack(anchor="w")
            self.value_labels[column] = value

        body = tk.Frame(self.page, bg=UIStyle.BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self.visits_shell, visits_body = UIStyle.panel(body, padx=18, pady=18)
        self.visits_shell.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(
            visits_body,
            text="Today's Scheduled Visits",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w")
        tk.Label(
            visits_body,
            text=date.today().isoformat(),
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(anchor="w", pady=(4, 12))
        self.visits_tree = self._build_tree(
            visits_body,
            [
                ("time", "Time"),
                ("patient", "Patient"),
                ("doctor", "Doctor"),
                ("status", "Status"),
            ],
        )

        self.surgeries_shell, surgeries_body = UIStyle.panel(body, padx=18, pady=18)
        self.surgeries_shell.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(
            surgeries_body,
            text="Today's Surgeries",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w")
        tk.Label(
            surgeries_body,
            text="Theater usage and assigned medical staff.",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(anchor="w", pady=(4, 12))
        self.surgeries_tree = self._build_tree(
            surgeries_body,
            [
                ("start_time", "Start"),
                ("patient", "Patient"),
                ("surgeon", "Surgeon"),
                ("theater_id", "Theater"),
            ],
        )

    def _build_tree(self, parent, columns):
        frame = tk.Frame(parent, bg=UIStyle.CARD_BG)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(
            frame, columns=[name for name, _ in columns], show="headings"
        )
        for name, heading in columns:
            tree.heading(name, text=heading)
            tree.column(name, anchor="w", width=120)
        tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scroll.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scroll.set)
        return tree

    def load_dashboard(self):
        today = date.today().isoformat()

        def worker():
            stats = []
            for _, endpoint in self.STAT_CARDS:
                response, error = self.api_client.list_resource(endpoint)
                stats.append((response, error))
            visits, visits_error = self.api_client.get_visits_by_date(today)
            surgeries, surgeries_error = self.api_client.get_surgeries_by_date(today)
            if not self._is_destroyed and self.page.winfo_exists():
                self.page.after(
                    0,
                    lambda: self._render_dashboard(
                        stats, visits, visits_error, surgeries, surgeries_error
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()

    def _render_dashboard(
        self, stats, visits, visits_error, surgeries, surgeries_error
    ):
        if self._is_destroyed or not self.page.winfo_exists():
            return

        for index, (response, error) in enumerate(stats):
            label = self.value_labels.get(index)
            if label and label.winfo_exists():
                label.config(text="Error" if error else str(len(response or [])))

        self._fill_tree(
            self.visits_tree,
            visits if not visits_error else [],
            ["time", "patient", "doctor", "status"],
        )
        self._fill_tree(
            self.surgeries_tree,
            surgeries if not surgeries_error else [],
            ["start_time", "patient", "surgeon", "theater_id"],
        )

    def _fill_tree(self, tree, rows, columns):
        for item in tree.get_children():
            tree.delete(item)
        if not rows:
            tree.insert("", "end", values=["No records"] + [""] * (len(columns) - 1))
            return
        for row in rows:
            tree.insert("", "end", values=[row.get(column, "") for column in columns])

    def destroy(self):
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
