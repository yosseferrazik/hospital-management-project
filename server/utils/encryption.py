import json
import os
from cryptography.fernet import Fernet
from flask import current_app

CRED_FILE = "login_credentials.enc"


def get_cipher():
    key = current_app.config["ENCRYPTION_KEY"].encode()
    return Fernet(key)


def save_credentials_to_file(username, password_hash_bcrypt):
    """Guardar usuari i contrasenya (hash bcrypt) en fitxer xifrat."""
    cipher = get_cipher()
    data = {}
    if os.path.exists(CRED_FILE):
        try:
            with open(CRED_FILE, "rb") as f:
                encrypted = f.read()
                decrypted = cipher.decrypt(encrypted)
                data = json.loads(decrypted.decode())
        except:
            pass
    data[username] = password_hash_bcrypt
    json_str = json.dumps(data)
    encrypted_data = cipher.encrypt(json_str.encode())
    with open(CRED_FILE, "wb") as f:
        f.write(encrypted_data)


def verify_credentials_from_file(username, password_bcrypt):
    cipher = get_cipher()
    if not os.path.exists(CRED_FILE):
        return False
    try:
        with open(CRED_FILE, "rb") as f:
            encrypted = f.read()
            decrypted = cipher.decrypt(encrypted)
            data = json.loads(decrypted.decode())
            stored_hash = data.get(username)
            if stored_hash:
                return stored_hash == password_bcrypt
    except:
        return False
    return False
