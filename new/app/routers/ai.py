from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.services.agents import AgentOrchestrator
from app.core.security import get_current_user
from pydantic import BaseModel
import json
from typing import Dict, Any

router = APIRouter(prefix="/api/ai", tags=["ai"])

class StreamRequest(BaseModel):
    prompt: str
    stats: Dict[str, Any]
    options: Dict[str, Any] = {}

@router.post("/stream-agent-response")
async def stream_agent_response(req: StreamRequest, user=Depends(get_current_user), request: Request = None):
    orchestrator = AgentOrchestrator(user.id)
    async def event_generator():
        try:
            heartbeat = asyncio.create_task(send_heartbeat())
            async for chunk in orchestrator.stream_orchestrator(req.prompt, req.stats, req.options):
                yield chunk
            heartbeat.cancel()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            yield f"data: {{\"stage\": \"error\", \"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})

async def send_heartbeat():
    while True:
        await asyncio.sleep(15)
        yield "data: {\"type\": \"heartbeat\"}\n\n"

@router.post("/generate-workout")
async def generate_workout(body: Dict, user=Depends(get_current_user)):
    # Similar to above, non-streaming
    orchestrator = AgentOrchestrator(user.id)
    plan = await orchestrator.run_agent("workout_generator", body["prompt"], body.get("context", {}))
    return plan  # Validated WorkoutPlan

@router.post("/health/generate-insights")
async def generate_insights(body: Dict, user=Depends(get_current_user)):
    # Uses recovery_advisor + habit_coach
    # ...
    pass