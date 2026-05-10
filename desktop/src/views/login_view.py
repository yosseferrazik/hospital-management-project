import threading
import tkinter as tk

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class LoginView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())
        self.show_password = False

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
        card.pack(padx=30, pady=30, fill="both", expand=False)

        tk.Label(
            card,
            text="Sa Palomera Hospital",
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
        ).pack(pady=(6, 22))

        self.username_entry = self._create_input_row(
            card, "Username", "Enter your username"
        )
        self.password_entry = self._create_password_row(
            card, "Password", "Enter password"
        )

        self.message_label = tk.Label(
            card,
            text="",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.ERROR_RED,
            anchor="w",
        )
        self.message_label.pack(pady=(8, 10), fill="x")
        self.message_label.pack_forget()

        buttons = tk.Frame(card, bg=UIStyle.CARD_BG)
        buttons.pack(fill="x", pady=(8, 0))

        self.login_btn = UIStyle.filled_button(buttons, "Sign in", self.do_login)
        self.login_btn.pack(fill="x", pady=(0, 8))
        UIStyle.secondary_button(
            buttons, "Create an account", self.app.show_register
        ).pack(fill="x")

        self.username_entry.bind("<Return>", lambda _e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda _e: self.do_login())
        self.username_entry.bind("<Key>", lambda _e: self._clear_message())
        self.password_entry.bind("<Key>", lambda _e: self._clear_message())

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

    def _create_password_row(self, parent, label, placeholder):
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
            command=lambda: self._toggle_password(entry, button, placeholder),
        )
        button.pack(side="right", padx=(8, 0))

        def on_focus_in(_):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(
                    fg=UIStyle.TEXT_DARK, show="" if self.show_password else "*"
                )

        def on_focus_out(_):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=UIStyle.TEXT_LIGHT, show="")
                self.show_password = False
                button.config(text="Show")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        return entry

    def _toggle_password(self, entry, button, placeholder):
        if entry.get() in ("", placeholder):
            return
        self.show_password = not self.show_password
        entry.config(show="" if self.show_password else "*")
        button.config(text="Hide" if self.show_password else "Show")

    def _clear_message(self):
        if self.message_label.winfo_ismapped():
            self.message_label.pack_forget()

    def do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if username == "Enter your username":
            username = ""
        if password == "Enter password":
            password = ""
        if not username or not password:
            self._show_message("Please fill in both fields.", error=True)
            return

        self.login_btn.config(state="disabled", text="Signing in...")

        def worker():
            response, error = self.api_client.login(username, password)
            self.frame.after(0, lambda: self._finish_login(username, response, error))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_login(self, username, response, error):
        self.login_btn.config(state="normal", text="Sign in")
        if error:
            self._show_message(f"Error: {error}", error=True)
            return
        if response and "access_token" in response:
            Session().set_token(response["access_token"], username, "")
            self._show_message("Welcome! Redirecting...", success=True)
            self.frame.after(600, self.app.show_main_interface)
            return
        self._show_message("Invalid credentials.", error=True)

    def _show_message(self, text, error=False, success=False):
        color = (
            UIStyle.ERROR_RED
            if error
            else UIStyle.SUCCESS_GREEN
            if success
            else UIStyle.TEXT_LIGHT
        )
        self.message_label.config(text=text, fg=color)
        self.message_label.pack(pady=(8, 10), fill="x")

    def destroy(self):
        self.frame.destroy()
