# py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from app.api.deps import get_current_user
from app.services.supabase_service import list_health_insights
from app.schemas import HealthInsightItem

router = APIRouter()

@router.get("/health/insights", response_model=List[HealthInsightItem])
async def get_insights(limit: int = Query(50, ge=1, le=100), user=Depends(get_current_user)):
    items = list_health_insights(user["supabase_id"], limit=limit)
    return items
