"""Singleton session — stores authentication token and user info."""


class Session:
    """Singleton that holds the current user's auth token, username, and role."""

    _instance = None
    token = None
    username = None
    role = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_token(self, token, username, role):
        """Store the JWT token and user details after login."""
        self.token = token
        self.username = username
        self.role = role

    def clear(self):
        """Clear session on logout."""
        self.token = None
        self.username = None
        self.role = None

    def get_headers(self):
        """Return HTTP Authorization header dict using the stored token."""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
