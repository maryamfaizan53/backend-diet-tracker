# py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
import json
from app.api.deps import get_current_user
from app.schemas import StreamAgentRequest, HealthGenerateRequest, HealthGenerateResponse
from app.services import agents as agent_svc
from app.services.supabase_service import create_health_insight
from app.core.config import get_settings
from app.services.openai_client import async_stream_chat
from loguru import logger

router = APIRouter()

settings = get_settings()

@router.post("/ai/stream-agent-response")
async def stream_agent(request: StreamAgentRequest, user=Depends(get_current_user)):
    user_context = request.supabase_id
    prompt = request.prompt
    agent = request.agent

    async def event_generator():
        try:
            if agent:
                # Single agent streaming
                system_prompt = agent_svc.AGENT_SPECS.get(agent)
                if not system_prompt:
                    raise HTTPException(status_code=400, detail="Unknown agent")
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": f"User context: {user}"}
                ]
                async for chunk in async_stream_chat(messages):
                    payload = {"agent": agent, "chunk": chunk}
                    yield f"data: {json.dumps(payload)}\n\n"
            else:
                # Orchestrator streaming by delegating to stream_orchestrator
                async for item in agent_svc.stream_orchestrator({"supabase_id": user["supabase_id"]}, prompt):
                    yield f"data: {json.dumps(item)}\n\n"
        except Exception as e:
            logger.exception("Streaming error")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/health/generate-insights", response_model=HealthGenerateResponse)
async def generate_insights(req: HealthGenerateRequest, user=Depends(get_current_user)):
    # Run orchestrator synchronously
    result = await agent_svc.run_agents_concurrently(req.context, req.prompt)
    # Save to Supabase
    saved = create_health_insight(user["supabase_id"], req.dict(), {r["name"]: r for r in result["agents"]}, result["aggregated_output"], result["confidence"])
    return HealthGenerateResponse(id=saved["id"], aggregated_output=result["aggregated_output"], confidence=result["confidence"], agents_output={r["name"]: r for r in result["agents"]})

@router.post("/customer-portal")
async def customer_portal(body: dict, user=Depends(get_current_user)):
    # Placeholder for Stripe customer portal integration - secure server-side only
    if not settings.STRIPE_SECRET_KEY:
        return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content={"message": "Stripe not configured"})
    # TODO: implement server-side Stripe session creation using STRIPE_SECRET_KEY
    return {"url": "https://stripe-portal.example/session-placeholder"}
