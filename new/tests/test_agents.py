# py
import pytest
import asyncio
from app.services import agents

@pytest.mark.asyncio
async def test_run_agent_returns_expected_keys(monkeypatch):
    async def fake_generate(messages, model="gpt-4o-mini", max_tokens=400):
        return {"choices":[{"message":{"content":"Test response with recommendation"}}]}
    monkeypatch.setattr("app.services.openai_client.async_generate", fake_generate)
    res = await agents.run_agent("nutrition", {"age":30}, "test prompt")
    assert "name" in res and "output" in res and "confidence" in res
    assert res["name"] == "nutrition"

@pytest.mark.asyncio
async def test_run_agents_concurrently_aggregates(monkeypatch):
    async def fake_generate(messages, model="gpt-4o-mini", max_tokens=400):
        return {"choices":[{"message":{"content":"Generic advice"}}]}
    monkeypatch.setattr("app.services.openai_client.async_generate", fake_generate)
    result = await agents.run_agents_concurrently({"age":30}, "help me")
    assert "agents" in result and "aggregated_output" in result and "confidence" in result
    assert len(result["agents"]) == 4
