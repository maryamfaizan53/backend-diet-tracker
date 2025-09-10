# py
from app.db.client import get_supabase
from loguru import logger
from typing import List, Dict
from datetime import datetime

supabase = get_supabase()

def upsert_user_profile(supabase_id: str, profile: Dict) -> Dict:
    # ensure users_profiles exists; upsert by supabase_id
    data = {
        "supabase_id": supabase_id,
        "email": profile.get("email"),
        "full_name": profile.get("full_name"),
        "birth_date": profile.get("birth_date"),
        "gender": profile.get("gender"),
        "updated_at": datetime.utcnow().isoformat()
    }
    resp = supabase.table("users_profiles").upsert(data, on_conflict="supabase_id").execute()
    if resp.error:
        logger.error("Supabase upsert_user_profile error: %s", resp.error.message)
        raise RuntimeError("DB error")
    return resp.data[0]

def create_health_insight(user_supabase_id: str, request_payload: Dict, agents_output: Dict, aggregated_output: str, confidence: float) -> Dict:
    # resolve user_id
    user = supabase.table("users_profiles").select("id").eq("supabase_id", user_supabase_id).maybe_single().execute()
    if user.error or not user.data:
        raise ValueError("User profile not found")
    payload = {
        "user_id": user.data["id"],
        "request_payload": request_payload,
        "agents_output": agents_output,
        "aggregated_output": aggregated_output,
        "confidence": confidence
    }
    resp = supabase.table("health_insights").insert(payload).execute()
    if resp.error:
        logger.error("Supabase create_health_insight error: %s", resp.error.message)
        raise RuntimeError("DB insert error")
    return resp.data[0]

def list_health_insights(user_supabase_id: str, limit: int = 50) -> List[Dict]:
    user = supabase.table("users_profiles").select("id").eq("supabase_id", user_supabase_id).maybe_single().execute()
    if user.error or not user.data:
        raise ValueError("User profile not found")
    resp = supabase.table("health_insights").select("*").eq("user_id", user.data["id"]).order("created_at", {"ascending": False}).limit(limit).execute()
    if resp.error:
        logger.error("Supabase list_health_insights error: %s", resp.error.message)
        raise RuntimeError("DB read error")
    return resp.data
