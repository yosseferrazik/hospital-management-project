import time
import threading


class ProcessTracker:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._processes = []
        return cls._instance

    def start(self, name):
        with self._lock:
            p = {"name": name, "status": "running", "message": None, "started": time.time()}
            self._processes.append(p)
            return p

    def end(self, proc, status="success", message=None):
        with self._lock:
            proc["status"] = status
            proc["message"] = message

    def running(self):
        with self._lock:
            return [p for p in self._processes if p["status"] == "running"]

    def last_completed(self, n=3):
        with self._lock:
            done = [p for p in self._processes if p["status"] != "running"]
            return done[-n:]

    def clean_old(self, max_age=30):
        with self._lock:
            now = time.time()
            self._processes = [p for p in self._processes if now - p["started"] < max_age]
