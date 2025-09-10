# py
from supabase import create_client, Client
from app.core.config import get_settings
from jose import jwt, JWTError

settings = get_settings()
_supabase: Client | None = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _supabase

def verify_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError as e:
        raise ValueError("Invalid token") from e
