import tkinter as tk
from tkinter import ttk, messagebox
from services.api_client import APIClient
from utils.session import Session


class VisitsView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())

        self.create_widgets()

    def create_widgets(self):
        # Filter frame
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filter_frame, text="Date (YYYY-MM-DD):").pack(side="left", padx=5)
        self.date_entry = ttk.Entry(filter_frame, width=15)
        self.date_entry.pack(side="left", padx=5)

        search_btn = ttk.Button(filter_frame, text="Search", command=self.search)
        search_btn.pack(side="left", padx=10)

        # Treeview columns
        columns = ("appointment_id", "time", "patient", "doctor", "diagnosis", "status")
        self.tree = ttk.Treeview(
            self.parent, columns=columns, show="headings", height=20
        )

        # Column headings
        headings = [
            "Appointment ID",
            "Time",
            "Patient",
            "Doctor",
            "Diagnosis",
            "Status",
        ]
        for col, heading in zip(columns, headings):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=140)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.parent, orient="vertical", command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def search(self):
        date = self.date_entry.get().strip()
        if not date:
            messagebox.showerror("Error", "Please enter a date")
            return

        response, error = self.api_client.get_visits_by_date(date)

        if error:
            messagebox.showerror("Error", f"Error: {error}")
            return

        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not response:
            self.tree.insert("", "end", values=("No visits", "", "", "", "", ""))
            return

        # Insert visit data
        for visit in response:
            values = (
                visit.get("appointment_id", ""),
                visit.get("time", ""),
                visit.get("patient", ""),
                visit.get("doctor", ""),
                (visit.get("diagnosis", "") or "")[:50],
                visit.get("status", ""),
            )
            self.tree.insert("", "end", values=values)
