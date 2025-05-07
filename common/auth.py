import json
import hashlib
from pathlib import Path

def create_auth_token(username: str, password: str) -> str:
    return hashlib.sha256(f"{username}:{password}".encode()).hexdigest()

def authenticate(auth_token: str) -> bool:
    if not auth_token:
        return False
    users_file = Path(__file__).parent.parent / "server" / "users.json"
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
        for username, password in users.items():
            if create_auth_token(username, password) == auth_token:
                return True
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return False