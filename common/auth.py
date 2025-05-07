import json
import hashlib
from pathlib import Path

def create_auth_token(username: str, password: str) -> str:
    """Cria um token de autenticação simples"""
    return hashlib.sha256(f"{username}:{password}".encode()).hexdigest()

def authenticate(auth_token: str) -> bool:
    """Verifica se o token é válido"""
    if not auth_token:
        return False
    
    users_file = Path(__file__).parent.parent / "server" / "users.json"
    
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
            
        # Verifica se algum usuário:senha combina com o token
        for username, password in users.items():
            if create_auth_token(username, password) == auth_token:
                return True
                
    except (FileNotFoundError, json.JSONDecodeError):
        pass
        
    return False