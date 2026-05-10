import threading
import tkinter as tk
from tkinter import messagebox, ttk

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class ResourceBrowser:
    RESOURCE_DEFINITIONS = {
        "staff": {
            "label": "Staff",
            "endpoint": "/staff",
            "key_fields": ["staff_id"],
            "fields": [
                ("national_id", "National ID", "entry"),
                ("first_name", "First Name", "entry"),
                ("last_name", "Last Name", "entry"),
                ("birth_date", "Birth Date (YYYY-MM-DD)", "entry"),
                ("phone", "Phone", "entry"),
                ("ssn", "SSN", "entry"),
                ("email", "Email", "entry"),
                ("address", "Address", "text"),
                ("staff_type", "Staff Type", "entry"),
            ],
            "list_columns": [
                ("staff_id", "ID"),
                ("national_id", "National ID"),
                ("first_name", "First Name"),
                ("last_name", "Last Name"),
                ("staff_type", "Type"),
                ("email", "Email"),
            ],
            "disable_create": True,
        },
        "floors": {
            "label": "Floors",
            "endpoint": "/floors",
            "key_fields": ["floor_id"],
            "fields": [("floor_number", "Floor Number", "entry")],
            "list_columns": [("floor_id", "ID"), ("floor_number", "Number")],
        },
        "rooms": {
            "label": "Rooms",
            "endpoint": "/rooms",
            "key_fields": ["room_id"],
            "fields": [
                ("room_number", "Room Number", "entry"),
                ("floor_id", "Floor ID", "entry"),
            ],
            "list_columns": [
                ("room_id", "ID"),
                ("room_number", "Room"),
                ("floor_id", "Floor ID"),
            ],
        },
        "operating_theaters": {
            "label": "Operating Theaters",
            "endpoint": "/operating_theaters",
            "key_fields": ["theater_id"],
            "fields": [
                ("theater_code", "Theater Code", "entry"),
                ("floor_id", "Floor ID", "entry"),
            ],
            "list_columns": [
                ("theater_id", "ID"),
                ("theater_code", "Code"),
                ("floor_id", "Floor ID"),
            ],
        },
        "medical_devices": {
            "label": "Medical Devices",
            "endpoint": "/medical_devices",
            "key_fields": ["device_id"],
            "fields": [
                ("device_type", "Device Type", "entry"),
                ("theater_id", "Theater ID", "entry"),
                ("quantity", "Quantity", "entry"),
            ],
            "list_columns": [
                ("device_id", "ID"),
                ("device_type", "Type"),
                ("theater_id", "Theater"),
                ("quantity", "Quantity"),
            ],
        },
        "medical_specialties": {
            "label": "Medical Specialties",
            "endpoint": "/medical_specialties",
            "key_fields": ["specialty_id"],
            "fields": [
                ("name", "Name", "entry"),
                ("description", "Description", "text"),
            ],
            "list_columns": [
                ("specialty_id", "ID"),
                ("name", "Name"),
                ("description", "Description"),
            ],
        },
        "patients": {
            "label": "Patients",
            "endpoint": "/patients",
            "key_fields": ["patient_id"],
            "fields": [
                ("national_id", "National ID", "entry"),
                ("first_name", "First Name", "entry"),
                ("last_name", "Last Name", "entry"),
                ("birth_date", "Birth Date (YYYY-MM-DD)", "entry"),
                ("gender", "Gender", "entry"),
                ("phone", "Phone", "entry"),
                ("email", "Email", "entry"),
                ("address", "Address", "text"),
                ("emergency_contact_name", "Emergency Contact", "entry"),
                ("emergency_contact_phone", "Emergency Phone", "entry"),
                ("blood_type", "Blood Type", "entry"),
                ("allergies", "Allergies", "text"),
            ],
            "list_columns": [
                ("patient_id", "ID"),
                ("national_id", "National ID"),
                ("first_name", "First Name"),
                ("last_name", "Last Name"),
                ("gender", "Gender"),
                ("phone", "Phone"),
            ],
        },
        "visits": {
            "label": "Visits",
            "endpoint": "/visits",
            "key_fields": ["visit_id"],
            "fields": [
                ("patient_id", "Patient ID", "entry"),
                ("doctor_id", "Doctor ID", "entry"),
                ("visit_timestamp", "Visit Timestamp (YYYY-MM-DD HH:MM:SS)", "entry"),
                ("diagnosis", "Diagnosis", "text"),
                ("notes", "Notes", "text"),
            ],
            "list_columns": [
                ("visit_id", "ID"),
                ("patient_id", "Patient ID"),
                ("doctor_id", "Doctor ID"),
                ("visit_timestamp", "Timestamp"),
                ("diagnosis", "Diagnosis"),
            ],
        },
        "scheduled_appointments": {
            "label": "Scheduled Appointments",
            "endpoint": "/scheduled_appointments",
            "key_fields": ["appointment_id"],
            "fields": [
                ("visit_id", "Visit ID", "entry"),
                ("appointment_date", "Date (YYYY-MM-DD)", "entry"),
                ("appointment_time", "Time (HH:MM:SS)", "entry"),
                ("status", "Status", "entry"),
            ],
            "list_columns": [
                ("appointment_id", "ID"),
                ("visit_id", "Visit ID"),
                ("appointment_date", "Date"),
                ("appointment_time", "Time"),
                ("status", "Status"),
            ],
        },
        "medications": {
            "label": "Medications",
            "endpoint": "/medications",
            "key_fields": ["medication_id"],
            "fields": [
                ("medication_name", "Name", "entry"),
                ("description", "Description", "text"),
            ],
            "list_columns": [
                ("medication_id", "ID"),
                ("medication_name", "Name"),
                ("description", "Description"),
            ],
        },
        "prescriptions": {
            "label": "Prescriptions",
            "endpoint": "/prescriptions",
            "key_fields": ["prescription_id"],
            "fields": [
                ("visit_id", "Visit ID", "entry"),
                ("medication_id", "Medication ID", "entry"),
                ("dosage", "Dosage", "entry"),
                ("frequency", "Frequency", "entry"),
                ("duration_days", "Duration (days)", "entry"),
                ("start_date", "Start Date (YYYY-MM-DD)", "entry"),
            ],
            "list_columns": [
                ("prescription_id", "ID"),
                ("visit_id", "Visit ID"),
                ("medication_id", "Medication ID"),
                ("dosage", "Dosage"),
                ("frequency", "Frequency"),
            ],
        },
        "admissions": {
            "label": "Admissions",
            "endpoint": "/admissions",
            "key_fields": ["admission_id"],
            "fields": [
                ("patient_id", "Patient ID", "entry"),
                ("room_id", "Room ID", "entry"),
                ("admission_date", "Admission Date (YYYY-MM-DD HH:MM:SS)", "entry"),
                ("expected_discharge_date", "Expected Discharge (YYYY-MM-DD)", "entry"),
                ("actual_discharge_date", "Actual Discharge (YYYY-MM-DD)", "entry"),
            ],
            "list_columns": [
                ("admission_id", "ID"),
                ("patient_id", "Patient ID"),
                ("room_id", "Room ID"),
                ("admission_date", "Admitted"),
                ("expected_discharge_date", "Expected"),
            ],
        },
        "surgeries": {
            "label": "Surgeries",
            "endpoint": "/surgeries",
            "key_fields": ["surgery_id"],
            "fields": [
                ("patient_id", "Patient ID", "entry"),
                ("theater_id", "Theater ID", "entry"),
                ("primary_surgeon_id", "Primary Surgeon ID", "entry"),
                ("surgery_date", "Surgery Date (YYYY-MM-DD)", "entry"),
                ("start_time", "Start Time (HH:MM:SS)", "entry"),
                ("end_time", "End Time (HH:MM:SS)", "entry"),
                ("procedure_type", "Procedure Type", "entry"),
                ("notes", "Notes", "text"),
            ],
            "list_columns": [
                ("surgery_id", "ID"),
                ("patient_id", "Patient ID"),
                ("theater_id", "Theater ID"),
                ("primary_surgeon_id", "Surgeon ID"),
                ("surgery_date", "Date"),
            ],
        },
        "surgery_assistants": {
            "label": "Surgery Assistants",
            "endpoint": "/surgery_assistants",
            "key_fields": ["surgery_id", "nurse_id"],
            "fields": [
                ("surgery_id", "Surgery ID", "entry"),
                ("nurse_id", "Nurse ID", "entry"),
                ("role", "Role", "entry"),
            ],
            "list_columns": [
                ("surgery_id", "Surgery ID"),
                ("nurse_id", "Nurse ID"),
                ("role", "Role"),
            ],
            "update_payload_fields": ["role"],
        },
        "pharmacy_dispensations": {
            "label": "Pharmacy Dispensations",
            "endpoint": "/pharmacy_dispensations",
            "key_fields": ["dispensation_id"],
            "fields": [
                ("admission_id", "Admission ID", "entry"),
                ("dispensed_at", "Dispensed At (YYYY-MM-DD HH:MM:SS)", "entry"),
                ("total_cost", "Total Cost", "entry"),
                ("notes", "Notes", "text"),
            ],
            "list_columns": [
                ("dispensation_id", "ID"),
                ("admission_id", "Admission ID"),
                ("dispensed_at", "Date"),
                ("total_cost", "Total"),
            ],
        },
        "dispensation_items": {
            "label": "Dispensation Items",
            "endpoint": "/dispensation_items",
            "key_fields": ["item_id"],
            "fields": [
                ("dispensation_id", "Dispensation ID", "entry"),
                ("medication_id", "Medication ID", "entry"),
                ("quantity", "Quantity", "entry"),
                ("unit_price", "Unit Price", "entry"),
            ],
            "list_columns": [
                ("item_id", "ID"),
                ("dispensation_id", "Dispensation ID"),
                ("medication_id", "Medication ID"),
                ("quantity", "Quantity"),
            ],
        },
        "radiology_exams": {
            "label": "Radiology Exams",
            "endpoint": "/radiology_exams",
            "key_fields": ["exam_id"],
            "fields": [
                ("patient_id", "Patient ID", "entry"),
                ("requesting_doctor_id", "Doctor ID", "entry"),
                ("exam_type", "Exam Type", "entry"),
                ("requested_at", "Requested At (YYYY-MM-DD HH:MM:SS)", "entry"),
                ("performed_at", "Performed At (YYYY-MM-DD HH:MM:SS)", "entry"),
                ("result_image_url", "Result Image URL", "entry"),
                ("radiologist_report", "Radiologist Report", "text"),
                ("status", "Status", "entry"),
            ],
            "list_columns": [
                ("exam_id", "ID"),
                ("patient_id", "Patient ID"),
                ("requesting_doctor_id", "Doctor ID"),
                ("exam_type", "Type"),
                ("status", "Status"),
            ],
        },
    }

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.session = Session()
        self.api_client = APIClient(self.session)
        self.selected_resource = tk.StringVar(value="patients")
        self.loading_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="Create mode")
        self._is_destroyed = False
        self.field_widgets = {}
        self.current_definition = None
        self.selected_keys = None

        self.create_widgets()
        self.load_resource()

    def create_widgets(self):
        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)
        self.page.grid_rowconfigure(1, weight=1)
        self.page.grid_columnconfigure(0, weight=1)

        top = tk.Frame(self.page, bg=UIStyle.BG)
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        top.columnconfigure(1, weight=1)

        tk.Label(
            top,
            text="Hospital Data Workspace",
            font=UIStyle.TITLE_FONT,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_DARK,
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            top,
            text="Unified CRUD access for the database resources exposed by the backend.",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_LIGHT,
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.resource_menu = tk.OptionMenu(
            top,
            self.selected_resource,
            *self.RESOURCE_DEFINITIONS.keys(),
            command=lambda _value: self.load_resource(),
        )
        self.resource_menu.config(
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
            activebackground=UIStyle.SURFACE,
            activeforeground=UIStyle.TEXT_DARK,
            relief="flat",
            highlightthickness=1,
            highlightbackground=UIStyle.BORDER_STRONG,
            width=24,
            anchor="w",
            padx=10,
        )
        self.resource_menu["menu"].config(
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
            activebackground=UIStyle.ACCENT_SOFT,
        )
        self.resource_menu.grid(row=0, column=1, rowspan=2, sticky="e")

        main = tk.Frame(self.page, bg=UIStyle.BG)
        main.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        self.list_frame = tk.Frame(main, bg=UIStyle.BG)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(1, weight=1)

        self.form_frame = tk.Frame(main, bg=UIStyle.BG)
        self.form_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.form_frame.columnconfigure(0, weight=1)

        self._create_list_panel()
        self._create_form_panel()

    def _create_list_panel(self):
        header_shell, header = UIStyle.panel(self.list_frame, padx=16, pady=14)
        header_shell.pack(fill="x", pady=(0, 12))

        self.list_title = tk.Label(
            header,
            text="List",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        )
        self.list_title.pack(side="left")

        tk.Label(
            header,
            textvariable=self.loading_var,
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(side="right", padx=(0, 12))
        UIStyle.filled_button(
            header, "Refresh", lambda: self.load_list(force_refresh=True)
        ).pack(side="right")

        table_shell, table_body = UIStyle.panel(self.list_frame, padx=0, pady=0)
        table_shell.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_body, columns=[], show="headings")
        self.tree.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        y_scroll = ttk.Scrollbar(table_body, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side="right", fill="y", padx=(0, 8), pady=12)
        self.tree.configure(yscrollcommand=y_scroll.set)

    def _create_form_panel(self):
        title_row = tk.Frame(self.form_frame, bg=UIStyle.BG)
        title_row.pack(fill="x", pady=(0, 10))
        self.form_title = tk.Label(
            title_row,
            text="Form",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_DARK,
        )
        self.form_title.pack(anchor="w")
        tk.Label(
            title_row,
            textvariable=self.mode_var,
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(anchor="w", pady=(4, 0))

        self.form_shell, form_container = UIStyle.panel(self.form_frame, padx=0, pady=0)
        self.form_shell.pack(fill="both", expand=True)
        self.scroll_outer, self.form_body = UIStyle.create_scrollable_area(
            form_container, bg=UIStyle.CARD_BG
        )
        self.scroll_outer.pack(fill="both", expand=True)
        self.form_body.columnconfigure(0, weight=1)

        self.button_frame = tk.Frame(self.form_frame, bg=UIStyle.BG)
        self.button_frame.pack(fill="x", pady=(16, 0))

        self.create_btn = UIStyle.filled_button(
            self.button_frame, "Create", self.create_item
        )
        self.create_btn.pack(side="left")
        self.update_btn = UIStyle.secondary_button(
            self.button_frame, "Save changes", self.update_item
        )
        self.update_btn.pack(side="left", padx=(10, 0))
        self.delete_btn = UIStyle.danger_button(
            self.button_frame, "Delete selected", self.delete_selected
        )
        self.delete_btn.pack(side="left", padx=(10, 0))
        self.clear_btn = UIStyle.secondary_button(
            self.button_frame, "Clear form", self.clear_form
        )
        self.clear_btn.pack(side="right")

        self._set_editing(False)

    def _set_editing(self, editing):
        self.mode_var.set("Edit mode" if editing else "Create mode")
        self.update_btn.config(state="normal" if editing else "disabled")
        self.delete_btn.config(state="normal" if editing else "disabled")

    def load_resource(self):
        resource_key = self.selected_resource.get()
        self.current_definition = self.RESOURCE_DEFINITIONS[resource_key]
        self.selected_keys = None
        self.list_title.config(text=f"{self.current_definition['label']} List")
        self.form_title.config(text=f"{self.current_definition['label']} Form")
        self._build_tree(self.current_definition["list_columns"])
        self._build_form(self.current_definition["fields"])
        self._set_editing(False)
        self.load_list(force_refresh=True)

    def _build_tree(self, columns):
        names = [name for name, _heading in columns]
        self.tree.config(columns=names)
        for col in names:
            self.tree.heading(col, text="")
            self.tree.column(col, width=0, stretch=False)
        for col, heading in columns:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=145, anchor="w", stretch=True)

    def _build_form(self, fields):
        for widget in self.form_body.winfo_children():
            widget.destroy()

        self.field_widgets = {}
        for row, (field_name, label, field_type) in enumerate(fields):
            tk.Label(
                self.form_body,
                text=label,
                font=UIStyle.FONT,
                bg=UIStyle.CARD_BG,
                fg=UIStyle.TEXT_DARK,
                anchor="w",
            ).grid(row=row * 2, column=0, sticky="ew", padx=16, pady=(12, 4))
            if field_type == "text":
                widget = UIStyle.form_text(self.form_body, height=4)
                widget.grid(
                    row=row * 2 + 1, column=0, sticky="ew", padx=16, pady=(0, 4)
                )
            else:
                widget = UIStyle.form_entry(self.form_body)
                widget.grid(
                    row=row * 2 + 1,
                    column=0,
                    sticky="ew",
                    padx=16,
                    pady=(0, 4),
                    ipady=8,
                )
            self.field_widgets[field_name] = {"widget": widget, "type": field_type}

    def load_list(self, force_refresh=False):
        definition = self.current_definition
        self.loading_var.set("Loading...")

        def worker():
            response, error = self.api_client.list_resource(
                definition["endpoint"], force_refresh=force_refresh
            )
            if not self._is_destroyed and self.page.winfo_exists():
                self.page.after(
                    0, lambda: self._render_list(response, error, definition)
                )

        threading.Thread(target=worker, daemon=True).start()

    def _render_list(self, response, error, definition):
        if self._is_destroyed or not self.page.winfo_exists():
            return

        self.loading_var.set("")
        for row in self.tree.get_children():
            self.tree.delete(row)

        if error:
            messagebox.showerror("Error", error)
            return

        if not response:
            self.tree.insert(
                "",
                "end",
                values=["No records"] + [""] * (len(definition["list_columns"]) - 1),
            )
            return

        for item in response:
            values = [item.get(col, "") for col, _ in definition["list_columns"]]
            self.tree.insert("", "end", values=values)

    def on_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return

        values = self.tree.item(selection[0], "values")
        if not values or values[0] == "No records":
            return

        column_names = [
            col for col, _heading in self.current_definition["list_columns"]
        ]
        row_map = dict(zip(column_names, values))
        self.selected_keys = [
            row_map[key] for key in self.current_definition["key_fields"]
        ]
        self.loading_var.set("Loading details...")

        def worker():
            response, error = self._fetch_selected_detail()
            if not self._is_destroyed and self.page.winfo_exists():
                self.page.after(0, lambda: self._render_detail(response, error))

        threading.Thread(target=worker, daemon=True).start()

    def _fetch_selected_detail(self):
        endpoint = self.current_definition["endpoint"]
        key_fields = self.current_definition["key_fields"]
        if len(key_fields) == 1:
            return self.api_client.get_resource(endpoint, self.selected_keys[0])
        path_suffix = "/".join(str(value) for value in self.selected_keys)
        return self.api_client.request_path("GET", f"{endpoint}/{path_suffix}")

    def _render_detail(self, response, error):
        self.loading_var.set("")
        if error:
            messagebox.showerror("Error", error)
            return
        if not response:
            return
        self.fill_form(response)
        self._set_editing(True)

    def _get_field_value(self, field_name):
        info = self.field_widgets[field_name]
        widget = info["widget"]
        if info["type"] == "text":
            value = widget.get("1.0", "end-1c").strip()
        else:
            value = widget.get().strip()
        return value

    def _set_field_value(self, field_name, value):
        info = self.field_widgets[field_name]
        widget = info["widget"]
        if info["type"] == "text":
            widget.delete("1.0", "end")
            if value not in (None, ""):
                widget.insert("1.0", str(value))
        else:
            widget.delete(0, tk.END)
            if value not in (None, ""):
                widget.insert(0, str(value))

    def _collect_form_data(self):
        return {name: self._get_field_value(name) for name in self.field_widgets}

    def _sanitize_payload(self, data, *, fields=None):
        payload = {}
        accepted = set(fields or data.keys())
        for key, value in data.items():
            if key not in accepted:
                continue
            payload[key] = value if value != "" else None
        return payload

    def _path_suffix(self):
        return "/".join(str(value) for value in self.selected_keys)

    def fill_form(self, data):
        for field_name in self.field_widgets:
            self._set_field_value(field_name, data.get(field_name, ""))

    def clear_form(self):
        for field_name in self.field_widgets:
            self._set_field_value(field_name, "")
        self.selected_keys = None
        self._set_editing(False)
        self.tree.selection_remove(self.tree.selection())

    def create_item(self):
        definition = self.current_definition
        if definition.get("disable_create"):
            messagebox.showinfo(
                "Info",
                "This resource must be created through the dedicated maintenance workflow.",
            )
            return

        data = self._sanitize_payload(self._collect_form_data())
        if not any(value not in (None, "") for value in data.values()):
            messagebox.showerror("Error", "Please complete at least one field")
            return

        response, error = self.api_client.create_resource(definition["endpoint"], data)
        if error:
            messagebox.showerror("Error", error)
            return

        messagebox.showinfo("Success", f"{definition['label']} created successfully")
        self.clear_form()
        self.load_list(force_refresh=True)

    def update_item(self):
        if not self.selected_keys:
            messagebox.showinfo("Info", "Select a record first")
            return

        definition = self.current_definition
        data = self._collect_form_data()
        accepted = definition.get("update_payload_fields")
        payload = self._sanitize_payload(data, fields=accepted)

        if len(definition["key_fields"]) == 1:
            _, error = self.api_client.update_resource(
                definition["endpoint"], self.selected_keys[0], payload
            )
        else:
            _, error = self.api_client.update_resource_path(
                definition["endpoint"], self._path_suffix(), payload
            )

        if error:
            messagebox.showerror("Error", error)
            return

        messagebox.showinfo("Success", f"{definition['label']} updated successfully")
        self.load_list(force_refresh=True)

    def delete_selected(self):
        if not self.selected_keys:
            messagebox.showinfo("Info", "Select a record first")
            return
        if not messagebox.askyesno("Confirm", "Delete selected record?"):
            return

        definition = self.current_definition
        if len(definition["key_fields"]) == 1:
            _, error = self.api_client.delete_resource(
                definition["endpoint"], self.selected_keys[0]
            )
        else:
            _, error = self.api_client.delete_resource_path(
                definition["endpoint"], self._path_suffix()
            )

        if error:
            messagebox.showerror("Error", error)
            return

        messagebox.showinfo("Success", f"{definition['label']} deleted successfully")
        self.clear_form()
        self.load_list(force_refresh=True)

    def destroy(self):
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
