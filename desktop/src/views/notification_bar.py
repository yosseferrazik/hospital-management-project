import tkinter as tk
from services.process_tracker import ProcessTracker
from utils.ui_style import UIStyle


class NotificationBar:
    def __init__(self, parent):
        self.parent = parent
        self.tracker = ProcessTracker()

        self.frame = tk.Frame(parent, bg=UIStyle.HEADER_BG, height=28)
        self.frame.grid_propagate(False)

        self.label = tk.Label(
            self.frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg=UIStyle.HEADER_BG,
            fg=UIStyle.HEADER_TEXT,
            anchor="w",
        )
        self.label.pack(side="left", padx=10)

        self._clear_after = None
        self._last_shown = None
        self._poll()

    def _poll(self):
        running = self.tracker.running()
        self.tracker.clean_old()

        if running:
            names = ", ".join(p["name"] for p in running)
            self.label.config(text=f"Running: {names}")
            if self._clear_after:
                self.frame.after_cancel(self._clear_after)
                self._clear_after = None
            self.frame.after(500, self._poll)
        elif self._clear_after:
            self.frame.after(500, self._poll)
        else:
            completed = self.tracker.last_completed(1)
            if completed:
                c = completed[-1]
                if c["started"] != self._last_shown:
                    msg = c.get("message") or c["name"]
                    icon = "OK" if c["status"] == "success" else "FAIL"
                    self.label.config(text=f"{icon} {msg}")
                    self._last_shown = c["started"]
                    self._clear_after = self.frame.after(5000, self._clear)
                    self.frame.after(500, self._poll)
                    return
            self.label.config(text="Ready")
            self.frame.after(2000, self._poll)

    def _clear(self):
        self._clear_after = None
        self._poll()
