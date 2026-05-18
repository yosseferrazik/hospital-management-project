import threading
import tkinter as tk
from tkinter import ttk, messagebox

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class UserManagementView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.session = Session()
        self.api_client = APIClient(self.session)
        self._is_destroyed = False

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)
        self.page.grid_rowconfigure(1, weight=1)
        self.page.grid_columnconfigure(0, weight=1)

        UIStyle.section_header(
            self.page,
            "User Management",
            "Create and manage system users (admin only).",
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 14))

        main = tk.Frame(self.page, bg=UIStyle.BG)
        main.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)

        left = tk.Frame(main, bg=UIStyle.BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        title = UIStyle.stat_card(left, "Existing Users", "All registered accounts")
        title[0].pack(fill="x")
        list_shell, list_body = UIStyle.panel(left, padx=0, pady=0)
        list_shell.pack(fill="both", expand=True, pady=(10, 0))
        list_body.rowconfigure(0, weight=1)
        list_body.columnconfigure(0, weight=1)

        self.user_tree = ttk.Treeview(list_body, columns=("user_id", "username", "role"), show="headings")
        self.user_tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.user_tree.heading("user_id", text="ID")
        self.user_tree.heading("username", text="Username")
        self.user_tree.heading("role", text="Role")
        self.user_tree.column("user_id", width=50)
        self.user_tree.column("username", width=160)
        self.user_tree.column("role", width=120)

        right = tk.Frame(main, bg=UIStyle.BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        form_shell, form_body = UIStyle.panel(right, padx=18, pady=18)
        form_shell.pack(fill="both", expand=True)

        tk.Label(form_body, text="Create New User", font=UIStyle.CARD_TITLE, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).pack(anchor="w")
        tk.Label(form_body, text="Fill all fields to register a new system account.", font=UIStyle.SUBTITLE_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT).pack(anchor="w", pady=(4, 16))

        fields_frame = tk.Frame(form_body, bg=UIStyle.CARD_BG)
        fields_frame.pack(fill="x")

        def add_field(label):
            row = tk.Frame(fields_frame, bg=UIStyle.CARD_BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=UIStyle.FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK, width=16, anchor="w").pack(side="left")
            return row

        self.username_var = tk.StringVar()
        row = add_field("Username:")
        ttk.Entry(row, textvariable=self.username_var, font=UIStyle.FONT).pack(side="left", fill="x", expand=True)

        self.password_var = tk.StringVar()
        row = add_field("Password:")
        ttk.Entry(row, textvariable=self.password_var, font=UIStyle.FONT, show="*").pack(side="left", fill="x", expand=True)

        self.role_var = tk.StringVar(value="DOCTOR")
        row = add_field("Role:")
        ttk.Combobox(row, textvariable=self.role_var, values=["ADMIN", "DOCTOR", "NURSE", "STAFF", "RECEPTIONIST"], font=UIStyle.FONT, state="readonly").pack(side="left", fill="x", expand=True)

        self.staff_id_var = tk.StringVar()
        row = add_field("Staff ID:")
        ttk.Entry(row, textvariable=self.staff_id_var, font=UIStyle.FONT).pack(side="left", fill="x", expand=True)

        btn_frame = tk.Frame(form_body, bg=UIStyle.CARD_BG)
        btn_frame.pack(fill="x", pady=(16, 0))
        UIStyle.filled_button(btn_frame, "Create User", self.create_user).pack(side="left")

    def load_users(self):
        def worker():
            response, error = self.api_client.get_users()
            if self._is_destroyed:
                return
            self.page.after(0, lambda: self._display_users(response, error))

        threading.Thread(target=worker, daemon=True).start()

    def _display_users(self, response, error):
        if error:
            return
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        users = response.get("users", []) if response else []
        for u in users:
            self.user_tree.insert("", "end", values=(u.get("user_id"), u.get("username"), u.get("role")))

    def create_user(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        role = self.role_var.get()
        staff_id = self.staff_id_var.get().strip()

        if not username or not password or not staff_id:
            messagebox.showerror("Error", "All fields are required.")
            return

        def worker():
            response, error = self.api_client.register_user(username, password, staff_id, role)
            if self._is_destroyed:
                return
            self.page.after(0, lambda: self._finish_create(response, error))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_create(self, response, error):
        if error:
            messagebox.showerror("Error", f"Failed to create user: {error}")
            return
        messagebox.showinfo("Success", f"User '{self.username_var.get()}' created successfully.")
        self.username_var.set("")
        self.password_var.set("")
        self.staff_id_var.set("")
        self.load_users()

    def destroy(self):
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
