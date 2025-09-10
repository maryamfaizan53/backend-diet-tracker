# py
from typing import Dict
from app.db.client import verify_jwt

def validate_prompt_length(prompt: str):
    if not (1 <= len(prompt) <= 2000):
        raise ValueError("prompt length must be between 1 and 2000")

def get_bearer_token(authorization_header: str) -> str:
    if not authorization_header:
        raise ValueError("Missing Authorization header")
    parts = authorization_header.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise ValueError("Invalid Authorization header")
    return parts[1]

def verify_supabase_jwt(token: str) -> Dict:
    return verify_jwt(token)
