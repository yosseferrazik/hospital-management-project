import tkinter as tk
from tkinter import ttk, messagebox
from views.maintenance_view import MaintenanceView
from views.surgeries_view import SurgeriesView
from views.visits_view import VisitsView
from utils.session import Session


class MainMenu:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg="#f0f0f0")
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self.frame, bg="#2c3e50", height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Sa Palomera Hospital - Management System",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white",
        )
        title.pack(pady=30)

        # Username display
        user = Session().username or "User"
        user_label = tk.Label(
            header,
            text=f"Welcome: {user}",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1",
        )
        user_label.pack()

        # Main buttons
        btn_frame = tk.Frame(self.frame, bg="#f0f0f0")
        btn_frame.pack(pady=80)

        # Row 1
        row1 = tk.Frame(btn_frame, bg="#f0f0f0")
        row1.pack()

        self.btn_maintenance = tk.Button(
            row1,
            text="Maintenance\n(Staff/Patient Registration)",
            font=("Arial", 12, "bold"),
            width=25,
            height=3,
            bg="#3498db",
            fg="white",
            relief="raised",
            command=self.open_maintenance,
        )
        self.btn_maintenance.pack(side="left", padx=20, pady=10)

        self.btn_reports = tk.Button(
            row1,
            text="Queries and Reports\n(View surgeries/visits by day)",
            font=("Arial", 12, "bold"),
            width=25,
            height=3,
            bg="#2980b9",
            fg="white",
            relief="raised",
            command=self.open_consultations,
        )
        self.btn_reports.pack(side="left", padx=20, pady=10)

        # Row 2
        row2 = tk.Frame(btn_frame, bg="#f0f0f0")
        row2.pack()

        self.btn_export = tk.Button(
            row2,
            text="Data Export\n(Coming Soon)",
            font=("Arial", 12, "bold"),
            width=25,
            height=3,
            bg="#95a5a6",
            fg="white",
            relief="raised",
            state="disabled",
        )
        self.btn_export.pack(side="left", padx=20, pady=10)

        self.btn_dummy = tk.Button(
            row2,
            text="Test Data\n(Generate/Clean)",
            font=("Arial", 12, "bold"),
            width=25,
            height=3,
            bg="#e67e22",
            fg="white",
            relief="raised",
            command=self.dummy_options,
        )
        self.btn_dummy.pack(side="left", padx=20, pady=10)

        # Logout
        logout_btn = tk.Button(
            self.frame,
            text="Logout",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8,
            command=self.logout,
        )
        logout_btn.pack(pady=40)

    def open_maintenance(self):
        window = tk.Toplevel(self.parent)
        window.title("Maintenance Management")
        window.geometry("800x600")
        window.configure(bg="#f0f0f0")
        MaintenanceView(window, self.app)

    def open_consultations(self):
        window = tk.Toplevel(self.parent)
        window.title("Queries and Reports")
        window.geometry("900x600")
        window.configure(bg="#f0f0f0")

        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        surgeries_frame = ttk.Frame(notebook)
        visits_frame = ttk.Frame(notebook)

        notebook.add(surgeries_frame, text="Surgeries by Day")
        notebook.add(visits_frame, text="Visits by Day")

        SurgeriesView(surgeries_frame, self.app)
        VisitsView(visits_frame, self.app)

    def dummy_options(self):
        confirmed = messagebox.askyesno(
            "Test Data",
            "Generate 50,000+ test records?\n\n"
            "This will create fictitious patients, staff and visits.\n"
            "Do you want to continue?",
        )
        if confirmed:
            self.generate_dummy()

    def generate_dummy(self):
        from services.api_client import APIClient
        from utils.session import Session

        client = APIClient(Session())
        response, error = client.generate_dummy()

        if error:
            messagebox.showerror("Error", f"Failed to generate: {error}")
        else:
            messagebox.showinfo("Success", "Test data generated successfully")

    def logout(self):
        Session().clear()
        self.destroy()
        self.app.show_login()

    def destroy(self):
        """Destroys the view frame"""
        self.frame.destroy()
