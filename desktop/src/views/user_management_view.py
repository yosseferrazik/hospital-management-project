"""User management view for admin — create, toggle, reset passwords."""

import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class UserManagementView:
    """Admin panel for managing system users — create, toggle active status, reset passwords."""

    def __init__(self, parent, app):
        """Initialize user management view, build widgets, and load user list."""
        self.parent = parent
        self.app = app
        self.session = Session()
        self.api_client = APIClient(self.session)
        self._is_destroyed = False

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        """Build user list panel, create user form, and manage selected user panel."""
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

        columns = ("user_id", "username", "role", "active")
        self.user_tree = ttk.Treeview(list_body, columns=columns, show="headings")
        self.user_tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.user_tree.heading("user_id", text="ID")
        self.user_tree.heading("username", text="Username")
        self.user_tree.heading("role", text="Role")
        self.user_tree.heading("active", text="Active")
        self.user_tree.column("user_id", width=50)
        self.user_tree.column("username", width=140)
        self.user_tree.column("role", width=100)
        self.user_tree.column("active", width=60, anchor="center")
        self.user_tree.bind("<<TreeviewSelect>>", self._on_user_select)

        right = tk.Frame(main, bg=UIStyle.BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        form_shell, form_body = UIStyle.panel(right, padx=18, pady=18)
        form_shell.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

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

        manage_shell, manage_body = UIStyle.panel(right, padx=18, pady=18)
        manage_shell.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        tk.Label(manage_body, text="Manage Selected User", font=UIStyle.CARD_TITLE, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK).pack(anchor="w")
        self.selected_user_label = tk.Label(
            manage_body, text="No user selected", font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT,
        )
        self.selected_user_label.pack(anchor="w", pady=(4, 12))
        manage_btn_row = tk.Frame(manage_body, bg=UIStyle.CARD_BG)
        manage_btn_row.pack(fill="x")
        self.toggle_btn = UIStyle.secondary_button(manage_btn_row, "Toggle Active", self._toggle_active)
        self.toggle_btn.pack(side="left", padx=(0, 8))
        self.reset_pw_btn = UIStyle.filled_button(manage_btn_row, "Reset Password", self._reset_password)
        self.reset_pw_btn.pack(side="left")
        self.toggle_btn.config(state="disabled")
        self.reset_pw_btn.config(state="disabled")

    def _on_user_select(self, _event=None):
        """Handle user selection in the treeview and enable management buttons."""
        selection = self.user_tree.selection()
        if not selection:
            self.toggle_btn.config(state="disabled")
            self.reset_pw_btn.config(state="disabled")
            self.selected_user_label.config(text="No user selected")
            return
        values = self.user_tree.item(selection[0], "values")
        if not values:
            return
        active_text = "Yes" if values[3] == "Yes" else "No"
        self.selected_user_label.config(text="User #" + str(values[0]) + ": " + values[1] + " (" + values[2] + ") - Active: " + active_text)
        self.toggle_btn.config(state="normal")
        self.reset_pw_btn.config(state="normal")
        self._selected_user_id = int(values[0])

    def _toggle_active(self):
        """Toggle the active status of the selected user."""
        if not hasattr(self, "_selected_user_id"):
            return
        def worker():
            response, error = self.api_client.admin_toggle_active(self._selected_user_id)
            if self._is_destroyed:
                return
            self.page.after(0, lambda: self._finish_toggle(response, error))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_toggle(self, response, error):
        """Show toggle result message and reload user list."""
        if error:
            messagebox.showerror("Error", "Failed to toggle: " + error)
            return
        messagebox.showinfo("Success", response.get("message", "Account toggled"))
        self.load_users()

    def _reset_password(self):
        """Prompt for new password and send reset request for the selected user."""
        if not hasattr(self, "_selected_user_id"):
            return
        new_pw = simpledialog.askstring("Reset Password", "Enter new password:", parent=self.page, show="*")
        if not new_pw:
            return
        def worker():
            response, error = self.api_client.admin_reset_password(self._selected_user_id, new_pw)
            if self._is_destroyed:
                return
            self.page.after(0, lambda: self._finish_reset_pw(response, error))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_reset_pw(self, response, error):
        """Show password reset result message."""
        if error:
            messagebox.showerror("Error", "Failed to reset password: " + error)
            return
        messagebox.showinfo("Success", "Password reset successfully")

    def load_users(self):
        """Fetch all users from the API in a background thread."""
        def worker():
            response, error = self.api_client.get_users()
            if self._is_destroyed:
                return
            self.page.after(0, lambda: self._display_users(response, error))
        threading.Thread(target=worker, daemon=True).start()

    def _display_users(self, response, error):
        """Populate the user treeview with fetched user data."""
        if error:
            return
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        users = response.get("users", []) if response else []
        for u in users:
            active = "Yes" if u.get("is_active", True) else "No"
            self.user_tree.insert("", "end", values=(u.get("user_id"), u.get("username"), u.get("role"), active))

    def create_user(self):
        """Validate and send new user registration request to the API."""
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
        """Show create result, clear form, and reload user list."""
        if error:
            messagebox.showerror("Error", "Failed to create user: " + error)
            return
        messagebox.showinfo("Success", "User '" + self.username_var.get() + "' created successfully.")
        self.username_var.set("")
        self.password_var.set("")
        self.staff_id_var.set("")
        self.load_users()

    def destroy(self):
        """Clean up user management view resources."""
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
