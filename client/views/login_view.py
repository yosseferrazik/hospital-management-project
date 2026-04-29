import tkinter as tk
from tkinter import messagebox
from services.api_client import APIClient
from utils.session import Session


class LoginView:  # Mantenemos el nombre original si es necesario
    BG = "#f0f2f5"
    CARD_BG = "#ffffff"
    SHADOW_COLOR = "#d1d5db"
    ACCENT = "#2563eb"
    ACCENT_HOVER = "#1d4ed8"
    TEXT_DARK = "#1f2937"
    TEXT_LIGHT = "#6b7280"
    BORDER = "#d1d5db"
    FOCUS_BORDER = "#2563eb"
    ERROR_RED = "#ef4444"
    SUCCESS_GREEN = "#10b981"
    CARD_WIDTH = 420

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())
        self.show_password = False

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

        # Contenedor para la tarjeta y su sombra
        card_wrapper = tk.Frame(center, bg=self.BG)
        card_wrapper.grid(row=0, column=0)

        # Sombra: un frame gris un poco más grande que la tarjeta
        shadow = tk.Frame(card_wrapper, bg=self.SHADOW_COLOR,
                          width=self.CARD_WIDTH + 8, height=300)
        shadow.pack(pady=4)  # pequeño margen vertical para que la sombra respire
        shadow.pack_propagate(False)

        # Tarjeta blanca
        card = tk.Frame(shadow, bg=self.CARD_BG, width=self.CARD_WIDTH)
        card.place(relx=0.5, rely=0.5, anchor="center", x=-2, y=-3)

        # Formulario
        form = tk.Frame(card, bg=self.CARD_BG)
        form.pack(fill="both", expand=True, padx=35, pady=30)
        form.columnconfigure(0, weight=1)

        # Icono
        tk.Label(form, text="🏥", font=("Segoe UI", 36),
                 bg=self.CARD_BG, fg=self.ACCENT).grid(row=0, column=0, pady=(0, 5))

        # Título
        tk.Label(form, text="Sa Palomera Hospital", font=("Segoe UI", 22, "bold"),
                 bg=self.CARD_BG, fg=self.TEXT_DARK).grid(row=1, column=0)

        # Subtítulo
        tk.Label(form, text="Hospital Management System", font=("Segoe UI", 12),
                 bg=self.CARD_BG, fg=self.TEXT_LIGHT).grid(row=2, column=0, pady=(2, 20))

        # ── Campos de entrada ──
        self.username_frame, self.username_entry = self._create_input_row(
            form, row=3, label="Username", placeholder="Enter your username"
        )

        self.password_frame, self.password_entry, self.toggle_btn = self._create_password_row(
            form, row=5, label="Password", placeholder="Enter password"
        )

        # ── Opciones adicionales ──
        options_frame = tk.Frame(form, bg=self.CARD_BG)
        options_frame.grid(row=7, column=0, pady=(6, 12), sticky="ew")

        self.remember_var = tk.BooleanVar()
        tk.Checkbutton(
            options_frame, text="Remember me", variable=self.remember_var,
            bg=self.CARD_BG, fg=self.TEXT_LIGHT,
            selectcolor=self.CARD_BG, activebackground=self.CARD_BG,
            activeforeground=self.TEXT_DARK, font=("Segoe UI", 10)
        ).pack(side="left")

        tk.Label(
            options_frame, text="Forgot password?",
            font=("Segoe UI", 10, "underline"), bg=self.CARD_BG,
            fg=self.ACCENT, cursor="hand2"
        ).pack(side="right")

        # ── Mensaje dinámico ──
        self.message_label = tk.Label(
            form, text="", font=("Segoe UI", 10),
            bg=self.CARD_BG, fg=self.ERROR_RED, anchor="w"
        )
        self.message_label.grid(row=8, column=0, pady=(0, 8), sticky="ew")
        self.message_label.grid_remove()

        # ── Botones ──
        btn_frame = tk.Frame(form, bg=self.CARD_BG)
        btn_frame.grid(row=9, column=0, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)

        login_btn = tk.Button(
            btn_frame, text="Sign in", font=("Segoe UI", 11, "bold"),
            bg=self.ACCENT, fg="white",
            activebackground=self.ACCENT_HOVER, activeforeground="white",
            relief="flat", borderwidth=0, padx=20, pady=10,
            cursor="hand2", command=self.do_login
        )
        login_btn.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        register_btn = tk.Button(
            btn_frame, text="Create an account", font=("Segoe UI", 11),
            bg=self.CARD_BG, fg=self.TEXT_LIGHT,
            activebackground="#f3f4f6", activeforeground=self.TEXT_DARK,
            relief="flat", borderwidth=0,
            highlightbackground=self.BORDER, highlightthickness=1,
            padx=20, pady=10, cursor="hand2",
            command=self.app.show_register
        )
        register_btn.grid(row=1, column=0, sticky="ew")

        # Ajustar altura de la sombra después de que todo se haya dibujado
        form.update_idletasks()
        card_height = form.winfo_reqheight() + 40  # margen extra
        shadow.config(height=card_height + 8)       # sombra 8px más alta que la tarjeta

        # ── Atajos de teclado + limpieza de mensajes al escribir ──
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.do_login())
        self.username_entry.bind("<Key>", lambda e: self._clear_message())
        self.password_entry.bind("<Key>", lambda e: self._clear_message())

    def _create_input_row(self, parent, row, label, placeholder=""):
        """Fila con etiqueta y campo subrayado."""
        tk.Label(
            parent, text=label, font=("Segoe UI", 11),
            bg=self.CARD_BG, fg=self.TEXT_DARK, anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=(15, 2))

        input_frame = tk.Frame(parent, bg=self.CARD_BG)
        input_frame.grid(row=row + 1, column=0, sticky="ew", pady=(0, 10))

        underline = tk.Frame(input_frame, height=2, bg=self.BORDER)
        underline.pack(side="bottom", fill="x")

        entry = tk.Entry(
            input_frame, font=("Segoe UI", 12),
            bg=self.CARD_BG, fg=self.TEXT_DARK,
            relief="flat", highlightthickness=0,
            insertbackground=self.TEXT_DARK
        )
        entry.pack(fill="x", ipady=6, pady=(0, 1))

        # Placeholder
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
        """Fila de contraseña con botón de visibilidad."""
        tk.Label(
            parent, text=label, font=("Segoe UI", 11),
            bg=self.CARD_BG, fg=self.TEXT_DARK, anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=(15, 2))

        input_frame = tk.Frame(parent, bg=self.CARD_BG)
        input_frame.grid(row=row + 1, column=0, sticky="ew", pady=(0, 10))

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

        toggle_btn = tk.Button(
            inner, text="👁", font=("Segoe UI", 10),
            bg=self.CARD_BG, fg=self.TEXT_LIGHT,
            activebackground=self.CARD_BG, activeforeground=self.ACCENT,
            relief="flat", borderwidth=0, cursor="hand2",
            command=lambda: self._toggle_password(entry, toggle_btn)
        )
        toggle_btn.pack(side="right", padx=(5, 0))

        # Placeholder
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=self.TEXT_LIGHT, show="")  # placeholder visible

            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, "end")
                    entry.config(fg=self.TEXT_DARK)
                    # Asegurar que el texto se oculte si no está visible
                    entry.config(show="•" if not self.show_password else "")
                underline.config(bg=self.FOCUS_BORDER)

            def on_focus_out(e):
                if entry.get() == "":
                    entry.insert(0, placeholder)
                    entry.config(fg=self.TEXT_LIGHT, show="")
                    # Resetear toggle visual al perder foco con campo vacío
                    self.show_password = False
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

    def _toggle_password(self, entry, btn):
        # Solo alterna si hay texto real (no el placeholder)
        if entry.get() == "Enter password" or entry.get() == "":
            return
        if self.show_password:
            entry.config(show="•")
            btn.config(text="👁")
            self.show_password = False
        else:
            entry.config(show="")
            btn.config(text="🙈")
            self.show_password = True

    def _clear_message(self):
        """Limpia el mensaje de error/éxito si está visible."""
        if self.message_label.winfo_ismapped():
            self.message_label.grid_remove()

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

        response, error = self.api_client.login(username, password)

        if error:
            self._show_message(f"Error: {error}", error=True)
            return

        if response and "access_token" in response:
            Session().set_token(response["access_token"], username, "")
            self._show_message("Welcome! Redirecting...", success=True)
            self.frame.after(800, self.app.show_main_menu)
        else:
            self._show_message("Invalid credentials.", error=True)

    def _show_message(self, text, error=False, success=False):
        color = self.ERROR_RED if error else self.SUCCESS_GREEN if success else self.TEXT_LIGHT
        self.message_label.config(text=text, fg=color)
        self.message_label.grid()

    def destroy(self):
        self.frame.destroy()