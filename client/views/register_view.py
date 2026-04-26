import tkinter as tk
from tkinter import messagebox, ttk
from services.api_client import APIClient
from utils.session import Session


class RegisterView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())

        self.frame = tk.Frame(parent, bg="#f0f0f0")
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self.frame,
            text="User Registration",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
        )
        title.pack(pady=30)

        form_frame = tk.Frame(self.frame, bg="white", relief="ridge", bd=2)
        form_frame.pack(pady=20, padx=100, fill="x")

        # Username
        tk.Label(form_frame, text="Username:", font=("Arial", 12), bg="white").grid(
            row=0, column=0, padx=20, pady=12, sticky="e"
        )
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.username_entry.grid(row=0, column=1, padx=20, pady=12)

        # Password
        tk.Label(form_frame, text="Password:", font=("Arial", 12), bg="white").grid(
            row=1, column=0, padx=20, pady=12, sticky="e"
        )
        self.password_entry = tk.Entry(
            form_frame, font=("Arial", 12), width=30, show="*"
        )
        self.password_entry.grid(row=1, column=1, padx=20, pady=12)

        # Confirm password
        tk.Label(form_frame, text="Confirm:", font=("Arial", 12), bg="white").grid(
            row=2, column=0, padx=20, pady=12, sticky="e"
        )
        self.confirm_entry = tk.Entry(
            form_frame, font=("Arial", 12), width=30, show="*"
        )
        self.confirm_entry.grid(row=2, column=1, padx=20, pady=12)

        # Staff ID
        tk.Label(form_frame, text="Staff ID:", font=("Arial", 12), bg="white").grid(
            row=3, column=0, padx=20, pady=12, sticky="e"
        )
        self.staff_id_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.staff_id_entry.grid(row=3, column=1, padx=20, pady=12)

        # Role
        tk.Label(form_frame, text="Role:", font=("Arial", 12), bg="white").grid(
            row=4, column=0, padx=20, pady=12, sticky="e"
        )
        self.role_var = tk.StringVar(value="STAFF")
        roles = ["ADMIN", "DOCTOR", "NURSE", "STAFF", "RECEPTIONIST"]
        role_menu = ttk.Combobox(
            form_frame,
            textvariable=self.role_var,
            values=roles,
            font=("Arial", 12),
            width=27,
        )
        role_menu.grid(row=4, column=1, padx=20, pady=12)

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)

        register_btn = tk.Button(
            btn_frame,
            text="Register",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=8,
            command=self.do_register,
        )
        register_btn.pack(side="left", padx=10)

        back_btn = tk.Button(
            btn_frame,
            text="Back",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            padx=30,
            pady=8,
            command=self.app.show_login,
        )
        back_btn.pack(side="left", padx=10)

    def do_register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        staff_id = self.staff_id_entry.get().strip()
        role = self.role_var.get()

        if not all([username, password, staff_id, role]):
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        response, error = self.api_client.register(username, password, staff_id, role)

        if error:
            messagebox.showerror("Error", f"Registration failed: {error}")
            return

        messagebox.showinfo("Success", f"User {username} registered successfully")
        self.app.show_login()

    def destroy(self):
        """Destroys the view frame"""
        self.frame.destroy()
