"""Operational reports for visits and surgeries by date."""

import threading
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class QueriesReportsView:
    """Side-by-side operational reports showing visits and surgeries for a selected date."""

    def __init__(self, parent, app):
        """Initialize reports view, build widgets, and load today's data."""
        self.parent = parent
        self.app = app
        self.session = Session()
        self.api_client = APIClient(self.session)
        self._is_destroyed = False

        self.create_widgets()
        self.date_entry.insert(0, date.today().isoformat())
        self.run_reports()

    def create_widgets(self):
        """Build date filter and side-by-side visits and surgeries panels."""
        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)

        UIStyle.section_header(
            self.page,
            "Operational Reports",
            "Live operational views built on the reporting endpoints that already exist in the backend.",
        )

        top_shell, top = UIStyle.panel(self.page, padx=18, pady=18)
        top_shell.pack(fill="x", padx=24, pady=(0, 12))

        tk.Label(
            top,
            text="Reference date",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w")
        filter_row = tk.Frame(top, bg=UIStyle.CARD_BG)
        filter_row.pack(fill="x", pady=(10, 0))
        self.date_entry = UIStyle.form_entry(filter_row)
        self.date_entry.pack(side="left", ipadx=60, ipady=8)
        UIStyle.filled_button(filter_row, "Load agenda", self.run_reports).pack(
            side="left", padx=(10, 0)
        )
        UIStyle.secondary_button(filter_row, "Today", self.load_today).pack(
            side="left", padx=(10, 0)
        )

        self.status_var = tk.StringVar(value="")
        tk.Label(
            top,
            textvariable=self.status_var,
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(anchor="w", pady=(10, 0))

        body = tk.Frame(self.page, bg=UIStyle.BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self.visits_shell, visits_body = UIStyle.panel(body, padx=18, pady=18)
        self.visits_shell.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(
            visits_body,
            text="Scheduled Visits",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w")
        tk.Label(
            visits_body,
            text="Appointments, assigned doctors and diagnostic context.",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(anchor="w", pady=(4, 12))
        self.visits_tree = self._build_tree(
            visits_body,
            [
                ("appointment_id", "Appointment ID"),
                ("time", "Time"),
                ("patient", "Patient"),
                ("doctor", "Doctor"),
                ("diagnosis", "Diagnosis"),
                ("status", "Status"),
            ],
        )

        self.surgeries_shell, surgeries_body = UIStyle.panel(body, padx=18, pady=18)
        self.surgeries_shell.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(
            surgeries_body,
            text="Scheduled Surgeries",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w")
        tk.Label(
            surgeries_body,
            text="Procedure schedule, theater allocation and assigned staff.",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(anchor="w", pady=(4, 12))
        self.surgeries_tree = self._build_tree(
            surgeries_body,
            [
                ("surgery_id", "Surgery ID"),
                ("theater_id", "Theater"),
                ("patient", "Patient"),
                ("surgeon", "Surgeon"),
                ("start_time", "Start"),
                ("end_time", "End"),
                ("procedure_type", "Procedure"),
            ],
        )

    def _build_tree(self, parent, columns):
        """Create a Treeview widget with specified columns and scrollbar."""
        frame = tk.Frame(parent, bg=UIStyle.CARD_BG)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(
            frame, columns=[name for name, _ in columns], show="headings"
        )
        for name, heading in columns:
            tree.heading(name, text=heading)
            tree.column(name, width=120, anchor="w")
        tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scroll.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scroll.set)
        return tree

    def load_today(self):
        """Reset date entry to today and reload reports."""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())
        self.run_reports()

    def run_reports(self):
        """Fetch visits and surgeries data for the selected date."""
        selected_date = self.date_entry.get().strip()
        if not selected_date:
            messagebox.showerror("Error", "Please enter a date in YYYY-MM-DD format")
            return

        self.status_var.set("Loading operational reports...")

        def worker():
            visits, visits_error = self.api_client.get_visits_by_date(selected_date)
            surgeries, surgeries_error = self.api_client.get_surgeries_by_date(
                selected_date
            )
            if not self._is_destroyed and self.page.winfo_exists():
                self.page.after(
                    0,
                    lambda: self._render_reports(
                        selected_date, visits, visits_error, surgeries, surgeries_error
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()

    def _render_reports(
        self, selected_date, visits, visits_error, surgeries, surgeries_error
    ):
        """Populate the visits and surgeries trees with fetched data."""
        self._fill_tree(
            self.visits_tree,
            visits or [],
            ["appointment_id", "time", "patient", "doctor", "diagnosis", "status"],
        )
        self._fill_tree(
            self.surgeries_tree,
            surgeries or [],
            [
                "surgery_id",
                "theater_id",
                "patient",
                "surgeon",
                "start_time",
                "end_time",
                "procedure_type",
            ],
        )

        if visits_error or surgeries_error:
            errors = [error for error in [visits_error, surgeries_error] if error]
            self.status_var.set("Some reports could not be loaded.")
            messagebox.showerror("Error", "\n".join(errors))
            return

        self.status_var.set(
            f"Agenda loaded for {selected_date}: {len(visits or [])} visits and {len(surgeries or [])} surgeries."
        )

    def _fill_tree(self, tree, rows, columns):
        """Populate a Treeview with rows from API response data."""
        for item in tree.get_children():
            tree.delete(item)
        if not rows:
            tree.insert("", "end", values=["No records"] + [""] * (len(columns) - 1))
            return
        for row in rows:
            tree.insert("", "end", values=[row.get(column, "") for column in columns])

    def destroy(self):
        """Clean up reports view resources."""
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
