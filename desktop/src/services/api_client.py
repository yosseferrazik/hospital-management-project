import time
import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL") or "http://100.78.155.2:5000/api"


class APIClient:
    def __init__(self, session):
        self.session = session
        self.http = requests.Session()
        self.timeout = 300
        self._cache = {}
        self._cache_ttl = 20

    def _request(self, method, endpoint, data=None, params=None, timeout=None):
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
        normalized_params = tuple(sorted((params or {}).items()))
        return endpoint, normalized_params

    def _get_cached(self, endpoint, params=None):
        key = self._cache_key(endpoint, params)
        cached = self._cache.get(key)
        if not cached:
            return None
        if time.time() - cached["ts"] > self._cache_ttl:
            self._cache.pop(key, None)
            return None
        return cached["value"]

    def _set_cached(self, endpoint, params, value):
        self._cache[self._cache_key(endpoint, params)] = {
            "value": value,
            "ts": time.time(),
        }

    def invalidate(self, endpoint=None):
        if endpoint is None:
            self._cache.clear()
            return
        for key in list(self._cache.keys()):
            if key[0] == endpoint:
                self._cache.pop(key, None)

    def list_resource(self, endpoint, params=None, force_refresh=False):
        if not force_refresh:
            cached = self._get_cached(endpoint, params)
            if cached is not None:
                return cached, None
        response, error = self._request("GET", endpoint, params=params)
        if not error:
            self._set_cached(endpoint, params, response)
        return response, error

    def get_resource(self, endpoint, resource_id):
        return self._request("GET", f"{endpoint}/{resource_id}")

    def request_path(self, method, path, data=None, params=None):
        return self._request(method, path, data=data, params=params)

    def create_resource(self, endpoint, data):
        response, error = self._request("POST", endpoint, data=data)
        if not error:
            self.invalidate(endpoint)
        return response, error

    def update_resource(self, endpoint, item_id, data):
        response, error = self._request("PUT", f"{endpoint}/{item_id}", data=data)
        if not error:
            self.invalidate(endpoint)
        return response, error

    def update_resource_path(self, endpoint, path_suffix, data):
        response, error = self._request("PUT", f"{endpoint}/{path_suffix}", data=data)
        if not error:
            self.invalidate(endpoint)
        return response, error

    def delete_resource(self, endpoint, item_id):
        response, error = self._request("DELETE", f"{endpoint}/{item_id}")
        if not error:
            self.invalidate(endpoint)
        return response, error

    def delete_resource_path(self, endpoint, path_suffix):
        response, error = self._request("DELETE", f"{endpoint}/{path_suffix}")
        if not error:
            self.invalidate(endpoint)
        return response, error

    def login(self, username, password):
        return self._request(
            "POST", "/auth/login", data={"username": username, "password": password}
        )

    def register(self, username, password, staff_id, role):
        return self._request(
            "POST",
            "/auth/register",
            data={
                "username": username,
                "password": password,
                "staff_id": staff_id,
                "role": role,
            },
        )

    def add_medical_staff(self, data):
        response, error = self._request("POST", "/maintenance/staff/medical", data=data)
        if not error:
            self.invalidate("/staff")
        return response, error

    def add_nursing_staff(self, data):
        response, error = self._request("POST", "/maintenance/staff/nursing", data=data)
        if not error:
            self.invalidate("/staff")
        return response, error

    def add_general_staff(self, data):
        response, error = self._request("POST", "/maintenance/staff/general", data=data)
        if not error:
            self.invalidate("/staff")
        return response, error

    def add_patient(self, data):
        response, error = self._request("POST", "/maintenance/patients", data=data)
        if not error:
            self.invalidate("/patients")
        return response, error

    def assign_nursing(self, nurse_id, doctor_id=None, floor_id=None):
        data = {"nurse_id": nurse_id}
        if doctor_id:
            data["doctor_id"] = doctor_id
        if floor_id:
            data["floor_id"] = floor_id
        return self._request("PUT", "/maintenance/nursing/assign", data=data)

    def get_surgeries_by_date(self, date):
        return self._request("GET", "/maintenance/surgeries", params={"date": date})

    def get_visits_by_date(self, date):
        return self._request(
            "GET", "/maintenance/visits/scheduled", params={"date": date}
        )

    def generate_dummy(self, count=14):
        return self._request("POST", "/dummy/generate", data={"count": count}, timeout=300)

    def cleanup_dummy(self):
        return self._request("DELETE", "/dummy/cleanup", data={})

    def get_all_staff(self, force_refresh=False):
        return self.list_resource("/staff", force_refresh=force_refresh)

    def get_all_floors(self, force_refresh=False):
        return self.list_resource("/floors", force_refresh=force_refresh)

    def get_all_rooms(self, force_refresh=False):
        return self.list_resource("/rooms", force_refresh=force_refresh)

    def get_all_operating_theaters(self, force_refresh=False):
        return self.list_resource("/operating_theaters", force_refresh=force_refresh)

    def get_all_visits(self, force_refresh=False):
        return self.list_resource("/visits", force_refresh=force_refresh)

    def get_all_prescriptions(self, force_refresh=False):
        return self.list_resource("/prescriptions", force_refresh=force_refresh)

    def register_user(self, username, password, staff_id, role):
        return self._request(
            "POST", "/auth/register",
            data={"username": username, "password": password, "staff_id": staff_id, "role": role},
        )

    def get_users(self):
        return self._request("GET", "/auth/users")

    def get_audit_logs(self, params=None):
        return self._request("GET", "/audit-logs", params=params)

    def get_audit_retention(self):
        return self._request("GET", "/audit-logs/retention")

    def cleanup_audit_logs(self, days=90):
        return self._request("DELETE", f"/audit-logs/cleanup?days={days}")

    def get_staff_list(self):
        return self.list_resource("/staff", force_refresh=True)

    def change_own_password(self, old_password, new_password):
        return self._request("PUT", "/auth/change-password", data={"old_password": old_password, "new_password": new_password})

    def admin_reset_password(self, user_id, new_password):
        return self._request("PUT", f"/auth/users/{user_id}/password", data={"new_password": new_password})

    def admin_toggle_active(self, user_id):
        return self._request("PUT", f"/auth/users/{user_id}/toggle-active")

    def get_report_visits(self, start_date=None, end_date=None, specialty=None, doctor_id=None):
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if specialty: params["specialty"] = specialty
        if doctor_id: params["doctor_id"] = doctor_id
        return self._request("GET", "/reports/visits", params=params)

    def get_report_surgeries(self, start_date=None, end_date=None, procedure_type=None, surgeon_id=None):
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if procedure_type: params["procedure_type"] = procedure_type
        if surgeon_id: params["surgeon_id"] = surgeon_id
        return self._request("GET", "/reports/surgeries", params=params)

    def get_report_admissions(self, start_date=None, end_date=None, floor_id=None):
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if floor_id: params["floor_id"] = floor_id
        return self._request("GET", "/reports/admissions", params=params)

    def get_report_medications(self, start_date=None, end_date=None):
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "/reports/medications", params=params)

    def get_report_financial(self, start_date=None, end_date=None):
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "/reports/financial", params=params)

    def get_report_radiology(self, start_date=None, end_date=None, status=None):
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if status: params["status"] = status
        return self._request("GET", "/reports/radiology", params=params)

    def get_report_doctor_workload(self, start_date=None, end_date=None):
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "/reports/doctor-workload", params=params)

    def get_report_summary(self, start_date=None, end_date=None):
        params = {}
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        return self._request("GET", "/reports/summary", params=params)
