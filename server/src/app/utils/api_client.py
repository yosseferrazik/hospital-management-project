"""External API client — forwards visit data to an external endpoint."""

import requests
from flask import current_app


def send_visits(data, format="json"):
    """POST visit data (JSON or XML) to the configured external API."""
    url = current_app.config.get("EXTERNAL_API_URL")
    username = current_app.config.get("EXTERNAL_API_USERNAME")
    password = current_app.config.get("EXTERNAL_API_PASSWORD")
    if not url:
        raise RuntimeError("EXTERNAL_API_URL not configured")
    headers = {"Content-Type": "application/xml" if format == "xml" else "application/json"}
    auth = (username, password) if username and password else None
    resp = requests.post(url, data=data, headers=headers, auth=auth, timeout=30)
    resp.raise_for_status()
    return resp
