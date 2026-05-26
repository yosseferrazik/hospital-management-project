"""HTTP API client for communicating with the backend server."""

import time
import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL") or "http://100.78.155.2:5000/api"


class APIClient:
    """Handles authenticated HTTP requests with optional response caching."""

    def __init__(self, session):
        self.session = session
        self.http = requests.Session()
        self.timeout = 300
        self._cache = {}
        self._cache_ttl = 20

    def _request(self, method, endpoint, data=None, params=None, timeout=None):
        """Execute an HTTP request and return (data, error)."""
        url = f"{API_BASE_URL}{endpoint}"
        headers = self.session.get_headers()
        headers["Content-Type"] = "application/json"

        try:
            request_args = {"headers": headers, "timeout": timeout or self.timeout}
            if method == "GET":
                request_args["params"] = params or data
                response = self.http.get(url, **request_args)
            elif method == "POST":
                request_args["json"] = data
                response = self.http.post(url, **request_args)
            elif method == "PUT":
                request_args["json"] = data
                response = self.http.put(url, **request_args)
            elif method == "DELETE":
                request_args["json"] = data
                response = self.http.delete(url, **request_args)
            else:
                return None, f"Unsupported method: {method}"

            if response.status_code in [200, 201]:
                if not response.content:
                    return {}, None
                return response.json(), None

            try:
                payload = response.json()
            except ValueError:
                payload = {}
            return None, payload.get("error", f"Error {response.status_code}")
        except requests.exceptions.ConnectionError:
            return None, "Could not connect to server. Is the backend running?"
        except requests.exceptions.Timeout:
            return None, "The server took too long to respond."
        except Exception as e:
            return None, str(e)

    def _cache_key(self, endpoint, params=None):
        """Generate a normalized cache key from endpoint and query params."""
        normalized_params = tuple(sorted((params or {}).items()))
        return endpoint, normalized_params

    def _get_cached(self, endpoint, params=None):
        """Return cached response if still within TTL, else None."""
        key = self._cache_key(endpoint, params)
        cached = self._cache.get(key)
        if not cached:
            return None
        if time.time() - cached["ts"] > self._cache_ttl:
            self._cache.pop(key, None)
            return None
        return cached["value"]

    def _set_cached(self, endpoint, params, value):
        """Store a response in the cache with the current timestamp."""
        self._cache[self._cache_key(endpoint, params)] = {
            "value": value,
            "ts": time.time(),
        }

    def invalidate(self, endpoint=None):
        """Clear cache for a specific endpoint or the entire cache."""
        if endpoint is None:
            self._cache.clear()
            return
        for key in list(self._cache.keys()):
            if key[0] == endpoint:
                self._cache.pop(key, None)

    def list_resource(self, endpoint, params=None, force_refresh=False):
        """GET a list from an endpoint with optional caching."""
        if not force_refresh:
            cached = self._get_cached(endpoint, params)
            if cached is not None:
                return cached, None
        response, error = self._request("GET", endpoint, params=params)
        if not error:
            self._set_cached(endpoint, params, response)
        return response, error

    def get_resource(self, endpoint, resource_id):
        """GET a single resource by ID."""
        return self._request("GET", f"{endpoint}/{resource_id}")

    def request_path(self, method, path, data=None, params=None):
        """Send a request to an arbitrary path with the given method."""
        return self._request(method, path, data=data, params=params)

    def create_resource(self, endpoint, data):
        """POST to create a resource, invalidating the list cache."""
        response, error = self._request("POST", endpoint, data=data)
        if not error:
            self.invalidate(endpoint)
        return response, error

    def update_resource(self, endpoint, item_id, data):
        """PUT to update a resource by ID, invalidating the list cache."""
        response, error = self._request("PUT", f"{endpoint}/{item_id}", data=data)
        if not error:
            self.invalidate(endpoint)
        return response, error

    def update_resource_path(self, endpoint, path_suffix, data):
        """PUT to update a resource at a custom path suffix."""
        response, error = self._request("PUT", f"{endpoint}/{path_suffix}", data=data)
        if not error:
            self.invalidate(endpoint)
        return response, error

    def delete_resource(self, endpoint, item_id):
        """DELETE a resource by ID, invalidating the list cache."""
        response, error = self._request("DELETE", f"{endpoint}/{item_id}")
        if not error:
            self.invalidate(endpoint)
        return response, error

    def delete_resource_path(self, endpoint, path_suffix):
        """DELETE a resource at a custom path suffix."""
        response, error = self._request("DELETE", f"{endpoint}/{path_suffix}")
        if not error:
            self.invalidate(endpoint)
        return response, error

    def login(self, username, password):
        """Authenticate with username/password, returns JWT token."""
        return self._request(
            "POST", "/auth/login", data={"username": username, "password": password}
        )

    def add_medical_staff(self, data):
        """Create a medical staff member (doctor)."""
        response, error = self._request("POST", "/maintenance/staff/medical", data=data)
        if not error:
            self.invalidate("/staff")
        return response, error

    def add_nursing_staff(self, data):
        """Create a nursing staff member."""
        response, error = self._request("POST", "/maintenance/staff/nursing", data=data)
        if not error:
            self.invalidate("/staff")
        return response, error

    def add_general_staff(self, data):
        """Create a general/administrative staff member."""
        response, error = self._request("POST", "/maintenance/staff/general", data=data)
        if not error:
            self.invalidate("/staff")
        return response, error

    def add_patient(self, data):
        """Create a new patient record."""
        response, error = self._request("POST", "/maintenance/patients", data=data)
        if not error:
            self.invalidate("/patients")
        return response, error

    def assign_nursing(self, nurse_id, doctor_id=None, floor_id=None):
        """Assign a nurse to a doctor or a floor."""
        data = {"nurse_id": nurse_id}
        if doctor_id:
            data["doctor_id"] = doctor_id
        if floor_id:
            data["floor_id"] = floor_id
        return self._request("PUT", "/maintenance/nursing/assign", data=data)

    def get_surgeries_by_date(self, date):
        """Fetch surgeries scheduled for a specific date."""
        return self._request("GET", "/maintenance/surgeries", params={"date": date})

    def get_visits_by_date(self, date):
        """Fetch scheduled visits for a specific date."""
        return self._request(
            "GET", "/maintenance/visits/scheduled", params={"date": date}
        )

    def generate_dummy(self, count=14):
        """Generate dummy test data."""
        return self._request("POST", "/dummy/generate", data={"count": count}, timeout=1800)

    def cleanup_dummy(self):
        """Remove all previously generated dummy data."""
        return self._request("DELETE", "/dummy/cleanup", data={})

    def get_all_staff(self, force_refresh=False):
        """Fetch all staff records."""
        return self.list_resource("/staff", force_refresh=force_refresh)

    def get_all_floors(self, force_refresh=False):
        """Fetch all floors."""
        return self.list_resource("/floors", force_refresh=force_refresh)

    def get_all_rooms(self, force_refresh=False):
        """Fetch all rooms."""
        return self.list_resource("/rooms", force_refresh=force_refresh)

    def get_all_operating_theaters(self, force_refresh=False):
        """Fetch all operating theaters."""
        return self.list_resource("/operating_theaters", force_refresh=force_refresh)

    def get_all_visits(self, force_refresh=False):
        """Fetch all visits."""
        return self.list_resource("/visits", force_refresh=force_refresh)

    def get_all_prescriptions(self, force_refresh=False):
        """Fetch all prescriptions."""
        return self.list_resource("/prescriptions", force_refresh=force_refresh)

    def register_user(self, username, password, staff_id, role):
        """Register a new application user."""
        return self._request(
            "POST", "/auth/register",
            data={"username": username, "password": password, "staff_id": staff_id, "role": role},
        )

    def get_users(self):
        """Fetch all registered app users."""
        return self._request("GET", "/auth/users")

    def get_audit_logs(self, params=None):
        """Fetch audit log entries with optional filters."""
        return self._request("GET", "/audit-logs", params=params)

    def get_audit_retention(self):
        """Get audit log retention configuration."""
        return self._request("GET", "/audit-logs/retention")

    def cleanup_audit_logs(self, days=90):
        """Delete audit logs older than the specified days."""
        return self._request("DELETE", f"/audit-logs/cleanup?days={days}")

    def get_audit_diagnostics(self):
        """Check audit trigger installation status."""
        return self._request("GET", "/audit-logs/diagnostics")

    def change_own_password(self, old_password, new_password):
        """Change the current user's password."""
        return self._request("PUT", "/auth/change-password", data={"old_password": old_password, "new_password": new_password})

    def admin_reset_password(self, user_id, new_password):
        """Admin: reset another user's password."""
        return self._request("PUT", f"/auth/users/{user_id}/password", data={"new_password": new_password})

    def admin_toggle_active(self, user_id):
        """Admin: enable or disable a user account."""
        return self._request("PUT", f"/auth/users/{user_id}/toggle-active")

    def get_report_visits(self, start_date=None, end_date=None, specialty=None, doctor_id=None):
        """Fetch visits report data."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if specialty: params["specialty"] = specialty
        if doctor_id: params["doctor_id"] = doctor_id
        return self._request("GET", "/reports/visits", params=params)

    def get_report_surgeries(self, start_date=None, end_date=None, procedure_type=None, surgeon_id=None):
        """Fetch surgeries report data."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if procedure_type: params["procedure_type"] = procedure_type
        if surgeon_id: params["surgeon_id"] = surgeon_id
        return self._request("GET", "/reports/surgeries", params=params)

    def get_report_admissions(self, start_date=None, end_date=None, floor_id=None):
        """Fetch admissions report data."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if floor_id: params["floor_id"] = floor_id
        return self._request("GET", "/reports/admissions", params=params)

    def get_report_medications(self, start_date=None, end_date=None):
        """Fetch medication report data."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "/reports/medications", params=params)

    def get_report_financial(self, start_date=None, end_date=None):
        """Fetch financial report data."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "/reports/financial", params=params)

    def get_report_radiology(self, start_date=None, end_date=None, status=None):
        """Fetch radiology report data."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if status: params["status"] = status
        return self._request("GET", "/reports/radiology", params=params)

    def get_report_doctor_workload(self, start_date=None, end_date=None):
        """Fetch doctor workload report data."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "/reports/doctor-workload", params=params)

    def get_report_summary(self, start_date=None, end_date=None):
        """Fetch summary report data."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "/reports/summary", params=params)

    def download_summary_pdf(self, start_date=None, end_date=None, save_path=None):
        """Download the summary PDF report, optionally saving to a file."""
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        url = f"{API_BASE_URL}/reports/summary/pdf"
        headers = self.session.get_headers()
        try:
            resp = self.http.get(url, headers=headers, params=params, timeout=60)
            if resp.status_code == 200:
                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(resp.content)
                    return save_path, None
                return resp.content, None
            try:
                payload = resp.json()
                return None, payload.get("error", f"Error {resp.status_code}")
            except Exception:
                return None, f"Error {resp.status_code}"
        except requests.exceptions.ConnectionError:
            return None, "Could not connect to server."
        except Exception as e:
            return None, str(e)
