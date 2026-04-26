# Client

This directory contains the Tkinter desktop client for the Hospital Sa Palomera project.

## Responsibilities
* Provide the login and registration flow for application users.
* Offer maintenance screens for staff and patient registration.
* Display daily surgery and visit queries.
* Interact with the Flask backend through the API client layer.

## Main Structure
```text
client/
├── services/        # HTTP client for backend communication
├── utils/           # Session and client-side helpers
├── views/           # Tkinter screens and windows
└── main.py          # Desktop application entry point
```

## Notes
* The client currently uses English labels throughout the user interface.
* Authentication state is stored in the in-memory session helper under `client/utils/session.py`.
