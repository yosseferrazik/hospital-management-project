class Session:
    _instance = None
    token = None
    username = None
    role = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_token(self, token, username, role):
        self.token = token
        self.username = username
        self.role = role

    def clear(self):
        self.token = None
        self.username = None
        self.role = None

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
