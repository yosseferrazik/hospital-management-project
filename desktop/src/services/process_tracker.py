"""Thread-safe singleton tracker for long-running background processes."""

import time
import threading


class ProcessTracker:
    """Tracks named processes (running/completed) for UI feedback."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._processes = []
        return cls._instance

    def start(self, name):
        """Register a new running process with the given name."""
        with self._lock:
            p = {"name": name, "status": "running", "message": None, "started": time.time()}
            self._processes.append(p)
            return p

    def end(self, proc, status="success", message=None):
        """Mark a process as completed with a status and optional message."""
        with self._lock:
            proc["status"] = status
            proc["message"] = message

    def running(self):
        """Return all currently running processes."""
        with self._lock:
            return [p for p in self._processes if p["status"] == "running"]

    def last_completed(self, n=3):
        """Return the last N completed processes."""
        with self._lock:
            done = [p for p in self._processes if p["status"] != "running"]
            return done[-n:]

    def clean_old(self, max_age=30):
        """Remove completed processes older than max_age seconds."""
        now = time.time()
        self._processes = [p for p in self._processes if p["status"] == "running" or now - p["started"] < max_age]
