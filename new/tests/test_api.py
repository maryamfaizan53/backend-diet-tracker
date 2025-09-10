# py
import pytest
from httpx import AsyncClient
from main import app
from app.api.deps import get_current_user
from app.services import agents
import asyncio

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_generate_insights_endpoint(monkeypatch):
    async def fake_current_user():
        return {"supabase_id": "test-user"}
    monkeypatch.setattr("app.api.deps.get_current_user", lambda: fake_current_user())
    async def fake_run_agents_concurrently(context, prompt):
        return {"agents": [{"name":"nutrition","output":"ok","confidence":0.8}], "aggregated_output":"ok", "confidence":0.8}
    monkeypatch.setattr("app.services.agents.run_agents_concurrently", fake_run_agents_concurrently)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/health/generate-insights", json={"supabase_id":"test-user","prompt":"hi","context":{}})
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_stream_agent_response(monkeypatch):
    async def fake_current_user():
        return {"supabase_id": "test-user"}
    monkeypatch.setattr("app.api.deps.get_current_user", lambda: fake_current_user())
    # monkeypatch streaming to yield small chunks
    async def fake_stream_orch(ctx, prompt):
        for i in range(3):
            yield {"agent":"nutrition","chunk":f"part{i}"}
    monkeypatch.setattr("app.services.agents.stream_orchestrator", fake_stream_orch)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/ai/stream-agent-response", json={"supabase_id":"test-user","prompt":"hi"})
        assert resp.status_code == 200
        text = await resp.aread()
        assert b"data:" in text
