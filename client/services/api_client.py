import requests
import json

API_BASE_URL = "http://localhost:5000/api"


class APIClient:
    def __init__(self, session):
        self.session = session

    def _request(self, method, endpoint, data=None):
        url = f"{API_BASE_URL}{endpoint}"
        headers = self.session.get_headers()
        headers["Content-Type"] = "application/json"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, json=data)
            else:
                return None, f"Unsupported method: {method}"

            if response.status_code in [200, 201]:
                return response.json(), None
            else:
                error_data = response.json()
                return None, error_data.get("error", f"Error {response.status_code}")
        except requests.exceptions.ConnectionError:
            return (
                None,
                "Could not connect to server. Is the backend running?",
            )
        except Exception as e:
            return None, str(e)

    # Auth endpoints
    def login(self, username, password):
        return self._request(
            "POST", "/auth/login", {"username": username, "password": password}
        )

    def register(self, username, password, staff_id, role):
        return self._request(
            "POST",
            "/auth/register",
            {
                "username": username,
                "password": password,
                "staff_id": staff_id,
                "role": role,
            },
        )

    # Staff endpoints
    def add_medical_staff(self, data):
        return self._request("POST", "/maintenance/staff/medical", data)

    def add_nursing_staff(self, data):
        return self._request("POST", "/maintenance/staff/nursing", data)

    def add_general_staff(self, data):
        return self._request("POST", "/maintenance/staff/general", data)

    def add_patient(self, data):
        return self._request("POST", "/maintenance/patients", data)

    def assign_nursing(self, nurse_id, doctor_id=None, floor_id=None):
        data = {"nurse_id": nurse_id}
        if doctor_id:
            data["doctor_id"] = doctor_id
        if floor_id:
            data["floor_id"] = floor_id
        return self._request("PUT", "/maintenance/nursing/assign", data)

    def get_surgeries_by_date(self, date):
        return self._request("GET", "/maintenance/surgeries", {"date": date})

    def get_visits_by_date(self, date):
        return self._request("GET", "/maintenance/visits/scheduled", {"date": date})

    # Dummy data
    def generate_dummy(self):
        return self._request("POST", "/dummy/generate", {})

    def cleanup_dummy(self):
        return self._request("DELETE", "/dummy/cleanup", {})
