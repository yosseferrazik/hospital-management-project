import tkinter as tk
from tkinter import messagebox, ttk
from services.api_client import APIClient
from utils.session import Session


class LoginView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())

        self.frame = tk.Frame(parent, bg="#f0f0f0")
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(
            self.frame,
            text="Sa Palomera Hospital",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
        )
        title.pack(pady=50)

        subtitle = tk.Label(
            self.frame,
            text="Hospital Management System",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#7f8c8d",
        )
        subtitle.pack(pady=10)

        # Form frame
        form_frame = tk.Frame(self.frame, bg="white", relief="ridge", bd=2)
        form_frame.pack(pady=40, padx=100, fill="x")

        # Username
        tk.Label(form_frame, text="Username:", font=("Arial", 12), bg="white").grid(
            row=0, column=0, padx=20, pady=15, sticky="e"
        )
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.username_entry.grid(row=0, column=1, padx=20, pady=15)

        # Password
        tk.Label(form_frame, text="Password:", font=("Arial", 12), bg="white").grid(
            row=1, column=0, padx=20, pady=15, sticky="e"
        )
        self.password_entry = tk.Entry(
            form_frame, font=("Arial", 12), width=30, show="*"
        )
        self.password_entry.grid(row=1, column=1, padx=20, pady=15)

        # Buttons
        button_frame = tk.Frame(form_frame, bg="white")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        login_btn = tk.Button(
            button_frame,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            padx=30,
            pady=8,
            command=self.do_login,
        )
        login_btn.pack(side="left", padx=10)

        register_btn = tk.Button(
            button_frame,
            text="Register",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            padx=30,
            pady=8,
            command=self.app.show_register,
        )
        register_btn.pack(side="left", padx=10)

        # Press Enter to login
        self.password_entry.bind("<Return>", lambda e: self.do_login())

    def do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return

        response, error = self.api_client.login(username, password)

        if error:
            messagebox.showerror("Authentication Error", f"Error: {error}")
            return

        if response and "access_token" in response:
            Session().set_token(response["access_token"], username, "")
            messagebox.showinfo("Success", f"Welcome {username}")
            self.app.show_main_menu()

    def destroy(self):
        """Destroys the view frame"""
        self.frame.destroy()
