"""Maintenance workspace with registration forms for staff, patients, and assignments."""

import tkinter as tk
from tkinter import messagebox, ttk

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class MaintenanceView:
    """Tabbed form view for doctor, nursing, staff, patient registration, and nurse assignments."""

    def __init__(self, parent, app):
        """Initialize maintenance view and build form tabs."""
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())
        self._is_destroyed = False

        self.create_widgets()

    def create_widgets(self):
        """Build notebook with registration and assignment tabs."""
        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)
        UIStyle.section_header(
            self.page,
            "Maintenance Workspace",
            "Dedicated forms for staff onboarding, patient intake and nursing assignments.",
        )

        notebook = ttk.Notebook(self.page)
        notebook.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        self.medical_container = tk.Frame(notebook, bg=UIStyle.BG)
        self.nursing_container = tk.Frame(notebook, bg=UIStyle.BG)
        self.general_container = tk.Frame(notebook, bg=UIStyle.BG)
        self.patient_container = tk.Frame(notebook, bg=UIStyle.BG)
        self.assign_container = tk.Frame(notebook, bg=UIStyle.BG)

        notebook.add(self.medical_container, text="Doctor")
        notebook.add(self.nursing_container, text="Nursing")
        notebook.add(self.general_container, text="General Staff")
        notebook.add(self.patient_container, text="Patient")
        notebook.add(self.assign_container, text="Assignments")

        self.medical_frame = tk.Frame(self.medical_container, bg=UIStyle.BG)
        self.medical_frame.pack(fill="both", expand=True)
        self.nursing_frame = tk.Frame(self.nursing_container, bg=UIStyle.BG)
        self.nursing_frame.pack(fill="both", expand=True)
        self.general_frame = tk.Frame(self.general_container, bg=UIStyle.BG)
        self.general_frame.pack(fill="both", expand=True)
        self.patient_frame = tk.Frame(self.patient_container, bg=UIStyle.BG)
        self.patient_frame.pack(fill="both", expand=True)
        self.assign_frame = tk.Frame(self.assign_container, bg=UIStyle.BG)
        self.assign_frame.pack(fill="both", expand=True)

        self.create_medical_form()
        self.create_nursing_form()
        self.create_general_form()
        self.create_patient_form()
        self.create_assign_form()

    def _build_form_shell(self, parent, title, subtitle):
        """Create a scrollable form panel with title and subtitle."""
        scrollable, content = UIStyle.create_scrollable_area(parent, bg=UIStyle.BG)

        form_shell = tk.Frame(
            content,
            bg=UIStyle.CARD_BG,
            highlightbackground=UIStyle.BORDER,
            highlightthickness=1,
        )
        form_shell.pack(fill="both", expand=False, padx=12, pady=12)

        form = tk.Frame(form_shell, bg=UIStyle.CARD_BG)
        form.pack(fill="both", expand=False, padx=24, pady=20)
        form.columnconfigure(1, weight=1)

        tk.Label(
            form,
            text=title,
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(
            form,
            text=subtitle,
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 16))
        return form

    def _render_fields(self, form, fields):
        """Render labeled form fields in a grid layout."""
        entries = {}
        for index, (label, key, field_type) in enumerate(fields, start=2):
            tk.Label(
                form,
                text=label,
                font=UIStyle.FONT,
                bg=UIStyle.CARD_BG,
                fg=UIStyle.TEXT_DARK,
            ).grid(row=index, column=0, sticky="ne", padx=(0, 12), pady=6)
            if field_type == "text":
                widget = UIStyle.form_text(form, height=4)
                widget.grid(row=index, column=1, sticky="ew", pady=6)
            else:
                widget = UIStyle.form_entry(form)
                widget.grid(row=index, column=1, sticky="ew", pady=6, ipady=8)
            entries[key] = (widget, field_type)
        return entries

    def _collect(self, entries):
        """Collect all form field values into a dictionary."""
        data = {}
        for key, (widget, field_type) in entries.items():
            if field_type == "text":
                value = widget.get("1.0", "end-1c").strip()
            else:
                value = widget.get().strip()
            if value:
                data[key] = value
        return data

    def _clear(self, entries):
        """Clear all form field values."""
        for widget, field_type in entries.values():
            if field_type == "text":
                widget.delete("1.0", "end")
            else:
                widget.delete(0, tk.END)

    def create_medical_form(self):
        """Build the doctor registration form fields."""
        form = self._build_form_shell(
            self.medical_frame,
            "Doctor registration",
            "Create medical staff records linked to a specialty and professional license.",
        )
        fields = [
            ("National ID:", "national_id", "entry"),
            ("First Name:", "first_name", "entry"),
            ("Last Name:", "last_name", "entry"),
            ("Birth Date (YYYY-MM-DD):", "birth_date", "entry"),
            ("Phone:", "phone", "entry"),
            ("Email:", "email", "entry"),
            ("Address:", "address", "text"),
            ("License Number:", "license_number", "entry"),
            ("Specialty ID:", "specialty_id", "entry"),
            ("SSN (optional):", "ssn", "entry"),
            ("Curriculum:", "curriculum", "text"),
        ]
        self.medical_entries = self._render_fields(form, fields)
        UIStyle.filled_button(form, "Register Doctor", self.submit_medical).grid(
            row=len(fields) + 2, column=0, columnspan=2, sticky="w", pady=(18, 0)
        )

    def submit_medical(self):
        """Validate and send doctor registration data to the API."""
        data = self._collect(self.medical_entries)
        if not all(
            data.get(key)
            for key in [
                "national_id",
                "first_name",
                "last_name",
                "birth_date",
                "specialty_id",
                "license_number",
            ]
        ):
            messagebox.showerror(
                "Error",
                "National ID, first name, last name, birth date, specialty ID and license number are required",
            )
            return
        response, error = self.api_client.add_medical_staff(data)
        if error:
            messagebox.showerror("Error", error)
            return
        messagebox.showinfo(
            "Success", f"Doctor registered with ID: {response['staff_id']}"
        )
        self._clear(self.medical_entries)

    def create_nursing_form(self):
        """Build the nursing registration form fields."""
        form = self._build_form_shell(
            self.nursing_frame,
            "Nursing registration",
            "Onboard nursing staff and capture certifications and license data.",
        )
        fields = [
            ("National ID:", "national_id", "entry"),
            ("First Name:", "first_name", "entry"),
            ("Last Name:", "last_name", "entry"),
            ("Birth Date (YYYY-MM-DD):", "birth_date", "entry"),
            ("Phone:", "phone", "entry"),
            ("Email:", "email", "entry"),
            ("Address:", "address", "text"),
            ("Nursing License Number:", "nursing_license", "entry"),
            ("Certifications:", "certifications", "text"),
            ("SSN (optional):", "ssn", "entry"),
        ]
        self.nursing_entries = self._render_fields(form, fields)
        UIStyle.filled_button(form, "Register Nurse", self.submit_nursing).grid(
            row=len(fields) + 2, column=0, columnspan=2, sticky="w", pady=(18, 0)
        )

    def submit_nursing(self):
        """Validate and send nursing registration data to the API."""
        data = self._collect(self.nursing_entries)
        if not all(
            data.get(key)
            for key in [
                "national_id",
                "first_name",
                "last_name",
                "birth_date",
                "nursing_license",
            ]
        ):
            messagebox.showerror(
                "Error",
                "National ID, first name, last name, birth date and nursing license are required",
            )
            return
        response, error = self.api_client.add_nursing_staff(data)
        if error:
            messagebox.showerror("Error", error)
            return
        messagebox.showinfo(
            "Success", f"Nurse registered with ID: {response['staff_id']}"
        )
        self._clear(self.nursing_entries)

    def create_general_form(self):
        """Build the general staff registration form fields."""
        form = self._build_form_shell(
            self.general_frame,
            "General staff registration",
            "Register non-clinical staff profiles with role-specific job types.",
        )
        fields = [
            ("National ID:", "national_id", "entry"),
            ("First Name:", "first_name", "entry"),
            ("Last Name:", "last_name", "entry"),
            ("Birth Date (YYYY-MM-DD):", "birth_date", "entry"),
            ("Phone:", "phone", "entry"),
            ("Email:", "email", "entry"),
            ("Address:", "address", "text"),
            ("Job Type:", "job_type", "entry"),
            ("SSN (optional):", "ssn", "entry"),
        ]
        self.general_entries = self._render_fields(form, fields)
        UIStyle.filled_button(form, "Register Staff", self.submit_general).grid(
            row=len(fields) + 2, column=0, columnspan=2, sticky="w", pady=(18, 0)
        )

    def submit_general(self):
        """Validate and send general staff registration data to the API."""
        data = self._collect(self.general_entries)
        if not all(
            data.get(key)
            for key in [
                "national_id",
                "first_name",
                "last_name",
                "birth_date",
                "job_type",
            ]
        ):
            messagebox.showerror(
                "Error",
                "National ID, first name, last name, birth date and job type are required",
            )
            return
        response, error = self.api_client.add_general_staff(data)
        if error:
            messagebox.showerror("Error", error)
            return
        messagebox.showinfo(
            "Success", f"Staff registered with ID: {response['staff_id']}"
        )
        self._clear(self.general_entries)

    def create_patient_form(self):
        """Build the patient registration form fields."""
        form = self._build_form_shell(
            self.patient_frame,
            "Patient registration",
            "Patient intake form aligned with the database structure and emergency fields.",
        )
        fields = [
            ("National ID:", "national_id", "entry"),
            ("First Name:", "first_name", "entry"),
            ("Last Name:", "last_name", "entry"),
            ("Birth Date (YYYY-MM-DD):", "birth_date", "entry"),
            ("Gender:", "gender", "entry"),
            ("Phone:", "phone", "entry"),
            ("Email:", "email", "entry"),
            ("Address:", "address", "text"),
            ("Emergency Contact Name:", "emergency_contact_name", "entry"),
            ("Emergency Contact Phone:", "emergency_contact_phone", "entry"),
            ("Blood Type:", "blood_type", "entry"),
            ("Allergies:", "allergies", "text"),
        ]
        self.patient_entries = self._render_fields(form, fields)
        UIStyle.filled_button(form, "Register Patient", self.submit_patient).grid(
            row=len(fields) + 2, column=0, columnspan=2, sticky="w", pady=(18, 0)
        )

    def submit_patient(self):
        """Validate and send patient registration data to the API."""
        data = self._collect(self.patient_entries)
        if not all(
            data.get(key)
            for key in ["national_id", "first_name", "last_name", "birth_date"]
        ):
            messagebox.showerror(
                "Error",
                "National ID, first name, last name and birth date are required",
            )
            return
        response, error = self.api_client.add_patient(data)
        if error:
            messagebox.showerror("Error", error)
            return
        messagebox.showinfo(
            "Success", f"Patient registered with ID: {response['patient_id']}"
        )
        self._clear(self.patient_entries)

    def create_assign_form(self):
        """Build the nurse assignment form with doctor/floor options."""
        form = self._build_form_shell(
            self.assign_frame,
            "Nursing assignments",
            "Assign a nurse either to a doctor or to a floor, using existing staff and floor IDs.",
        )

        tk.Label(
            form,
            text="Nurse ID:",
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).grid(row=2, column=0, sticky="e", padx=(0, 12), pady=8)
        self.nurse_id_entry = UIStyle.form_entry(form)
        self.nurse_id_entry.grid(row=2, column=1, sticky="ew", pady=8, ipady=8)

        tk.Label(
            form,
            text="Doctor ID:",
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).grid(row=3, column=0, sticky="e", padx=(0, 12), pady=8)
        self.doctor_id_entry = UIStyle.form_entry(form)
        self.doctor_id_entry.grid(row=3, column=1, sticky="ew", pady=8, ipady=8)

        tk.Label(
            form,
            text="Floor ID:",
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).grid(row=4, column=0, sticky="e", padx=(0, 12), pady=8)
        self.floor_id_entry = UIStyle.form_entry(form)
        self.floor_id_entry.grid(row=4, column=1, sticky="ew", pady=8, ipady=8)

        UIStyle.filled_button(form, "Assign Nurse", self.assign).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(18, 0)
        )

    def assign(self):
        """Validate and send nurse assignment request to the API."""
        nurse_id = self.nurse_id_entry.get().strip()
        doctor_id = self.doctor_id_entry.get().strip()
        floor_id = self.floor_id_entry.get().strip()
        if not nurse_id:
            messagebox.showerror("Error", "Nurse ID is required")
            return
        if doctor_id:
            _, error = self.api_client.assign_nursing(nurse_id, doctor_id=doctor_id)
        elif floor_id:
            _, error = self.api_client.assign_nursing(nurse_id, floor_id=floor_id)
        else:
            messagebox.showerror("Error", "Specify either a doctor ID or a floor ID")
            return
        if error:
            messagebox.showerror("Error", error)
            return
        messagebox.showinfo("Success", "Assignment completed successfully")
        self.nurse_id_entry.delete(0, tk.END)
        self.doctor_id_entry.delete(0, tk.END)
        self.floor_id_entry.delete(0, tk.END)

    def destroy(self):
        """Clean up maintenance view resources."""
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
