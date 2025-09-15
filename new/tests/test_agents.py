# # py
# import pytest
# import asyncio
# from app.services import agents

# @pytest.mark.asyncio
# async def test_run_agent_returns_expected_keys(monkeypatch):
#     async def fake_generate(messages, model="gpt-4o-mini", max_tokens=400):
#         return {"choices":[{"message":{"content":"Test response with recommendation"}}]}
#     monkeypatch.setattr("app.services.openai_client.async_generate", fake_generate)
#     res = await agents.run_agent("nutrition", {"age":30}, "test prompt")
#     assert "name" in res and "output" in res and "confidence" in res
#     assert res["name"] == "nutrition"

# @pytest.mark.asyncio
# async def test_run_agents_concurrently_aggregates(monkeypatch):
#     async def fake_generate(messages, model="gpt-4o-mini", max_tokens=400):
#         return {"choices":[{"message":{"content":"Generic advice"}}]}
#     monkeypatch.setattr("app.services.openai_client.async_generate", fake_generate)
#     result = await agents.run_agents_concurrently({"age":30}, "help me")
#     assert "agents" in result and "aggregated_output" in result and "confidence" in result
#     assert len(result["agents"]) == 4

import pytest
from unittest.mock import AsyncMock, patch
from app.services.agents import AgentOrchestrator, WorkoutPlan
from app.services.openai_client import openai_client

@pytest.mark.asyncio
async def test_run_agent():
    with patch.object(openai_client, 'call_with_tools', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = {"choices": [{"message": {"content": '{"title": "Test", "duration_minutes": 30, "exercises": []}'}}]}
        orch = AgentOrchestrator("test_user")
        result = await orch.run_agent("workout_generator", "test prompt", {})
        assert isinstance(result, dict)
        assert result["title"] == "Test"

@pytest.mark.asyncio
async def test_streaming():
    # Mock streaming chunks
    # Assert yields correct stages
    pass

# Run: pytest tests/ -v