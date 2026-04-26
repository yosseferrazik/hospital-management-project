import tkinter as tk
from tkinter import ttk, messagebox
from services.api_client import APIClient
from utils.session import Session


class SurgeriesView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())

        self.create_widgets()

    def create_widgets(self):
        # Date selector
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filter_frame, text="Date (YYYY-MM-DD):").pack(side="left", padx=5)
        self.date_entry = ttk.Entry(filter_frame, width=15)
        self.date_entry.pack(side="left", padx=5)

        search_btn = ttk.Button(filter_frame, text="Search", command=self.search)
        search_btn.pack(side="left", padx=10)

        # Treeview
        columns = (
            "surgery_id",
            "theater_id",
            "patient",
            "surgeon",
            "start_time",
            "end_time",
            "procedure",
        )
        self.tree = ttk.Treeview(
            self.parent, columns=columns, show="headings", height=20
        )

        headings = [
            "ID",
            "Theater",
            "Patient",
            "Surgeon",
            "Start Time",
            "End Time",
            "Procedure",
        ]
        for col, heading in zip(columns, headings):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=120)

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

        response, error = self.api_client.get_surgeries_by_date(date)

        if error:
            messagebox.showerror("Error", f"Error: {error}")
            return

        # Clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not response:
            self.tree.insert("", "end", values=("No surgeries", "", "", "", "", "", ""))
            return

        for surgery in response:
            values = (
                surgery.get("surgery_id", ""),
                surgery.get("theater_id", ""),
                surgery.get("patient", ""),
                surgery.get("surgeon", ""),
                surgery.get("start_time", ""),
                surgery.get("end_time", ""),
                surgery.get("procedure_type", "")[:50],
            )
            self.tree.insert("", "end", values=values)
