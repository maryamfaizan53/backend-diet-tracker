# py
from fastapi import Header, HTTPException, status
from app.utils.validators import get_bearer_token, verify_supabase_jwt
from app.core.rate_limiter import allow_request
from app.core.config import get_settings

settings = get_settings()

async def get_current_user(authorization: str = Header(...)):
    try:
        token = get_bearer_token(authorization)
        payload = verify_supabase_jwt(token)
        supabase_id = payload.get("sub")
        if not supabase_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        allowed = await allow_request(supabase_id)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        return {"supabase_id": supabase_id, "claims": payload}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization")
