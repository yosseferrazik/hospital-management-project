import threading
import tkinter as tk
from tkinter import messagebox, ttk
from collections import defaultdict, Counter
from datetime import datetime

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class StatisticsView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())
        self._is_destroyed = False
        self.data = {}

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)

        UIStyle.section_header(
            self.page,
            "Hospital Statistics",
            "Operational insights and performance metrics",
        )

        notebook = ttk.Notebook(self.page)
        notebook.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        self.overview_frame = ttk.Frame(notebook)
        self.staff_frame = ttk.Frame(notebook)
        self.visits_frame = ttk.Frame(notebook)
        self.rankings_frame = ttk.Frame(notebook)

        notebook.add(self.overview_frame, text="Floor Overview")
        notebook.add(self.staff_frame, text="Staff Report")
        notebook.add(self.visits_frame, text="Visits Report")
        notebook.add(self.rankings_frame, text="Rankings & Top")

        self.setup_overview_tab()
        self.setup_staff_tab()
        self.setup_visits_tab()
        self.setup_rankings_tab()

    def setup_overview_tab(self):
        scrollable, content = UIStyle.create_scrollable_area(
            self.overview_frame, bg=UIStyle.BG
        )

        tk.Label(
            content,
            text="Floor Details",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w", padx=24, pady=(16, 12))

        self.overview_tree_frame = tk.Frame(content, bg=UIStyle.BG)
        self.overview_tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    def setup_staff_tab(self):
        scrollable, content = UIStyle.create_scrollable_area(
            self.staff_frame, bg=UIStyle.BG
        )

        tk.Label(
            content,
            text="Hospital Staff Directory",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w", padx=24, pady=(16, 12))

        self.staff_tree_frame = tk.Frame(content, bg=UIStyle.BG)
        self.staff_tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    def setup_visits_tab(self):
        scrollable, content = UIStyle.create_scrollable_area(
            self.visits_frame, bg=UIStyle.BG
        )

        tk.Label(
            content,
            text="Visits by Day",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w", padx=24, pady=(16, 12))

        self.visits_tree_frame = tk.Frame(content, bg=UIStyle.BG)
        self.visits_tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    def setup_rankings_tab(self):
        scrollable, content = UIStyle.create_scrollable_area(
            self.rankings_frame, bg=UIStyle.BG
        )

        doctor_label = tk.Label(
            content,
            text="Top Doctors by Patient Count",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_DARK,
        )
        doctor_label.pack(anchor="w", padx=24, pady=(16, 12))

        self.doctors_tree_frame = tk.Frame(content, bg=UIStyle.BG)
        self.doctors_tree_frame.pack(fill="both", expand=False, padx=24, pady=(0, 24))

        diseases_label = tk.Label(
            content,
            text="Top Diseases",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_DARK,
        )
        diseases_label.pack(anchor="w", padx=24, pady=(16, 12))

        self.diseases_tree_frame = tk.Frame(content, bg=UIStyle.BG)
        self.diseases_tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    def load_data(self):
        def worker():
            try:
                staffdata, error = self.api_client.get_all_staff(force_refresh=True)
                if not error:
                    self.data["staff"] = staffdata or []

                floorsdata, error = self.api_client.get_all_floors(force_refresh=True)
                if not error:
                    self.data["floors"] = floorsdata or []

                roomsdata, error = self.api_client.get_all_rooms(force_refresh=True)
                if not error:
                    self.data["rooms"] = roomsdata or []

                thdata, error = self.api_client.get_all_operating_theaters(
                    force_refresh=True
                )
                if not error:
                    self.data["theaters"] = thdata or []

                visitsdata, error = self.api_client.get_all_visits(force_refresh=True)
                if not error:
                    self.data["visits"] = visitsdata or []

                prescdata, error = self.api_client.get_all_prescriptions(
                    force_refresh=True
                )
                if not error:
                    self.data["prescriptions"] = prescdata or []

                self.parent.after(0, self.render_data)
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def render_data(self):
        if not self.data:
            messagebox.showwarning("Data", "No data loaded from server")
            return

        self.render_overview()
        self.render_staff_report()
        self.render_visits_report()
        self.render_rankings()

    def render_overview(self):
        for widget in self.overview_tree_frame.winfo_children():
            widget.destroy()

        floors = self.data.get("floors", [])
        rooms = self.data.get("rooms", [])
        theaters = self.data.get("theaters", [])

        if not floors:
            tk.Label(
                self.overview_tree_frame,
                text="No floor data available",
                font=UIStyle.SUBTITLE_FONT,
                bg=UIStyle.BG,
                fg=UIStyle.TEXT_LIGHT,
            ).pack(pady=20)
            return

        tree = ttk.Treeview(
            self.overview_tree_frame,
            columns=("Floor", "Rooms", "Theaters", "Nurses"),
            height=15,
            show="headings",
        )

        tree.column("Floor", width=100, anchor="center")
        tree.column("Rooms", width=100, anchor="center")
        tree.column("Theaters", width=100, anchor="center")
        tree.column("Nurses", width=100, anchor="center")

        tree.heading("Floor", text="Floor")
        tree.heading("Rooms", text="Rooms")
        tree.heading("Theaters", text="Theaters")
        tree.heading("Nurses", text="Nursing Staff")

        floors_map = {f.get("floor_id"): f for f in floors}
        rooms_by_floor = defaultdict(int)
        theaters_by_floor = defaultdict(int)
        nurses_by_floor = defaultdict(int)

        for room in rooms:
            floor_id = room.get("floor_id")
            if floor_id:
                rooms_by_floor[floor_id] += 1

        for theater in theaters:
            floor_id = theater.get("floor_id")
            if floor_id:
                theaters_by_floor[floor_id] += 1

        staff = self.data.get("staff", [])
        for person in staff:
            if person.get("staff_type") == "NURSING":
                floor_id = person.get("floor_id")
                if floor_id:
                    nurses_by_floor[floor_id] += 1

        for floor_id, floor in sorted(floors_map.items()):
            floor_num = floor.get("floor_number", f"Floor {floor_id}")
            room_count = rooms_by_floor.get(floor_id, 0)
            theater_count = theaters_by_floor.get(floor_id, 0)
            nurse_count = nurses_by_floor.get(floor_id, 0)

            tree.insert(
                "",
                "end",
                values=(floor_num, room_count, theater_count, nurse_count),
            )

        tree.pack(fill="both", expand=True)

    def render_staff_report(self):
        for widget in self.staff_tree_frame.winfo_children():
            widget.destroy()

        staff = self.data.get("staff", [])
        if not staff:
            tk.Label(
                self.staff_tree_frame,
                text="No staff data available",
                font=UIStyle.SUBTITLE_FONT,
                bg=UIStyle.BG,
                fg=UIStyle.TEXT_LIGHT,
            ).pack(pady=20)
            return

        tree = ttk.Treeview(
            self.staff_tree_frame,
            columns=("Name", "Type", "Contact", "Hire Date"),
            height=20,
            show="headings",
        )

        tree.column("Name", width=150, anchor="w")
        tree.column("Type", width=100, anchor="center")
        tree.column("Contact", width=150, anchor="w")
        tree.column("Hire Date", width=100, anchor="center")

        tree.heading("Name", text="Name")
        tree.heading("Type", text="Staff Type")
        tree.heading("Contact", text="Contact Info")
        tree.heading("Hire Date", text="Hire Date")

        for person in sorted(staff, key=lambda x: x.get("first_name", "")):
            name = f"{person.get('first_name', '')} {person.get('last_name', '')}"
            staff_type = person.get("staff_type", "UNKNOWN")
            contact = person.get("phone", "N/A")
            hire_date = (
                person.get("hire_date", "N/A")[:10]
                if person.get("hire_date")
                else "N/A"
            )

            tree.insert("", "end", values=(name, staff_type, contact, hire_date))

        tree.pack(fill="both", expand=True)

    def render_visits_report(self):
        for widget in self.visits_tree_frame.winfo_children():
            widget.destroy()

        visits = self.data.get("visits", [])
        if not visits:
            tk.Label(
                self.visits_tree_frame,
                text="No visit data available",
                font=UIStyle.SUBTITLE_FONT,
                bg=UIStyle.BG,
                fg=UIStyle.TEXT_LIGHT,
            ).pack(pady=20)
            return

        visits_by_day = defaultdict(int)
        for visit in visits:
            timestamp = visit.get("visit_timestamp", "")
            if timestamp:
                day = timestamp[:10]
                visits_by_day[day] += 1

        tree = ttk.Treeview(
            self.visits_tree_frame,
            columns=("Date", "Visits"),
            height=20,
            show="headings",
        )

        tree.column("Date", width=150, anchor="center")
        tree.column("Visits", width=100, anchor="center")

        tree.heading("Date", text="Date")
        tree.heading("Visits", text="Visit Count")

        for day in sorted(visits_by_day.keys(), reverse=True):
            count = visits_by_day[day]
            tree.insert("", "end", values=(day, count))

        tree.pack(fill="both", expand=True)

    def render_rankings(self):
        for widget in self.doctors_tree_frame.winfo_children():
            widget.destroy()

        visits = self.data.get("visits", [])
        staff = self.data.get("staff", [])
        staff_by_id = {s.get("staff_id"): s for s in staff}

        doctor_visit_count = Counter()
        for visit in visits:
            doctor_id = visit.get("doctor_id")
            if doctor_id:
                doctor_visit_count[doctor_id] += 1

        doctors_tree = ttk.Treeview(
            self.doctors_tree_frame,
            columns=("Doctor Name", "Patients"),
            height=10,
            show="headings",
        )

        doctors_tree.column("Doctor Name", width=200, anchor="w")
        doctors_tree.column("Patients", width=100, anchor="center")

        doctors_tree.heading("Doctor Name", text="Doctor Name")
        doctors_tree.heading("Patients", text="Patient Count")

        for doctor_id, count in doctor_visit_count.most_common(10):
            doctor = staff_by_id.get(doctor_id)
            if doctor:
                name = f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}"
                doctors_tree.insert("", "end", values=(name, count))

        doctors_tree.pack(fill="both", expand=False)

        for widget in self.diseases_tree_frame.winfo_children():
            widget.destroy()

        prescriptions = self.data.get("prescriptions", [])
        diagnosis_counter = Counter()

        for visit in visits:
            diagnosis = visit.get("diagnosis")
            if diagnosis and diagnosis.strip() and diagnosis != "N/A":
                diagnosis_counter[diagnosis] += 1

        diseases_tree = ttk.Treeview(
            self.diseases_tree_frame,
            columns=("Disease", "Count"),
            height=15,
            show="headings",
        )

        diseases_tree.column("Disease", width=250, anchor="w")
        diseases_tree.column("Count", width=100, anchor="center")

        diseases_tree.heading("Disease", text="Disease / Diagnosis")
        diseases_tree.heading("Count", text="Cases")

        for disease, count in diagnosis_counter.most_common(20):
            diseases_tree.insert("", "end", values=(disease, count))

        diseases_tree.pack(fill="both", expand=True)

    def destroy(self):
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
