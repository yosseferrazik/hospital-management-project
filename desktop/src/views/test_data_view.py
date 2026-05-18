import threading
import tkinter as tk
from tkinter import messagebox, ttk

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class TestDataView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.session = Session()
        self.api_client = APIClient(self.session)
        self._is_destroyed = False

        self.create_widgets()

    def create_widgets(self):
        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)
        UIStyle.section_header(
            self.page,
            "Dummy Data Tools",
            "Controlled generation and cleanup of sample hospital data through the backend service.",
        )

        content = tk.Frame(self.page, bg=UIStyle.BG)
        content.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        controls_shell, controls = UIStyle.panel(content, padx=18, pady=18)
        controls_shell.pack(fill="x", pady=(0, 12))

        tk.Label(
            controls,
            text="Seed database fixtures",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w")
        tk.Label(
            controls,
            text="This uses the backend dummy endpoints, so generated data stays consistent with relational constraints.",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
            justify="left",
        ).pack(anchor="w", pady=(4, 12))

        count_row = tk.Frame(controls, bg=UIStyle.CARD_BG)
        count_row.pack(fill="x", pady=(0, 10))
        tk.Label(
            count_row,
            text="Patient count:",
            font=UIStyle.FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(side="left")
        self.count_var = tk.StringVar(value="14")
        self.count_entry = ttk.Spinbox(
            count_row,
            from_=1,
            to=50000,
            textvariable=self.count_var,
            width=10,
            font=UIStyle.FONT,
        )
        self.count_entry.pack(side="left", padx=(8, 0))
        tk.Label(
            count_row,
            text="(1–50 000)",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(side="left", padx=(6, 0))

        buttons = tk.Frame(controls, bg=UIStyle.CARD_BG)
        buttons.pack(fill="x")
        UIStyle.filled_button(buttons, "Generate Dummy Data", self.generate_data).pack(
            side="left"
        )
        UIStyle.danger_button(buttons, "Clean Dummy Data", self.clear_data).pack(
            side="left", padx=(10, 0)
        )

        self.progress = ttk.Progressbar(content, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 12))

        log_shell, log = UIStyle.panel(content, padx=18, pady=18)
        log_shell.pack(fill="both", expand=True)
        tk.Label(
            log,
            text="Execution log",
            font=UIStyle.CARD_TITLE,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_DARK,
        ).pack(anchor="w")
        tk.Label(
            log,
            text="Keep an eye on generation and cleanup responses from the backend.",
            font=UIStyle.SUBTITLE_FONT,
            bg=UIStyle.CARD_BG,
            fg=UIStyle.TEXT_LIGHT,
        ).pack(anchor="w", pady=(4, 12))
        self.log_text = tk.Text(
            log,
            height=12,
            font=UIStyle.MONO_FONT,
            bg=UIStyle.SURFACE,
            fg=UIStyle.TEXT,
            relief="flat",
            padx=10,
            pady=10,
        )
        self.log_text.pack(fill="both", expand=True)

    def generate_data(self):
        try:
            count = int(self.count_var.get())
            count = max(1, min(count, 50000))
        except ValueError:
            count = 14
        self._run_async(
            "Generating dummy data...",
            lambda: self.api_client.generate_dummy(count=count),
            f"Dummy data generated successfully ({count} patients).",
        )

    def clear_data(self):
        if not messagebox.askyesno(
            "Confirm cleanup",
            "This will remove dummy records registered by the backend. Continue?",
        ):
            return
        self._run_async(
            "Cleaning dummy data...",
            self.api_client.cleanup_dummy,
            "Dummy data removed successfully.",
        )

    def _run_async(self, start_message, action, success_message):
        self.log(start_message)
        self.progress.start()

        def worker():
            response, error = action()
            if self._is_destroyed or not self.page.winfo_exists():
                return
            self.page.after(
                0, lambda: self._finish_async(response, error, success_message)
            )

        threading.Thread(target=worker, daemon=True).start()

    def _finish_async(self, response, error, success_message):
        self.progress.stop()
        if error:
            self.log(f"Error: {error}")
            messagebox.showerror("Error", error)
            return
        payload_message = (
            response.get("message") if isinstance(response, dict) else None
        )
        self.log(payload_message or success_message)
        messagebox.showinfo("Success", payload_message or success_message)

    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def destroy(self):
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
