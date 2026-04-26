import tkinter as tk
from tkinter import ttk, messagebox
from services.api_client import APIClient
from utils.session import Session


class MaintenanceView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())

        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.medical_frame = ttk.Frame(notebook)
        self.nursing_frame = ttk.Frame(notebook)
        self.general_frame = ttk.Frame(notebook)
        self.patient_frame = ttk.Frame(notebook)
        self.assign_frame = ttk.Frame(notebook)

        notebook.add(self.medical_frame, text="Doctor Registration")
        notebook.add(self.nursing_frame, text="Nursing Staff Registration")
        notebook.add(self.general_frame, text="General Staff Registration")
        notebook.add(self.patient_frame, text="Patient Registration")
        notebook.add(self.assign_frame, text="Assign Nursing")

        self.create_medical_form()
        self.create_nursing_form()
        self.create_general_form()
        self.create_patient_form()
        self.create_assign_form()

    def create_medical_form(self):
        form = ttk.Frame(self.medical_frame, padding=20)
        form.pack(fill="both", expand=True)

        fields = [
            ("National ID:", "national_id"),
            ("First Name:", "first_name"),
            ("Last Name:", "last_name"),
            ("Birth Date (YYYY-MM-DD):", "birth_date"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address"),
            ("License Number:", "license_number"),
            ("Specialty ID:", "specialty_id"),
            ("SSN (optional):", "ssn"),
            ("Curriculum:", "curriculum"),
        ]

        self.medical_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(
                row=i, column=0, sticky="e", padx=5, pady=5
            )
            entry = ttk.Entry(form, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.medical_entries[key] = entry

        submit_btn = ttk.Button(
            form, text="Register Doctor", command=self.submit_medical
        )
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def submit_medical(self):
        data = {key: entry.get().strip() for key, entry in self.medical_entries.items()}
        if not data["national_id"] or not data["first_name"] or not data["last_name"]:
            messagebox.showerror(
                "Error", "National ID, first name and last name are required"
            )
            return

        response, error = self.api_client.add_medical_staff(data)
        if error:
            messagebox.showerror("Error", f"Error: {error}")
        else:
            messagebox.showinfo(
                "Success", f"Doctor registered with ID: {response['staff_id']}"
            )
            for entry in self.medical_entries.values():
                entry.delete(0, tk.END)

    def create_nursing_form(self):
        form = ttk.Frame(self.nursing_frame, padding=20)
        form.pack(fill="both", expand=True)

        fields = [
            ("National ID:", "national_id"),
            ("First Name:", "first_name"),
            ("Last Name:", "last_name"),
            ("Birth Date (YYYY-MM-DD):", "birth_date"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address"),
            ("Nursing License Number:", "nursing_license"),
            ("Certifications:", "certifications"),
            ("SSN (optional):", "ssn"),
        ]

        self.nursing_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(
                row=i, column=0, sticky="e", padx=5, pady=5
            )
            entry = ttk.Entry(form, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.nursing_entries[key] = entry

        submit_btn = ttk.Button(
            form, text="Register Nurse", command=self.submit_nursing
        )
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def submit_nursing(self):
        data = {key: entry.get().strip() for key, entry in self.nursing_entries.items()}
        if not data["national_id"] or not data["first_name"] or not data["last_name"]:
            messagebox.showerror(
                "Error", "National ID, first name and last name are required"
            )
            return

        response, error = self.api_client.add_nursing_staff(data)
        if error:
            messagebox.showerror("Error", f"Error: {error}")
        else:
            messagebox.showinfo(
                "Success", f"Nurse registered with ID: {response['staff_id']}"
            )
            for entry in self.nursing_entries.values():
                entry.delete(0, tk.END)

    def create_general_form(self):
        form = ttk.Frame(self.general_frame, padding=20)
        form.pack(fill="both", expand=True)

        fields = [
            ("National ID:", "national_id"),
            ("First Name:", "first_name"),
            ("Last Name:", "last_name"),
            ("Birth Date (YYYY-MM-DD):", "birth_date"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address"),
            ("Job Type:", "job_type"),
            ("SSN (optional):", "ssn"),
        ]

        self.general_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(
                row=i, column=0, sticky="e", padx=5, pady=5
            )
            entry = ttk.Entry(form, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.general_entries[key] = entry

        submit_btn = ttk.Button(
            form, text="Register Staff", command=self.submit_general
        )
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def submit_general(self):
        data = {key: entry.get().strip() for key, entry in self.general_entries.items()}
        if not data["national_id"] or not data["first_name"] or not data["last_name"]:
            messagebox.showerror(
                "Error", "National ID, first name and last name are required"
            )
            return

        response, error = self.api_client.add_general_staff(data)
        if error:
            messagebox.showerror("Error", f"Error: {error}")
        else:
            messagebox.showinfo(
                "Success", f"Staff registered with ID: {response['staff_id']}"
            )
            for entry in self.general_entries.values():
                entry.delete(0, tk.END)

    def create_patient_form(self):
        form = ttk.Frame(self.patient_frame, padding=20)
        form.pack(fill="both", expand=True)

        fields = [
            ("National ID:", "national_id"),
            ("First Name:", "first_name"),
            ("Last Name:", "last_name"),
            ("Birth Date (YYYY-MM-DD):", "birth_date"),
            ("Gender (MALE/FEMALE/OTHER):", "gender"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address"),
            ("Emergency Contact Name:", "emergency_contact_name"),
            ("Emergency Contact Phone:", "emergency_contact_phone"),
            ("Blood Type (A+/A-/etc):", "blood_type"),
            ("Allergies:", "allergies"),
        ]

        self.patient_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(
                row=i, column=0, sticky="e", padx=5, pady=5
            )
            entry = ttk.Entry(form, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.patient_entries[key] = entry

        submit_btn = ttk.Button(
            form, text="Register Patient", command=self.submit_patient
        )
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def submit_patient(self):
        data = {key: entry.get().strip() for key, entry in self.patient_entries.items()}
        if not data["national_id"] or not data["first_name"] or not data["last_name"]:
            messagebox.showerror(
                "Error", "National ID, first name and last name are required"
            )
            return

        response, error = self.api_client.add_patient(data)
        if error:
            messagebox.showerror("Error", f"Error: {error}")
        else:
            messagebox.showinfo(
                "Success", f"Patient registered with ID: {response['patient_id']}"
            )
            for entry in self.patient_entries.values():
                entry.delete(0, tk.END)

    def create_assign_form(self):
        form = ttk.Frame(self.assign_frame, padding=20)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Nurse ID:").grid(
            row=0, column=0, padx=5, pady=10, sticky="e"
        )
        self.nurse_id_entry = ttk.Entry(form, width=30)
        self.nurse_id_entry.grid(row=0, column=1, padx=5, pady=10)

        ttk.Label(form, text="Assign to Doctor (ID):").grid(
            row=1, column=0, padx=5, pady=10, sticky="e"
        )
        self.doctor_id_entry = ttk.Entry(form, width=30)
        self.doctor_id_entry.grid(row=1, column=1, padx=5, pady=10)

        ttk.Label(form, text="Or to Floor (ID):").grid(
            row=2, column=0, padx=5, pady=10, sticky="e"
        )
        self.floor_id_entry = ttk.Entry(form, width=30)
        self.floor_id_entry.grid(row=2, column=1, padx=5, pady=10)

        def assign():
            nurse_id = self.nurse_id_entry.get().strip()
            doctor_id = self.doctor_id_entry.get().strip()
            floor_id = self.floor_id_entry.get().strip()

            if not nurse_id:
                messagebox.showerror("Error", "Nurse ID is required")
                return

            if doctor_id:
                response, error = self.api_client.assign_nursing(
                    nurse_id, doctor_id=doctor_id
                )
            elif floor_id:
                response, error = self.api_client.assign_nursing(
                    nurse_id, floor_id=floor_id
                )
            else:
                messagebox.showerror("Error", "You must specify a doctor or floor")
                return

            if error:
                messagebox.showerror("Error", f"Error: {error}")
            else:
                messagebox.showinfo("Success", "Assignment completed successfully")
                self.nurse_id_entry.delete(0, tk.END)
                self.doctor_id_entry.delete(0, tk.END)
                self.floor_id_entry.delete(0, tk.END)

        submit_btn = ttk.Button(form, text="Assign", command=assign)
        submit_btn.grid(row=3, column=0, columnspan=2, pady=20)
