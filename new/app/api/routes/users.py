# py
from fastapi import APIRouter
from app.schemas import UserProfileRequest
from app.services.supabase_service import upsert_user_profile

router = APIRouter()

@router.post("/users/profile")
async def upsert_profile(body: UserProfileRequest):
    record = upsert_user_profile(body.supabase_id, body.dict())
    return record
