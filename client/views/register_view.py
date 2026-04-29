import tkinter as tk
from tkinter import messagebox, ttk
from services.api_client import APIClient
from utils.session import Session


class RegisterView:
    # ── Paleta de diseño ──
    BG = "#f0f2f5"
    CARD_BG = "#ffffff"
    SHADOW = "#d1d5db"
    ACCENT = "#2563eb"
    ACCENT_HOVER = "#1d4ed8"
    TEXT_DARK = "#1f2937"
    TEXT_LIGHT = "#6b7280"
    BORDER = "#d1d5db"
    FOCUS_BORDER = "#2563eb"
    ERROR_RED = "#ef4444"
    SUCCESS_GREEN = "#10b981"
    CARD_WIDTH = 460

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())
        self.show_password = False
        self.show_confirm = False

        self.frame = tk.Frame(parent, bg=self.BG)
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Centrar todo el contenido
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        center = tk.Frame(self.frame, bg=self.BG)
        center.grid(row=0, column=0, sticky="nsew")
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=1)

        card_wrapper = tk.Frame(center, bg=self.BG)
        card_wrapper.grid(row=0, column=0)

        # Sombra de la tarjeta
        shadow = tk.Frame(card_wrapper, bg=self.SHADOW,
                          width=self.CARD_WIDTH + 8, height=300)
        shadow.pack(pady=4)
        shadow.pack_propagate(False)

        card = tk.Frame(shadow, bg=self.CARD_BG, width=self.CARD_WIDTH)
        card.place(relx=0.5, rely=0.5, anchor="center", x=-2, y=-3)

        form = tk.Frame(card, bg=self.CARD_BG)
        form.pack(fill="both", expand=True, padx=35, pady=30)
        form.columnconfigure(0, weight=1)

        # Icono y títulos
        tk.Label(form, text="🏥", font=("Segoe UI", 36),
                 bg=self.CARD_BG, fg=self.ACCENT).grid(row=0, column=0, pady=(0, 5))

        tk.Label(form, text="Create an account",
                 font=("Segoe UI", 22, "bold"),
                 bg=self.CARD_BG, fg=self.TEXT_DARK).grid(row=1, column=0)

        tk.Label(form, text="Hospital Management System",
                 font=("Segoe UI", 12),
                 bg=self.CARD_BG, fg=self.TEXT_LIGHT).grid(row=2, column=0, pady=(2, 20))

        # ── Campos de entrada ──
        self.username_frame, self.username_entry = self._create_input_row(
            form, row=3, label="Username", placeholder="Choose a username"
        )

        self.pass_frame, self.pass_entry, self.pass_toggle = self._create_password_row(
            form, row=5, label="Password", placeholder="Create a password"
        )

        self.confirm_frame, self.confirm_entry, self.confirm_toggle = self._create_password_row(
            form, row=7, label="Confirm password", placeholder="Repeat the password"
        )

        self.staff_frame, self.staff_entry = self._create_input_row(
            form, row=9, label="Staff ID", placeholder="Enter your staff ID"
        )

        # ── Rol (Combobox estilizado) ──
        tk.Label(form, text="Role", font=("Segoe UI", 11),
                 bg=self.CARD_BG, fg=self.TEXT_DARK, anchor="w").grid(
            row=11, column=0, sticky="w", pady=(15, 2))

        role_container = tk.Frame(form, bg=self.CARD_BG)
        role_container.grid(row=12, column=0, sticky="ew", pady=(0, 10))

        self.role_var = tk.StringVar(value="Select a role")
        roles = ["ADMIN", "DOCTOR", "NURSE", "STAFF", "RECEPTIONIST"]

        self.role_menu = tk.OptionMenu(
            role_container, self.role_var, *roles,
            command=self._on_role_select
        )
        self.role_menu.config(
            font=("Segoe UI", 12),
            bg=self.CARD_BG,
            fg=self.TEXT_LIGHT,
            activebackground=self.CARD_BG,
            activeforeground=self.TEXT_DARK,
            relief="flat",
            highlightthickness=0,
            anchor="w",
            width=30
        )
        self.role_menu["menu"].config(
            font=("Segoe UI", 11),
            bg=self.CARD_BG,
            fg=self.TEXT_DARK,
            activebackground="#e2e8f0",
            relief="flat"
        )
        self.role_menu.pack(fill="x", ipady=4)

        # Mensaje dinámico (error/éxito)
        self.message_label = tk.Label(
            form, text="", font=("Segoe UI", 10),
            bg=self.CARD_BG, fg=self.ERROR_RED, anchor="w"
        )
        self.message_label.grid(row=13, column=0, pady=(5, 10), sticky="ew")
        self.message_label.grid_remove()

        # ── Botones ──
        btn_frame = tk.Frame(form, bg=self.CARD_BG)
        btn_frame.grid(row=14, column=0, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)

        register_btn = tk.Button(
            btn_frame, text="Register", font=("Segoe UI", 11, "bold"),
            bg=self.ACCENT, fg="white",
            activebackground=self.ACCENT_HOVER, activeforeground="white",
            relief="flat", borderwidth=0, padx=20, pady=10,
            cursor="hand2", command=self.do_register
        )
        register_btn.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        back_btn = tk.Button(
            btn_frame, text="← Back to login", font=("Segoe UI", 11),
            bg=self.CARD_BG, fg=self.TEXT_LIGHT,
            activebackground="#f3f4f6", activeforeground=self.TEXT_DARK,
            relief="flat", borderwidth=0,
            highlightbackground=self.BORDER, highlightthickness=1,
            padx=20, pady=10, cursor="hand2",
            command=self.app.show_login
        )
        back_btn.grid(row=1, column=0, sticky="ew")

        # Ajustar altura de la sombra
        form.update_idletasks()
        card_height = form.winfo_reqheight() + 40
        shadow.config(height=card_height + 8)

        # Atajos y limpieza de mensaje al escribir
        self._bind_clear_message(self.username_entry)
        self._bind_clear_message(self.pass_entry)
        self._bind_clear_message(self.confirm_entry)
        self._bind_clear_message(self.staff_entry)

    def _create_input_row(self, parent, row, label, placeholder=""):
        """Fila con etiqueta y campo subrayado (estilo login)."""
        tk.Label(parent, text=label, font=("Segoe UI", 11),
                 bg=self.CARD_BG, fg=self.TEXT_DARK, anchor="w").grid(
            row=row, column=0, sticky="w", pady=(15, 2))

        input_frame = tk.Frame(parent, bg=self.CARD_BG)
        input_frame.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))

        underline = tk.Frame(input_frame, height=2, bg=self.BORDER)
        underline.pack(side="bottom", fill="x")

        entry = tk.Entry(
            input_frame, font=("Segoe UI", 12),
            bg=self.CARD_BG, fg=self.TEXT_DARK,
            relief="flat", highlightthickness=0,
            insertbackground=self.TEXT_DARK
        )
        entry.pack(fill="x", ipady=6, pady=(0, 1))

        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=self.TEXT_LIGHT)

            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, "end")
                    entry.config(fg=self.TEXT_DARK)
                underline.config(bg=self.FOCUS_BORDER)

            def on_focus_out(e):
                if entry.get() == "":
                    entry.insert(0, placeholder)
                    entry.config(fg=self.TEXT_LIGHT)
                underline.config(bg=self.BORDER)

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        else:
            def on_focus_in(e):
                underline.config(bg=self.FOCUS_BORDER)
            def on_focus_out(e):
                underline.config(bg=self.BORDER)
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        return input_frame, entry

    def _create_password_row(self, parent, row, label, placeholder=""):
        """Fila de contraseña con botón de visibilidad (estilo login)."""
        tk.Label(parent, text=label, font=("Segoe UI", 11),
                 bg=self.CARD_BG, fg=self.TEXT_DARK, anchor="w").grid(
            row=row, column=0, sticky="w", pady=(15, 2))

        input_frame = tk.Frame(parent, bg=self.CARD_BG)
        input_frame.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))

        underline = tk.Frame(input_frame, height=2, bg=self.BORDER)
        underline.pack(side="bottom", fill="x")

        inner = tk.Frame(input_frame, bg=self.CARD_BG)
        inner.pack(fill="x", pady=(0, 1))

        entry = tk.Entry(
            inner, font=("Segoe UI", 12),
            bg=self.CARD_BG, fg=self.TEXT_DARK,
            relief="flat", highlightthickness=0,
            insertbackground=self.TEXT_DARK
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6)

        # Botón de visibilidad (creado sin comando para evitar error de ámbito)
        toggle_btn = tk.Button(
            inner, text="👁", font=("Segoe UI", 10),
            bg=self.CARD_BG, fg=self.TEXT_LIGHT,
            activebackground=self.CARD_BG, activeforeground=self.ACCENT,
            relief="flat", borderwidth=0, cursor="hand2"
        )
        toggle_btn.pack(side="right", padx=(5, 0))

        # Asignar el comando después de que toggle_btn ya esté definido
        toggle_btn.config(
            command=lambda e=entry, b=toggle_btn, lbl=label: self._toggle_password_btn(e, b, lbl)
        )

        # Placeholder
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=self.TEXT_LIGHT, show="")

            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, "end")
                    entry.config(fg=self.TEXT_DARK)
                    if label == "Password" and not self.show_password:
                        entry.config(show="•")
                    elif label == "Confirm password" and not self.show_confirm:
                        entry.config(show="•")
                underline.config(bg=self.FOCUS_BORDER)

            def on_focus_out(e):
                if entry.get() == "":
                    entry.insert(0, placeholder)
                    entry.config(fg=self.TEXT_LIGHT, show="")
                    if label == "Password":
                        self.show_password = False
                        toggle_btn.config(text="👁")
                    else:
                        self.show_confirm = False
                        toggle_btn.config(text="👁")
                underline.config(bg=self.BORDER)

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        else:
            entry.config(show="•")
            def on_focus_in(e):
                underline.config(bg=self.FOCUS_BORDER)
            def on_focus_out(e):
                underline.config(bg=self.BORDER)
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        return input_frame, entry, toggle_btn

    def _toggle_password_btn(self, entry, btn, label):
        """Alterna visibilidad de la contraseña correspondiente."""
        if label == "Password":
            self.show_password = not self.show_password
            show = self.show_password
        else:
            self.show_confirm = not self.show_confirm
            show = self.show_confirm

        if entry.get() in ("", "Create a password", "Repeat the password"):
            return

        if show:
            entry.config(show="")
            btn.config(text="🙈")
        else:
            entry.config(show="•")
            btn.config(text="👁")

    def _on_role_select(self, value):
        """Callback al seleccionar un rol, cambia el color del texto."""
        if value != "Select a role":
            self.role_menu.config(fg=self.TEXT_DARK)

    def _bind_clear_message(self, widget):
        widget.bind("<Key>", lambda e: self._clear_message())

    def _clear_message(self):
        if self.message_label.winfo_ismapped():
            self.message_label.grid_remove()

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

        response, error = self.api_client.register(username, password, staff_id, role)

        if error:
            self._show_message(f"Registration failed: {error}", error=True)
            return

        self._show_message(f"User {username} registered successfully!", success=True)
        self.frame.after(1000, self.app.show_login)

    def _show_message(self, text, error=False, success=False):
        color = self.ERROR_RED if error else self.SUCCESS_GREEN if success else self.TEXT_LIGHT
        self.message_label.config(text=text, fg=color)
        self.message_label.grid()

    def destroy(self):
        self.frame.destroy()