# py
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime

class UserProfileRequest(BaseModel):
    supabase_id: str = Field(..., min_length=1)
    email: Optional[EmailStr]
    full_name: Optional[str]
    birth_date: Optional[date]
    gender: Optional[str]

class HealthGenerateRequest(BaseModel):
    supabase_id: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1, max_length=2000)
    context: Dict[str, Any] = Field(default_factory=dict)

class HealthGenerateResponse(BaseModel):
    id: str
    aggregated_output: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    agents_output: Dict[str, Any]

class StreamAgentRequest(BaseModel):
    supabase_id: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1, max_length=2000)
    agent: Optional[str] = None  # if None orchestrator stream is used

class HealthInsightItem(BaseModel):
    id: str
    aggregated_output: str
    confidence: float
    created_at: datetime
