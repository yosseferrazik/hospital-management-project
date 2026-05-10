import threading
import tkinter as tk

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class RegisterView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())
        self.show_password = False
        self.show_confirm = False

        self.frame = UIStyle.page(parent)
        self.create_widgets()

    def create_widgets(self):
        scrollable, scroll_content = UIStyle.create_scrollable_area(
            self.frame, bg=UIStyle.BG
        )

        card_shell = tk.Frame(
            scroll_content,
            bg=UIStyle.CARD_BG,
            highlightbackground=UIStyle.BORDER,
            highlightthickness=1,
        )
        card_shell.pack(pady=30, padx=30, fill="both", expand=False)

        card = tk.Frame(card_shell, bg=UIStyle.CARD_BG)
        card.pack(padx=30, pady=28, fill="both", expand=False)

        tk.Label(
            card,
            text="Create an account",
            font=UIStyle.HEADER_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack()
        tk.Label(
            card,
            text="Hospital Management System",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(pady=(6, 18))

        self.username_entry = self._create_input_row(
            card, "Username", "Choose a username"
        )
        self.pass_entry = self._create_password_row(
            card, "Password", "Create a password", is_confirm=False
        )
        self.confirm_entry = self._create_password_row(
            card, "Confirm password", "Repeat the password", is_confirm=True
        )
        self.staff_entry = self._create_input_row(
            card, "Staff ID", "Enter your staff ID"
        )

        tk.Label(
            card,
            text="Role",
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
            anchor="w",
        ).pack(fill="x", pady=(12, 4))
        self.role_var = tk.StringVar(value="Select a role")
        self.role_menu = tk.OptionMenu(
            card, self.role_var, "ADMIN", "DOCTOR", "NURSE", "STAFF", "RECEPTIONIST"
        )
        self.role_menu.config(
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
            activebackground=UIStyle.SURFACE,
            activeforeground=UIStyle.TEXT_DARK,
            relief="flat",
            highlightthickness=1,
            highlightbackground=UIStyle.BORDER,
        )
        self.role_menu["menu"].config(
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
            activebackground=UIStyle.ACCENT_SOFT,
        )
        self.role_menu.pack(fill="x", pady=(0, 0))

        self.message_label = tk.Label(
            card,
            text="",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.ERROR_RED,
            anchor="w",
        )
        self.message_label.pack(fill="x", pady=(8, 10))
        self.message_label.pack_forget()

        buttons = tk.Frame(card, bg=UIStyle.CARD_BG)
        buttons.pack(fill="x", pady=(8, 0))

        self.register_btn = UIStyle.filled_button(buttons, "Register", self.do_register)
        self.register_btn.pack(fill="x", pady=(0, 8))
        UIStyle.secondary_button(buttons, "Back to login", self.app.show_login).pack(
            fill="x"
        )

        for widget in [
            self.username_entry,
            self.pass_entry,
            self.confirm_entry,
            self.staff_entry,
        ]:
            widget.bind("<Key>", lambda _e: self._clear_message())

    def _create_input_row(self, parent, label, placeholder):
        tk.Label(
            parent,
            text=label,
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
            anchor="w",
        ).pack(fill="x", pady=(12, 4))
        entry = UIStyle.form_entry(parent)
        entry.pack(fill="x", ipady=8, pady=(0, 0))
        entry.insert(0, placeholder)
        entry.config(fg=UIStyle.TEXT_LIGHT)

        def on_focus_in(_):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(fg=UIStyle.TEXT_DARK)

        def on_focus_out(_):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=UIStyle.TEXT_LIGHT)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        return entry

    def _create_password_row(self, parent, label, placeholder, *, is_confirm):
        tk.Label(
            parent,
            text=label,
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
            anchor="w",
        ).pack(fill="x", pady=(12, 4))
        shell = tk.Frame(parent, bg=UIStyle.CARD_BG)
        shell.pack(fill="x", ipady=8, pady=(0, 0))
        shell.columnconfigure(0, weight=1)

        entry = UIStyle.form_entry(shell)
        entry.pack(side="left", fill="both", expand=True, ipady=8)
        entry.insert(0, placeholder)
        entry.config(fg=UIStyle.TEXT_LIGHT)

        button = tk.Button(
            shell,
            text="Show",
            font=UIStyle.SMALL_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
            activebackground=UIStyle.CARD_BG,
            activeforeground=UIStyle.ACCENT,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
        )
        button.pack(side="right", padx=(8, 0))
        button.config(
            command=lambda: self._toggle_password(
                entry, button, placeholder, is_confirm
            )
        )

        def on_focus_in(_):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(
                    fg=UIStyle.TEXT_DARK,
                    show="" if self._is_visible(is_confirm) else "*",
                )

        def on_focus_out(_):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=UIStyle.TEXT_LIGHT, show="")
                self._set_visible(is_confirm, False)
                button.config(text="Show")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        return entry

    def _is_visible(self, is_confirm):
        return self.show_confirm if is_confirm else self.show_password

    def _set_visible(self, is_confirm, value):
        if is_confirm:
            self.show_confirm = value
        else:
            self.show_password = value

    def _toggle_password(self, entry, button, placeholder, is_confirm):
        if entry.get() in ("", placeholder):
            return
        visible = not self._is_visible(is_confirm)
        self._set_visible(is_confirm, visible)
        entry.config(show="" if visible else "*")
        button.config(text="Hide" if visible else "Show")

    def _clear_message(self):
        if self.message_label.winfo_ismapped():
            self.message_label.pack_forget()

    def do_register(self):
        username = self.username_entry.get().strip()
        password = self.pass_entry.get()
        confirm = self.confirm_entry.get()
        staff_id = self.staff_entry.get().strip()
        role = self.role_var.get()

        if username == "Choose a username":
            username = ""
        if password == "Create a password":
            password = ""
        if confirm == "Repeat the password":
            confirm = ""
        if staff_id == "Enter your staff ID":
            staff_id = ""
        if role == "Select a role":
            role = ""

        if not all([username, password, confirm, staff_id, role]):
            self._show_message("All fields are required.", error=True)
            return
        if password != confirm:
            self._show_message("Passwords do not match.", error=True)
            return

        self.register_btn.config(state="disabled", text="Registering...")

        def worker():
            response, error = self.api_client.register(
                username, password, staff_id, role
            )
            self.frame.after(
                0, lambda: self._finish_register(username, response, error)
            )

        threading.Thread(target=worker, daemon=True).start()

    def _finish_register(self, username, response, error):
        self.register_btn.config(state="normal", text="Register")
        if error:
            self._show_message(f"Registration failed: {error}", error=True)
            return
        if response is None:
            self._show_message("Registration failed.", error=True)
            return
        self._show_message(f"User {username} registered successfully!", success=True)
        self.frame.after(800, self.app.show_login)

    def _show_message(self, text, error=False, success=False):
        color = (
            UIStyle.ERROR_RED
            if error
            else UIStyle.SUCCESS_GREEN
            if success
            else UIStyle.TEXT_LIGHT
        )
        self.message_label.config(text=text, fg=color)
        self.message_label.pack(fill="x", pady=(8, 10))

    def destroy(self):
        self.frame.destroy()
